"""
settings.py
Pengaturan umum aplikasi: nama, versi, environment, dan path-path penting
(cache, session, log). Tidak berisi kredensial (lihat firebase.py untuk itu).
"""
from pathlib import Path

from desktop.config.environment import get_env

APP_NAME = get_env("APP_NAME", "G-SmartClass")
APP_VERSION = get_env("APP_VERSION", "1.0.0")
ENVIRONMENT = get_env("ENVIRONMENT", "development")
LOG_LEVEL = get_env("LOG_LEVEL", "DEBUG")

ROOT_DIR = Path(__file__).resolve().parents[2]
DESKTOP_DIR = ROOT_DIR / "desktop"

CACHE_DIR = DESKTOP_DIR / "cache"
SESSION_DIR = CACHE_DIR / "session"
IMAGES_CACHE_DIR = CACHE_DIR / "images"
FILES_CACHE_DIR = CACHE_DIR / "files"
TEMP_CACHE_DIR = CACHE_DIR / "temp"
LOG_DIR = DESKTOP_DIR / "logger" / "logs"

SESSION_FILE = SESSION_DIR / "session.enc"
SESSION_KEY_FILE = SESSION_DIR / "key.key"
SESSION_METADATA_FILE = SESSION_DIR / "metadata.json"

for _dir in (CACHE_DIR, SESSION_DIR, IMAGES_CACHE_DIR, FILES_CACHE_DIR, TEMP_CACHE_DIR, LOG_DIR):
    _dir.mkdir(parents=True, exist_ok=True)

# Batas waktu Pair Device (sesuai blueprint: QR berlaku 60 detik, one-time-use)
PAIR_DEVICE_QR_TTL_SECONDS = 60
PAIR_DEVICE_CODE_TTL_SECONDS = 60

# Batas waktu OTP email verification (6 digit, sesuai desain UI: 00:45 sebelum resend)
EMAIL_OTP_TTL_SECONDS = 300  # kode berlaku 5 menit
EMAIL_OTP_RESEND_COOLDOWN_SECONDS = 45

# Splash screen
SPLASH_MIN_DURATION_MS = 2000
SPLASH_MAX_DURATION_MS = 6000
