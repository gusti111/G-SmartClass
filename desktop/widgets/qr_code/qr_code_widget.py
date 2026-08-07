"""
qr_code_widget.py
Custom widget QLabel yang menampilkan QR Code dari sebuah payload string
(dipakai di login.ui & pair_device.ui lewat mekanisme "Promote to").

Membutuhkan package `qrcode[pil]` (lihat desktop/requirements.txt).
"""
import io

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel

try:
    import qrcode
except ImportError:  # pragma: no cover
    qrcode = None


class QRCodeWidget(QLabel):
    """Extends QLabel supaya tetap kompatibel dengan .ui yang mem-promote QLabel."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self._payload = ""

    def set_payload(self, payload: str) -> None:
        self._payload = payload
        if not qrcode:
            self.setText("[qrcode package belum terinstall]")
            return

        qr = qrcode.QRCode(border=1, box_size=6)
        qr.add_data(payload)
        qr.make(fit=True)
        image = qr.make_image(fill_color="#0F172A", back_color="#FFFFFF")

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")

        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue(), "PNG")
        self.setPixmap(
            pixmap.scaled(self.width() or 180, self.height() or 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def clear_qr(self) -> None:
        self._payload = ""
        self.clear()
        self.setText("[QR CODE]")

    @property
    def payload(self) -> str:
        return self._payload
