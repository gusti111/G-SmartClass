"""
pair_device_service.py
Lapisan orkestrasi tipis di atas PairDeviceRepository. Disediakan agar
PairDeviceController tidak memanggil repository langsung, konsisten dengan
pola Controller -> Service -> Repository -> Firebase di seluruh modul
Authentication.
"""
from desktop.features.authentication.pair_device.repositories import pair_device_repository
from desktop.models.failure_model import Result


def create_pair_token(uid: str, id_token: str, mode: str) -> Result:
    return pair_device_repository.create_pair_token(uid, id_token, mode)


def get_pair_token_status(token: str, id_token: str) -> Result:
    return pair_device_repository.get_pair_token_status(token, id_token)


def consume_pair_token(token: str, id_token: str) -> Result:
    return pair_device_repository.consume_pair_token(token, id_token)
