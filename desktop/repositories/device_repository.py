"""
device_repository.py
- Registrasi device saat login (users/{uid}/devices/{deviceId})
- Pair Device: generate token QR/kode 6 digit (pair_tokens/{token}), approve, consume.

Aturan keamanan Pair Device (sesuai SDD):
    * 1 kali penggunaan (dihapus dari Firestore setelah dipakai)
    * berlaku maksimal 60 detik (dicek lewat expiresAt)
"""
import random
import string
from datetime import datetime, timedelta, timezone

from desktop.config.constants import COLLECTION_PAIR_TOKENS, ERROR_PAIR_TOKEN_ALREADY_USED, ERROR_PAIR_TOKEN_EXPIRED
from desktop.config.settings import PAIR_DEVICE_QR_TTL_SECONDS
from desktop.models.device_model import DeviceModel
from desktop.models.failure_model import Failure, Result
from desktop.services import device_service, firestore_service


def register_device(uid: str, id_token: str, app_version: str) -> Result:
    summary = device_service.get_device_summary()
    now = datetime.now(timezone.utc).isoformat()
    device = DeviceModel(
        device_id=summary["deviceId"],
        platform=summary["platform"],
        os_name=summary["osName"],
        app_version=app_version,
        status="active",
        paired_at=now,
        last_active_at=now,
    )
    path = f"users/{uid}/devices/{device.device_id}"
    result = firestore_service.set_document(path, device.to_firestore_fields(), id_token, merge=True)
    if not result.is_success:
        return result
    return Result.success(device)


def _generate_token(length: int = 24) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choice(alphabet) for _ in range(length))


def _generate_six_digit_code() -> str:
    return "".join(random.choice(string.digits) for _ in range(6))


def create_pair_token(uid: str, id_token: str, mode: str = "qr") -> Result:
    """mode: 'qr' atau 'code'. Mengembalikan dict berisi token/kode + waktu kedaluwarsa."""
    token = _generate_token() if mode == "qr" else _generate_six_digit_code()
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=PAIR_DEVICE_QR_TTL_SECONDS)

    payload = {
        "uid": uid,
        "mode": mode,
        "status": "pending",
        "expiresAt": expires_at.isoformat(),
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    result = firestore_service.set_document(f"{COLLECTION_PAIR_TOKENS}/{token}", payload, id_token, merge=False)
    if not result.is_success:
        return result

    return Result.success({"token": token, "expiresAt": payload["expiresAt"], "mode": mode})


def get_pair_token_status(token: str, id_token: str) -> Result:
    """Dipakai Desktop untuk polling status: 'pending' | 'approved' | tidak ditemukan (kedaluwarsa/terpakai)."""
    result = firestore_service.get_document(f"{COLLECTION_PAIR_TOKENS}/{token}", id_token)
    if not result.is_success:
        return Result.error(Failure.from_code(ERROR_PAIR_TOKEN_EXPIRED))

    data = result.data
    expires_at_raw = data.get("expiresAt")
    if expires_at_raw:
        expires_at = datetime.fromisoformat(expires_at_raw)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) >= expires_at:
            return Result.error(Failure.from_code(ERROR_PAIR_TOKEN_EXPIRED))

    return Result.success(data)


def consume_pair_token(token: str, id_token: str) -> Result:
    """Dipanggil setelah device baru berhasil menyelesaikan pairing -- token langsung
    dihapus agar tidak bisa dipakai ulang (one-time-use)."""
    status_result = get_pair_token_status(token, id_token)
    if not status_result.is_success:
        return status_result

    if status_result.data.get("status") != "approved":
        return Result.error(Failure.from_code(ERROR_PAIR_TOKEN_ALREADY_USED))

    delete_result = firestore_service.delete_document(f"{COLLECTION_PAIR_TOKENS}/{token}", id_token)
    if not delete_result.is_success:
        return delete_result
    return Result.success(True)
