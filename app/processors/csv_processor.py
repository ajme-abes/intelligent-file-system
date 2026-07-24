import pandas as pd
from app.core.base_processor import BaseProcessor


class CSVProcessor(BaseProcessor):

    def load(self, file_path: str) -> pd.DataFrame:
        return pd.read_csv(file_path)

    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.drop_duplicates()

        # Type-aware fill: numeric columns → 0, string/object columns → empty string
        numeric_cols = data.select_dtypes(include="number").columns
        string_cols = data.select_dtypes(include="object").columns
        data[numeric_cols] = data[numeric_cols].fillna(0)
        data[string_cols] = data[string_cols].fillna("")

        return data

    def save(self, data: pd.DataFrame, output_path: str) -> None:
        data.to_csv(output_path, index=False)