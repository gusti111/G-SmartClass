"""
forgot_password_controller.py
"""
from PySide6.QtCore import QObject, Signal

from desktop.core.task_runner import TaskRunner
from desktop.features.authentication.forgot_password.services import forgot_password_service


class ForgotPasswordController(QObject):
    send_started = Signal()
    send_succeeded = Signal(object)
    send_failed = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._runner = None

    def submit_email(self, email: str) -> None:
        self.send_started.emit()
        self._runner = TaskRunner(forgot_password_service.send_reset_link, email)
        self._runner.succeeded.connect(self.send_succeeded.emit)
        self._runner.failed.connect(self.send_failed.emit)
        self._runner.start()
