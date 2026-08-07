"""
pair_device_repository.py
Tipis: mendelegasikan ke desktop.repositories.device_repository (shared).
"""
from desktop.models.failure_model import Result
from desktop.repositories import device_repository

from desktop.features.authentication.pair_device.models.pair_device_model import PairToken


def create_pair_token(uid: str, id_token: str, mode: str) -> Result:
    result = device_repository.create_pair_token(uid, id_token, mode)
    if not result.is_success:
        return result
    data = result.data
    return Result.success(PairToken(token=data["token"], mode=data["mode"], expires_at=data["expiresAt"]))


def get_pair_token_status(token: str, id_token: str) -> Result:
    return device_repository.get_pair_token_status(token, id_token)


def consume_pair_token(token: str, id_token: str) -> Result:
    return device_repository.consume_pair_token(token, id_token)
