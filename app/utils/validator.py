from app.config.settings import settings


def is_supported_file(file_path: str) -> bool:
    """Returns True if the file extension is in the supported set (case-insensitive)."""
    ext = file_path.rsplit(".", 1)[-1].lower() if "." in file_path else ""
    return f".{ext}" in settings.SUPPORTED_EXTENSIONS
