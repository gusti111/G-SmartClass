"""
splash_controller.py
Menjalankan seluruh proses inisialisasi Splash Screen di background thread
(supaya UI tidak freeze), lalu memberi tahu SplashView halaman mana yang
harus dituju berikutnya ('login' atau 'dashboard').

Proses berat (cek koneksi internet, refresh session ke Firebase) dijalankan
lewat TaskRunner (QThread) yang memanggil middleware.auth_guard.resolve_initial_route().
Progress bar hanya animasi visual (SPLASH_STEPS) yang berjalan paralel supaya
splash tidak terasa diam walau proses network sedang berlangsung.
"""
from typing import Optional

from PySide6.QtCore import QObject, QTimer, Signal

from desktop.config.settings import SPLASH_MIN_DURATION_MS
from desktop.core.task_runner import TaskRunner
from desktop.features.authentication.splash.models.splash_state_model import SPLASH_STEPS
from desktop.logger.logger import get_logger
from desktop.middleware.auth_guard import resolve_initial_route

logger = get_logger(__name__)


class SplashController(QObject):
    progress_changed = Signal(int, str)
    initialization_finished = Signal(str)  # "login" | "dashboard"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._step_index = 0
        self._route_resolved = None
        self._min_duration_elapsed = False

        self._step_timer = QTimer(self)
        self._step_timer.timeout.connect(self._advance_step)

        self._min_duration_timer = QTimer(self)
        self._min_duration_timer.setSingleShot(True)
        self._min_duration_timer.timeout.connect(self._on_min_duration_elapsed)

        self._runner: Optional[TaskRunner] = None

    def start(self) -> None:
        logger.info("Splash: memulai inisialisasi aplikasi.")
        self._step_timer.start(180)
        self._min_duration_timer.start(SPLASH_MIN_DURATION_MS)

        self._runner = TaskRunner(resolve_initial_route)
        self._runner.succeeded.connect(self._on_route_resolved)
        self._runner.failed.connect(lambda _failure: self._on_route_resolved("login"))
        self._runner.start()

    def _advance_step(self) -> None:
        if self._step_index < len(SPLASH_STEPS) - 1:
            step = SPLASH_STEPS[self._step_index]
            self.progress_changed.emit(step.percent, step.status_text)
            self._step_index += 1
        else:
            self._step_timer.stop()

    def _on_min_duration_elapsed(self) -> None:
        self._min_duration_elapsed = True
        self._maybe_finish()

    def _on_route_resolved(self, route: str) -> None:
        self._route_resolved = route
        self._maybe_finish()

    def _maybe_finish(self) -> None:
        """Splash baru benar-benar pindah halaman setelah DUA syarat terpenuhi:
        durasi minimum sudah lewat (UX: tidak berkedip terlalu cepat) DAN
        proses resolve route (cek session ke Firebase) sudah selesai."""
        if self._route_resolved is None or not self._min_duration_elapsed:
            return

        self._step_timer.stop()
        self.progress_changed.emit(100, "Selesai.")
        logger.info("Splash: inisialisasi selesai, mengarahkan ke '%s'.", self._route_resolved)
        self.initialization_finished.emit(self._route_resolved)
