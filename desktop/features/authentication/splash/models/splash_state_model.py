"""
splash_state_model.py
Representasi kecil dari progres inisialisasi Splash Screen, dipakai untuk
mengirim update progress bar + status text ke SplashView dari
SplashController/worker thread.
"""
from dataclasses import dataclass


@dataclass
class SplashStep:
    percent: int
    status_text: str


SPLASH_STEPS = [
    SplashStep(10, "Memuat tema..."),
    SplashStep(25, "Memuat font..."),
    SplashStep(40, "Memuat konfigurasi..."),
    SplashStep(55, "Menginisialisasi Firebase..."),
    SplashStep(70, "Memeriksa koneksi internet..."),
    SplashStep(85, "Memeriksa sesi login..."),
    SplashStep(100, "Selesai."),
]
