"""
auth_service.py
Wrapper REST API untuk Firebase Identity Toolkit (Authentication).
Tidak memakai firebase-admin ataupun Pyrebase -- murni `requests`, konsisten
dengan solusi EduTrack (menghindari isu koneksi streaming/gRPC).

Referensi endpoint:
https://firebase.google.com/docs/reference/rest/auth
"""
from datetime import datetime, timedelta, timezone

import requests

from desktop.config.constants import (
    ERROR_EMAIL_ALREADY_IN_USE,
    ERROR_INVALID_CREDENTIALS,
    ERROR_NETWORK_UNAVAILABLE,
    ERROR_WEAK_PASSWORD,
)
from desktop.config.firebase import FIREBASE_CONFIG, identity_toolkit_url, secure_token_url
from desktop.logger.logger import get_logger
from desktop.models.failure_model import Failure, Result

logger = get_logger(__name__)

# Pemetaan error message mentah dari Firebase -> kode error internal kita
_FIREBASE_ERROR_MAP = {
    "EMAIL_EXISTS": ERROR_EMAIL_ALREADY_IN_USE,
    "EMAIL_NOT_FOUND": ERROR_INVALID_CREDENTIALS,
    "INVALID_PASSWORD": ERROR_INVALID_CREDENTIALS,
    "INVALID_LOGIN_CREDENTIALS": ERROR_INVALID_CREDENTIALS,
    "WEAK_PASSWORD": ERROR_WEAK_PASSWORD,
}


def _post(url: str, payload: dict) -> Result:
    try:
        response = requests.post(url, json=payload, timeout=FIREBASE_CONFIG.http_timeout)
    except requests.exceptions.RequestException as exc:
        logger.error("Network error saat memanggil %s: %s", url, exc)
        return Result.error(Failure.from_code(ERROR_NETWORK_UNAVAILABLE, raw=str(exc)))

    data = response.json() if response.content else {}

    if response.status_code >= 400:
        raw_message = data.get("error", {}).get("message", "UNKNOWN_ERROR")
        code = _FIREBASE_ERROR_MAP.get(raw_message.split(":")[0].strip())
        if code:
            return Result.error(Failure.from_code(code, raw=raw_message))
        return Result.error(Failure.unknown(raw=raw_message))

    return Result.success(data)


def sign_up_with_email_password(email: str, password: str) -> Result:
    """Registrasi akun baru. Mengembalikan idToken, refreshToken, localId (uid)."""
    return _post(
        identity_toolkit_url("accounts:signUp"),
        {"email": email, "password": password, "returnSecureToken": True},
    )


def sign_in_with_email_password(email: str, password: str) -> Result:
    return _post(
        identity_toolkit_url("accounts:signInWithPassword"),
        {"email": email, "password": password, "returnSecureToken": True},
    )


def send_password_reset_email(email: str) -> Result:
    return _post(
        identity_toolkit_url("accounts:sendOobCode"),
        {"requestType": "PASSWORD_RESET", "email": email},
    )


def send_email_verification(id_token: str) -> Result:
    """Mengirim link verifikasi bawaan Firebase. Catatan: desain UI G-SmartClass
    memakai kode OTP 6 digit custom (lihat email_verification_repository.py),
    jadi fungsi ini disediakan sebagai cadangan/alternatif resmi dari Firebase."""
    return _post(
        identity_toolkit_url("accounts:sendOobCode"),
        {"requestType": "VERIFY_EMAIL", "idToken": id_token},
    )


def get_account_info(id_token: str) -> Result:
    """Mengambil info akun (termasuk emailVerified) berdasarkan idToken."""
    return _post(identity_toolkit_url("accounts:lookup"), {"idToken": id_token})


def refresh_id_token(refresh_token: str) -> Result:
    try:
        response = requests.post(
            secure_token_url(),
            data={"grant_type": "refresh_token", "refresh_token": refresh_token},
            timeout=FIREBASE_CONFIG.http_timeout,
        )
    except requests.exceptions.RequestException as exc:
        logger.error("Network error saat refresh token: %s", exc)
        return Result.error(Failure.from_code(ERROR_NETWORK_UNAVAILABLE, raw=str(exc)))

    data = response.json() if response.content else {}
    if response.status_code >= 400:
        return Result.error(Failure.unknown(raw=str(data)))
    return Result.success(data)


def compute_expiry_iso(expires_in_seconds: str) -> str:
    """Firebase mengembalikan 'expiresIn' sebagai string detik (biasanya 3600)."""
    try:
        seconds = int(expires_in_seconds)
    except (TypeError, ValueError):
        seconds = 3600
    expiry = datetime.now(timezone.utc) + timedelta(seconds=seconds)
    return expiry.isoformat()


def check_internet_connection() -> bool:
    """Dipakai Splash Screen untuk mengecek konektivitas sebelum lanjut ke Login/Dashboard."""
    try:
        requests.head("https://identitytoolkit.googleapis.com", timeout=5)
        return True
    except requests.exceptions.RequestException:
        return False
