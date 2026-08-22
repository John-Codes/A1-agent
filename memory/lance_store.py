from datetime import datetime
from uuid import uuid4

from config import LANCEDB_PATH, LANCEDB_TABLE
from memory.embeddings import embed_text


def store_record(kind, title, text, source_path="", tags=None):
    vector = embed_text(_search_text(title, text, tags or []))
    table = _table(vector)
    record = _record(kind, title, text, source_path, tags or [], vector)
    table.add([record])
    return f"Stored memory {record['id']} ({kind}: {title})."


def search_records(query, kind="", limit=5):
    vector = embed_text(query)
    table = _table(vector)
    rows = table.search(vector).limit(int(limit)).to_list()
    rows = [row for row in rows if not kind or row.get("kind") == kind]
    return _format_rows(rows[: int(limit)])


def _table(vector):
    db = _connect()
    if LANCEDB_TABLE in _table_names(db):
        return db.open_table(LANCEDB_TABLE)
    return db.create_table(LANCEDB_TABLE, data=[_seed(vector)])


def _table_names(db):
    tables = db.list_tables()
    return tables.tables if hasattr(tables, "tables") else tables


def _connect():
    try:
        import lancedb
    except ImportError as exc:
        raise ImportError("Install lancedb from gateway/requirements.txt.") from exc
    LANCEDB_PATH.mkdir(parents=True, exist_ok=True)
    return lancedb.connect(str(LANCEDB_PATH))


def _record(kind, title, text, source_path, tags, vector):
    return {
        "id": str(uuid4()),
        "kind": kind,
        "title": title,
        "text": text,
        "source_path": source_path,
        "tags": ", ".join(tags),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "vector": vector,
    }


def _seed(vector):
    return _record("seed", "seed", "LanceDB memory initialized.", "", [], vector)


def _search_text(title, text, tags):
    return "\n".join([title, text, ", ".join(tags)]).strip()


def _format_rows(rows):
    if not rows:
        return "No memory results."
    lines = []
    for row in rows:
        lines.append(f"- {row['kind']} | {row['title']} | {row.get('source_path', '')}")
        lines.append(f"  {row['text'][:500]}")
    return "\n".join(lines)
