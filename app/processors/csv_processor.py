import pandas as pd

from app.core.base_processor import BaseProcessor
from app.cleaning.cleaner import DataCleaner


class CSVProcessor(BaseProcessor):

    def __init__(self) -> None:
        self._cleaner = DataCleaner()

    def load(self, file_path: str) -> pd.DataFrame:
        return pd.read_csv(file_path)

    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        cleaned, report = self._cleaner.clean(data)
        print(f"[CSV Cleaning] {report.summary()}")
        return cleaned

    def save(self, data: pd.DataFrame, output_path: str) -> None:
        data.to_csv(output_path, index=False)
