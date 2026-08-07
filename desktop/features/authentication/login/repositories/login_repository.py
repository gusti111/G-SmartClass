"""
login_repository.py
Tipis: mendelegasikan ke desktop.repositories.auth_repository (shared),
disediakan supaya LoginController tidak bergantung langsung pada modul
repositories root -- memudahkan penggantian logic khusus halaman Login
(mis. rate limiting percobaan login) tanpa menyentuh AuthRepository bersama.
"""
from desktop.models.failure_model import Result
from desktop.repositories import auth_repository


def login(email: str, password: str, remember_me: bool) -> Result:
    return auth_repository.login_with_email_password(email.strip(), password, remember_me)
