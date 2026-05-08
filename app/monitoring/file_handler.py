import time
from watchdog.events import FileSystemEventHandler
from app.core.data_file import DataFile
from app.utils.validotor import is_supported_file
from app.monitoring.logging import logger

class FileHandler(FileSystemEventHandler):
    
    processed_data = set()
    def on_created(self, event):
        if event.is_directory:
            return 
        file_path = event.src_path
        if file_path in self.processed_data:
            return
        if not is_supported_file(file_path):
            logger.warning(f"[WARNING] Unsupported file skipped: {file_path}")
            return
        try:
            time.sleep(1)
            data_file = DataFile(file_path)
            metadata = data_file.get_metadata()
            logger.info(f"[INFO] Detected new file: {metadata}")

            print("\n [New File]")
            print(metadata)


            self.processed_data.add(file_path)
            
        except Exception as e:
            logger.error(f"[ERROR] Error processing file {file_path}: {e}")
