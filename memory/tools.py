from memory.ingest import read_document
from memory.json_body import optional_tags, optional_text, parse_json, require_text
from memory.lance_store import search_records, store_record


def memory_store(body):
    data = parse_json(body)
    kind = require_text(data, "kind")
    title = require_text(data, "title")
    text = require_text(data, "text")
    source_path = optional_text(data, "source_path")
    return store_record(kind, title, text, source_path, optional_tags(data))


def memory_search(body):
    data = parse_json(body)
    query = require_text(data, "query")
    kind = optional_text(data, "kind")
    limit = int(data.get("limit", 5))
    return search_records(query, kind, max(1, min(limit, 20)))


def memory_ingest_path(body):
    data = parse_json(body)
    path, text = read_document(require_text(data, "path"))
    title = optional_text(data, "title") or path.name
    return store_record("document", title, text, str(path), optional_tags(data))
