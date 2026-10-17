import json
import time
from threading import Thread

from config import CONTEXT_DIR
from memory.lance_store import search_records, store_record

# 2026-10-16: 300s caused near-constant full-corpus + Trello re-embedding on
# this CPU-only box (pegged a core after almost every message). 1800s matches
# the heartbeat interval; mtime changes still trigger an immediate sync.
STALE_SECONDS = 1800
_last_sync, _last_context_mtime, _running = 0, 0, False
def sync_if_stale(background=True):
    global _last_sync, _last_context_mtime, _running
    mtime = _context_mtime()
    stale = mtime != _last_context_mtime or time.time() - _last_sync > STALE_SECONDS
    if not stale or _running:
        return "RAG sync is fresh."
    if background:
        Thread(target=_safe_sync, daemon=True).start()
        return "RAG sync started."
    return sync_now()
def sync_now():
    global _last_sync, _last_context_mtime, _running
    if _running:
        return "RAG sync already running."
    _running = True
    try:
        counts = {"context": _sync_context(), **_sync_trello()}
        _last_context_mtime, _last_sync = _context_mtime(), time.time()
        return "Synced " + ", ".join(f"{k}={v}" for k, v in counts.items()) + "."
    finally:
        _running = False
def retrieve(query, limit=6):
    try:
        return search_records(query, "", limit)
    except Exception as exc:
        return f"RAG retrieval unavailable: {exc}"
def run_rag_sync(body=""):
    data = json.loads(body or "{}")
    action = data.get("action", "sync")
    if action == "status":
        return f"last_sync={int(_last_sync)} running={_running}"
    if action != "sync":
        raise ValueError(f"Unknown rag_sync action: {action}")
    return sync_now()
def _safe_sync():
    try:
        sync_now()
    except Exception:
        pass
def _sync_context():
    count = 0
    for path in sorted([*CONTEXT_DIR.glob("*.md"), *CONTEXT_DIR.glob("*.xml")]):
        for idx, chunk in enumerate(_chunks(path.read_text(encoding="utf-8"))):
            title = f"{path.name} chunk {idx + 1}"
            kind = "life_log" if path.name == "LIFE_LOG.xml" else "context"
            store_record(kind, title, chunk, str(path), ["context", path.name])
            count += 1
    return count
def _sync_trello():
    from tools.trello_clone.client import TrelloCloneClient
    client = TrelloCloneClient()
    counts = {"trello_projects": 0, "trello_boards": 0, "trello_tasks": 0}
    sources = (("trello_project", "/projects", "trello_projects"),
               ("trello_board", "/boards", "trello_boards"),
               ("trello_task", "/tasks", "trello_tasks"))
    for kind, path, key in sources:
        try:
            for item in _items(client.get(path, {"limit": 100})):
                store_record(kind, _title(item), _text(kind, item), "", ["trello"])
                counts[key] += 1
        except Exception as exc:
            counts[f"{key}_error"] = str(exc)[:120]
    return counts
def _chunks(text, size=900):
    parts, current = [], ""
    for para in [p.strip() for p in text.split("\n\n") if p.strip()]:
        if len(current) + len(para) > size and current:
            parts.append(current)
            current = para
        else:
            current = f"{current}\n\n{para}".strip()
    return parts + ([current] if current else [])
def _items(data):
    if isinstance(data, list):
        return data
    if not isinstance(data, dict):
        return []
    for key in ("items", "data", "results", "projects", "boards", "tasks"):
        if isinstance(data.get(key), list):
            return data[key]
    return []
def _title(item): return str(item.get("title") or item.get("name") or item.get("id") or "untitled")
def _text(kind, item): return f"{kind}\n" + json.dumps(item, indent=2, sort_keys=True)[:1200]
def _context_paths(): return [*CONTEXT_DIR.glob("*.md"), *CONTEXT_DIR.glob("*.xml")]
def _context_mtime(): return max((p.stat().st_mtime for p in _context_paths()), default=0)
