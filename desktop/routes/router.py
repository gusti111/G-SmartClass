"""
router.py
Router sederhana berbasis QStackedWidget untuk berpindah antar halaman
Authentication (Splash, Login, Register, Forgot Password, Email Verification,
Pair Device) dan nantinya Dashboard.

Setiap View diregistrasi lewat register_view(name, factory) supaya lazy-loaded
(baru dibuat saat pertama kali dinavigasi), menghindari import-cycle & startup
yang berat.
"""
from typing import Callable, Dict

from PySide6.QtWidgets import QStackedWidget, QWidget

from desktop.logger.logger import get_logger

logger = get_logger(__name__)


class AppRouter:
    def __init__(self, stacked_widget: QStackedWidget):
        self._stacked_widget = stacked_widget
        self._factories: Dict[str, Callable[["AppRouter"], QWidget]] = {}
        self._instances: Dict[str, QWidget] = {}

    def register_view(self, name: str, factory: Callable[["AppRouter"], QWidget]) -> None:
        self._factories[name] = factory

    def navigate(self, name: str, **kwargs) -> None:
        if name not in self._instances:
            if name not in self._factories:
                raise ValueError(f"Route '{name}' belum diregistrasi di AppRouter.")
            logger.debug("Membuat instance view untuk route '%s'", name)
            view = self._factories[name](self)
            self._instances[name] = view
            self._stacked_widget.addWidget(view)

        view = self._instances[name]
        if hasattr(view, "on_enter"):
            view.on_enter(**kwargs)
        self._stacked_widget.setCurrentWidget(view)
        logger.debug("Navigasi ke route '%s'", name)

    def current_route_widget(self) -> QWidget:
        return self._stacked_widget.currentWidget()
