import os
import json
from pathlib import Path


DEFAULT_CONFIG = {
    "app": {
        "name": "TLS - Traffic Light Simulation",
        "version": "1.0.0",
        "language": "id",
        "theme": "light",
    },
    "simulation": {
        "step_length": 1.0,
        "default_port": 8813,
        "max_vehicles": 5000,
    },
    "sumo": {
        "binary_path": "",
        "netconvert_path": "",
        "timeout": 30,
    },
    "gui": {
        "viewer_fps": 30,
        "show_heatmap": False,
        "show_vehicle_labels": False,
        "background_color": "#1a1a2e",
    },
    "storage": {
        "database_path": "~/.tls/tls.db",
    },
}


class Config:
    def __init__(self):
        self._data = DEFAULT_CONFIG.copy()
        self._load_from_file()
        self._apply_env_overrides()

    def _get_config_dir(self) -> Path:
        return Path.home() / ".tls"

    def _get_config_path(self) -> Path:
        return self._get_config_dir() / "config.json"

    def _load_from_file(self):
        config_path = self._get_config_path()
        if config_path.exists():
            try:
                with open(config_path) as f:
                    user_config = json.load(f)
                self._deep_merge(self._data, user_config)
            except (json.JSONDecodeError, OSError):
                pass

    def _apply_env_overrides(self):
        env_map = {
            "TLS_LANGUAGE": ("app", "language"),
            "TLS_SUMO_PATH": ("sumo", "binary_path"),
            "TLS_DB_PATH": ("storage", "database_path"),
        }
        for env_var, (section, key) in env_map.items():
            value = os.environ.get(env_var)
            if value:
                self._data[section][key] = value

    def _deep_merge(self, base, override):
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def _ensure_dirs(self):
        self._get_config_dir().mkdir(parents=True, exist_ok=True)
        db_path = self.get("storage", "database_path")
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    def get(self, section, key=None):
        if key is None:
            return self._data.get(section, {})
        return self._data.get(section, {}).get(key)

    def set(self, section, key, value):
        if section not in self._data:
            self._data[section] = {}
        self._data[section][key] = value
        self._save()

    def _save(self):
        config_path = self._get_config_path()
        self._get_config_dir().mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(self._data, f, indent=2)

    def get_sumo_binary(self) -> str:
        path = self.get("sumo", "binary_path")
        if path and os.path.exists(path):
            return path
        for candidate in ["sumo", "/usr/bin/sumo", "/usr/local/bin/sumo"]:
            if os.path.exists(candidate):
                return candidate
        return "sumo"

    def get_netconvert_binary(self) -> str:
        path = self.get("sumo", "netconvert_path")
        if path and os.path.exists(path):
            return path
        for candidate in ["netconvert", "/usr/bin/netconvert"]:
            if os.path.exists(candidate):
                return candidate
        return "netconvert"

    def get_db_path(self) -> str:
        path = self.get("storage", "database_path")
        return os.path.expanduser(path)


def load_config() -> Config:
    config = Config()
    config._ensure_dirs()
    return config
