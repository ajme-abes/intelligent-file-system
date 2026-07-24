"""
Central configuration for the Intelliginet File System.

All values can be overridden via environment variables so the system
is fully configurable in Docker / CI without touching code.

Usage anywhere in the app:
    from app.config import settings
    print(settings.INPUT_DIR)
"""

import os
from pathlib import Path

# ── Project root ──────────────────────────────────────────────────────────────
# settings.py lives at  <root>/app/config/settings.py  → root is two levels up
_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings:
    # ── Directory paths ───────────────────────────────────────────────────────
    ROOT_DIR: Path = _ROOT
    INPUT_DIR: Path = Path(os.getenv("INPUT_DIR",  str(_ROOT / "data" / "input")))
    OUTPUT_DIR: Path = Path(os.getenv("OUTPUT_DIR", str(_ROOT / "data" / "output")))
    LOG_DIR: Path = Path(os.getenv("LOG_DIR",   str(_ROOT / "logs")))

    # ── Processing ────────────────────────────────────────────────────────────
    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "4"))
    DEBOUNCE_SECONDS: float = float(os.getenv("DEBOUNCE_SECONDS", "2.0"))
    FILE_WRITE_DELAY: float = float(os.getenv("FILE_WRITE_DELAY", "0.5"))

    # ── Logging ───────────────────────────────────────────────────────────────
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")   # "json" | "text"
    LOG_FILE: Path = Path(os.getenv("LOG_FILE", str(_ROOT / "logs" / "system.log")))

    # ── Supported file types ──────────────────────────────────────────────────
    SUPPORTED_EXTENSIONS: frozenset[str] = frozenset({".csv", ".txt", ".json"})

    def ensure_dirs(self) -> None:
        """Create all required directories if they do not exist."""
        for directory in (self.INPUT_DIR, self.OUTPUT_DIR, self.LOG_DIR):
            directory.mkdir(parents=True, exist_ok=True)

    def __repr__(self) -> str:
        return (
            f"Settings("
            f"INPUT_DIR={self.INPUT_DIR}, "
            f"OUTPUT_DIR={self.OUTPUT_DIR}, "
            f"MAX_WORKERS={self.MAX_WORKERS}, "
            f"LOG_LEVEL={self.LOG_LEVEL}, "
            f"LOG_FORMAT={self.LOG_FORMAT}"
            f")"
        )


# Singleton — import this everywhere
settings = Settings()
