"""
login_view.py
View untuk halaman Login (AUTH-002). Memuat login.ui, menghubungkan seluruh
widget ke LoginController, dan menangani navigasi antar halaman lewat
AppRouter (Register, Forgot Password, Dashboard).
"""
import os

from PySide6.QtWidgets import QButtonGroup, QLineEdit, QVBoxLayout, QWidget

from desktop.core.base_view import load_ui
from desktop.core import ui_polish
from desktop.features.authentication.login.controllers.login_controller import LoginController
from desktop.services import notification_service

_UI_PATH = os.path.join(os.path.dirname(__file__), "..", "ui", "login.ui")


class LoginView(QWidget):
    def __init__(self, router, parent=None):
        super().__init__(parent)
        self._router = router

        self.ui = load_ui(os.path.abspath(_UI_PATH), self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self._controller = LoginController(self)
        self._setup_window_controls()
        self._setup_theme_toggle()
        self._setup_tabs()
        self._setup_password_field()
        self._setup_actions()
        self._connect_controller_signals()
        self._apply_visual_polish()

    # ------------------------------------------------------------------
    def on_enter(self, **kwargs) -> None:
        # Bersihkan pesan error/loading tiap kali halaman ini ditampilkan kembali
        self._set_loading(False)

    # ------------------------------------------------------------------
    def _setup_window_controls(self) -> None:
        ui_polish.apply_window_control_icons(self.ui)
        self.ui.btnMinimize.clicked.connect(lambda: self.window().showMinimized())
        self.ui.btnClose.clicked.connect(lambda: self.window().close())

        def _toggle_maximize():
            window = self.window()
            if window.isMaximized():
                window.showNormal()
            else:
                window.showMaximized()

        self.ui.btnMaximize.clicked.connect(_toggle_maximize)

    def _setup_theme_toggle(self) -> None:
        ui_polish.apply_theme_toggle_icons(self.ui)
        theme_group = QButtonGroup(self)
        theme_group.setExclusive(True)
        theme_group.addButton(self.ui.btnThemeDark)
        theme_group.addButton(self.ui.btnThemeLight)
        # Catatan: penerapan tema global (light.qss/dark.qss) dikelola di desktop/app.py.
        # Di sini cukup memastikan hanya salah satu tombol yang aktif (exclusive toggle).

    def _setup_tabs(self) -> None:
        tab_group = QButtonGroup(self)
        tab_group.setExclusive(True)
        tab_group.addButton(self.ui.tabEmailLogin)
        tab_group.addButton(self.ui.tabQrLogin)

        self.ui.tabEmailLogin.toggled.connect(self._on_tab_toggled)
        self.ui.tabQrLogin.toggled.connect(self._on_tab_toggled)

    def _on_tab_toggled(self) -> None:
        if self.ui.tabEmailLogin.isChecked():
            self.ui.loginStackedWidget.setCurrentWidget(self.ui.pageEmailLogin)
            self._controller.stop_qr_login_session()
        else:
            self.ui.loginStackedWidget.setCurrentWidget(self.ui.pageQrLogin)
            payload = self._controller.start_qr_login_session()
            self.ui.qrCodeLoginWidget.set_payload(payload)

    def _setup_password_field(self) -> None:
        def _toggle_password_visibility(checked: bool) -> None:
            self.ui.inputPassword.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)
            ui_polish.set_button_icon(
                self.ui.btnTogglePassword, "icon_eye_off" if checked else "icon_eye", size=16, clear_text=True
            )

        ui_polish.set_button_icon(self.ui.btnTogglePassword, "icon_eye", size=16, clear_text=True)
        self.ui.btnTogglePassword.toggled.connect(_toggle_password_visibility)

    def _setup_actions(self) -> None:
        self.ui.btnLogin.clicked.connect(self._on_login_clicked)
        self.ui.btnForgotPassword.clicked.connect(lambda: self._router.navigate("forgot_password"))
        self.ui.btnGoToRegister.clicked.connect(lambda: self._router.navigate("register"))

        for button in (self.ui.btnLoginGoogle, self.ui.btnLoginMicrosoft, self.ui.btnLoginApple):
            button.clicked.connect(self._on_sso_clicked)

    def _on_sso_clicked(self) -> None:
        notification_service.show_info(
            self,
            "Login SSO (Google/Microsoft/Apple) membutuhkan alur OAuth berbasis browser "
            "yang belum diimplementasikan pada versi REST API murni ini. "
            "Silakan gunakan Login Email untuk saat ini.",
            title="Segera Hadir",
        )

    def _on_login_clicked(self) -> None:
        email = self.ui.inputEmail.text().strip()
        password = self.ui.inputPassword.text()
        remember_me = self.ui.chkRememberMe.isChecked()
        self._controller.submit_login(email, password, remember_me)

    # ------------------------------------------------------------------
    def _apply_visual_polish(self) -> None:
        """Menerapkan ikon, ilustrasi, dan shadow supaya tampilan tidak flat/kaku
        (struktur .ui tetap sama, hanya di-'kaya'-kan lewat kode)."""
        ui_polish.apply_sso_button_icons(self.ui)
        ui_polish.set_button_icon(self.ui.btnLogin, "icon_send", size=16)
        self.ui.btnLogin.setText("Masuk")
        ui_polish.apply_help_button_icon(self.ui)
        ui_polish.apply_secure_badge(self.ui)
        ui_polish.apply_card_shadow(self.ui.authCard, blur=48, y_offset=14, alpha=40)
        if hasattr(self.ui, "iconLanguage"):
            ui_polish.set_label_icon(self.ui.iconLanguage, "icon_globe", size=16)

    def _connect_controller_signals(self) -> None:
        self._controller.login_started.connect(lambda: self._set_loading(True))
        self._controller.login_succeeded.connect(self._on_login_succeeded)
        self._controller.login_failed.connect(self._on_login_failed)

    def _set_loading(self, is_loading: bool) -> None:
        self.ui.btnLogin.setEnabled(not is_loading)
        self.ui.btnLogin.setText("Memproses..." if is_loading else "Masuk")

    def _on_login_succeeded(self, payload: dict) -> None:
        self._set_loading(False)
        self._router.navigate("dashboard")

    def _on_login_failed(self, failure) -> None:
        self._set_loading(False)
        notification_service.show_error(self, failure.message)
