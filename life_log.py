from datetime import datetime
from html import escape
import os

from config import LIFE_LOG_PATH
from local_summary import summarize
from tools.log import log_exception


def run_life_log(body):
    raw = _entry_text(body)
    if not raw:
        raise ValueError("Life log entry is empty.")
    created_at = datetime.now().astimezone().isoformat(timespec="seconds")
    summary = _summarize(raw)
    _append_entry(created_at, raw, summary)
    return f"Life log saved at {created_at}."


def _entry_text(body):
    text = (body or "").strip()
    if not text:
        return ""
    start, end = text.find("<entry>"), text.find("</entry>")
    if start >= 0 and end > start:
        return text[start + len("<entry>"):end].strip()
    return text


def _summarize(raw):
    prompt = (
        "Summarize this private life-log entry in one short sentence. "
        "Preserve the main lesson or pattern. Return plain text only.\n\n"
        f"Entry:\n{raw}"
    )
    try:
        summary = summarize(prompt, os.environ.get("LIFE_LOG_OLLAMA_MODEL", "qwen3:4b"))
    except Exception as exc:
        log_exception("life_log.summary", exc)
        summary = raw[:240].strip()
    return " ".join(summary.split()) or raw[:240].strip()


def _append_entry(created_at, raw, summary):
    LIFE_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    existing = _existing_log()
    entry = _entry_xml(created_at, raw, summary)
    LIFE_LOG_PATH.write_text(
        f"{existing.rstrip()}\n{entry}\n</life_log>\n",
        encoding="utf-8",
    )


def _existing_log():
    if not LIFE_LOG_PATH.exists():
        return "<life_log>"
    text = LIFE_LOG_PATH.read_text(encoding="utf-8").strip()
    if not text:
        return "<life_log>"
    if text.endswith("</life_log>"):
        return text[: -len("</life_log>")].rstrip()
    return f"<life_log>\n{text}"


def _entry_xml(created_at, raw, summary):
    return (
        "<entry>\n"
        f"  <created_at>{escape(created_at)}</created_at>\n"
        f"  <raw>{escape(raw)}</raw>\n"
        f"  <summary>{escape(summary)}</summary>\n"
        "</entry>"
    )
