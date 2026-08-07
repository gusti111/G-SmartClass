"""
register_controller.py
"""
from PySide6.QtCore import QObject, Signal

from desktop.core.task_runner import TaskRunner
from desktop.features.authentication.register.models.register_model import RegisterFormData
from desktop.features.authentication.register.services import register_service


class RegisterController(QObject):
    register_started = Signal()
    register_succeeded = Signal(object)  # {"user": UserModel, "idToken": str, "refreshToken": str, "expiresIn": str}
    register_failed = Signal(object)     # Failure

    def __init__(self, parent=None):
        super().__init__(parent)
        self._runner = None

    def submit_register(self, form: RegisterFormData) -> None:
        self.register_started.emit()
        self._runner = TaskRunner(register_service.register, form)
        self._runner.succeeded.connect(self.register_succeeded.emit)
        self._runner.failed.connect(self.register_failed.emit)
        self._runner.start()
