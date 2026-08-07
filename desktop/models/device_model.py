"""
device_model.py
Merepresentasikan dokumen Firestore: users/{uid}/devices/{deviceId}
"""
from dataclasses import dataclass


@dataclass
class DeviceModel:
    device_id: str
    platform: str      # "desktop"
    os_name: str        # "Windows 11", "macOS 14", dll (dari module `platform`)
    app_version: str
    ip_address: str = ""
    status: str = "active"   # "active" | "revoked"
    paired_at: str = ""
    last_active_at: str = ""

    def to_firestore_fields(self) -> dict:
        return {
            "platform": self.platform,
            "osName": self.os_name,
            "appVersion": self.app_version,
            "ipAddress": self.ip_address,
            "status": self.status,
            "pairedAt": self.paired_at,
            "lastActiveAt": self.last_active_at,
        }

    @staticmethod
    def from_firestore_fields(device_id: str, fields: dict) -> "DeviceModel":
        return DeviceModel(
            device_id=device_id,
            platform=fields.get("platform", "desktop"),
            os_name=fields.get("osName", ""),
            app_version=fields.get("appVersion", ""),
            ip_address=fields.get("ipAddress", ""),
            status=fields.get("status", "active"),
            paired_at=fields.get("pairedAt", ""),
            last_active_at=fields.get("lastActiveAt", ""),
        )
