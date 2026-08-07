"""
G-SmartClass Desktop - Entry Point
Menjalankan aplikasi PySide6 dari root project.

Cara pakai:
    python main.py
"""
import os
import sys

# Pastikan root project ada di sys.path agar "desktop.*" bisa di-import
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from desktop.app import run_application  # noqa: E402

if __name__ == "__main__":
    sys.exit(run_application())
