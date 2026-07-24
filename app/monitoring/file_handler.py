import time
import os
from watchdog.events import FileSystemEventHandler
from app.core.data_file import DataFile
from app.utils.validator import is_supported_file
from app.monitoring.logging import logger
from app.pipeline.dispatcher import TaskDispatcher


class FileHandler(FileSystemEventHandler):
    """
    Handles filesystem events for the monitored input directory.
    Submits new/modified files to the processing pipeline via TaskDispatcher.
    """

    def __init__(self):
        super().__init__()
        # Instance-level state — safe if multiple monitors are ever created
        self._processed_data: dict[str, float] = {}
        self._dispatcher = TaskDispatcher()

    def _submit(self, file_path: str) -> None:
        """Common logic for submitting a file to the pipeline."""
        if not is_supported_file(file_path):
            logger.warning(f"[WARNING] Unsupported file skipped: {file_path}")
            return

        try:
            data_file = DataFile(file_path)
            metadata = data_file.get_metadata()
            logger.info(f"[INFO] Detected file: {metadata}")
            print(f"\n[New File] {metadata}")

            self._dispatcher.submit_task(file_path)
            self._processed_data[file_path] = time.time()

        except Exception as e:
            logger.error(f"[ERROR] Error submitting file {file_path}: {e}", exc_info=True)

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = event.src_path

        if file_path in self._processed_data:
            return

        # Brief delay to ensure the file is fully written before processing
        time.sleep(0.5)
        self._submit(file_path)

    def on_modified(self, event):
        if event.is_directory:
            return

        file_path = event.src_path
        current_time = time.time()
        last_time = self._processed_data.get(file_path, 0)

        # Debounce: ignore rapid successive modify events (< 2s apart)
        if current_time - last_time < 2:
            return

        logger.info(f"[INFO] File modified: {file_path} — re-queuing for processing")
        print(f"\n[Modified] {os.path.basename(file_path)} — re-queuing")

        # Remove from tracking so _submit doesn't skip it, then re-submit
        self._processed_data.pop(file_path, None)
        self._submit(file_path)

    def on_deleted(self, event):
        if event.is_directory:
            return

        file_path = event.src_path
        self._processed_data.pop(file_path, None)

        logger.info(f"[INFO] File deleted: {file_path} — removed from tracking")
        print(f"\n[Deleted] {os.path.basename(file_path)} removed from tracking")
