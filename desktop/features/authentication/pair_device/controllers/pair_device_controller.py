"""
pair_device_controller.py
Mengelola generate token (QR/kode 6 digit), countdown auto-refresh 60 detik,
dan polling status approval dari perangkat lain.
"""
from PySide6.QtCore import QObject, QTimer, Signal

from desktop.config.settings import PAIR_DEVICE_QR_TTL_SECONDS
from desktop.core.task_runner import TaskRunner
from desktop.features.authentication.pair_device.services import pair_device_service
from desktop.logger.logger import get_logger

logger = get_logger(__name__)

_POLL_INTERVAL_MS = 2000


class PairDeviceController(QObject):
    token_created = Signal(object)     # PairToken
    token_failed = Signal(object)      # Failure
    countdown_changed = Signal(int)    # detik tersisa
    paired_succeeded = Signal()
    paired_failed = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._uid = ""
        self._id_token = ""
        self._current_mode = "qr"
        self._current_token = ""
        self._seconds_left = PAIR_DEVICE_QR_TTL_SECONDS

        self._create_runner = None
        self._poll_runner = None
        self._consume_runner = None

        self._countdown_timer = QTimer(self)
        self._countdown_timer.timeout.connect(self._tick_countdown)

        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._poll_status)

    def set_session(self, uid: str, id_token: str) -> None:
        self._uid = uid
        self._id_token = id_token

    @property
    def current_mode(self) -> str:
        return self._current_mode

    def generate_token(self, mode: str) -> None:
        self._stop_timers()
        self._current_mode = mode
        self._create_runner = TaskRunner(pair_device_service.create_pair_token, self._uid, self._id_token, mode)
        self._create_runner.succeeded.connect(self._on_token_created)
        self._create_runner.failed.connect(self.token_failed.emit)
        self._create_runner.start()

    def _on_token_created(self, pair_token) -> None:
        self._current_token = pair_token.token
        self._seconds_left = PAIR_DEVICE_QR_TTL_SECONDS
        self.token_created.emit(pair_token)
        self.countdown_changed.emit(self._seconds_left)

        self._countdown_timer.start(1000)
        self._poll_timer.start(_POLL_INTERVAL_MS)

    def _tick_countdown(self) -> None:
        self._seconds_left -= 1
        self.countdown_changed.emit(max(self._seconds_left, 0))
        if self._seconds_left <= 0:
            # Auto-refresh token baru begitu kedaluwarsa (sesuai spesifikasi UI)
            self.generate_token(self._current_mode)

    def _poll_status(self) -> None:
        if not self._current_token:
            return
        self._poll_runner = TaskRunner(
            pair_device_service.get_pair_token_status, self._current_token, self._id_token
        )
        self._poll_runner.succeeded.connect(self._on_status_result)
        self._poll_runner.failed.connect(lambda _f: None)  # token belum approved/expired, tunggu tick berikutnya
        self._poll_runner.start()

    def _on_status_result(self, data: dict) -> None:
        if data.get("status") == "approved":
            self._stop_timers()
            self._consume_runner = TaskRunner(
                pair_device_service.consume_pair_token, self._current_token, self._id_token
            )
            self._consume_runner.succeeded.connect(lambda _r: self.paired_succeeded.emit())
            self._consume_runner.failed.connect(self.paired_failed.emit)
            self._consume_runner.start()

    def _stop_timers(self) -> None:
        self._countdown_timer.stop()
        self._poll_timer.stop()

    def stop(self) -> None:
        self._stop_timers()
