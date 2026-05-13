import time
import os
from watchdog.events import FileSystemEventHandler
from app.core.data_file import DataFile
from app.utils.validator import is_supported_file
from app.monitoring.logging import logger
from app.pipeline.dispatcher import TaskDispatcher


class FileHandler(FileSystemEventHandler):
    
    processed_data = {}
    dispatcher = TaskDispatcher()

    def on_created(self, event):
        if event.is_directory:
            return 
        file_path = event.src_path
        
        # Safe dictionary key check
        if file_path in self.processed_data:
            return
            
        if not is_supported_file(file_path):
            logger.warning(f"[WARNING] Unsupported file skipped: {file_path}")
            return
            
        try:
            time.sleep(1)
            
            # 1. FIX: Added parenthesis and passed the file_path argument
            self.dispatcher.submit_task(file_path)
            
            data_file = DataFile(file_path)
            metadata = data_file.get_metadata()
            logger.info(f"[INFO] Detected new file: {metadata}")

            print("\n [New File]")
            print(metadata)

            # 2. FIX: Dictionary tracking assignment instead of .add()
            self.processed_data[file_path] = time.time()
            
        except Exception as e:
            logger.error(f"[ERROR] Error processing file {file_path}: {e}")
    
    def on_modified(self, event):
        if event.is_directory:
            return
        current_time = time.time()
        last_modified_time = self.processed_data.get(event.src_path, 0)

        if current_time - last_modified_time < 2:
            return
        
        logger.info(f"[INFO] File Modified {event.src_path} - re-scaninig")
        # Update timestamp before passing
        self.processed_data[event.src_path] = current_time
        self.on_created(event)

    def on_deleted(self, event):
        if event.is_directory:
            return
        
        if event.src_path in self.processed_data:
            del self.processed_data[event.src_path]

        logger.info(f"[INFO] File Deleted {event.src_path} - removed from processed list")
        print(f"\n [Deleted] {os.path.basename(event.src_path)} removed from processed list")
