from concurrent.futures import ThreadPoolExecutor

from app.config.settings import settings
from app.pipeline.pipeline import ProcessingPipeline


class TaskDispatcher:
    def __init__(self, max_workers: int | None = None):
        workers = max_workers if max_workers is not None else settings.MAX_WORKERS
        self.executor = ThreadPoolExecutor(max_workers=workers)
        self.pipeline = ProcessingPipeline()

    def submit_task(self, file_path: str) -> None:
        print(f"[Queue] Submitting: {file_path}")
        self.executor.submit(self.pipeline.run, file_path)

    def shutdown(self, wait: bool = True) -> None:
        """Drain in-flight tasks and shut down the thread pool."""
        self.executor.shutdown(wait=wait)
        print("[Queue] Dispatcher shut down.")
