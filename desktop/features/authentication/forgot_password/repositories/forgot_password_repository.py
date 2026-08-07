"""
forgot_password_repository.py
"""
from desktop.models.failure_model import Result
from desktop.repositories import auth_repository


def send_reset_link(email: str) -> Result:
    return auth_repository.send_password_reset(email.strip())
