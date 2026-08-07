"""
pair_device_model.py
"""
from dataclasses import dataclass


@dataclass
class PairToken:
    token: str
    mode: str          # "qr" | "code"
    expires_at: str

    @property
    def qr_payload(self) -> str:
        return f"gsmartclass://pair?token={self.token}"

    @property
    def display_code(self) -> str:
        """Untuk mode 'code': tampilkan sebagai '123 456' agar mudah dibaca."""
        if self.mode == "code" and len(self.token) == 6:
            return f"{self.token[:3]} {self.token[3:]}"
        return self.token
