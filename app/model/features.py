"""
Feature extraction for file-level ML classification.

Converts a raw file path into a fixed-length numeric feature vector
that the FileTypeClassifier can train and predict on.

Features (13 total):
  0  file size in bytes (log-scaled)
  1  number of lines (log-scaled)
  2  average line length (normalised)
  3  ratio of numeric characters
  4  ratio of alphabetic characters
  5  ratio of whitespace characters
  6  ratio of punctuation/special characters
  7  number of unique characters (normalised 0-1)
  8  ratio of lines that look like key:value / key=value pairs
  9  ratio of lines starting with { or [  (JSON-ish)
  10 ratio of lines containing commas      (CSV-ish)
  11 ratio of lines that are blank
  12 ratio of lines starting with # or //  (comment/log-ish)
"""

from __future__ import annotations

import math
import os
from typing import List


def extract_features(file_path: str) -> List[float]:
    """
    Return a 13-element feature vector for *file_path*.
    Falls back to all-zeros if the file cannot be read as text.
    """
    try:
        size = os.path.getsize(file_path)
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except OSError:
        return [0.0] * 13

    if not content:
        return [0.0] * 13

    lines = content.splitlines()
    n_lines = len(lines) or 1
    total_chars = len(content) or 1

    n_digits = sum(c.isdigit() for c in content)
    n_alpha = sum(c.isalpha() for c in content)
    n_space = sum(c.isspace() for c in content)
    n_punct = total_chars - n_digits - n_alpha - n_space
    unique_chars = len(set(content))

    kv_lines = sum(1 for line in lines if ":" in line or "=" in line)
    json_lines = sum(1 for line in lines if line.lstrip().startswith(("{", "[")))
    comma_lines = sum(1 for line in lines if "," in line)
    blank_lines = sum(1 for line in lines if not line.strip())
    comment_lines = sum(1 for line in lines if line.lstrip().startswith(("#", "//")))

    avg_line_len = sum(len(line) for line in lines) / n_lines

    return [
        math.log1p(size),           # 0
        math.log1p(n_lines),        # 1
        avg_line_len / 200.0,       # 2  normalised
        n_digits / total_chars,     # 3
        n_alpha / total_chars,      # 4
        n_space / total_chars,      # 5
        n_punct / total_chars,      # 6
        unique_chars / 128.0,       # 7  normalised
        kv_lines / n_lines,         # 8
        json_lines / n_lines,       # 9
        comma_lines / n_lines,      # 10
        blank_lines / n_lines,      # 11
        comment_lines / n_lines,    # 12
    ]
