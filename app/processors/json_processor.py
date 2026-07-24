import json

import pandas as pd

from app.core.base_processor import BaseProcessor
from app.cleaning.cleaner import DataCleaner


class JsonProcessor(BaseProcessor):

    def __init__(self) -> None:
        self._cleaner = DataCleaner()

    def load(self, file_path: str) -> pd.DataFrame:
        """
        Handles multiple JSON shapes:
          - Array of objects  → [{...}, {...}]        (most common)
          - Dict of dicts     → {"0": {...}, "1": {...}}
          - Flat dict         → {"key": "value", ...}  → single-row DataFrame
        """
        with open(file_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        if isinstance(raw, list):
            return pd.DataFrame(raw)
        elif isinstance(raw, dict):
            if raw and isinstance(next(iter(raw.values())), dict):
                return pd.DataFrame.from_dict(raw, orient="index")
            else:
                return pd.DataFrame([raw])
        else:
            raise ValueError(f"Unsupported JSON structure: {type(raw)}")

    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        cleaned, report = self._cleaner.clean(data)
        print(f"[JSON Cleaning] {report.summary()}")
        return cleaned

    def save(self, data: pd.DataFrame, output_path: str) -> None:
        data.to_json(output_path, orient="records", indent=2)
