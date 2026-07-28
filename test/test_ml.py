"""
Tests for the ML layer:
  - app.model.features   — feature extraction
  - app.model.classifier — FileTypeClassifier
  - app.model.anomaly    — AnomalyDetector
  - app.model.report     — ReportGenerator
"""

import json
import os

import numpy as np
import pandas as pd
import pytest

from app.model.features import extract_features
from app.model.classifier import FileTypeClassifier, CATEGORIES
from app.model.anomaly import AnomalyDetector
from app.model.report import ReportGenerator
from app.cleaning.cleaner import CleaningReport


# ── Feature extraction ────────────────────────────────────────────────────────

class TestFeatureExtraction:

    def test_returns_13_features(self, csv_file):
        feats = extract_features(csv_file)
        assert len(feats) == 13

    def test_all_floats(self, csv_file):
        feats = extract_features(csv_file)
        assert all(isinstance(v, float) for v in feats)

    def test_nonexistent_file_returns_zeros(self):
        feats = extract_features("/nonexistent/path/file.csv")
        assert feats == [0.0] * 13

    def test_empty_file_returns_zeros(self, tmp_path):
        empty = tmp_path / "empty.txt"
        empty.write_text("", encoding="utf-8")
        feats = extract_features(str(empty))
        assert feats == [0.0] * 13

    def test_csv_has_high_comma_ratio(self, csv_file):
        feats = extract_features(csv_file)
        comma_ratio = feats[10]
        assert comma_ratio > 0.5   # most lines in a CSV have commas

    def test_json_has_high_kv_ratio(self, json_flat_file):
        feats = extract_features(json_flat_file)
        kv_ratio = feats[8]
        assert kv_ratio > 0.0


# ── Classifier ────────────────────────────────────────────────────────────────

class TestFileTypeClassifier:

    @pytest.fixture()
    def clf(self):
        return FileTypeClassifier()

    def test_predict_returns_known_category(self, clf, csv_file):
        label, confidence = clf.predict(csv_file)
        assert label in CATEGORIES

    def test_confidence_between_0_and_1(self, clf, csv_file):
        _, confidence = clf.predict(csv_file)
        assert 0.0 <= confidence <= 1.0

    def test_predict_txt_file(self, clf, txt_file):
        label, confidence = clf.predict(txt_file)
        assert label in CATEGORIES
        assert confidence > 0.0

    def test_predict_json_file(self, clf, json_flat_file):
        label, confidence = clf.predict(json_flat_file)
        assert label in CATEGORIES

    def test_predict_nonexistent_file(self, clf):
        # Should not raise — returns a prediction on zero features
        label, confidence = clf.predict("/nonexistent/path.csv")
        assert label in CATEGORIES

    def test_fit_and_predict(self, tmp_path):
        clf = FileTypeClassifier.__new__(FileTypeClassifier)
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import LabelEncoder
        clf._encoder = LabelEncoder().fit(CATEGORIES)
        clf._model = RandomForestClassifier(n_estimators=10, random_state=0)
        X = np.random.default_rng(0).random((50, 13))
        y = (CATEGORIES * 10)[:50]
        clf._model.fit(X, y)
        label, conf = clf.predict("/any/file.csv")
        assert label in CATEGORIES


# ── Anomaly Detector ──────────────────────────────────────────────────────────

class TestAnomalyDetector:

    @pytest.fixture()
    def numeric_df(self):
        rng = np.random.default_rng(42)
        normal = pd.DataFrame({"x": rng.normal(0, 1, 50), "y": rng.normal(0, 1, 50)})
        # Add obvious outliers
        outliers = pd.DataFrame({"x": [100.0, -100.0], "y": [100.0, -100.0]})
        return pd.concat([normal, outliers], ignore_index=True)

    @pytest.fixture()
    def string_only_df(self):
        return pd.DataFrame({"name": ["Alice", "Bob", "Charlie"]})

    def test_adds_anomaly_column(self, numeric_df):
        result, _ = AnomalyDetector().detect(numeric_df)
        assert "_anomaly" in result.columns

    def test_anomaly_column_is_bool(self, numeric_df):
        result, _ = AnomalyDetector().detect(numeric_df)
        assert result["_anomaly"].dtype == bool

    def test_flags_obvious_outliers(self, numeric_df):
        result, summary = AnomalyDetector().detect(numeric_df)
        assert summary["anomaly_count"] > 0

    def test_summary_keys_present(self, numeric_df):
        _, summary = AnomalyDetector().detect(numeric_df)
        assert {"total_rows", "anomaly_count", "anomaly_ratio", "numeric_cols_used"} == set(summary)

    def test_anomaly_ratio_between_0_and_1(self, numeric_df):
        _, summary = AnomalyDetector().detect(numeric_df)
        assert 0.0 <= summary["anomaly_ratio"] <= 1.0

    def test_no_numeric_cols_skipped(self, string_only_df):
        result, summary = AnomalyDetector().detect(string_only_df)
        assert "_anomaly" in result.columns
        assert summary["anomaly_count"] == 0
        assert summary["numeric_cols_used"] == []

    def test_single_row_skipped(self):
        df = pd.DataFrame({"x": [1.0]})
        result, summary = AnomalyDetector().detect(df)
        assert summary["anomaly_count"] == 0

    def test_does_not_mutate_input(self, numeric_df):
        original_cols = list(numeric_df.columns)
        AnomalyDetector().detect(numeric_df)
        assert list(numeric_df.columns) == original_cols


