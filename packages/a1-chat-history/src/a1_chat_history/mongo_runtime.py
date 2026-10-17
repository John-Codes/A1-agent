import shutil
import time
from pathlib import Path
from urllib.parse import urlparse

MONGOD_CANDIDATES = (
    "/usr/bin/mongod",
    "/usr/local/bin/mongod",
    "/opt/homebrew/bin/mongod",
)


def find_mongod():
    found = shutil.which("mongod")
    if found:
        return found
    for path in MONGOD_CANDIDATES:
        if Path(path).exists():
            return path
    return None


def mongo_reachable(uri, timeout_ms=2000):
    try:
        from pymongo import MongoClient

        client = MongoClient(uri, serverSelectionTimeoutMS=timeout_ms)
        client.admin.command("ping")
        client.close()
        return True
    except Exception:
        return False


def start_mongod(settings, log=print, wait_seconds=30):
    """Start a dedicated local mongod for A1 history. Returns True when ready."""
    binary = find_mongod()
    if not binary:
        log("No mongod binary found; install MongoDB or point A1_HISTORY_MONGO_URI at a server.")
        return False
    data_dir = Path(settings.mongo_data_dir).expanduser()
    data_dir.mkdir(parents=True, exist_ok=True)
    port = urlparse(settings.mongo_uri).port or 27017
    log(f"Starting built-in MongoDB: {binary} (dbpath={data_dir}, port={port})")
    subprocess_run = [
        binary,
        "--dbpath", str(data_dir),
        "--port", str(port),
        "--bind_ip", "127.0.0.1",
        "--logpath", str(data_dir / "mongod.log"),
        "--fork",
    ]
    result = subprocess.run(subprocess_run, capture_output=True, text=True)
    if result.returncode != 0:
        log(f"mongod failed to start: {result.stderr.strip()[:300]}")
        return False
    deadline = time.monotonic() + wait_seconds
    while time.monotonic() < deadline:
        if mongo_reachable(settings.mongo_uri, settings.mongo_timeout_ms):
            return True
        time.sleep(0.5)
    log("mongod started but did not become ready in time.")
    return False
