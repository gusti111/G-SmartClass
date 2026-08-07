"""
user_repository.py
CRUD profil pengguna di Firestore: users/{uid}
"""
from datetime import datetime, timezone

from desktop.config.constants import COLLECTION_USERS
from desktop.models.failure_model import Result
from desktop.models.user_model import UserModel
from desktop.services import firestore_service


def get_user_profile(uid: str, id_token: str) -> Result:
    result = firestore_service.get_document(f"{COLLECTION_USERS}/{uid}", id_token)
    if not result.is_success:
        return result
    return Result.success(UserModel.from_firestore_fields(uid, result.data))


def create_user_profile(user: UserModel, id_token: str) -> Result:
    now = datetime.now(timezone.utc).isoformat()
    user.created_at = user.created_at or now
    user.updated_at = now
    result = firestore_service.set_document(
        f"{COLLECTION_USERS}/{user.uid}", user.to_firestore_fields(), id_token, merge=False
    )
    if not result.is_success:
        return result
    return Result.success(user)


def update_user_profile(uid: str, fields: dict, id_token: str) -> Result:
    fields = dict(fields)
    fields["updatedAt"] = datetime.now(timezone.utc).isoformat()
    return firestore_service.set_document(f"{COLLECTION_USERS}/{uid}", fields, id_token, merge=True)


def touch_last_login(uid: str, id_token: str) -> Result:
    return update_user_profile(uid, {"lastLoginAt": datetime.now(timezone.utc).isoformat()}, id_token)
