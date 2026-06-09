import json
import os
from pathlib import Path

DEFAULT_CONFIG = {
    "app": {
        "name": "Traffic Light Simulation",
        "version": "1.0.0",
        "debug": False,
    },
    "simulation": {
        "default_algorithm": "fixed",
        "cycle_time": 60,
        "min_green": 10,
        "max_green": 45,
        "flow_rate": 500,
        "vehicle_type": "car",
    },
    "sumo": {
        "host": "127.0.0.1",
        "port": 8813,
        "num_retries": 5,
        "retry_interval": 1.0,
    },
    "logging": {
        "level": "INFO",
        "file": "logs/tls.log",
    },
    "display": {
        "show_heatmap": False,
        "show_vehicle_labels": False,
    },
}


class Config:
    def __init__(self, path=None):
        self.data = DEFAULT_CONFIG.copy()
        if path:
            self.load(path)

    def load(self, path):
        p = Path(path)
        if p.exists():
            with open(p) as f:
                loaded = json.load(f)
                self._merge(self.data, loaded)

    def get(self, section, key=None, default=None):
        section_data = self.data.get(section, {})
        if key is None:
            return section_data
        return section_data.get(key, default)

    def _merge(self, base, override):
        for k, v in override.items():
            if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                self._merge(base[k], v)
            else:
                base[k] = v

    def save(self, path):
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w") as f:
            json.dump(self.data, f, indent=2)
