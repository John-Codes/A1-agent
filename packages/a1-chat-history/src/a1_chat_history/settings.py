import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_HOME = Path(
    os.environ.get("A1_HISTORY_HOME", str(Path.home() / ".local" / "share" / "a1-chat-history"))
)
DEFAULT_WORKSPACE_ID = "default"


def _flag(name, default="0"):
    return os.environ.get(name, default).lower() in {"1", "true", "yes"}


@dataclass
class Settings:
    host: str = "127.0.0.1"
    port: int = 8004
    storage: str = "auto"  # auto | json | mongo
    data_file: str = str(DEFAULT_HOME / "history.json")
    mongo_uri: str = "mongodb://127.0.0.1:27017"
    mongo_db: str = "a1_chat_history"
    mongo_timeout_ms: int = 2000
    mongo_data_dir: str = str(DEFAULT_HOME / "mongo")
    auto_start_mongo: bool = False
    tool_token: str = ""

    @classmethod
    def from_env(cls):
        env = os.environ.get
        return cls(
            host=env("A1_HISTORY_HOST", "127.0.0.1"),
            port=int(env("A1_HISTORY_PORT", "8004")),
            storage=env("A1_HISTORY_STORAGE", "auto").lower(),
            data_file=env("A1_HISTORY_DATA_FILE", str(DEFAULT_HOME / "history.json")),
            mongo_uri=env("A1_HISTORY_MONGO_URI", "mongodb://127.0.0.1:27017"),
            mongo_db=env("A1_HISTORY_MONGO_DB", "a1_chat_history"),
            mongo_timeout_ms=int(env("A1_HISTORY_MONGO_TIMEOUT_MS", "2000")),
            mongo_data_dir=env("A1_HISTORY_MONGO_DATA_DIR", str(DEFAULT_HOME / "mongo")),
            auto_start_mongo=_flag("A1_HISTORY_AUTO_MONGO"),
            tool_token=env("A1_HISTORY_TOKEN", ""),
        )
