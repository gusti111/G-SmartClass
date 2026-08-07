"""
base_view.py
Helper untuk memuat file .ui (dibuat di Qt Designer) secara runtime memakai
QUiLoader, sesuai kesepakatan "dual-purpose .ui" (bisa dibuka di Designer,
juga bisa di-load langsung tanpa kompilasi ke .py).

Custom widget yang dipromosikan di .ui (mis. QRCodeWidget) didaftarkan di
sini sekali agar semua View bisa memakainya.
"""
from PySide6.QtCore import QFile, QIODevice
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget

import desktop.resources.resources_rc  # noqa: F401  (registrasi Qt Resource :/logo, :/icons, :/illustrations)
from desktop.widgets.qr_code.qr_code_widget import QRCodeWidget

_loader = QUiLoader()
_loader.registerCustomWidget(QRCodeWidget)


def load_ui(ui_path: str, parent: QWidget = None) -> QWidget:
    ui_file = QFile(ui_path)
    if not ui_file.open(QIODevice.ReadOnly):
        raise FileNotFoundError(f"Tidak bisa membuka file .ui: {ui_path}")

    try:
        widget = _loader.load(ui_file, parent)
    finally:
        ui_file.close()

    if widget is None:
        raise RuntimeError(f"Gagal memuat .ui: {ui_path} (periksa customwidgets/header path).")

    return widget
