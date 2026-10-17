import sys

from ..mongo_runtime import mongo_reachable, start_mongod
from ..settings import Settings
from .json_store import JsonStore


def get_store(settings: Settings, log=print):
    """Resolve the storage backend. Returns (store, backend_description)."""
    if settings.storage == "json":
        return JsonStore(settings.data_file), "json-file"

    if settings.storage in {"mongo", "auto"}:
        store, reason = _mongo_store(settings)
        if store is not None:
            return store, "mongodb"
        if settings.auto_start_mongo and start_mongod(settings, log=log):
            store, reason = _mongo_store(settings)
            if store is not None:
                return store, "mongodb (auto-started)"
        if settings.storage == "mongo":
            raise SystemExit(
                f"MongoDB requested but unavailable ({reason}). "
                "Fix the server, pass --auto-mongo with a mongod binary installed, "
                "or use --storage json."
            )
        log(f"MongoDB unavailable ({reason}); using JSON file storage.")
    return JsonStore(settings.data_file), "json-file"


def _mongo_store(settings: Settings):
    try:
        from .mongo_store import MongoStore
    except ImportError:
        return None, "pymongo not installed (pip install a1-chat-history[mongo])"
    if not mongo_reachable(settings.mongo_uri, settings.mongo_timeout_ms):
        return None, f"no server at {settings.mongo_uri}"
    try:
        return MongoStore(settings.mongo_uri, settings.mongo_db, settings.mongo_timeout_ms), None
    except Exception as exc:
        return None, str(exc)
