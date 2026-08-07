"""
splash_view.py
View untuk Splash Screen (AUTH-001). Memuat splash.ui lewat QUiLoader,
menjalankan SplashController, lalu berpindah ke 'login' atau 'dashboard'
lewat AppRouter begitu inisialisasi selesai.
"""
import os

from PySide6.QtWidgets import QVBoxLayout, QWidget

from desktop.core.base_view import load_ui
from desktop.features.authentication.splash.controllers.splash_controller import SplashController

_UI_PATH = os.path.join(os.path.dirname(__file__), "..", "ui", "splash.ui")


class SplashView(QWidget):
    def __init__(self, router, parent=None):
        super().__init__(parent)
        self._router = router
        self._started = False

        self.ui = load_ui(os.path.abspath(_UI_PATH), self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self._controller = SplashController(self)
        self._controller.progress_changed.connect(self._on_progress_changed)
        self._controller.initialization_finished.connect(self._on_initialization_finished)

    def on_enter(self, **kwargs) -> None:
        if self._started:
            return
        self._started = True
        self._controller.start()

    def _on_progress_changed(self, percent: int, status_text: str) -> None:
        self.ui.loadingProgressBar.setValue(percent)
        self.ui.lblLoadingStatus.setText(status_text)

    def _on_initialization_finished(self, route: str) -> None:
        self._router.navigate(route)
