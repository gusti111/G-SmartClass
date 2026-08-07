"""
pair_device_view.py
View untuk halaman Pair Device (AUTH-006). Halaman ini diakses SETELAH user
login (butuh session aktif) untuk menghubungkan perangkat baru. Karena modul
Dashboard belum ada, halaman ini masih bisa diuji manual dengan menavigasi
router.navigate("pair_device") selama session lokal tersedia.
"""
import os

from PySide6.QtWidgets import QButtonGroup, QVBoxLayout, QWidget

from desktop.core.base_view import load_ui
from desktop.core import ui_polish
from desktop.features.authentication.pair_device.controllers.pair_device_controller import PairDeviceController
from desktop.middleware.auth_guard import require_authenticated_session
from desktop.services import notification_service

_UI_PATH = os.path.join(os.path.dirname(__file__), "..", "ui", "pair_device.ui")


class PairDeviceView(QWidget):
    def __init__(self, router, parent=None):
        super().__init__(parent)
        self._router = router

        self.ui = load_ui(os.path.abspath(_UI_PATH), self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self._controller = PairDeviceController(self)
        self._setup_window_controls()
        self._setup_theme_toggle()
        self._setup_tabs()
        self._connect_controller_signals()
        self._apply_visual_polish()

    # ------------------------------------------------------------------
    def on_enter(self, **kwargs) -> None:
        session = require_authenticated_session()
        if session is None:
            notification_service.show_error(self, "Sesi Anda tidak valid. Silakan login kembali.")
            self._router.navigate("login")
            return

        self._controller.set_session(session.uid, session.id_token)
        self._controller.generate_token("qr" if self.ui.tabQrCode.isChecked() else "code")

    def closeEvent(self, event) -> None:  # noqa: N802 (Qt naming)
        self._controller.stop()
        super().closeEvent(event)

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
        ui_polish.set_label_icon(self.ui.lblIconDevices, "icon_devices", size=48)
        ui_polish.set_button_icon(self.ui.btnUse6DigitCode, "icon_keyboard", size=16)
        self.ui.btnUse6DigitCode.setText("Gunakan Kode 6 Digit")
        self.ui.lblSecureBadge.setText(self.ui.lblSecureBadge.text().replace("🛡", "").strip())
        self.ui.lblHowToTitle.setText(self.ui.lblHowToTitle.text().replace("?", "", 1).strip())
        ui_polish.apply_help_button_icon(self.ui)
        ui_polish.apply_secure_badge(self.ui)
        if hasattr(self.ui, "iconSecureShield"):
            ui_polish.set_label_icon(self.ui.iconSecureShield, "icon_shield_check", size=22)
        ui_polish.apply_card_shadow(self.ui.authCard, blur=48, y_offset=14, alpha=40)

    def _setup_tabs(self) -> None:
        tab_group = QButtonGroup(self)
        tab_group.setExclusive(True)
        tab_group.addButton(self.ui.tabQrCode)
        tab_group.addButton(self.ui.tabSixDigitCode)

        self.ui.tabQrCode.toggled.connect(self._on_tab_toggled)
        self.ui.tabSixDigitCode.toggled.connect(self._on_tab_toggled)
        self.ui.btnUse6DigitCode.clicked.connect(lambda: self.ui.tabSixDigitCode.setChecked(True))
        self.ui.btnBackToLogin.clicked.connect(lambda: self._router.navigate("login"))

    def _on_tab_toggled(self) -> None:
        if self.ui.tabQrCode.isChecked():
            self.ui.pairStackedWidget.setCurrentWidget(self.ui.pageQrCode)
            self._controller.generate_token("qr")
        else:
            self.ui.pairStackedWidget.setCurrentWidget(self.ui.pageSixDigitCode)
            self._controller.generate_token("code")

    # ------------------------------------------------------------------
    def _connect_controller_signals(self) -> None:
        self._controller.token_created.connect(self._on_token_created)
        self._controller.token_failed.connect(lambda failure: notification_service.show_error(self, failure.message))
        self._controller.countdown_changed.connect(self._on_countdown_changed)
        self._controller.paired_succeeded.connect(self._on_paired_succeeded)
        self._controller.paired_failed.connect(lambda failure: notification_service.show_error(self, failure.message))

    def _on_token_created(self, pair_token) -> None:
        if pair_token.mode == "qr":
            self.ui.qrCodeWidget.set_payload(pair_token.qr_payload)
        else:
            self.ui.lblSixDigitCode.setText(pair_token.display_code)

    def _on_countdown_changed(self, seconds_left: int) -> None:
        minutes, seconds = divmod(max(seconds_left, 0), 60)
        text = f"{minutes:02d}:{seconds:02d}"
        if hasattr(self.ui, "lblQrTimerValue"):
            self.ui.lblQrTimerValue.setText(text)

    def _on_paired_succeeded(self) -> None:
        notification_service.show_success(self, "Perangkat baru berhasil terhubung ke akun Anda.")
        self._controller.generate_token(self._controller.current_mode)  # sediakan token baru untuk pairing berikutnya
