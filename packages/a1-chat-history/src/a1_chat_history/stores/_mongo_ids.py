"""ObjectId helpers for the MongoCRUD-backed store."""
from bson import ObjectId


def object_id(value):
    try:
        return ObjectId(value)
    except Exception:
        return None


def msg_filter(session_id, message_id):
    oid = object_id(message_id)
    if oid is not None:
        return {"session_id": session_id, "_id": oid}
    return {"session_id": session_id, "id": message_id}


def eq_filter(**fields):
    return {key: value for key, value in fields.items() if value}
