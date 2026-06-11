import pytest
import shutil
import tempfile
import logging
from pathlib import Path
from app.utils.logger import get_logger, reset_logger


class TestLogger:
    def setup_method(self):
        reset_logger()

    def test_get_logger(self, tmp_path):
        log_dir = str(tmp_path / "logs")
        logger = get_logger("test_logger", log_dir=log_dir)
        assert logger.name == "test_logger"
        assert logger.hasHandlers()
        # check that file handler added
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.handlers.RotatingFileHandler)]
        assert len(file_handlers) >= 1

    def test_logger_same_name_returns_same(self):
        a = get_logger("same_logger_test")
        b = get_logger("same_logger_test")
        assert a is b

    def test_logger_creates_log_file(self, tmp_path):
        log_dir = str(tmp_path / "logs")
        logger = get_logger("file_test", log_dir=log_dir)
        logger.info("test message")
        log_file = Path(log_dir) / "tls.log"
        assert log_file.exists()
        content = log_file.read_text()
        assert "test message" in content
