"""
failure_model.py
Representasi error terpusat (dipakai oleh semua repository/service) supaya
Controller/View cukup menampilkan `failure.message` tanpa perlu tahu detail
teknis HTTP/Firestore di baliknya.
"""
from dataclasses import dataclass
from typing import Optional

from desktop.config.constants import ERROR_MESSAGES, ERROR_UNKNOWN


@dataclass
class Failure:
    code: int
    message: str
    raw: Optional[str] = None

    @staticmethod
    def from_code(code: int, raw: Optional[str] = None) -> "Failure":
        return Failure(code=code, message=ERROR_MESSAGES.get(code, ERROR_MESSAGES[ERROR_UNKNOWN]), raw=raw)

    @staticmethod
    def unknown(raw: Optional[str] = None) -> "Failure":
        return Failure.from_code(ERROR_UNKNOWN, raw=raw)

    def __str__(self) -> str:  # pragma: no cover
        return f"[{self.code}] {self.message}"


class Result:
    """Wrapper sederhana ala Either/Result: sukses membawa `data`, gagal membawa `failure`."""

    def __init__(self, data=None, failure: Optional[Failure] = None):
        self.data = data
        self.failure = failure

    @property
    def is_success(self) -> bool:
        return self.failure is None

    @staticmethod
    def success(data=None) -> "Result":
        return Result(data=data)

    @staticmethod
    def error(failure: Failure) -> "Result":
        return Result(failure=failure)
