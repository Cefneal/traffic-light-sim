import sys
from pathlib import Path

from app.utils.config import load_config
from app.utils.logger import get_logger


def main():
    config = load_config()

    logger = get_logger()
    logger.info(f"Starting {config.get('app', 'name')} v{config.get('app', 'version')}")

    try:
        from PyQt6.QtWidgets import QApplication
        from app.gui.main_window import MainWindow
        from app.engine.sim_controller import SimController

        app = QApplication(sys.argv)
        sim = SimController(config)
        window = MainWindow(config)
        icon_path = Path(__file__).resolve().parent.parent / "resources" / "icon.png"
        if icon_path.exists():
            from PyQt6.QtGui import QIcon
            window.setWindowIcon(QIcon(str(icon_path)))
        window.set_sim_controller(sim)
        window.show()
        sys.exit(app.exec())
    except ImportError:
        logger.warning("PyQt6 not available, running in headless mode")
        print(f"{config.get('app', 'name')} v{config.get('app', 'version')}")
        print("GUI requires PyQt6 - install with: pip install PyQt6")


if __name__ == "__main__":
    main()
