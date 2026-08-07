"""
environment.py
Loader untuk file .env di root project. Dipanggil sekali di awal (desktop/app.py)
sebelum modul lain (firebase.py, settings.py) membaca os.environ.
"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT_DIR / ".env"
ENV_EXAMPLE_PATH = ROOT_DIR / ".env.example"

_loaded = False


def load_environment() -> None:
    """Load .env sekali saja. Jika .env belum ada, fallback ke .env.example
    supaya aplikasi tetap bisa dijalankan (dengan placeholder) saat development awal."""
    global _loaded
    if _loaded:
        return

    if load_dotenv is None:
        # python-dotenv belum terinstall; biarkan os.environ apa adanya.
        _loaded = True
        return

    if ENV_PATH.exists():
        load_dotenv(dotenv_path=ENV_PATH, override=False)
    elif ENV_EXAMPLE_PATH.exists():
        load_dotenv(dotenv_path=ENV_EXAMPLE_PATH, override=False)

    _loaded = True


def get_env(key: str, default: str = "") -> str:
    load_environment()
    return os.environ.get(key, default)


def get_env_bool(key: str, default: bool = False) -> bool:
    value = get_env(key, str(default))
    return str(value).strip().lower() in ("1", "true", "yes", "on")


def get_env_int(key: str, default: int = 0) -> int:
    value = get_env(key, str(default))
    try:
        return int(value)
    except ValueError:
        return default
