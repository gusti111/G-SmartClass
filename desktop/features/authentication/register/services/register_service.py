"""
register_service.py
"""
from desktop.features.authentication.register.models.register_model import (
    RegisterFormData,
    role_label_to_value,
    validate_register_form,
)
from desktop.features.authentication.register.repositories import register_repository
from desktop.models.failure_model import Failure, Result


def register(form: RegisterFormData) -> Result:
    error_message = validate_register_form(form)
    if error_message:
        return Result.error(Failure(code=0, message=error_message))

    role_value = role_label_to_value(form.role_label)
    return register_repository.register(
        email=form.email,
        password=form.password,
        full_name=form.full_name,
        role=role_value,
        phone=form.phone,
        institution=form.institution,
    )
