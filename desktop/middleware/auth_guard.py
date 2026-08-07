"""
auth_guard.py
Middleware kecil untuk memutuskan apakah pengguna boleh masuk ke Dashboard
atau harus diarahkan ke Login. Dipakai oleh SplashController dan bisa dipakai
ulang oleh Router saat berpindah ke halaman yang butuh autentikasi.
"""
from desktop.logger.logger import get_logger
from desktop.models.failure_model import Result
from desktop.repositories import auth_repository

logger = get_logger(__name__)


def resolve_initial_route() -> str:
    """Dipanggil Splash Screen. Return 'dashboard' jika session lokal valid &
    berhasil di-refresh, selain itu 'login'."""
    refresh_result: Result = auth_repository.refresh_session()
    if refresh_result.is_success:
        logger.info("Session valid, uid=%s -> Dashboard", refresh_result.data.uid)
        return "dashboard"

    logger.info("Tidak ada session valid -> Login")
    return "login"


def require_authenticated_session():
    """Dipakai oleh halaman selain Authentication sebelum menampilkan data
    sensitif. Mengembalikan SessionModel atau None."""
    from desktop.services import session_service

    session = session_service.load_session()
    if session is None:
        return None
    if session_service.is_session_expired(session):
        return None
    return session
