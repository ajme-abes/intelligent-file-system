"""Tests for app.cleaning.cleaner.DataCleaner"""

import pandas as pd
import pytest
from app.cleaning.cleaner import DataCleaner


@pytest.fixture()
def dirty_df():
    return pd.DataFrame({
        "ID": [1, 2, 2, 3],
        "Name ": ["Alice", "Bob", "Bob", None],   # trailing space in col name, one null; rows 2&3 identical
        "Score": [95.0, 80.0, 80.0, 70.0],        # rows 2&3 identical (no null here)
        "Empty Col": [None, None, None, None],     # fully empty — will be dropped before dedup
    })


def test_duplicates_removed(dirty_df):
    cleaner = DataCleaner()
    result, report = cleaner.clean(dirty_df)
    assert report.duplicates_removed == 1
    assert len(result) == 3


def test_empty_column_dropped(dirty_df):
    cleaner = DataCleaner(drop_empty_cols=True)
    result, report = cleaner.clean(dirty_df)
    assert "empty_col" not in result.columns
    assert len(report.empty_cols_dropped) == 1


def test_numeric_null_filled_with_zero():
    df = pd.DataFrame({"value": [1.0, None, 3.0]})
    result, report = DataCleaner().clean(df)
    assert result["value"].isna().sum() == 0
    assert 0 in result["value"].values
    assert "value" in report.nulls_filled


def test_string_null_filled_with_empty_string():
    df = pd.DataFrame({"name": ["Alice", None, "Charlie"]})
    result, report = DataCleaner().clean(df)
    assert result["name"].isna().sum() == 0
    assert "" in result["name"].values
    assert "name" in report.nulls_filled


def test_column_name_normalised(dirty_df):
    cleaner = DataCleaner(normalise_columns=True)
    result, report = cleaner.clean(dirty_df)
    assert "name" in result.columns        # "Name " → "name"
    assert "Name " not in result.columns


def test_report_summary_not_empty(dirty_df):
    _, report = DataCleaner().clean(dirty_df)
    summary = report.summary()
    assert isinstance(summary, str)
    assert len(summary) > 0


def test_original_dataframe_not_mutated(dirty_df):
    original_shape = dirty_df.shape
    DataCleaner().clean(dirty_df)
    assert dirty_df.shape == original_shape


def test_no_normalise_option():
    df = pd.DataFrame({"My Column": [1, 2]})
    cleaner = DataCleaner(normalise_columns=False)
    result, _ = cleaner.clean(df)
    assert "My Column" in result.columns
