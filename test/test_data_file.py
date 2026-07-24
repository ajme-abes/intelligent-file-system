"""Tests for app.core.data_file.DataFile"""

import pytest
from app.core.data_file import DataFile


def test_csv_detection(csv_file):
    df = DataFile(csv_file)
    assert df.file_type == "csv"
    assert df.extension == ".csv"
    assert df.name == "users.csv"


def test_json_detection(json_flat_file):
    df = DataFile(json_flat_file)
    assert df.file_type == "json"


def test_txt_detection(txt_file):
    df = DataFile(txt_file)
    assert df.file_type == "txt"


def test_unsupported_raises(png_file):
    with pytest.raises(ValueError, match="Unsupported file type"):
        DataFile(png_file)


def test_metadata_keys(csv_file):
    meta = DataFile(csv_file).get_metadata()
    assert set(meta.keys()) == {"name", "path", "type"}
