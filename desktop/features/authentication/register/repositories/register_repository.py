"""
register_repository.py
Mendelegasikan proses registrasi ke desktop.repositories.auth_repository.
"""
from desktop.models.failure_model import Result
from desktop.repositories import auth_repository


def register(email: str, password: str, full_name: str, role: str, phone: str, institution: str) -> Result:
    return auth_repository.register_account(
        email=email.strip(),
        password=password,
        display_name=full_name.strip(),
        role=role,
        phone=phone.strip(),
        institution=institution.strip(),
    )
