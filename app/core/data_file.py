import os


class DataFile:

    supported_types = {
        ".csv": "csv",
        ".txt": "txt",
        ".json": "json",
    }

    def __init__(self, path: str):
        self.path = path
        self.name = os.path.basename(path)
        self.extension = self._get_extension()
        self.file_type = self._detect_type()

    def _get_extension(self) -> str:
        return os.path.splitext(self.path)[1].lower()

    def _detect_type(self) -> str:
        if self.extension in self.supported_types:
            return self.supported_types[self.extension]
        raise ValueError(f"Unsupported file type: {self.extension}")

    def get_metadata(self) -> dict:
        return {
            "name": self.name,
            "path": self.path,
            "type": self.file_type,
        }
