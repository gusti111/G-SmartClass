"""
login_controller.py
Menghubungkan interaksi widget di login.ui dengan login_repository (business
logic) memakai TaskRunner (QThread) agar UI tidak freeze saat memanggil
Firebase.
"""
import uuid

from PySide6.QtCore import QObject, QTimer, Signal

from desktop.core.task_runner import TaskRunner
from desktop.features.authentication.login.models.login_model import LoginFormData
from desktop.features.authentication.login.services import login_service
from desktop.logger.logger import get_logger

logger = get_logger(__name__)

_QR_LOGIN_TTL_SECONDS = 60


class LoginController(QObject):
    login_started = Signal()
    login_succeeded = Signal(object)   # payload: {"user": UserModel, "session": SessionModel}
    login_failed = Signal(object)      # payload: Failure

    qr_countdown_changed = Signal(int)  # detik tersisa

    def __init__(self, parent=None):
        super().__init__(parent)
        self._runner = None

        self._qr_seconds_left = _QR_LOGIN_TTL_SECONDS
        self._qr_timer = QTimer(self)
        self._qr_timer.timeout.connect(self._tick_qr_countdown)

    # ------------------------------------------------------------------
    # Email + Password login
    # ------------------------------------------------------------------
    def submit_login(self, email: str, password: str, remember_me: bool) -> None:
        form = LoginFormData(email=email, password=password, remember_me=remember_me)

        self.login_started.emit()
        self._runner = TaskRunner(login_service.login, form)
        self._runner.succeeded.connect(self.login_succeeded.emit)
        self._runner.failed.connect(self.login_failed.emit)
        self._runner.start()

    # ------------------------------------------------------------------
    # QR Login (belum tersambung ke Cloud Function -- lihat catatan di bawah)
    # ------------------------------------------------------------------
    def start_qr_login_session(self) -> str:
        """Membuat payload QR lokal untuk ditampilkan. CATATAN PENTING:
        alur QR Login butuh Cloud Function ('approveLoginRequest') di
        backend/functions yang divalidasi oleh aplikasi mobile G-SmartClass
        yang sudah login -- fungsi tersebut belum ada di tahap ini, sehingga
        polling status persetujuan belum diaktifkan. QR ini baru sebatas
        representasi visual + auto-refresh 60 detik."""
        token = str(uuid.uuid4())
        self._qr_seconds_left = _QR_LOGIN_TTL_SECONDS
        self._qr_timer.start(1000)
        logger.debug("QR login session dibuat (lokal, belum tersambung backend): %s", token)
        return f"gsmartclass://login?token={token}"

    def stop_qr_login_session(self) -> None:
        self._qr_timer.stop()

    def _tick_qr_countdown(self) -> None:
        self._qr_seconds_left -= 1
        self.qr_countdown_changed.emit(self._qr_seconds_left)
        if self._qr_seconds_left <= 0:
            self._qr_timer.stop()
