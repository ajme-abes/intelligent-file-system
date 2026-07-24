import os
import logging

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Use an explicit handler instead of basicConfig so we don't conflict
# with any root logger already initialised by a third-party library.
logger = logging.getLogger("FileMonitor")
logger.setLevel(logging.INFO)

if not logger.handlers:
    _handler = logging.FileHandler(f"{LOG_DIR}/system.log", encoding="utf-8")
    _handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(_handler)