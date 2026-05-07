from app.core.base_processor import BaseProcessor

class TXTProcessor(BaseProcessor):

    def load(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.readlines()

    def process(self, data):
        return [line.strip() for line in data if line.strip()]

    def save(self, data, output_path: str):
        with open(output_path, "w", encoding="utf-8") as f:
            for line in data:
                f.write(line + "\n")
    