"""
login_model.py
Data form Login + aturan validasi client-side sebelum memanggil repository
(mengurangi request sia-sia ke Firebase untuk input yang jelas-jelas salah).
"""
import re
from dataclasses import dataclass
from typing import Optional

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass
class LoginFormData:
    email: str
    password: str
    remember_me: bool = True


def validate_login_form(form: LoginFormData) -> Optional[str]:
    """Return pesan error (str) jika tidak valid, atau None jika valid."""
    if not form.email.strip():
        return "Email tidak boleh kosong."
    if not _EMAIL_PATTERN.match(form.email.strip()):
        return "Format email tidak valid."
    if not form.password:
        return "Kata sandi tidak boleh kosong."
    if len(form.password) < 8:
        return "Kata sandi minimal 8 karakter."
    return None
