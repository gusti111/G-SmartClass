"""
forgot_password_service.py
"""
from desktop.features.authentication.forgot_password.models.forgot_password_model import validate_email
from desktop.features.authentication.forgot_password.repositories import forgot_password_repository
from desktop.models.failure_model import Failure, Result


def send_reset_link(email: str) -> Result:
    error_message = validate_email(email)
    if error_message:
        return Result.error(Failure(code=0, message=error_message))

    return forgot_password_repository.send_reset_link(email)
