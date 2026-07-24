"""Tests for CSV, JSON, and TXT processors"""

import json
import os

import pandas as pd
import pytest

from app.processors.csv_processor import CSVProcessor
from app.processors.json_processor import JsonProcessor
from app.processors.txt_processor import TXTProcessor


# ── CSV ───────────────────────────────────────────────────────────────────────

class TestCSVProcessor:

    def test_load_returns_dataframe(self, csv_file):
        df = CSVProcessor().load(csv_file)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 4                # 4 rows including duplicate

    def test_process_removes_duplicates(self, csv_file):
        p = CSVProcessor()
        result = p.process(p.load(csv_file))
        assert len(result) == 3            # duplicate removed

    def test_process_fills_string_nulls(self, csv_file):
        p = CSVProcessor()
        result = p.process(p.load(csv_file))
        assert result["name"].isna().sum() == 0

    def test_save_creates_file(self, csv_file, tmp_output):
        p = CSVProcessor()
        out = str(tmp_output / "out.csv")
        p.save(p.process(p.load(csv_file)), out)
        assert os.path.exists(out)
        reloaded = pd.read_csv(out)
        assert len(reloaded) == 3


# ── JSON ──────────────────────────────────────────────────────────────────────

class TestJsonProcessor:

    def test_load_array_json(self, json_array_file):
        df = JsonProcessor().load(json_array_file)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3

    def test_load_flat_json(self, json_flat_file):
        df = JsonProcessor().load(json_flat_file)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert "status" in df.columns

    def test_process_removes_duplicates(self, json_array_file):
        p = JsonProcessor()
        result = p.process(p.load(json_array_file))
        assert len(result) == 2            # one duplicate removed

    def test_process_fills_numeric_nulls(self, json_array_file):
        p = JsonProcessor()
        result = p.process(p.load(json_array_file))
        assert result["score"].isna().sum() == 0
        assert 0.0 in result["score"].values

    def test_save_creates_valid_json(self, json_array_file, tmp_output):
        p = JsonProcessor()
        out = str(tmp_output / "out.json")
        p.save(p.process(p.load(json_array_file)), out)
        assert os.path.exists(out)
        with open(out, encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, list)
        assert len(data) == 2


# ── TXT ───────────────────────────────────────────────────────────────────────

class TestTXTProcessor:

    def test_load_returns_list(self, txt_file):
        lines = TXTProcessor().load(txt_file)
        assert isinstance(lines, list)

    def test_process_removes_blank_lines(self, txt_file):
        p = TXTProcessor()
        result = p.process(p.load(txt_file))
        assert all(line.strip() != "" for line in result)
        assert len(result) == 3            # "hello world", "foo bar", "baz"

    def test_process_strips_whitespace(self, txt_file):
        p = TXTProcessor()
        result = p.process(p.load(txt_file))
        assert "baz" in result             # "  baz  " stripped

    def test_save_creates_file(self, txt_file, tmp_output):
        p = TXTProcessor()
        out = str(tmp_output / "out.txt")
        p.save(p.process(p.load(txt_file)), out)
        assert os.path.exists(out)
        with open(out, encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
        assert len(lines) == 3
