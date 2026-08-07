"""
login_service.py
Lapisan orkestrasi antara LoginController dan LoginRepository:
menjalankan validasi form terlebih dahulu sebelum memanggil repository,
sehingga Controller tidak perlu tahu detail validasi maupun pemanggilan data.
"""
from desktop.features.authentication.login.models.login_model import LoginFormData, validate_login_form
from desktop.features.authentication.login.repositories import login_repository
from desktop.models.failure_model import Failure, Result


def login(form: LoginFormData) -> Result:
    error_message = validate_login_form(form)
    if error_message:
        return Result.error(Failure(code=0, message=error_message))

    return login_repository.login(form.email, form.password, form.remember_me)
