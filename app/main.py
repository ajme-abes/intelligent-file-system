from app.config.settings import settings
from app.monitoring.monitor import FileMonitor
from app.monitoring.logging import logger


def main() -> None:
    settings.ensure_dirs()
    logger.info(f"Starting Intelliginet File System | config={settings!r}")
    print(f"[INFO] Config loaded: {settings!r}")

    monitor = FileMonitor(str(settings.INPUT_DIR))
    print("[INFO] Starting file monitor...")
    monitor.start()


if __name__ == "__main__":
    main()
