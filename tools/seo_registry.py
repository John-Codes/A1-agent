"""Small, Markdown-only CRUD registries for SEO planning."""
from pathlib import Path
import re
import threading
import fcntl

ROOT = Path(__file__).resolve().parents[1] / "context"
FILES = {"cdl_keywords": ROOT / "CDL_SEO_KEYWORDS.md", "google_seo_rules": ROOT / "GOOGLE_SEO_RULES.md"}
LOCK = threading.RLock()


def run_seo_registry(body, kind):
    import json
    data = json.loads(body or "{}")
    action = data.pop("action", "read")
    path = FILES[kind]
    with LOCK:
        with path.with_suffix('.lock').open('w') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            text = path.read_text(encoding="utf-8")
            if action == "read":
                return text
            if action == "list":
                return _list_rows(text, kind)
            if action in {"create", "update", "delete"}:
                result = _mutate(text, data, action, kind)
                temp = path.with_suffix('.tmp')
                temp.write_text(result, encoding="utf-8")
                temp.replace(path)
                return _list_rows(result, kind)
    raise ValueError("Unsupported SEO registry action")


def _list_rows(text, kind):
    marker = "KW-" if kind == "cdl_keywords" else "SEO-"
    return "\n".join(line for line in text.splitlines() if marker in line and line.lstrip().startswith(("|", "#")))


def _mutate(text, data, action, kind):
    key = "id" if kind == "cdl_keywords" else "id"
    ident = str(data.get(key, "")).strip()
    if action == 'create' and not ident:
        prefix = 'KW' if kind == 'cdl_keywords' else 'SEO'
        used = [int(n) for n in re.findall(rf'{prefix}-(\d{{3}})', text)]
        ident = f'{prefix}-{max(used, default=0) + 1:03d}'
        data['id'] = ident
    if not re.fullmatch(r"KW-\d{3}" if kind == "cdl_keywords" else r"SEO-\d{3}", ident):
        raise ValueError("id must be a stable registry id")
    lines = text.splitlines()
    indexes = [i for i, line in enumerate(lines) if re.match(rf'^\|\s*{ident}\s*\||^## {ident}\b', line)]
    if action == "delete":
        if not indexes:
            raise ValueError("Registry id not found")
        del lines[indexes[0]]
        return "\n".join(lines) + "\n"
    if action == "update" and indexes:
        lines[indexes[0]] = _render(data, kind, lines[indexes[0]])
        return "\n".join(lines) + "\n"
    if action == "update":
        raise ValueError("Registry id not found")
    if indexes:
        raise ValueError("Registry id already exists")
    insert = _render(data, kind, "")
    pos = max((i for i, line in enumerate(lines) if line.startswith("|")), default=len(lines) - 1)
    lines.insert(pos + 1, insert)
    return "\n".join(lines) + "\n"


def _render(data, kind, old):
    if kind == "cdl_keywords":
        fields = ("id", "state", "topic", "english", "spanish", "priority", "status")
        previous = dict(zip(fields, [v.strip() for v in old.strip('| ').split('|')])) if old else {'priority': 'P1', 'status': 'active'}
        previous.update(data)
        if not all(str(previous.get(k, '')).strip() for k in fields):
            raise ValueError('Keyword requires state, topic, english, and spanish.')
        vals = [previous.get(k, "") for k in fields]
    else:
        vals = [data.get(k, "") for k in ("id", "title", "type", "status", "rule", "source")]
    if old and not any(vals[1:]):
        return old
    return "| " + " | ".join(str(v).replace("|", "/").replace("\n", " ") for v in vals) + " |"