# ── Report Generator ──────────────────────────────────────────────────────────

class TestReportGenerator:

    @pytest.fixture()
    def sample_df(self):
        return pd.DataFrame({"id": [1, 2, 3], "name": ["a", "b", "c"], "score": [10.0, 20.0, 30.0]})

    @pytest.fixture()
    def cleaning_report(self):
        r = CleaningReport()
        r.original_rows = 4
        r.final_rows    = 3
        r.duplicates_removed = 1
        return r

    def test_report_written_to_disk(self, tmp_path, csv_file, sample_df, cleaning_report, monkeypatch):
        from app.config import settings
        monkeypatch.setattr(settings, "OUTPUT_DIR", tmp_path)

        gen = ReportGenerator()
        gen.generate(
            file_path=csv_file,
            file_type="csv",
            cleaning_report=cleaning_report,
            classification=("user_data", 0.82),
            anomaly_summary={"total_rows": 3, "anomaly_count": 0, "anomaly_ratio": 0.0, "numeric_cols_used": []},
            data=sample_df,
        )
        reports_dir = tmp_path / "reports"
        report_files = list(reports_dir.glob("*.report.json"))
        assert len(report_files) == 1

    def test_report_is_valid_json(self, tmp_path, csv_file, sample_df, cleaning_report, monkeypatch):
        from app.config import settings
        monkeypatch.setattr(settings, "OUTPUT_DIR", tmp_path)

        gen = ReportGenerator()
        gen.generate(
            file_path=csv_file,
            file_type="csv",
            cleaning_report=cleaning_report,
            classification=("user_data", 0.82),
            anomaly_summary={"total_rows": 3, "anomaly_count": 0, "anomaly_ratio": 0.0, "numeric_cols_used": []},
            data=sample_df,
        )
        report_file = list((tmp_path / "reports").glob("*.report.json"))[0]
        with open(report_file, encoding="utf-8") as f:
            data = json.load(f)
        assert "file" in data
        assert "cleaning" in data
        assert "ml" in data
        assert "statistics" in data
        assert "generated_at" in data

    def test_report_dict_returned(self, tmp_path, csv_file, sample_df, cleaning_report, monkeypatch):
        from app.config import settings
        monkeypatch.setattr(settings, "OUTPUT_DIR", tmp_path)

        gen = ReportGenerator()
        result = gen.generate(
            file_path=csv_file,
            file_type="csv",
            cleaning_report=cleaning_report,
            classification=("financial", 0.65),
            anomaly_summary={"total_rows": 3, "anomaly_count": 1, "anomaly_ratio": 0.33, "numeric_cols_used": ["score"]},
            data=sample_df,
        )
        assert isinstance(result, dict)
        assert result["ml"]["classification"]["label"] == "financial"
        assert result["ml"]["anomaly"]["anomaly_count"] == 1

    def test_col_stats_for_numeric_columns(self, tmp_path, csv_file, sample_df, cleaning_report, monkeypatch):
        from app.config import settings
        monkeypatch.setattr(settings, "OUTPUT_DIR", tmp_path)

        gen = ReportGenerator()
        result = gen.generate(
            file_path=csv_file,
            file_type="csv",
            cleaning_report=cleaning_report,
            classification=("financial", 0.65),
            anomaly_summary={"total_rows": 3, "anomaly_count": 0, "anomaly_ratio": 0.0, "numeric_cols_used": []},
            data=sample_df,
        )
        col_stats = result["statistics"]["col_stats"]
        assert "score" in col_stats
        assert col_stats["score"]["min"] == 10.0
        assert col_stats["score"]["max"] == 30.0
