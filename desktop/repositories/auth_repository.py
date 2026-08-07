"""
auth_repository.py
Orkestrasi tertinggi untuk alur autentikasi: menggabungkan AuthService (Identity
Toolkit), UserRepository (Firestore profile), DeviceRepository (device
registration), dan SessionService (penyimpanan lokal terenkripsi).

Ini adalah satu-satunya pintu masuk yang dipanggil oleh
login/register/forgot_password controllers.
"""
import uuid
from datetime import datetime, timezone

from desktop.config.constants import ERROR_EMAIL_NOT_VERIFIED
from desktop.config.settings import APP_VERSION
from desktop.models.failure_model import Failure, Result
from desktop.models.session_model import SessionModel
from desktop.models.user_model import UserModel
from desktop.repositories import device_repository, user_repository
from desktop.services import auth_service, session_service


def login_with_email_password(email: str, password: str, remember_me: bool = True) -> Result:
    auth_result = auth_service.sign_in_with_email_password(email, password)
    if not auth_result.is_success:
        return auth_result

    auth_data = auth_result.data
    uid = auth_data["localId"]
    id_token = auth_data["idToken"]

    profile_result = user_repository.get_user_profile(uid, id_token)
    if not profile_result.is_success:
        return profile_result
    user: UserModel = profile_result.data

    device_result = device_repository.register_device(uid, id_token, APP_VERSION)
    if not device_result.is_success:
        return device_result

    user_repository.touch_last_login(uid, id_token)

    session = SessionModel(
        uid=uid,
        email=user.email,
        id_token=id_token,
        refresh_token=auth_data["refreshToken"],
        device_id=device_result.data.device_id,
        session_id=str(uuid.uuid4()),
        login_at=datetime.now(timezone.utc).isoformat(),
        expired_at=auth_service.compute_expiry_iso(auth_data.get("expiresIn", "3600")),
        remember_me=remember_me,
        role=user.role,
    )
    session_service.save_session(session)

    return Result.success({"user": user, "session": session})


def register_account(email: str, password: str, display_name: str, role: str, phone: str, institution: str) -> Result:
    auth_result = auth_service.sign_up_with_email_password(email, password)
    if not auth_result.is_success:
        return auth_result

    auth_data = auth_result.data
    uid = auth_data["localId"]
    id_token = auth_data["idToken"]

    user = UserModel(
        uid=uid,
        email=email,
        display_name=display_name,
        role=role,
        phone=phone,
        institution=institution,
        email_verified=False,
        status="pending_verification",
    )
    profile_result = user_repository.create_user_profile(user, id_token)
    if not profile_result.is_success:
        return profile_result

    return Result.success(
        {
            "user": user,
            "idToken": id_token,
            "refreshToken": auth_data.get("refreshToken", ""),
            "expiresIn": auth_data.get("expiresIn", "3600"),
        }
    )


def send_password_reset(email: str) -> Result:
    return auth_service.send_password_reset_email(email)


def refresh_session() -> Result:
    """Dipanggil Splash Screen: cek session lokal, kalau ada coba refresh idToken."""
    session = session_service.load_session()
    if session is None:
        return Result.error(Failure.unknown(raw="NO_LOCAL_SESSION"))

    refresh_result = auth_service.refresh_id_token(session.refresh_token)
    if not refresh_result.is_success:
        session_service.clear_session()
        return refresh_result

    data = refresh_result.data
    session.id_token = data["id_token"]
    session.refresh_token = data["refresh_token"]
    session.expired_at = auth_service.compute_expiry_iso(data.get("expires_in", "3600"))
    session_service.save_session(session)

    return Result.success(session)


def create_session_after_verification(
    user: UserModel, id_token: str, refresh_token: str, expires_in: str, remember_me: bool = True
) -> Result:
    """Dipanggil EmailVerificationController setelah kode OTP berhasil diverifikasi,
    supaya user tidak perlu login ulang secara manual pasca-registrasi."""
    device_result = device_repository.register_device(user.uid, id_token, APP_VERSION)
    if not device_result.is_success:
        return device_result

    session = SessionModel(
        uid=user.uid,
        email=user.email,
        id_token=id_token,
        refresh_token=refresh_token,
        device_id=device_result.data.device_id,
        session_id=str(uuid.uuid4()),
        login_at=datetime.now(timezone.utc).isoformat(),
        expired_at=auth_service.compute_expiry_iso(expires_in),
        remember_me=remember_me,
        role=user.role,
    )
    session_service.save_session(session)
    return Result.success(session)


def logout() -> None:
    session_service.clear_session()


def ensure_email_verified(id_token: str) -> Result:
    account_result = auth_service.get_account_info(id_token)
    if not account_result.is_success:
        return account_result

    users = account_result.data.get("users", [])
    if not users or not users[0].get("emailVerified", False):
        return Result.error(Failure.from_code(ERROR_EMAIL_NOT_VERIFIED))
    return Result.success(True)
