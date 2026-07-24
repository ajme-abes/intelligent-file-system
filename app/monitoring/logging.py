"""
Structured logging setup for Intelliginet File System.

- JSON format  → machine-readable, great for log aggregators (Datadog, ELK, etc.)
- Text format  → human-readable fallback (set LOG_FORMAT=text in env)
- Log level and file path driven entirely by settings (env-var-overridable)
"""

import json
import logging
import traceback
from datetime import datetime, timezone


class _JsonFormatter(logging.Formatter):
    """Emit each log record as a single JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "lineno": record.lineno,
        }
        if record.exc_info:
            payload["exception"] = traceback.format_exception(*record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def _build_logger() -> logging.Logger:
    # Import here to avoid a circular dependency at module-load time
    from app.config.settings import settings  # noqa: PLC0415

    settings.LOG_DIR.mkdir(parents=True, exist_ok=True)

    _logger = logging.getLogger("FileMonitor")
    _logger.setLevel(getattr(logging, settings.LOG_LEVEL, logging.INFO))

    if _logger.handlers:
        return _logger  # already initialised (e.g. during tests)

    # File handler — always structured JSON
    file_handler = logging.FileHandler(str(settings.LOG_FILE), encoding="utf-8")
    file_handler.setFormatter(_JsonFormatter())
    _logger.addHandler(file_handler)

    # Console handler — JSON or plain text depending on LOG_FORMAT env var
    console_handler = logging.StreamHandler()
    if settings.LOG_FORMAT == "json":
        console_handler.setFormatter(_JsonFormatter())
    else:
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s")
        )
    _logger.addHandler(console_handler)

    return _logger


logger = _build_logger()
