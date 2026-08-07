"""
register_view.py
View untuk halaman Register (AUTH-003). Setelah registrasi berhasil,
pengguna diarahkan ke halaman Email Verification (kode OTP 6 digit dikirim
di sana, lihat email_verification_controller.py).
"""
import os

from PySide6.QtWidgets import QButtonGroup, QLineEdit, QVBoxLayout, QWidget

from desktop.core.base_view import load_ui
from desktop.core import ui_polish
from desktop.features.authentication.register.controllers.register_controller import RegisterController
from desktop.features.authentication.register.models.register_model import RegisterFormData
from desktop.services import notification_service

_UI_PATH = os.path.join(os.path.dirname(__file__), "..", "ui", "register.ui")


class RegisterView(QWidget):
    def __init__(self, router, parent=None):
        super().__init__(parent)
        self._router = router

        self.ui = load_ui(os.path.abspath(_UI_PATH), self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self._controller = RegisterController(self)
        self._setup_window_controls()
        self._setup_theme_toggle()
        self._setup_password_fields()
        self._setup_actions()
        self._connect_controller_signals()
        self._apply_visual_polish()

    def on_enter(self, **kwargs) -> None:
        self._set_loading(False)

    def _setup_window_controls(self) -> None:
        ui_polish.apply_window_control_icons(self.ui)
        self.ui.btnMinimize.clicked.connect(lambda: self.window().showMinimized())
        self.ui.btnClose.clicked.connect(lambda: self.window().close())

        def _toggle_maximize():
            window = self.window()
            window.showNormal() if window.isMaximized() else window.showMaximized()

        self.ui.btnMaximize.clicked.connect(_toggle_maximize)

    def _setup_theme_toggle(self) -> None:
        ui_polish.apply_theme_toggle_icons(self.ui)
        theme_group = QButtonGroup(self)
        theme_group.setExclusive(True)
        theme_group.addButton(self.ui.btnThemeLight)
        theme_group.addButton(self.ui.btnThemeDark)

    def _setup_password_fields(self) -> None:
        def _toggle(checked, field, button):
            field.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)
            ui_polish.set_button_icon(button, "icon_eye_off" if checked else "icon_eye", size=15, clear_text=True)

        ui_polish.set_button_icon(self.ui.btnTogglePassword, "icon_eye", size=15, clear_text=True)
        ui_polish.set_button_icon(self.ui.btnToggleConfirmPassword, "icon_eye", size=15, clear_text=True)
        self.ui.btnTogglePassword.toggled.connect(
            lambda checked: _toggle(checked, self.ui.inputPassword, self.ui.btnTogglePassword)
        )
        self.ui.btnToggleConfirmPassword.toggled.connect(
            lambda checked: _toggle(checked, self.ui.inputConfirmPassword, self.ui.btnToggleConfirmPassword)
        )

    def _setup_actions(self) -> None:
        self.ui.btnRegister.clicked.connect(self._on_register_clicked)
        self.ui.btnBackToLogin.clicked.connect(lambda: self._router.navigate("login"))
        self.ui.btnGoToLogin.clicked.connect(lambda: self._router.navigate("login"))
        self.ui.btnRegisterGoogle.clicked.connect(self._on_sso_clicked)
        self.ui.btnTermsLink.clicked.connect(
            lambda: notification_service.show_info(self, "Halaman Syarat & Ketentuan belum tersedia.")
        )
        self.ui.btnPrivacyLink.clicked.connect(
            lambda: notification_service.show_info(self, "Halaman Kebijakan Privasi belum tersedia.")
        )

    def _apply_visual_polish(self) -> None:
        ui_polish.apply_back_to_login_icon(self.ui)
        ui_polish.apply_sso_button_icons(self.ui)
        ui_polish.set_button_icon(self.ui.btnRegister, "icon_graduation_cap", size=17)
        self.ui.btnRegister.setText("Daftar Sekarang")
        ui_polish.apply_help_button_icon(self.ui)
        ui_polish.apply_secure_badge(self.ui)
        ui_polish.apply_card_shadow(self.ui.authCard, blur=48, y_offset=14, alpha=40)

    def _on_sso_clicked(self) -> None:
        notification_service.show_info(
            self,
            "Daftar dengan Google membutuhkan alur OAuth berbasis browser yang belum "
            "diimplementasikan pada versi REST API murni ini.",
            title="Segera Hadir",
        )

    def _on_register_clicked(self) -> None:
        form = RegisterFormData(
            full_name=self.ui.inputFullName.text(),
            role_label=self.ui.cmbRole.currentText(),
            email=self.ui.inputEmail.text(),
            phone=self.ui.inputPhone.text(),
            password=self.ui.inputPassword.text(),
            confirm_password=self.ui.inputConfirmPassword.text(),
            institution=self.ui.inputInstitution.text(),
            agreement_checked=self.ui.chkAgreement.isChecked(),
        )
        self._controller.submit_register(form)

    def _connect_controller_signals(self) -> None:
        self._controller.register_started.connect(lambda: self._set_loading(True))
        self._controller.register_succeeded.connect(self._on_register_succeeded)
        self._controller.register_failed.connect(self._on_register_failed)

    def _set_loading(self, is_loading: bool) -> None:
        self.ui.btnRegister.setEnabled(not is_loading)
        self.ui.btnRegister.setText("Memproses..." if is_loading else "Daftar Sekarang")

    def _on_register_succeeded(self, payload: dict) -> None:
        self._set_loading(False)
        user = payload["user"]
        notification_service.show_success(
            self, f"Akun berhasil dibuat untuk {user.email}. Silakan verifikasi email Anda."
        )
        self._router.navigate(
            "email_verification",
            email=user.email,
            id_token=payload["idToken"],
            uid=user.uid,
            user=user,
            refresh_token=payload["refreshToken"],
            expires_in=payload["expiresIn"],
        )

    def _on_register_failed(self, failure) -> None:
        self._set_loading(False)
        notification_service.show_error(self, failure.message)
