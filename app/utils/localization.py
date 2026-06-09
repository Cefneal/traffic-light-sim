import json
from pathlib import Path


class Localization:
    def __init__(self, locale="en_US"):
        self.locale = locale
        self.translations = {}
        self._load()

    def _load(self):
        path = Path(__file__).parent.parent.parent / "resources" / "locales" / f"{self.locale}.json"
        if path.exists():
            with open(path) as f:
                self.translations = json.load(f)

    def t(self, key, default=None):
        return self.translations.get(key, default or key)

    def set_locale(self, locale):
        self.locale = locale
        self._load()
