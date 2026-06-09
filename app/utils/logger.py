import logging
import sys
from pathlib import Path

_LOG_INITIALIZED = False


def get_logger(name="tls"):
    logger = logging.getLogger(name)

    if _LOG_INITIALIZED:
        return logger

    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    global _LOG_INITIALIZED
    _LOG_INITIALIZED = True

    return logger
