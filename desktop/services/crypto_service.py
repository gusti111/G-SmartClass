"""
crypto_service.py
Memusatkan seluruh proses enkripsi/dekripsi session menggunakan Fernet
(package `cryptography`). Fase MVP: key disimpan sebagai file lokal
(desktop/cache/session/key.key). Untuk versi produksi, key sebaiknya
dipindah ke Windows Credential Manager / DPAPI / macOS Keychain
(lihat catatan roadmap keamanan pada SDD Authentication).
"""
from cryptography.fernet import Fernet, InvalidToken

from desktop.config.settings import SESSION_KEY_FILE
from desktop.logger.logger import get_logger

logger = get_logger(__name__)


def generate_key() -> bytes:
    return Fernet.generate_key()


def load_key() -> bytes:
    """Ambil key yang sudah ada, atau buat baru jika belum ada (first run)."""
    if SESSION_KEY_FILE.exists():
        return SESSION_KEY_FILE.read_bytes()

    key = generate_key()
    SESSION_KEY_FILE.write_bytes(key)
    logger.info("Session encryption key baru dibuat di %s", SESSION_KEY_FILE)
    return key


def rotate_key() -> bytes:
    """Membuat key baru. CATATAN: memanggil ini akan membuat session.enc lama
    tidak bisa didekripsi lagi -- pastikan clear_session() dipanggil dulu."""
    key = generate_key()
    SESSION_KEY_FILE.write_bytes(key)
    logger.warning("Session encryption key dirotasi.")
    return key


def encrypt(plaintext: str) -> bytes:
    fernet = Fernet(load_key())
    return fernet.encrypt(plaintext.encode("utf-8"))


def decrypt(ciphertext: bytes) -> str:
    fernet = Fernet(load_key())
    try:
        return fernet.decrypt(ciphertext).decode("utf-8")
    except InvalidToken as exc:
        logger.error("Gagal mendekripsi session (invalid token / key berubah): %s", exc)
        raise
