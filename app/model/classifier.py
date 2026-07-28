"""
FileTypeClassifier
==================
Predicts the *semantic category* of a file based on its content features.

Categories
----------
  config      — configuration files  (JSON/YAML-like, key=value heavy)
  user_data   — tabular records with names/IDs (CSV-like)
  financial   — numeric-heavy tables (scores, amounts, prices)
  log         — timestamped or comment-heavy text
  unknown     — everything else

The classifier is a Random Forest trained on synthetic seed data that
covers the shape of each category.  When a real labelled dataset is
available, call  `FileTypeClassifier.fit(X, y)` and `save()` to replace
the seed model.

The trained model is persisted to  <root>/app/model/weights/classifier.joblib
so it survives process restarts.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

from app.model.features import extract_features

logger = logging.getLogger("FileMonitor")

# Where the trained model lives on disk
_WEIGHTS_DIR = Path(__file__).parent / "weights"
_MODEL_PATH = _WEIGHTS_DIR / "classifier.joblib"

CATEGORIES = ["config", "user_data", "financial", "log", "unknown"]


def _seed_training_data() -> tuple[np.ndarray, np.ndarray]:
    """
    Generate synthetic training samples so the model works out-of-the-box
    without requiring a labelled dataset.

    Feature index reference — see features.py:
      0=log_size, 1=log_lines, 2=avg_line_len, 3=digit_ratio, 4=alpha_ratio,
      5=space_ratio, 6=punct_ratio, 7=unique_chars, 8=kv_ratio,
      9=json_ratio, 10=comma_ratio, 11=blank_ratio, 12=comment_ratio
    """
    rng = np.random.default_rng(42)

    def _jitter(base: List[float], n: int = 30, noise: float = 0.05) -> np.ndarray:
        arr = np.array(base, dtype=float)
        return arr + rng.normal(0, noise, size=(n, len(arr)))

    # config  — kv_ratio high, json_ratio high, few commas
    config = _jitter([6.0, 3.0, 0.15, 0.05, 0.30, 0.10, 0.10, 0.50, 0.70, 0.60, 0.05, 0.05, 0.05])
    # user_data — comma_ratio high, moderate alpha, low kv
    user = _jitter([7.0, 4.0, 0.20, 0.10, 0.45, 0.12, 0.08, 0.45, 0.10, 0.00, 0.80, 0.02, 0.01])
    # financial — digit_ratio high, comma_ratio high
    fin = _jitter([7.5, 4.0, 0.18, 0.30, 0.25, 0.12, 0.10, 0.40, 0.05, 0.00, 0.75, 0.02, 0.01])
    # log — comment_ratio high, blank_ratio higher, moderate alpha
    log = _jitter([8.0, 5.0, 0.25, 0.08, 0.40, 0.15, 0.12, 0.55, 0.10, 0.00, 0.05, 0.10, 0.35])
    # unknown — balanced / random-ish
    unk = _jitter([5.0, 2.5, 0.12, 0.12, 0.35, 0.18, 0.15, 0.42, 0.20, 0.10, 0.15, 0.08, 0.08])

    X = np.clip(np.vstack([config, user, fin, log, unk]), 0.0, None)
    y = np.array(
        ["config"] * 30 + ["user_data"] * 30
        + ["financial"] * 30 + ["log"] * 30 + ["unknown"] * 30
    )
    return X, y


class FileTypeClassifier:
    """
    Thin wrapper around a scikit-learn RandomForestClassifier.

    Usage
    -----
    clf = FileTypeClassifier()        # loads from disk or trains on seed data
    label, confidence = clf.predict("path/to/file.csv")
    """

    def __init__(self) -> None:
        self._encoder = LabelEncoder().fit(CATEGORIES)
        self._model: RandomForestClassifier | None = None
        self._load_or_train()

    # ── Public API ────────────────────────────────────────────────────────────

    def predict(self, file_path: str) -> tuple[str, float]:
        """
        Predict the semantic category of *file_path*.

        Returns
        -------
        (label, confidence)
            label      — one of CATEGORIES
            confidence — probability of the top prediction  (0.0 – 1.0)
        """
        features = np.array(extract_features(file_path)).reshape(1, -1)
        proba = self._model.predict_proba(features)[0]
        idx = int(np.argmax(proba))
        label = self._model.classes_[idx]
        return label, round(float(proba[idx]), 4)

    def fit(self, X: np.ndarray, y: np.ndarray) -> "FileTypeClassifier":
        """Train (or re-train) the model on a provided dataset."""
        self._model = RandomForestClassifier(n_estimators=100, random_state=42)
        self._model.fit(X, y)
        logger.info(f"[Classifier] Model trained on {len(y)} samples.")
        return self

    def save(self) -> None:
        """Persist the trained model to disk."""
        _WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(self._model, _MODEL_PATH)
        logger.info(f"[Classifier] Model saved to {_MODEL_PATH}")

    # ── Private ───────────────────────────────────────────────────────────────

    def _load_or_train(self) -> None:
        if _MODEL_PATH.exists():
            try:
                self._model = joblib.load(_MODEL_PATH)
                logger.info(f"[Classifier] Loaded model from {_MODEL_PATH}")
                return
            except Exception as e:
                logger.warning(f"[Classifier] Could not load model ({e}), retraining.")

        logger.info("[Classifier] No saved model found — training on seed data.")
        X, y = _seed_training_data()
        self.fit(X, y)
        self.save()
