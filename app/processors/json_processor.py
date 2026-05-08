import pandas as pd
from app.core.base_processor import BaseProcessor
class JsonProcessor(BaseProcessor):
    def load(self, file_path: str):
        return pd.read_json(file_path, orient='index')
    def process(self, data):
        data = data.drop_duplicates()
        data = data.fillna(0)
        return data
    def save(self, data, output_path: str):
        data.to_json(output_path, orient='index')