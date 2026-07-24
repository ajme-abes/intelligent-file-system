import json
import pandas as pd
from app.core.base_processor import BaseProcessor


class JsonProcessor(BaseProcessor):

    def load(self, file_path: str) -> pd.DataFrame:
        """
        Handles multiple JSON shapes:
        - Array of objects  → records orient  (most common: [{...}, {...}])
        - Dict of dicts     → index orient    ({"0": {...}, "1": {...}})
        - Flat dict         → single-row DataFrame
        """
        with open(file_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        if isinstance(raw, list):
            return pd.DataFrame(raw)
        elif isinstance(raw, dict):
            # Check if values are dicts (index-oriented) or scalars (flat)
            if raw and isinstance(next(iter(raw.values())), dict):
                return pd.DataFrame.from_dict(raw, orient="index")
            else:
                return pd.DataFrame([raw])
        else:
            raise ValueError(f"Unsupported JSON structure: {type(raw)}")

    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.drop_duplicates()

        # Type-aware fill: numeric columns → 0, string/object columns → empty string
        numeric_cols = data.select_dtypes(include="number").columns
        string_cols = data.select_dtypes(include="object").columns
        data[numeric_cols] = data[numeric_cols].fillna(0)
        data[string_cols] = data[string_cols].fillna("")

        return data

    def save(self, data: pd.DataFrame, output_path: str) -> None:
        data.to_json(output_path, orient="records", indent=2)