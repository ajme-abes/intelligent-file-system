import pandas as pd
from app.core.base_processor import BaseProcessor
class CSVProcessor(BaseProcessor):

    def load(self, file_path: str):
        return pd.read_csv(file_path)
    def process(self, data):
        data = data.drop_duplicates()
        data = data.fillna(0)
        return data
    def save(self, data, output_path: str):
        data.to_csv(output_path, index=False)
    