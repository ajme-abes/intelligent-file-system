from app.core.base_processor import BaseProcessor
from app.monitoring.logging import logger


class TXTProcessor(BaseProcessor):

    def load(self, file_path: str) -> list[str]:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.readlines()

    def process(self, data: list[str]) -> list[str]:
        original = len(data)
        cleaned = [line.strip() for line in data if line.strip()]
        removed = original - len(cleaned)
        logger.info(f"[TXT Cleaning] Lines: {original} → {len(cleaned)} (removed {removed} blank)")
        print(f"[TXT Cleaning] Lines: {original} → {len(cleaned)} (removed {removed} blank)")
        return cleaned

    def save(self, data: list[str], output_path: str) -> None:
        with open(output_path, "w", encoding="utf-8") as f:
            for line in data:
                f.write(line + "\n")
