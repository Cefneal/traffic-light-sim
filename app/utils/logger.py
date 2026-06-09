import logging
import sys
import threading
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOG_INITIALIZED = False
_LOCK = threading.Lock()


def get_logger(name="tls", log_dir="logs", log_level=logging.INFO,
               console_level=logging.INFO, file_level=logging.DEBUG):
    global _LOG_INITIALIZED
    logger = logging.getLogger(name)

    if _LOG_INITIALIZED:
        return logger

    with _LOCK:
        if _LOG_INITIALIZED:
            return logger

        logger.setLevel(logging.DEBUG)

        fmt = logging.Formatter(
            "%(asctime)s | %(levelname)-7s | %(name)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(console_level)
        ch.setFormatter(fmt)
        logger.addHandler(ch)

        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        fh = RotatingFileHandler(
            str(log_path / "tls.log"),
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
        )
        fh.setLevel(file_level)
        fh.setFormatter(fmt)
        logger.addHandler(fh)

        sys.excepthook = lambda exc_type, exc_value, exc_tb: (
            logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_tb))
        )

        _LOG_INITIALIZED = True

    return logger


def reset_logger():
    global _LOG_INITIALIZED
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    _LOG_INITIALIZED = False
