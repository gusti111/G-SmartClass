"""
email_verification_model.py
Firebase Authentication secara native hanya mendukung verifikasi email lewat
TAUTAN (oobCode), bukan kode 6 digit. Karena desain UI G-SmartClass memakai
kode 6 digit, kita implementasikan skema custom:

    1. Client men-generate kode 6 digit + hash (SHA-256) lalu menuliskannya
       ke Firestore: email_otps/{email} (codeHash, expiresAt, attempts).
    2. (Idealnya) sebuah Cloud Function ter-trigger untuk benar-benar
       mengirim email berisi kode tsb -- BELUM diimplementasikan pada tahap
       ini karena backend/functions belum dibangun. Lihat catatan di
       email_verification_repository.py.
    3. Saat user submit kode, client mem-verifikasi hash-nya cocok & belum
       kedaluwarsa, lalu menandai users/{uid}.emailVerified = true.
"""
import hashlib
import random
from datetime import datetime, timedelta, timezone

from desktop.config.settings import EMAIL_OTP_TTL_SECONDS

OTP_LENGTH = 6


def generate_otp_code() -> str:
    return "".join(random.choice("0123456789") for _ in range(OTP_LENGTH))


def hash_otp_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def build_otp_document(code: str) -> dict:
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=EMAIL_OTP_TTL_SECONDS)
    return {
        "codeHash": hash_otp_code(code),
        "expiresAt": expires_at.isoformat(),
        "attempts": 0,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }


def is_otp_expired(expires_at_iso: str) -> bool:
    try:
        expires_at = datetime.fromisoformat(expires_at_iso)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) >= expires_at
    except (ValueError, TypeError):
        return True
