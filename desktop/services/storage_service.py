"""
storage_service.py
Wrapper REST API untuk Firebase Storage (upload avatar, dsb).
Diimplementasikan minimal untuk kebutuhan Authentication (upload avatar saat
Register); fitur upload materi/tugas dsb menyusul di modul Academic.

Referensi: https://firebase.google.com/docs/reference/rest/storage
"""
import mimetypes
import urllib.parse

import requests

from desktop.config.constants import ERROR_NETWORK_UNAVAILABLE
from desktop.config.firebase import FIREBASE_CONFIG
from desktop.logger.logger import get_logger
from desktop.models.failure_model import Failure, Result

logger = get_logger(__name__)

_STORAGE_BASE = "https://firebasestorage.googleapis.com/v0/b"


def upload_file(local_path: str, remote_path: str, id_token: str) -> Result:
    """remote_path contoh: 'avatar/UID123.jpg'"""
    bucket = FIREBASE_CONFIG.storage_bucket
    encoded_path = urllib.parse.quote(remote_path, safe="")
    url = f"{_STORAGE_BASE}/{bucket}/o?uploadType=media&name={encoded_path}"

    content_type = mimetypes.guess_type(local_path)[0] or "application/octet-stream"
    headers = {"Authorization": f"Bearer {id_token}", "Content-Type": content_type}

    try:
        with open(local_path, "rb") as file_obj:
            response = requests.post(url, headers=headers, data=file_obj, timeout=FIREBASE_CONFIG.http_timeout)
    except (requests.exceptions.RequestException, OSError) as exc:
        logger.error("Gagal upload file %s: %s", local_path, exc)
        return Result.error(Failure.from_code(ERROR_NETWORK_UNAVAILABLE, raw=str(exc)))

    if response.status_code >= 400:
        return Result.error(Failure.unknown(raw=response.text))

    data = response.json()
    download_token = data.get("downloadTokens", "")
    public_url = f"{_STORAGE_BASE}/{bucket}/o/{encoded_path}?alt=media&token={download_token}"
    return Result.success(public_url)
