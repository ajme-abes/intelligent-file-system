from concurrent.futures import ThreadPoolExecutor
from app.pipeline.pipeline import ProcessingPipeline


class TaskDispatcher:
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.pipeline = ProcessingPipeline()

    def submit_task(self, file_path: str) -> None:
        print(f"[Queue] Submitting: {file_path}")
        self.executor.submit(self.pipeline.run, file_path)

    def shutdown(self, wait: bool = True) -> None:
        """Gracefully shut down the thread pool, optionally waiting for in-flight tasks."""
        self.executor.shutdown(wait=wait)
        print("[Queue] Dispatcher shut down.")