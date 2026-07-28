"""
AnomalyDetector
===============
Uses scikit-learn's IsolationForest to flag statistically anomalous rows
in tabular (CSV / JSON) data.

How it works
------------
1. Extract all numeric columns from the cleaned DataFrame.
2. Fit an IsolationForest on those columns.
3. Predict -1 (anomaly) or +1 (normal) for every row.
4. Add an  `_anomaly`  boolean column to the DataFrame.
5. Return the annotated DataFrame + a summary dict.

If there are no numeric columns (e.g. a pure-text CSV) the DataFrame is
returned unchanged with an empty summary.
"""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd
from sklearn.ensemble import IsolationForest

logger = logging.getLogger("FileMonitor")


class AnomalyDetector:
    """
    Wraps IsolationForest for per-file anomaly detection.

    Parameters
    ----------
    contamination : float | "auto"
        Expected fraction of anomalies in the data.
        "auto" lets IsolationForest decide (recommended for unknown data).
    random_state : int
        Seed for reproducibility.
    """

    def __init__(
        self,
        contamination: float | str = "auto",
        random_state: int = 42,
    ) -> None:
        self.contamination = contamination
        self.random_state = random_state

    def detect(self, data: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
        """
        Annotate *data* with an `_anomaly` column and return a summary.

        Returns
        -------
        (annotated_df, summary)
            annotated_df — original DataFrame + boolean `_anomaly` column
            summary      — dict with keys: total_rows, anomaly_count,
                           anomaly_ratio, numeric_cols_used
        """
        numeric_cols = data.select_dtypes(include="number").columns.tolist()

        empty_summary: dict[str, Any] = {
            "total_rows": len(data),
            "anomaly_count": 0,
            "anomaly_ratio": 0.0,
            "numeric_cols_used": [],
        }

        if not numeric_cols or len(data) < 2:
            logger.info("[Anomaly] Skipped — insufficient numeric data.")
            result = data.copy()
            result["_anomaly"] = False
            return result, empty_summary

        X = data[numeric_cols].fillna(0).values

        iso = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
        )
        predictions = iso.fit_predict(X)   # +1 = normal, -1 = anomaly
        is_anomaly = predictions == -1

        result = data.copy()
        result["_anomaly"] = is_anomaly

        anomaly_count = int(is_anomaly.sum())
        summary: dict[str, Any] = {
            "total_rows": len(data),
            "anomaly_count": anomaly_count,
            "anomaly_ratio": round(anomaly_count / len(data), 4),
            "numeric_cols_used": numeric_cols,
        }

        logger.info(
            f"[Anomaly] {anomaly_count}/{len(data)} rows flagged "
            f"({summary['anomaly_ratio']:.1%}) "
            f"using cols: {numeric_cols}"
        )
        return result, summary
