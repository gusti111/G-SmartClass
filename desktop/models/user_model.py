"""
user_model.py
Merepresentasikan dokumen Firestore: users/{uid}
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class UserModel:
    uid: str
    email: str
    display_name: str
    role: str  # "admin" | "guru" | "murid"
    photo_url: str = ""
    phone: str = ""
    institution: str = ""
    email_verified: bool = False
    status: str = "active"
    created_at: str = ""
    updated_at: str = ""
    last_login_at: str = ""

    @staticmethod
    def from_firestore_fields(uid: str, fields: dict) -> "UserModel":
        """fields adalah dict hasil parsing Firestore REST `document.fields`
        (sudah disederhanakan oleh FirestoreService, bukan format bertipe {"stringValue": ...})."""
        return UserModel(
            uid=uid,
            email=fields.get("email", ""),
            display_name=fields.get("displayName", ""),
            role=fields.get("role", "murid"),
            photo_url=fields.get("photoUrl", ""),
            phone=fields.get("phone", ""),
            institution=fields.get("institution", ""),
            email_verified=fields.get("emailVerified", False),
            status=fields.get("status", "active"),
            created_at=fields.get("createdAt", ""),
            updated_at=fields.get("updatedAt", ""),
            last_login_at=fields.get("lastLoginAt", ""),
        )

    def to_firestore_fields(self) -> dict:
        return {
            "email": self.email,
            "displayName": self.display_name,
            "role": self.role,
            "photoUrl": self.photo_url,
            "phone": self.phone,
            "institution": self.institution,
            "emailVerified": self.email_verified,
            "status": self.status,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "lastLoginAt": self.last_login_at,
        }
