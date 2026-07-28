"""
ReportGenerator
===============
Produces a structured JSON intelligence report for every processed file.

Report structure
----------------
{
  "file":        { name, path, type, size_bytes },
  "cleaning":    { original_rows, final_rows, duplicates_removed,
                   nulls_filled, cols_renamed, empty_cols_dropped },
  "ml": {
    "classification": { label, confidence },
    "anomaly":        { total_rows, anomaly_count, anomaly_ratio,
                        numeric_cols_used }
  },
  "statistics":  { row_count, col_count, numeric_cols, string_cols,
                   col_stats: { col: { min, max, mean, null_count } } },
  "generated_at": "<ISO-8601 UTC timestamp>"
}

Reports are saved to  <OUTPUT_DIR>/reports/<filename>.report.json
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from app.cleaning.cleaner import CleaningReport
from app.config.settings import settings

logger = logging.getLogger("FileMonitor")


class ReportGenerator:

    def __init__(self) -> None:
        self._reports_dir = settings.OUTPUT_DIR / "reports"

    def generate(
        self,
        *,
        file_path: str,
        file_type: str,
        cleaning_report: CleaningReport,
        classification: tuple[str, float],
        anomaly_summary: dict[str, Any],
        data: pd.DataFrame,
    ) -> dict[str, Any]:
        """
        Build the full intelligence report dict and write it to disk.

        Returns the report dict (useful for logging / testing).
        """
        # ── File metadata ─────────────────────────────────────────────────────
        file_size = 0
        try:
            file_size = os.path.getsize(file_path)
        except OSError:
            pass

        # ── Column statistics ─────────────────────────────────────────────────
        numeric_cols = data.select_dtypes(include="number").columns.tolist()
        string_cols  = data.select_dtypes(exclude="number").columns.tolist()

        col_stats: dict[str, Any] = {}
        for col in numeric_cols:
            col_stats[col] = {
                "min":        _safe(data[col].min()),
                "max":        _safe(data[col].max()),
                "mean":       _safe(data[col].mean()),
                "null_count": int(data[col].isna().sum()),
            }

        # ── Assemble report ───────────────────────────────────────────────────
        report: dict[str, Any] = {
            "file": {
                "name":       os.path.basename(file_path),
                "path":       file_path,
                "type":       file_type,
                "size_bytes": file_size,
            },
            "cleaning": {
                "original_rows":     cleaning_report.original_rows,
                "final_rows":        cleaning_report.final_rows,
                "duplicates_removed": cleaning_report.duplicates_removed,
                "nulls_filled":      cleaning_report.nulls_filled,
                "cols_renamed":      cleaning_report.cols_renamed,
                "empty_cols_dropped": cleaning_report.empty_cols_dropped,
            },
            "ml": {
                "classification": {
                    "label":      classification[0],
                    "confidence": classification[1],
                },
                "anomaly": anomaly_summary,
            },
            "statistics": {
                "row_count":    len(data),
                "col_count":    len(data.columns),
                "numeric_cols": numeric_cols,
                "string_cols":  string_cols,
                "col_stats":    col_stats,
            },
            "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        }

        # ── Write to disk ─────────────────────────────────────────────────────
        self._reports_dir.mkdir(parents=True, exist_ok=True)
        stem = Path(file_path).stem
        out_path = self._reports_dir / f"{stem}.report.json"

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"[Report] Intelligence report saved: {out_path}")
        print(f"[Report] Saved: {out_path}")
        return report


# ── Helpers ───────────────────────────────────────────────────────────────────

def _safe(value: Any) -> Any:
    """Convert numpy scalars to native Python types for JSON serialisation."""
    if hasattr(value, "item"):
        return value.item()
    return value
