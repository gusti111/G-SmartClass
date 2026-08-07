"""
forgot_password_view.py
View untuk halaman Forgot Password (AUTH-004).
"""
import os

from PySide6.QtWidgets import QButtonGroup, QVBoxLayout, QWidget

from desktop.core.base_view import load_ui
from desktop.core import ui_polish
from desktop.features.authentication.forgot_password.controllers.forgot_password_controller import (
    ForgotPasswordController,
)
from desktop.services import notification_service

_UI_PATH = os.path.join(os.path.dirname(__file__), "..", "ui", "forgot_password.ui")


class ForgotPasswordView(QWidget):
    def __init__(self, router, parent=None):
        super().__init__(parent)
        self._router = router

        self.ui = load_ui(os.path.abspath(_UI_PATH), self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self._controller = ForgotPasswordController(self)
        self._setup_window_controls()
        self._setup_theme_toggle()
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

    def _apply_visual_polish(self) -> None:
        ui_polish.apply_back_to_login_icon(self.ui)
        ui_polish.set_label_icon(self.ui.lblIconEnvelope, "icon_mail_lock", size=64)
        ui_polish.set_button_icon(self.ui.btnSendReset, "icon_send", size=16)
        self.ui.btnSendReset.setText("Kirim Tautan Reset")
        ui_polish.set_button_icon(self.ui.btnNeedHelp, "icon_help_circle", size=16)
        self.ui.btnNeedHelp.setText("Butuh Bantuan?")
        ui_polish.apply_help_button_icon(self.ui)
        ui_polish.apply_secure_badge(self.ui)
        if hasattr(self.ui, "iconNoticeShield"):
            ui_polish.set_label_icon(self.ui.iconNoticeShield, "icon_shield_check", size=22)
        ui_polish.apply_card_shadow(self.ui.authCard, blur=48, y_offset=14, alpha=40)

    def _setup_actions(self) -> None:
        self.ui.btnSendReset.clicked.connect(self._on_send_clicked)
        self.ui.btnBackToLogin.clicked.connect(lambda: self._router.navigate("login"))
        self.ui.btnGoToLogin.clicked.connect(lambda: self._router.navigate("login"))
        self.ui.btnNeedHelp.clicked.connect(
            lambda: notification_service.show_info(
                self, "Hubungi admin sekolah/institusi Anda, atau email support@gsmartclass.app"
            )
        )

    def _on_send_clicked(self) -> None:
        self._controller.submit_email(self.ui.inputEmail.text())

    def _connect_controller_signals(self) -> None:
        self._controller.send_started.connect(lambda: self._set_loading(True))
        self._controller.send_succeeded.connect(self._on_send_succeeded)
        self._controller.send_failed.connect(self._on_send_failed)

    def _set_loading(self, is_loading: bool) -> None:
        self.ui.btnSendReset.setEnabled(not is_loading)
        self.ui.btnSendReset.setText("Mengirim..." if is_loading else "Kirim Tautan Reset")

    def _on_send_succeeded(self, _payload) -> None:
        self._set_loading(False)
        notification_service.show_success(
            self, f"Tautan reset kata sandi telah dikirim ke {self.ui.inputEmail.text().strip()}."
        )

    def _on_send_failed(self, failure) -> None:
        self._set_loading(False)
        notification_service.show_error(self, failure.message)
