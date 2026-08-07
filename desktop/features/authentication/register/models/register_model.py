"""
register_model.py
Data form Register + validasi client-side.
"""
import re
from dataclasses import dataclass
from typing import Optional

from desktop.config.constants import ROLE_ADMIN, ROLE_GURU, VALID_REGISTER_ROLES

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_ROLE_LABEL_TO_VALUE = {"Guru": ROLE_GURU, "Admin": ROLE_ADMIN}


@dataclass
class RegisterFormData:
    full_name: str
    role_label: str
    email: str
    phone: str
    password: str
    confirm_password: str
    institution: str
    agreement_checked: bool


def role_label_to_value(role_label: str) -> Optional[str]:
    return _ROLE_LABEL_TO_VALUE.get(role_label)


def validate_register_form(form: RegisterFormData) -> Optional[str]:
    if not form.full_name.strip():
        return "Nama lengkap tidak boleh kosong."

    role_value = role_label_to_value(form.role_label)
    if role_value is None or role_value not in VALID_REGISTER_ROLES:
        return "Silakan pilih peran (Guru/Admin)."

    if not form.email.strip():
        return "Email tidak boleh kosong."
    if not _EMAIL_PATTERN.match(form.email.strip()):
        return "Format email tidak valid."

    if not form.password:
        return "Kata sandi tidak boleh kosong."
    if len(form.password) < 8:
        return "Kata sandi minimal 8 karakter."
    if form.password != form.confirm_password:
        return "Konfirmasi kata sandi tidak sesuai."

    if not form.agreement_checked:
        return "Anda harus menyetujui Syarat & Ketentuan dan Kebijakan Privasi."

    return None
