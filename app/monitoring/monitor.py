import time
import signal
from watchdog.observers import Observer
from app.monitoring.file_handler import FileHandler
from app.monitoring.logging import logger


class FileMonitor:
    def __init__(self, watch_directory: str):
        self.watch_directory = watch_directory
        self.observer = Observer()
        self._handler: FileHandler | None = None

    def start(self):
        self._handler = FileHandler()
        self.observer.schedule(
            self._handler,
            self.watch_directory,
            recursive=False
        )
        self.observer.start()
        logger.info(f"[INFO] File monitor started for directory: {self.watch_directory}")
        print(f"[INFO] Watching: {self.watch_directory}  (Ctrl+C to stop)")

        # Register signal handlers for clean shutdown on SIGINT / SIGTERM
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

        try:
            while self.observer.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.observer.stop()
        self.observer.join()          # Wait for the observer thread to finish

        # Shut down the dispatcher thread pool cleanly
        if self._handler is not None:
            self._handler._dispatcher.shutdown()

        logger.info("[INFO] File monitor stopped.")
        print("\n[Stopped]")

    def _handle_signal(self, signum, frame):
        logger.info(f"[INFO] Signal {signum} received — shutting down.")
        self.stop()