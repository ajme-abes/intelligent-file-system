import threading

from app.config.settings import settings
from app.core.data_file import DataFile
from app.utils.validator import is_supported_file
from app.processors.csv_processor import CSVProcessor
from app.processors.json_processor import JsonProcessor
from app.processors.txt_processor import TXTProcessor
from app.monitoring.logging import logger


class ProcessingPipeline:
    def __init__(self):
        self._processors = {
            "csv": CSVProcessor(),
            "json": JsonProcessor(),
            "txt": TXTProcessor(),
        }

    def get_processor(self, file_type: str):
        return self._processors.get(file_type)

    def run(self, file_path: str) -> bool:
        thread_name = threading.current_thread().name
        print(f"\n[Pipeline Start] {file_path}  (thread: {thread_name})")

        if not is_supported_file(file_path):
            logger.error(f"Unsupported file type: {file_path}")
            print(f"[Pipeline Failed] Unsupported file type: {file_path}")
            return False

        try:
            data_file = DataFile(file_path)
            processor = self.get_processor(data_file.file_type)

            if not processor:
                logger.error(f"No processor found for file type: {data_file.file_type}")
                print(f"[Pipeline Failed] No processor found for: {data_file.file_type}")
                return False

            data = processor.load(data_file.path)
            processed_data = processor.process(data)

            # Output path comes from config — never hardcoded
            settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            output_path = settings.OUTPUT_DIR / f"processed_{data_file.name}"
            processor.save(processed_data, str(output_path))

            logger.info(f"Processed file saved: {output_path}")
            print(f"[Pipeline Success] Saved to: {output_path}")

        except Exception as e:
            logger.error(f"Failed to process file {file_path}: {e}", exc_info=True)
            print(f"[Pipeline Failed] Error processing {file_path}: {e}")
            return False

        return True
