"""
DataCleaner — production-grade data cleaning for DataFrame-based processors.

Responsibilities:
  - Remove exact duplicate rows
  - Type-aware null imputation  (numeric → 0, string → "")
  - Strip leading/trailing whitespace from all string columns
  - Drop columns that are entirely empty (all NaN)
  - Normalise column names  (lowercase, spaces → underscores)
  - Report a cleaning summary so callers can log what changed
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import pandas as pd

logger = logging.getLogger("FileMonitor")


@dataclass
class CleaningReport:
    """Immutable record of every transformation applied during a cleaning run."""

    original_rows: int = 0
    original_cols: int = 0
    duplicates_removed: int = 0
    nulls_filled: dict[str, int] = field(default_factory=dict)
    empty_cols_dropped: list[str] = field(default_factory=list)
    cols_renamed: dict[str, str] = field(default_factory=dict)
    final_rows: int = 0
    final_cols: int = 0

    def summary(self) -> str:
        lines = [
            f"Rows : {self.original_rows} → {self.final_rows}  "
            f"(removed {self.duplicates_removed} duplicates)",
            f"Cols : {self.original_cols} → {self.final_cols}  "
            f"(dropped {len(self.empty_cols_dropped)} empty)",
        ]
        if self.nulls_filled:
            filled = ", ".join(f"{c}:{n}" for c, n in self.nulls_filled.items())
            lines.append(f"Nulls filled: {filled}")
        if self.cols_renamed:
            renamed = ", ".join(f"{o}→{n}" for o, n in self.cols_renamed.items())
            lines.append(f"Cols renamed: {renamed}")
        return " | ".join(lines)


class DataCleaner:
    """
    Applies a configurable cleaning pipeline to a pandas DataFrame.

    Parameters
    ----------
    normalise_columns : bool
        Lowercase column names and replace spaces with underscores. Default True.
    drop_empty_cols : bool
        Drop columns where every value is NaN. Default True.
    strip_strings : bool
        Strip whitespace from all string/object columns. Default True.
    """

    def __init__(
        self,
        normalise_columns: bool = True,
        drop_empty_cols: bool = True,
        strip_strings: bool = True,
    ) -> None:
        self.normalise_columns = normalise_columns
        self.drop_empty_cols = drop_empty_cols
        self.strip_strings = strip_strings

    def clean(self, data: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
        """
        Run the full cleaning pipeline.

        Returns
        -------
        tuple[pd.DataFrame, CleaningReport]
            The cleaned DataFrame and a report describing every change made.
        """
        report = CleaningReport(
            original_rows=len(data),
            original_cols=len(data.columns),
        )

        data = data.copy()  # never mutate the caller's data

        # 1. Normalise column names
        if self.normalise_columns:
            new_names = {
                col: col.strip().lower().replace(" ", "_")
                for col in data.columns
                if col != col.strip().lower().replace(" ", "_")
            }
            if new_names:
                data.rename(columns=new_names, inplace=True)
                report.cols_renamed = new_names

        # 2. Drop fully-empty columns
        if self.drop_empty_cols:
            empty = [c for c in data.columns if data[c].isna().all()]
            if empty:
                data.drop(columns=empty, inplace=True)
                report.empty_cols_dropped = empty

        # 3. Strip whitespace from string columns (before dedup so values compare cleanly)
        if self.strip_strings:
            for col in data.select_dtypes(include=["object", "string"]).columns:
                data[col] = data[col].str.strip()

        # 4. Remove duplicate rows (after strip so "Bob " == "Bob" deduplicates correctly)
        before = len(data)
        data.drop_duplicates(inplace=True)
        report.duplicates_removed = before - len(data)

        # 5. Type-aware null imputation
        nulls_filled: dict[str, int] = {}
        for col in data.columns:
            null_count = int(data[col].isna().sum())
            if null_count == 0:
                continue
            if pd.api.types.is_numeric_dtype(data[col]):
                data[col] = data[col].fillna(0)
            else:
                data[col] = data[col].fillna("")
            nulls_filled[col] = null_count
        report.nulls_filled = nulls_filled

        report.final_rows = len(data)
        report.final_cols = len(data.columns)

        logger.info(f"[Cleaning] {report.summary()}")
        return data, report
