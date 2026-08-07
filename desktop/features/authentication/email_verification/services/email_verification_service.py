"""
email_verification_service.py
Menggabungkan verifikasi kode OTP dengan pembuatan session penuh (login
otomatis) setelah verifikasi berhasil, supaya EmailVerificationController
cukup memanggil satu fungsi saja.
"""
from desktop.features.authentication.email_verification.repositories import email_verification_repository
from desktop.models.failure_model import Result
from desktop.repositories import auth_repository


def send_otp(email: str, id_token: str) -> Result:
    return email_verification_repository.send_otp(email, id_token)


def verify_otp_and_create_session(email: str, code: str, uid: str, id_token: str, user, refresh_token: str,
                                   expires_in: str) -> Result:
    verify_result = email_verification_repository.verify_otp(email, code, uid, id_token)
    if not verify_result.is_success:
        return verify_result

    user.email_verified = True
    user.status = "active"
    return auth_repository.create_session_after_verification(user, id_token, refresh_token, expires_in)
