import sys
from pathlib import Path

from app.utils.config import Config
from app.utils.logger import get_logger


def main():
    config_path = Path(__file__).parent.parent / "config.json"
    config = Config(str(config_path) if config_path.exists() else None)

    logger = get_logger()
    logger.info(f"Starting {config.get('app', 'name')} v{config.get('app', 'version')}")

    try:
        from PyQt6.QtWidgets import QApplication
        from app.gui.main_window import MainWindow

        app = QApplication(sys.argv)
        window = MainWindow(config)
        window.show()
        sys.exit(app.exec())
    except ImportError:
        logger.warning("PyQt6 not available, running in headless mode")
        print(f"{config.get('app', 'name')} v{config.get('app', 'version')}")
        print("GUI requires PyQt6 - install with: pip install PyQt6")


if __name__ == "__main__":
    main()
