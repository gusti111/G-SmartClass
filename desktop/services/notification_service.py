"""
notification_service.py
Helper untuk menampilkan feedback ke pengguna (toast/alert sederhana).
Fase MVP memakai QMessageBox; nanti bisa diganti toast custom di
desktop/widgets/toast/ tanpa mengubah pemanggilnya.
"""
from PySide6.QtWidgets import QMessageBox, QWidget


def show_error(parent: QWidget, message: str, title: str = "Terjadi Kesalahan") -> None:
    QMessageBox.critical(parent, title, message)


def show_success(parent: QWidget, message: str, title: str = "Berhasil") -> None:
    QMessageBox.information(parent, title, message)


def show_info(parent: QWidget, message: str, title: str = "Informasi") -> None:
    QMessageBox.information(parent, title, message)


def confirm(parent: QWidget, message: str, title: str = "Konfirmasi") -> bool:
    result = QMessageBox.question(parent, title, message, QMessageBox.Yes | QMessageBox.No)
    return result == QMessageBox.Yes
