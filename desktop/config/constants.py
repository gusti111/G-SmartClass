"""
constants.py
Konstanta yang dipakai lintas modul Authentication: nama collection Firestore,
role, dan kode error standar (mengacu ke BAB 5.10 - Error Code pada SDD).
"""

# ---------------------------------------------------------------------------
# Firestore collections
# ---------------------------------------------------------------------------
COLLECTION_USERS = "users"
COLLECTION_DEVICES_SUBCOLLECTION = "devices"       # users/{uid}/devices/{deviceId}
COLLECTION_SESSIONS_SUBCOLLECTION = "sessions"     # users/{uid}/sessions/{sessionId}
COLLECTION_PAIR_TOKENS = "pair_tokens"             # pair_tokens/{token}
COLLECTION_EMAIL_OTPS = "email_otps"               # email_otps/{email}

# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------
ROLE_ADMIN = "admin"
ROLE_GURU = "guru"
ROLE_MURID = "murid"
VALID_REGISTER_ROLES = (ROLE_GURU, ROLE_ADMIN)  # sesuai catatan: murid tidak self-register

# ---------------------------------------------------------------------------
# Error codes (BAB 5.10)
# ---------------------------------------------------------------------------
ERROR_USER_NOT_FOUND = 1001
ERROR_TOKEN_EXPIRED = 1002
ERROR_PERMISSION_DENIED = 1003
ERROR_EMAIL_ALREADY_IN_USE = 1004
ERROR_INVALID_CREDENTIALS = 1005
ERROR_EMAIL_NOT_VERIFIED = 1006
ERROR_WEAK_PASSWORD = 1007
ERROR_NETWORK_UNAVAILABLE = 1008
ERROR_OTP_INVALID = 1009
ERROR_OTP_EXPIRED = 1010
ERROR_PAIR_TOKEN_EXPIRED = 1011
ERROR_PAIR_TOKEN_ALREADY_USED = 1012
ERROR_UNKNOWN = 1099

ERROR_MESSAGES = {
    ERROR_USER_NOT_FOUND: "Akun tidak ditemukan.",
    ERROR_TOKEN_EXPIRED: "Sesi Anda telah berakhir, silakan login kembali.",
    ERROR_PERMISSION_DENIED: "Anda tidak memiliki akses untuk melakukan tindakan ini.",
    ERROR_EMAIL_ALREADY_IN_USE: "Email sudah terdaftar. Silakan masuk atau gunakan email lain.",
    ERROR_INVALID_CREDENTIALS: "Email atau kata sandi salah.",
    ERROR_EMAIL_NOT_VERIFIED: "Email Anda belum diverifikasi.",
    ERROR_WEAK_PASSWORD: "Kata sandi minimal 8 karakter.",
    ERROR_NETWORK_UNAVAILABLE: "Tidak dapat terhubung ke server. Periksa koneksi internet Anda.",
    ERROR_OTP_INVALID: "Kode verifikasi tidak sesuai.",
    ERROR_OTP_EXPIRED: "Kode verifikasi sudah kedaluwarsa.",
    ERROR_PAIR_TOKEN_EXPIRED: "Kode/QR pairing sudah kedaluwarsa.",
    ERROR_PAIR_TOKEN_ALREADY_USED: "Kode/QR pairing sudah pernah digunakan.",
    ERROR_UNKNOWN: "Terjadi kesalahan tak terduga. Silakan coba lagi.",
}
