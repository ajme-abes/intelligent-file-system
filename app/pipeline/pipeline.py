from app.core.data_file import DataFile
from app.utils.validator import is_supported_file
from app.processors.csv_processor import CSVProcessor
from app.processors.json_processor import JsonProcessor
from app.processors.txt_processor import TXTProcessor
from app.monitoring.logging import logger
import threading
import os
class ProcessingPipeline:
    def __init__(self):
        self._processors = {
            "csv": CSVProcessor(),
            "json": JsonProcessor(),
            "txt": TXTProcessor()

        }

    def get_processor(self, file_type):

        return self._processors.get(file_type)
    def run(self, file_path):
        thread_name = threading.current_thread().name
        print(f"\n[Pipeline Start]  {file_path}")
        print(f"[Thread] {thread_name}")

        if not is_supported_file(file_path):
            logger.error(f"Unsupported file type: {file_path}")
            print(f"[Pipeline Failed] Unsupported file type: {file_path}")
            return False
        
        try:

            print(type(file_path), file_path)
            data_file = DataFile(file_path)
            processor = self.get_processor(data_file.file_type.lower())

            if not processor:
                logger.error(f"[Error] no processor found for file type : {data_file.file_type}")
                print(f"[Pipeline Failed] No processor found for file type: {data_file.file_type}")
                return False
            data = processor.load(data_file.path)
            processed_data = processor.process(data)

            os.makedirs("data/output", exist_ok=True)
            output_path = f"data/output/processed_{data_file.name}"
            processor.save(processed_data, output_path)
            print(f"[Pipeline Success] Processed file saved to: {output_path}")

        except Exception as e:
            logger.error(f"[Error] Failed to process file: {file_path}")
            print(f"[Pipeline Failed] Error occurred while processing {file_path}: {e}")
            return False

        return True

