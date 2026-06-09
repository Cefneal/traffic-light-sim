import os
import json
from typing import Optional


TRANSLATIONS: dict[str, dict[str, str]] = {}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCALE_DIR = os.path.join(os.path.dirname(BASE_DIR), "resources", "locales")


def _load_translations():
    global TRANSLATIONS
    locale_paths = {
        "id": os.path.join(LOCALE_DIR, "id_ID.json"),
        "en": os.path.join(LOCALE_DIR, "en_US.json"),
    }
    for lang, path in locale_paths.items():
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as f:
                    TRANSLATIONS[lang] = json.load(f)
            except (json.JSONDecodeError, OSError):
                TRANSLATIONS[lang] = {}
        else:
            TRANSLATIONS[lang] = {}


def t(key: str, lang: str = "id", default: Optional[str] = None) -> str:
    if not TRANSLATIONS:
        _load_translations()
    keys = key.split(".")
    value = TRANSLATIONS.get(lang, {})
    for k in keys:
        if isinstance(value, dict):
            value = value.get(k)
        else:
            return default or key
    if isinstance(value, str):
        return value
    fallback = TRANSLATIONS.get("en", {})
    for k in keys:
        if isinstance(fallback, dict):
            fallback = fallback.get(k)
        else:
            return default or key
    return fallback if isinstance(fallback, str) else (default or key)


def available_languages() -> list[dict]:
    return [
        {"code": "id", "name": "Bahasa Indonesia", "flag": "id"},
        {"code": "en", "name": "English", "flag": "gb"},
    ]


def reload_translations():
    _load_translations()
