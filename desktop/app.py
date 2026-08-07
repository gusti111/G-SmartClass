"""
app.py
Bootstrap aplikasi desktop G-SmartClass.

Urutan startup:
    1. Load .env (config/environment.py)
    2. Buat QApplication + load tema dasar (light.qss)
    3. Siapkan MainWindow berisi QStackedWidget + AppRouter
    4. Registrasi seluruh view Authentication (lazy factory)
    5. Tampilkan Splash Screen sebagai halaman pertama
"""
import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from desktop.config.environment import load_environment
from desktop.config.settings import APP_NAME, DESKTOP_DIR
from desktop.logger.logger import get_logger
from desktop.routes.router import AppRouter
import desktop.resources.resources_rc  # noqa: F401  (registrasi Qt Resource lebih awal)

logger = get_logger(__name__)


def _register_authentication_routes(router: AppRouter) -> None:
    """Import di dalam fungsi supaya startup app.py tetap ringan
    (menghindari import Firebase/requests dsb sebelum benar-benar dibutuhkan)."""
    from desktop.features.authentication.splash.views.splash_view import SplashView
    from desktop.features.authentication.login.views.login_view import LoginView
    from desktop.features.authentication.register.views.register_view import RegisterView
    from desktop.features.authentication.forgot_password.views.forgot_password_view import ForgotPasswordView
    from desktop.features.authentication.email_verification.views.email_verification_view import (
        EmailVerificationView,
    )
    from desktop.features.authentication.pair_device.views.pair_device_view import PairDeviceView

    router.register_view("splash", lambda r: SplashView(router=r))
    router.register_view("login", lambda r: LoginView(router=r))
    router.register_view("register", lambda r: RegisterView(router=r))
    router.register_view("forgot_password", lambda r: ForgotPasswordView(router=r))
    router.register_view("email_verification", lambda r: EmailVerificationView(router=r))
    router.register_view("pair_device", lambda r: PairDeviceView(router=r))

    # Dashboard belum dibangun pada tahap ini (modul terpisah). Placeholder
    # sederhana disediakan supaya Splash/Login tidak crash saat navigate("dashboard").
    from PySide6.QtWidgets import QLabel

    router.register_view(
        "dashboard",
        lambda r: QLabel("Dashboard belum diimplementasikan.\n(Modul selanjutnya)"),
    )


def _load_theme(app: QApplication, theme_name: str = "light") -> None:
    theme_path = DESKTOP_DIR / "themes" / f"{theme_name}.qss"
    if theme_path.exists():
        app.setStyleSheet(theme_path.read_text(encoding="utf-8"))
    else:
        logger.warning("Theme file tidak ditemukan: %s", theme_path)


def run_application() -> int:
    load_environment()

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    _load_theme(app, "light")

    main_window = QMainWindow()
    main_window.setWindowTitle(APP_NAME)
    main_window.resize(1456, 1030)

    stacked_widget = QStackedWidget()
    main_window.setCentralWidget(stacked_widget)

    router = AppRouter(stacked_widget)
    _register_authentication_routes(router)

    main_window.show()
    router.navigate("splash")

    logger.info("%s berhasil dijalankan.", APP_NAME)
    return app.exec()
