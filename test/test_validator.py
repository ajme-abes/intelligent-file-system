"""Tests for app.utils.validator"""

import pytest
from app.utils.validator import is_supported_file


@pytest.mark.parametrize("path,expected", [
    ("file.csv",   True),
    ("file.CSV",   True),   # case-insensitive
    ("file.json",  True),
    ("file.JSON",  True),
    ("file.txt",   True),
    ("file.TXT",   True),
    ("file.png",   False),
    ("file.pdf",   False),
    ("file.docx",  False),
    ("file",       False),  # no extension
    (".hidden",    False),  # dot-file with no real extension
    ("/path/to/DATA.CSV", True),
])
def test_is_supported_file(path, expected):
    assert is_supported_file(path) == expected
