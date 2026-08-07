"""
email_verification_controller.py
"""
from PySide6.QtCore import QObject, QTimer, Signal

from desktop.config.settings import EMAIL_OTP_RESEND_COOLDOWN_SECONDS
from desktop.core.task_runner import TaskRunner
from desktop.features.authentication.email_verification.services import email_verification_service


class EmailVerificationController(QObject):
    send_otp_started = Signal()
    send_otp_succeeded = Signal(object)
    send_otp_failed = Signal(object)

    verify_started = Signal()
    verify_succeeded = Signal(object)  # SessionModel
    verify_failed = Signal(object)

    resend_countdown_changed = Signal(int)  # detik tersisa, 0 = tombol resend aktif

    def __init__(self, parent=None):
        super().__init__(parent)
        self._send_runner = None
        self._verify_runner = None

        self._seconds_left = 0
        self._cooldown_timer = QTimer(self)
        self._cooldown_timer.timeout.connect(self._tick_cooldown)

    def send_otp(self, email: str, id_token: str) -> None:
        self.send_otp_started.emit()
        self._send_runner = TaskRunner(email_verification_service.send_otp, email, id_token)
        self._send_runner.succeeded.connect(self._on_send_succeeded)
        self._send_runner.failed.connect(self.send_otp_failed.emit)
        self._send_runner.start()

    def _on_send_succeeded(self, payload) -> None:
        self.send_otp_succeeded.emit(payload)
        self._start_resend_cooldown()

    def _start_resend_cooldown(self) -> None:
        self._seconds_left = EMAIL_OTP_RESEND_COOLDOWN_SECONDS
        self.resend_countdown_changed.emit(self._seconds_left)
        self._cooldown_timer.start(1000)

    def _tick_cooldown(self) -> None:
        self._seconds_left -= 1
        self.resend_countdown_changed.emit(max(self._seconds_left, 0))
        if self._seconds_left <= 0:
            self._cooldown_timer.stop()

    def verify_code(self, email: str, code: str, uid: str, id_token: str, user, refresh_token: str,
                     expires_in: str) -> None:
        self.verify_started.emit()
        self._verify_runner = TaskRunner(
            email_verification_service.verify_otp_and_create_session,
            email, code, uid, id_token, user, refresh_token, expires_in,
        )
        self._verify_runner.succeeded.connect(self.verify_succeeded.emit)
        self._verify_runner.failed.connect(self.verify_failed.emit)
        self._verify_runner.start()
