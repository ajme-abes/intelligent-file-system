"""
Pytest configuration and shared fixtures for the Intelliginet test suite.

All tests use isolated temporary directories so they never touch the real
data/input or data/output folders.
"""

import json
import os
import pytest
import pandas as pd


# ── Helpers ───────────────────────────────────────────────────────────────────

def _write(path: str, content: str) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture()
def tmp_input(tmp_path):
    """Isolated input directory under pytest's tmp_path."""
    d = tmp_path / "input"
    d.mkdir()
    return d


@pytest.fixture()
def tmp_output(tmp_path):
    """Isolated output directory under pytest's tmp_path."""
    d = tmp_path / "output"
    d.mkdir()
    return d


@pytest.fixture()
def csv_file(tmp_input):
    """Valid CSV with duplicates and a missing value."""
    p = tmp_input / "users.csv"
    p.write_text(
        "id,name,role\n"
        "1,Alice,Admin\n"
        "2,Bob,User\n"
        "2,Bob,User\n"       # duplicate
        "3,,Viewer\n",       # missing name
        encoding="utf-8",
    )
    return str(p)


@pytest.fixture()
def json_array_file(tmp_input):
    """Array-of-objects JSON (most common real-world shape)."""
    p = tmp_input / "records.json"
    p.write_text(
        json.dumps([
            {"id": 1, "name": "Alice", "score": None},
            {"id": 2, "name": "Bob",   "score": 90},
            {"id": 2, "name": "Bob",   "score": 90},  # duplicate
        ]),
        encoding="utf-8",
    )
    return str(p)


@pytest.fixture()
def json_flat_file(tmp_input):
    """Flat-dict JSON → should become a single-row DataFrame."""
    p = tmp_input / "config.json"
    p.write_text(json.dumps({"status": "active", "version": 1}), encoding="utf-8")
    return str(p)


@pytest.fixture()
def txt_file(tmp_input):
    """Text file with blank lines and whitespace."""
    p = tmp_input / "notes.txt"
    p.write_text("hello world\n\n  \nfoo bar\n  baz  \n", encoding="utf-8")
    return str(p)


@pytest.fixture()
def png_file(tmp_input):
    """Unsupported file type."""
    p = tmp_input / "image.png"
    p.write_bytes(b"\x89PNG\r\n\x1a\n")
    return str(p)
