"""
email_verification_repository.py

CATATAN ARSITEKTUR PENTING:
Menuliskan kode OTP ke Firestore (langkah di bawah) TIDAK SAMA DENGAN
mengirim email tersebut ke pengguna. Pengiriman email sesungguhnya harus
dilakukan lewat Cloud Function (mis. Firestore-triggered function
`sendOtpEmail` atau HTTP callable) yang memakai layanan email pihak ketiga
(SendGrid/Nodemailer), KARENA kredensial pengiriman email tidak boleh berada
di client. Cloud Function tersebut belum dibangun pada tahap ini
(backend/functions masih kosong) -- kode di bawah sudah menyiapkan payload
& endpoint pemanggilannya (best-effort, non-fatal jika function belum ada),
sehingga tinggal disambungkan begitu backend siap.
"""
from desktop.config.constants import COLLECTION_EMAIL_OTPS, ERROR_OTP_EXPIRED, ERROR_OTP_INVALID
from desktop.config.firebase import cloud_function_url
from desktop.logger.logger import get_logger
from desktop.models.failure_model import Failure, Result
from desktop.repositories import user_repository
from desktop.services import firestore_service

from desktop.features.authentication.email_verification.models.email_verification_model import (
    build_otp_document,
    generate_otp_code,
    hash_otp_code,
    is_otp_expired,
)

logger = get_logger(__name__)


def send_otp(email: str, id_token: str) -> Result:
    code = generate_otp_code()
    document = build_otp_document(code)

    write_result = firestore_service.set_document(
        f"{COLLECTION_EMAIL_OTPS}/{email}", document, id_token, merge=False
    )
    if not write_result.is_success:
        return write_result

    _trigger_send_email_best_effort(email, code)
    return Result.success({"email": email})


def _trigger_send_email_best_effort(email: str, code: str) -> None:
    """Memanggil Cloud Function pengirim email. Jika belum ada (404/timeout),
    kegagalan ini TIDAK menggagalkan alur -- hanya dicatat di log, karena kode
    tetap valid di Firestore untuk keperluan demo/pengembangan lokal."""
    import requests

    try:
        requests.post(cloud_function_url("sendOtpEmail"), json={"email": email, "code": code}, timeout=5)
    except requests.exceptions.RequestException as exc:
        logger.warning(
            "Cloud Function 'sendOtpEmail' belum tersedia/tidak terjangkau (%s). "
            "Kode OTP tetap tersimpan di Firestore untuk verifikasi manual/testing.",
            exc,
        )


def verify_otp(email: str, code: str, uid: str, id_token: str) -> Result:
    doc_result = firestore_service.get_document(f"{COLLECTION_EMAIL_OTPS}/{email}", id_token)
    if not doc_result.is_success:
        return Result.error(Failure.from_code(ERROR_OTP_INVALID))

    data = doc_result.data
    if is_otp_expired(data.get("expiresAt", "")):
        return Result.error(Failure.from_code(ERROR_OTP_EXPIRED))

    if hash_otp_code(code) != data.get("codeHash"):
        return Result.error(Failure.from_code(ERROR_OTP_INVALID))

    update_result = user_repository.update_user_profile(
        uid, {"emailVerified": True, "status": "active"}, id_token
    )
    if not update_result.is_success:
        return update_result

    firestore_service.delete_document(f"{COLLECTION_EMAIL_OTPS}/{email}", id_token)
    return Result.success(True)
