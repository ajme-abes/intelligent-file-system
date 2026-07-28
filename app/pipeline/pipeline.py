"""
ProcessingPipeline
==================
Orchestrates the full file-processing lifecycle:

  1. Validate  — check file type is supported
  2. Load      — delegate to the correct processor (CSV / JSON / TXT)
  3. Clean     — DataCleaner normalises, deduplicates, fills nulls
  4. Classify  — FileTypeClassifier predicts semantic category
  5. Detect    — AnomalyDetector flags outlier rows (tabular files only)
  6. Save      — processed data written to data/output/
  7. Report    — intelligence report written to data/output/reports/
"""

import threading
from typing import Any

import pandas as pd

from app.config.settings import settings
from app.core.data_file import DataFile
from app.utils.validator import is_supported_file
from app.processors.csv_processor import CSVProcessor
from app.processors.json_processor import JsonProcessor
from app.processors.txt_processor import TXTProcessor
from app.model.classifier import FileTypeClassifier
from app.model.anomaly import AnomalyDetector
from app.model.report import ReportGenerator
from app.monitoring.logging import logger


class ProcessingPipeline:

    def __init__(self) -> None:
        self._processors = {
            "csv":  CSVProcessor(),
            "json": JsonProcessor(),
            "txt":  TXTProcessor(),
        }
        self._classifier = FileTypeClassifier()
        self._detector   = AnomalyDetector()
        self._reporter   = ReportGenerator()

    def get_processor(self, file_type: str):
        return self._processors.get(file_type)

    def run(self, file_path: str) -> bool:
        thread_name = threading.current_thread().name
        print(f"\n[Pipeline Start] {file_path}  (thread: {thread_name})")

        # ── 1. Validate ───────────────────────────────────────────────────────
        if not is_supported_file(file_path):
            logger.error(f"Unsupported file type: {file_path}")
            print(f"[Pipeline Failed] Unsupported file type: {file_path}")
            return False

        try:
            data_file = DataFile(file_path)
            processor = self.get_processor(data_file.file_type)

            if not processor:
                logger.error(f"No processor found for file type: {data_file.file_type}")
                print(f"[Pipeline Failed] No processor found for: {data_file.file_type}")
                return False

            # ── 2. Load ───────────────────────────────────────────────────────
            raw_data = processor.load(data_file.path)

            # ── 3. Clean (processor.process() runs DataCleaner internally) ───
            cleaned_data = processor.process(raw_data)

            # Retrieve cleaning report for the report generator.
            # Processors expose it via _cleaner; TXT has no cleaner.
            cleaning_report = _get_cleaning_report(processor, raw_data, cleaned_data)

            # ── 4. Classify ───────────────────────────────────────────────────
            label, confidence = self._classifier.predict(data_file.path)
            print(f"[ML] Classification: {label}  (confidence: {confidence:.1%})")
            logger.info(f"[ML] {data_file.name} → {label} ({confidence:.1%})")

            # ── 5. Anomaly detection (tabular only) ───────────────────────────
            anomaly_summary: dict[str, Any] = {
                "total_rows": 0, "anomaly_count": 0,
                "anomaly_ratio": 0.0, "numeric_cols_used": [],
            }

            if isinstance(cleaned_data, pd.DataFrame):
                annotated, anomaly_summary = self._detector.detect(cleaned_data)
                if anomaly_summary["anomaly_count"] > 0:
                    print(
                        f"[ML] Anomalies: {anomaly_summary['anomaly_count']} / "
                        f"{anomaly_summary['total_rows']} rows flagged"
                    )
                # Save the anomaly-annotated version
                final_data = annotated
            else:
                final_data = cleaned_data

            # ── 6. Save processed file ────────────────────────────────────────
            settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            output_path = settings.OUTPUT_DIR / f"processed_{data_file.name}"
            processor.save(final_data, str(output_path))

            logger.info(f"Processed file saved: {output_path}")
            print(f"[Pipeline Success] Saved to: {output_path}")

            # ── 7. Generate intelligence report ───────────────────────────────
            report_data = final_data if isinstance(final_data, pd.DataFrame) else pd.DataFrame()
            self._reporter.generate(
                file_path=data_file.path,
                file_type=data_file.file_type,
                cleaning_report=cleaning_report,
                classification=(label, confidence),
                anomaly_summary=anomaly_summary,
                data=report_data,
            )

        except Exception as e:
            logger.error(f"Failed to process file {file_path}: {e}", exc_info=True)
            print(f"[Pipeline Failed] Error processing {file_path}: {e}")
            return False

        return True


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_cleaning_report(processor, raw_data, cleaned_data):
    """
    Extract the CleaningReport from the processor if available,
    otherwise run the cleaner again to get it (safe — cleaner is pure).
    For TXTProcessor (no DataFrame cleaner) return a minimal report.
    """
    from app.cleaning.cleaner import CleaningReport, DataCleaner

    if hasattr(processor, "_cleaner"):
        # Re-run clean() to get the report — it's a pure function, no side effects
        _, report = processor._cleaner.clean(
            raw_data if isinstance(raw_data, pd.DataFrame) else pd.DataFrame()
        )
        return report

    # TXT processor — build a minimal report from line counts
    report = CleaningReport()
    if isinstance(raw_data, list) and isinstance(cleaned_data, list):
        report.original_rows = len(raw_data)
        report.final_rows    = len(cleaned_data)
        report.duplicates_removed = len(raw_data) - len(cleaned_data)
    return report
