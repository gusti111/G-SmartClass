"""
firebase.py
Konfigurasi Firebase & builder endpoint REST API.

G-SmartClass mengakses Firebase murni lewat REST API (tanpa Firebase Admin SDK / Pyrebase),
konsisten dengan pendekatan yang dipakai di proyek EduTrack (Flutter) untuk menghindari
masalah koneksi streaming/gRPC. Semua request dilakukan dengan `requests` biasa.

Referensi endpoint resmi Google:
- Identity Toolkit (Auth):  https://identitytoolkit.googleapis.com/v1/...
- Secure Token (Refresh):   https://securetoken.googleapis.com/v1/token
- Firestore REST:           https://firestore.googleapis.com/v1/projects/{project}/databases/(default)/documents
- Realtime Database:        https://{database_url}/{path}.json
- Cloud Functions (HTTP):   {FUNCTIONS_BASE_URL}/{functionName}
"""
from dataclasses import dataclass

from desktop.config.environment import get_env, get_env_int


@dataclass(frozen=True)
class FirebaseConfig:
    api_key: str
    auth_domain: str
    project_id: str
    storage_bucket: str
    messaging_sender_id: str
    app_id: str
    database_url: str
    functions_region: str
    functions_base_url: str
    http_timeout: int


def load_firebase_config() -> FirebaseConfig:
    return FirebaseConfig(
        api_key=get_env("FIREBASE_API_KEY", "YOUR_API_KEY"),
        auth_domain=get_env("FIREBASE_AUTH_DOMAIN", ""),
        project_id=get_env("FIREBASE_PROJECT_ID", "YOUR_PROJECT_ID"),
        storage_bucket=get_env("FIREBASE_STORAGE_BUCKET", ""),
        messaging_sender_id=get_env("FIREBASE_MESSAGING_SENDER_ID", ""),
        app_id=get_env("FIREBASE_APP_ID", ""),
        database_url=get_env("FIREBASE_DATABASE_URL", ""),
        functions_region=get_env("FUNCTIONS_REGION", "asia-southeast1"),
        functions_base_url=get_env("FUNCTIONS_BASE_URL", ""),
        http_timeout=get_env_int("HTTP_TIMEOUT_SECONDS", 15),
    )


# Singleton config yang dipakai di seluruh services/repositories
FIREBASE_CONFIG = load_firebase_config()


# ---------------------------------------------------------------------------
# Endpoint builders
# ---------------------------------------------------------------------------
IDENTITY_TOOLKIT_BASE = "https://identitytoolkit.googleapis.com/v1"
SECURE_TOKEN_BASE = "https://securetoken.googleapis.com/v1"
FIRESTORE_BASE = "https://firestore.googleapis.com/v1"


def identity_toolkit_url(action: str) -> str:
    """action contoh: 'accounts:signUp', 'accounts:signInWithPassword',
    'accounts:sendOobCode', 'accounts:update', 'accounts:lookup'"""
    return f"{IDENTITY_TOOLKIT_BASE}/{action}?key={FIREBASE_CONFIG.api_key}"


def secure_token_url() -> str:
    return f"{SECURE_TOKEN_BASE}/token?key={FIREBASE_CONFIG.api_key}"


def firestore_document_url(path: str) -> str:
    """path contoh: 'users/UID123' atau 'pair_tokens/abcd'"""
    return f"{FIRESTORE_BASE}/projects/{FIREBASE_CONFIG.project_id}/databases/(default)/documents/{path}"


def firestore_query_url() -> str:
    return (
        f"{FIRESTORE_BASE}/projects/{FIREBASE_CONFIG.project_id}"
        f"/databases/(default)/documents:runQuery"
    )


def realtime_database_url(path: str) -> str:
    base = FIREBASE_CONFIG.database_url.rstrip("/")
    return f"{base}/{path}.json"


def cloud_function_url(function_name: str) -> str:
    base = FIREBASE_CONFIG.functions_base_url.rstrip("/")
    return f"{base}/{function_name}"
