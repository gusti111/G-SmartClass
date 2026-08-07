"""
email_verification_view.py
View untuk halaman Email Verification (AUTH-005): 6 kotak OTP dengan
auto-advance fokus antar kotak, countdown resend, dan verifikasi kode.
"""
import os

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtWidgets import QButtonGroup, QVBoxLayout, QWidget

from desktop.core.base_view import load_ui
from desktop.core import ui_polish
from desktop.features.authentication.email_verification.controllers.email_verification_controller import (
    EmailVerificationController,
)
from desktop.services import notification_service

_UI_PATH = os.path.join(os.path.dirname(__file__), "..", "ui", "email_verification.ui")


class _OtpBackspaceFilter(QObject):
    """Event filter kecil supaya tombol Backspace pada kotak OTP kosong
    otomatis memindahkan fokus ke kotak sebelumnya."""

    def __init__(self, otp_boxes, parent=None):
        super().__init__(parent)
        self._otp_boxes = otp_boxes

    def eventFilter(self, watched, event) -> bool:  # noqa: N802 (Qt naming)
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Backspace:
            if watched in self._otp_boxes and not watched.text():
                index = self._otp_boxes.index(watched)
                if index > 0:
                    self._otp_boxes[index - 1].setFocus()
        return False


class EmailVerificationView(QWidget):
    def __init__(self, router, parent=None):
        super().__init__(parent)
        self._router = router
        self._email = ""
        self._id_token = ""
        self._uid = ""
        self._user = None
        self._refresh_token = ""
        self._expires_in = "3600"

        self.ui = load_ui(os.path.abspath(_UI_PATH), self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self._otp_boxes = [
            self.ui.inputOtp1,
            self.ui.inputOtp2,
            self.ui.inputOtp3,
            self.ui.inputOtp4,
            self.ui.inputOtp5,
            self.ui.inputOtp6,
        ]

        self._controller = EmailVerificationController(self)
        self._setup_window_controls()
        self._setup_theme_toggle()
        self._setup_otp_boxes()
        self._setup_actions()
        self._connect_controller_signals()
        self._apply_visual_polish()

    # ------------------------------------------------------------------
    def on_enter(self, email: str = "", id_token: str = "", uid: str = "", user=None,
                 refresh_token: str = "", expires_in: str = "3600", **kwargs) -> None:
        self._email = email
        self._id_token = id_token
        self._uid = uid
        self._user = user
        self._refresh_token = refresh_token
        self._expires_in = expires_in

        self.ui.lblEmailChipText.setText(email)
        self.ui.lblEmailTarget.setText(email)
        self._clear_otp_boxes()
        self.ui.inputOtp1.setFocus()

        if email and id_token:
            self._controller.send_otp(email, id_token)

    # ------------------------------------------------------------------
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
        ui_polish.set_label_icon(self.ui.lblIconEnvelope, "icon_mail_check", size=64)
        ui_polish.set_button_icon(self.ui.btnVerify, "icon_check_circle", size=16)
        self.ui.btnVerify.setText("Verifikasi")
        ui_polish.set_button_icon(self.ui.btnResendCode, "icon_mail", size=16)
        self.ui.btnResendCode.setText("Kirim Ulang Kode")
        ui_polish.apply_help_button_icon(self.ui)
        ui_polish.apply_secure_badge(self.ui)
        if hasattr(self.ui, "iconEmailChip"):
            ui_polish.set_label_icon(self.ui.iconEmailChip, "icon_mail", size=18)
        ui_polish.apply_card_shadow(self.ui.authCard, blur=48, y_offset=14, alpha=40)

    def _setup_otp_boxes(self) -> None:
        backspace_filter = _OtpBackspaceFilter(self._otp_boxes, self)
        for index, box in enumerate(self._otp_boxes):
            box.installEventFilter(backspace_filter)
            box.textChanged.connect(lambda text, i=index: self._on_otp_box_changed(i, text))
        self._backspace_filter = backspace_filter  # simpan referensi agar tidak digarbage-collect

    def _on_otp_box_changed(self, index: int, text: str) -> None:
        if text and index < len(self._otp_boxes) - 1:
            self._otp_boxes[index + 1].setFocus()

    def _clear_otp_boxes(self) -> None:
        for box in self._otp_boxes:
            box.blockSignals(True)
            box.clear()
            box.blockSignals(False)

    def _collect_otp_code(self) -> str:
        return "".join(box.text().strip() for box in self._otp_boxes)

    def _setup_actions(self) -> None:
        self.ui.btnVerify.clicked.connect(self._on_verify_clicked)
        self.ui.btnResendCode.clicked.connect(self._on_resend_clicked)
        self.ui.btnBackToLogin.clicked.connect(lambda: self._router.navigate("login"))
        self.ui.btnGoToRegister.clicked.connect(lambda: self._router.navigate("register"))
        self.ui.btnChangeEmail.clicked.connect(lambda: self._router.navigate("register"))

    def _on_verify_clicked(self) -> None:
        code = self._collect_otp_code()
        if len(code) != 6:
            notification_service.show_error(self, "Masukkan 6 digit kode verifikasi.")
            return
        self._controller.verify_code(
            self._email, code, self._uid, self._id_token, self._user, self._refresh_token, self._expires_in
        )

    def _on_resend_clicked(self) -> None:
        self._clear_otp_boxes()
        self.ui.inputOtp1.setFocus()
        self._controller.send_otp(self._email, self._id_token)

    # ------------------------------------------------------------------
    def _connect_controller_signals(self) -> None:
        self._controller.send_otp_failed.connect(
            lambda failure: notification_service.show_error(self, failure.message)
        )
        self._controller.resend_countdown_changed.connect(self._on_resend_countdown_changed)

        self._controller.verify_started.connect(lambda: self._set_verifying(True))
        self._controller.verify_succeeded.connect(self._on_verify_succeeded)
        self._controller.verify_failed.connect(self._on_verify_failed)

    def _on_resend_countdown_changed(self, seconds_left: int) -> None:
        if seconds_left <= 0:
            self.ui.btnResendCode.setEnabled(True)
            self.ui.lblResendHint.setText("Tidak menerima kode? Periksa folder spam Anda.")
        else:
            self.ui.btnResendCode.setEnabled(False)
            self.ui.lblResendHint.setText(
                f"Tidak menerima kode? Periksa folder spam atau kirim ulang kode dalam 00:{seconds_left:02d}"
            )

    def _set_verifying(self, is_loading: bool) -> None:
        self.ui.btnVerify.setEnabled(not is_loading)
        self.ui.btnVerify.setText("Memverifikasi..." if is_loading else "Verifikasi")

    def _on_verify_succeeded(self, _session) -> None:
        self._set_verifying(False)
        notification_service.show_success(self, "Email berhasil diverifikasi. Selamat datang di G-SmartClass!")
        self._router.navigate("dashboard")

    def _on_verify_failed(self, failure) -> None:
        self._set_verifying(False)
        notification_service.show_error(self, failure.message)
