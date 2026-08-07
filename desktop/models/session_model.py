"""
session_model.py
Struktur data yang disimpan terenkripsi di desktop/cache/session/session.enc
"""
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class SessionModel:
    uid: str
    email: str
    id_token: str
    refresh_token: str
    device_id: str
    session_id: str
    login_at: str
    expired_at: str
    remember_me: bool = True
    role: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "SessionModel":
        return SessionModel(
            uid=data.get("uid", ""),
            email=data.get("email", ""),
            id_token=data.get("idToken", data.get("id_token", "")),
            refresh_token=data.get("refreshToken", data.get("refresh_token", "")),
            device_id=data.get("deviceId", data.get("device_id", "")),
            session_id=data.get("sessionId", data.get("session_id", "")),
            login_at=data.get("loginAt", data.get("login_at", "")),
            expired_at=data.get("expiredAt", data.get("expired_at", "")),
            remember_me=data.get("rememberMe", data.get("remember_me", True)),
            role=data.get("role", ""),
        )
