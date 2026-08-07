"""
ui_polish.py
Helper terpusat untuk "mempercantik" tampilan native PySide6 tanpa mengubah
struktur .ui secara berlebihan (sesuai kesepakatan: .ui tetap seperti
wireframe, polish visual -- ikon, gambar, shadow -- diterapkan lewat kode).
"""
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtWidgets import QGraphicsDropShadowEffect

ICON_DIR = ":/icons"
ILLUSTRATION_DIR = ":/illustrations"
LOGO_PATH = ":/logo/gsmartclass_mark.svg"


def set_button_icon(button, icon_name: str, size: int = 18, keep_text: bool = True, clear_text: bool = False) -> None:
    if button is None:
        return
    button.setIcon(QIcon(f"{ICON_DIR}/{icon_name}.svg"))
    button.setIconSize(QSize(size, size))
    if clear_text or not keep_text:
        button.setText("")


def set_label_icon(label, icon_name: str, size: int = 32) -> None:
    """Mengganti isi QLabel (yang tadinya berupa teks emoji) dengan pixmap ikon SVG."""
    if label is None:
        return
    label.setText("")
    pixmap = QPixmap(f"{ICON_DIR}/{icon_name}.svg")
    label.setPixmap(pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation))


def apply_window_control_icons(ui) -> None:
    mapping = {"btnMinimize": "icon_minimize", "btnMaximize": "icon_maximize", "btnClose": "icon_close"}
    for name, icon in mapping.items():
        set_button_icon(getattr(ui, name, None), icon, size=14, clear_text=True)


def apply_theme_toggle_icons(ui) -> None:
    set_button_icon(getattr(ui, "btnThemeLight", None), "icon_sun", size=16, clear_text=True)
    set_button_icon(getattr(ui, "btnThemeDark", None), "icon_moon", size=16, clear_text=True)


def apply_back_to_login_icon(ui) -> None:
    button = getattr(ui, "btnBackToLogin", None)
    if button is None:
        return
    set_button_icon(button, "icon_arrow_left", size=16, keep_text=True)
    button.setText(button.text().replace("←", "").strip())


def apply_sso_button_icons(ui) -> None:
    mapping = {
        "btnLoginGoogle": ("icon_google", "Google"),
        "btnLoginMicrosoft": ("icon_microsoft", "Microsoft"),
        "btnLoginApple": ("icon_apple", "Apple"),
        "btnRegisterGoogle": ("icon_google", "Daftar dengan Google"),
    }
    for name, (icon, text) in mapping.items():
        button = getattr(ui, name, None)
        if button is None:
            continue
        set_button_icon(button, icon, size=18)
        button.setText(text)


def apply_help_button_icon(ui) -> None:
    button = getattr(ui, "btnHelp", None)
    if button is None:
        return
    set_button_icon(button, "icon_message_circle", size=15)
    button.setText("Butuh bantuan? Hubungi kami")


def apply_secure_badge(ui) -> None:
    label = getattr(ui, "lblSecureBadge", None)
    if label is None:
        return
    label.setText("Aman & Terpercaya")


def apply_card_shadow(widget, blur: int = 40, x_offset: int = 0, y_offset: int = 12, alpha: int = 45) -> None:
    """Efek shadow lembut di bawah kartu (sesuai spesifikasi desain: 'Drop Shadow')."""
    if widget is None:
        return
    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(blur)
    effect.setOffset(x_offset, y_offset)
    effect.setColor(QColor(15, 23, 42, alpha))
    widget.setGraphicsEffect(effect)
