"""
forgot_password_model.py
"""
import re
from typing import Optional

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_email(email: str) -> Optional[str]:
    if not email.strip():
        return "Email tidak boleh kosong."
    if not _EMAIL_PATTERN.match(email.strip()):
        return "Format email tidak valid."
    return None
