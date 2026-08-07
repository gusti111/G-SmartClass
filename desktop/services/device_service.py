"""
device_service.py
Mengelola identitas perangkat desktop (Device ID persisten) dan informasi
platform, dipakai untuk Login (registrasi device) dan Pair Device.
"""
import platform
import uuid
from pathlib import Path

from desktop.config.settings import CACHE_DIR
from desktop.logger.logger import get_logger

logger = get_logger(__name__)

_DEVICE_ID_FILE = CACHE_DIR / "device_id.txt"


def get_or_create_device_id() -> str:
    """Device ID persisten per-instalasi (bukan per-user), disimpan sebagai file
    biasa di cache -- tidak sensitif, jadi tidak perlu dienkripsi."""
    if _DEVICE_ID_FILE.exists():
        existing = _DEVICE_ID_FILE.read_text(encoding="utf-8").strip()
        if existing:
            return existing

    new_id = str(uuid.uuid4())
    _DEVICE_ID_FILE.write_text(new_id, encoding="utf-8")
    logger.info("Device ID baru dibuat: %s", new_id)
    return new_id


def get_os_name() -> str:
    return f"{platform.system()} {platform.release()}"


def get_device_summary() -> dict:
    return {
        "deviceId": get_or_create_device_id(),
        "platform": "desktop",
        "osName": get_os_name(),
        "machine": platform.machine(),
    }
