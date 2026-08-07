"""
firestore_service.py
Wrapper REST API untuk Cloud Firestore (CRUD dasar + runQuery sederhana).
Semua request menyertakan `Authorization: Bearer {idToken}` milik user yang
sedang login, sehingga Firestore Security Rules (RBAC) tetap berlaku.

Referensi: https://firebase.google.com/docs/firestore/reference/rest
"""
from typing import Any, Optional

import requests

from desktop.config.constants import ERROR_NETWORK_UNAVAILABLE, ERROR_USER_NOT_FOUND
from desktop.config.firebase import FIREBASE_CONFIG, firestore_document_url
from desktop.logger.logger import get_logger
from desktop.models.failure_model import Failure, Result

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Konversi antara dict Python biasa <-> format bertipe Firestore REST
# ---------------------------------------------------------------------------
def _to_firestore_value(value: Any) -> dict:
    if isinstance(value, bool):
        return {"booleanValue": value}
    if isinstance(value, int):
        return {"integerValue": str(value)}
    if isinstance(value, float):
        return {"doubleValue": value}
    if value is None:
        return {"nullValue": None}
    return {"stringValue": str(value)}


def _from_firestore_value(value: dict) -> Any:
    if "stringValue" in value:
        return value["stringValue"]
    if "integerValue" in value:
        return int(value["integerValue"])
    if "doubleValue" in value:
        return float(value["doubleValue"])
    if "booleanValue" in value:
        return value["booleanValue"]
    if "nullValue" in value:
        return None
    if "mapValue" in value:
        return {k: _from_firestore_value(v) for k, v in value["mapValue"].get("fields", {}).items()}
    if "arrayValue" in value:
        return [_from_firestore_value(v) for v in value["arrayValue"].get("values", [])]
    return None


def to_firestore_fields(data: dict) -> dict:
    return {k: _to_firestore_value(v) for k, v in data.items()}


def from_firestore_document(document: dict) -> dict:
    fields = document.get("fields", {})
    return {k: _from_firestore_value(v) for k, v in fields.items()}


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------
def get_document(path: str, id_token: str) -> Result:
    headers = {"Authorization": f"Bearer {id_token}"}
    try:
        response = requests.get(firestore_document_url(path), headers=headers, timeout=FIREBASE_CONFIG.http_timeout)
    except requests.exceptions.RequestException as exc:
        return Result.error(Failure.from_code(ERROR_NETWORK_UNAVAILABLE, raw=str(exc)))

    if response.status_code == 404:
        return Result.error(Failure.from_code(ERROR_USER_NOT_FOUND, raw=path))
    if response.status_code >= 400:
        return Result.error(Failure.unknown(raw=response.text))

    return Result.success(from_firestore_document(response.json()))


def set_document(path: str, data: dict, id_token: str, merge: bool = True) -> Result:
    headers = {"Authorization": f"Bearer {id_token}"}
    body = {"fields": to_firestore_fields(data)}
    url = firestore_document_url(path)

    params = {}
    if merge:
        params["updateMask.fieldPaths"] = list(data.keys())

    try:
        response = requests.patch(url, headers=headers, json=body, params=params, timeout=FIREBASE_CONFIG.http_timeout)
    except requests.exceptions.RequestException as exc:
        return Result.error(Failure.from_code(ERROR_NETWORK_UNAVAILABLE, raw=str(exc)))

    if response.status_code >= 400:
        return Result.error(Failure.unknown(raw=response.text))

    return Result.success(from_firestore_document(response.json()))


def delete_document(path: str, id_token: Optional[str] = None) -> Result:
    headers = {"Authorization": f"Bearer {id_token}"} if id_token else {}
    try:
        response = requests.delete(firestore_document_url(path), headers=headers, timeout=FIREBASE_CONFIG.http_timeout)
    except requests.exceptions.RequestException as exc:
        return Result.error(Failure.from_code(ERROR_NETWORK_UNAVAILABLE, raw=str(exc)))

    if response.status_code >= 400 and response.status_code != 404:
        return Result.error(Failure.unknown(raw=response.text))
    return Result.success(True)
