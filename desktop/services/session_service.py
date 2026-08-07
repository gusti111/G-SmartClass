"""
session_service.py
Menyimpan/membaca/menghapus session pengguna secara terenkripsi.

Alur:
    save_session(SessionModel) -> encrypt(json) -> session.enc + metadata.json
    load_session() -> decrypt(session.enc) -> SessionModel | None
    clear_session() -> hapus session.enc & metadata.json (dipanggil saat logout)
    is_session_expired(session) -> bandingkan expired_at dengan waktu sekarang
"""
import json
from datetime import datetime, timezone
from typing import Optional

from desktop.config.settings import SESSION_FILE, SESSION_METADATA_FILE
from desktop.logger.logger import get_logger
from desktop.models.session_model import SessionModel
from desktop.services import crypto_service

logger = get_logger(__name__)


def save_session(session: SessionModel) -> None:
    payload = json.dumps(session.to_dict())
    encrypted = crypto_service.encrypt(payload)
    SESSION_FILE.write_bytes(encrypted)

    metadata = {
        "uid": session.uid,
        "email": session.email,
        "deviceId": session.device_id,
        "loginAt": session.login_at,
        "rememberMe": session.remember_me,
    }
    SESSION_METADATA_FILE.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    logger.info("Session tersimpan untuk uid=%s", session.uid)


def load_session() -> Optional[SessionModel]:
    if not SESSION_FILE.exists():
        return None
    try:
        decrypted = crypto_service.decrypt(SESSION_FILE.read_bytes())
        data = json.loads(decrypted)
        return SessionModel.from_dict(data)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Session lokal tidak valid/rusak, dianggap tidak ada: %s", exc)
        clear_session()
        return None


def clear_session() -> None:
    for path in (SESSION_FILE, SESSION_METADATA_FILE):
        try:
            if path.exists():
                path.unlink()
        except OSError as exc:  # pragma: no cover
            logger.error("Gagal menghapus %s: %s", path, exc)
    logger.info("Session lokal dihapus (logout).")


def is_session_expired(session: SessionModel) -> bool:
    if not session.expired_at:
        return True
    try:
        expired_at = datetime.fromisoformat(session.expired_at)
        if expired_at.tzinfo is None:
            expired_at = expired_at.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) >= expired_at
    except ValueError:
        return True
