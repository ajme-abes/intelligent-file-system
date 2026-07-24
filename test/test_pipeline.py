"""Integration tests for ProcessingPipeline.run()"""

import json
import os

import pytest

from app.pipeline.pipeline import ProcessingPipeline


@pytest.fixture()
def pipeline():
    return ProcessingPipeline()


# ── Happy paths ───────────────────────────────────────────────────────────────

def test_pipeline_processes_csv(pipeline, csv_file, tmp_output, monkeypatch):
    # Point the pipeline output to our isolated tmp_output
    from app.config import settings
    monkeypatch.setattr(settings, "OUTPUT_DIR", tmp_output)

    result = pipeline.run(csv_file)
    assert result is True
    assert (tmp_output / "processed_users.csv").exists()


def test_pipeline_processes_json_array(pipeline, json_array_file, tmp_output, monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "OUTPUT_DIR", tmp_output)

    result = pipeline.run(json_array_file)
    assert result is True
    out = tmp_output / "processed_records.json"
    assert out.exists()
    with open(out, encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)


def test_pipeline_processes_txt(pipeline, txt_file, tmp_output, monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "OUTPUT_DIR", tmp_output)

    result = pipeline.run(txt_file)
    assert result is True
    assert (tmp_output / "processed_notes.txt").exists()


# ── Failure paths ─────────────────────────────────────────────────────────────

def test_pipeline_rejects_unsupported_type(pipeline, png_file):
    result = pipeline.run(png_file)
    assert result is False


def test_pipeline_handles_nonexistent_file(pipeline, tmp_output, monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "OUTPUT_DIR", tmp_output)

    result = pipeline.run("/nonexistent/path/file.csv")
    assert result is False


def test_pipeline_handles_empty_csv(pipeline, tmp_input, tmp_output, monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "OUTPUT_DIR", tmp_output)

    empty = tmp_input / "empty.csv"
    empty.write_text("id,name\n", encoding="utf-8")  # header only, no data rows
    result = pipeline.run(str(empty))
    assert result is True   # empty file is valid — outputs empty CSV


def test_pipeline_handles_malformed_json(pipeline, tmp_input, tmp_output, monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "OUTPUT_DIR", tmp_output)

    bad = tmp_input / "bad.json"
    bad.write_text("{not valid json", encoding="utf-8")
    result = pipeline.run(str(bad))
    assert result is False
