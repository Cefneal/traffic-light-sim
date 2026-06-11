import pytest
import tempfile
import json
from pathlib import Path
from app.utils.config import Config, DEFAULT_CONFIG


class TestConfig:
    def test_default_values(self):
        config = Config()
        assert config.get("app", "name") == "TLS - Traffic Light Simulation"
        assert config.get("simulation", "max_vehicles") == 5000
        assert config.get("nonexistent") == {}

    def test_set_and_get(self):
        config = Config()
        config.set("test", "key", "value")
        assert config.get("test", "key") == "value"

    def test_get_section(self):
        config = Config()
        section = config.get("app")
        assert section["name"] == "TLS - Traffic Light Simulation"
        assert section["version"] == "1.0.0"

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("TLS_LANGUAGE", "en")
        config = Config()
        assert config.get("app", "language") == "en"

    def test_get_sumo_binary_default(self):
        config = Config()
        path = config.get_sumo_binary()
        assert isinstance(path, str)
        assert len(path) > 0

    def test_get_db_path_expands_user(self):
        config = Config()
        path = config.get_db_path()
        assert "~" not in path
