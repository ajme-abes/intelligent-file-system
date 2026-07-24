supported_extensions = {".csv", ".txt", ".json"}


def is_supported_file(file_path: str) -> bool:
    """Returns True if the file extension is supported (case-insensitive)."""
    ext = file_path.rsplit(".", 1)[-1].lower() if "." in file_path else ""
    return f".{ext}" in supported_extensions