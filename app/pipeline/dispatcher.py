from concurrent.futures import ThreadPoolExecutor
from app.pipeline.pipeline import ProcessingPipeline

class TaskDispatcher:
    def __init__(self, max_workers=4):
        self.excuter = ThreadPoolExecutor(max_workers=max_workers)
        self.pipeline = ProcessingPipeline()

    def submit_task(self, file_path):
        print(f"[Queue] submitting {file_path}")

        self.excuter.submit(
            self.pipeline.run,
            file_path
        )
        