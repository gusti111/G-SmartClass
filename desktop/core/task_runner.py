"""
task_runner.py
Helper QThread generik supaya setiap Controller tidak perlu menulis ulang
boilerplate QThread untuk memanggil repository (network call) tanpa mem-block
UI thread.

Contoh pemakaian di controller:

    self._runner = TaskRunner(auth_repository.login_with_email_password, email, password)
    self._runner.succeeded.connect(self._on_login_success)
    self._runner.failed.connect(self._on_login_failed)
    self._runner.start()
"""
from PySide6.QtCore import QThread, Signal

from desktop.models.failure_model import Result


class TaskRunner(QThread):
    succeeded = Signal(object)
    failed = Signal(object)

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self._fn = fn
        self._args = args
        self._kwargs = kwargs

    def run(self) -> None:
        try:
            result = self._fn(*self._args, **self._kwargs)
        except Exception as exc:  # noqa: BLE001
            from desktop.models.failure_model import Failure

            self.failed.emit(Failure.unknown(raw=str(exc)))
            return

        if isinstance(result, Result):
            if result.is_success:
                self.succeeded.emit(result.data)
            else:
                self.failed.emit(result.failure)
        else:
            self.succeeded.emit(result)
