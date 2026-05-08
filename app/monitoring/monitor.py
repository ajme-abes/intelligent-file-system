import time
from watchdog.observers import Observer
from app.monitoring.file_handler import FileHandler
from app.monitoring.logging import logger

class FileMonitor:
    def __init__(self, watch_directory: str):
        self.watch_directory = watch_directory
        self.observer = Observer()

    def start(self):
        event_handler = FileHandler()
        self.observer.schedule(
            event_handler,
            self.watch_directory,
            recursive=False
        )
        self.observer.start()
        logger.info(f"[INFO] File monitor started for directory: {self.watch_directory}")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
            logger.info("[INFO] File monitor stopped.")

    def stop(self):
        self.observer.stop()
        self.observer.join()
        logger.info("[INFO] File monitor stopped.")
        print("\n[Stopped]")