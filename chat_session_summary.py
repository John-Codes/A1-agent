from datetime import datetime
from threading import Thread
from time import sleep

import requests

from config import (
    AONE_MODEL_CONTEXT,
    CHAT_HISTORY_API_URL,
    CHAT_HISTORY_API_TOKEN,
    CHAT_SUMMARY_DELAY,
    CHAT_HISTORY_TIMEOUT,
    LOG_PATH,
    OLLAMA_MODEL,
    OLLAMA_HOST,
    REQUEST_TIMEOUT,
)

RECENT_LIMIT = 12


def generate_and_save_chat_title_and_summary(session_id):
    if not session_id:
        return
    Thread(target=_generate_and_save, args=(session_id,), daemon=True).start()


def _generate_and_save(session_id):
    sleep(CHAT_SUMMARY_DELAY)
    try:
        messages = _messages(session_id)[-RECENT_LIMIT:]
        title, summary = _summarize(messages)
        result = _save_generated_title_and_summary(session_id, title, summary)
        _log(f"summary session={session_id} status_code={result.status_code}")
    except Exception as exc:
        _log(f"summary error_code={type(exc).__name__} body={exc}")


def _messages(session_id):
    response = requests.get(
        _url(f"/sessions/{session_id}/messages"),
        headers=_headers(),
        timeout=CHAT_HISTORY_TIMEOUT,
    )
    _require_ok(response)
    return response.json()


def _summarize(messages):
    transcript = "\n".join(_line(row) for row in messages)
    prompt = (
        "Name this chat and summarize what it is about. Return plain text only.\n"
        "Line 1: a short useful title, no label.\n"
        "Line 2: one sentence summary, no label.\n\n"
        f"Conversation:\n{transcript}"
    )
    response = requests.post(
        f"{OLLAMA_HOST.rstrip('/')}/api/chat",
        json={
            "model": OLLAMA_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"num_ctx": AONE_MODEL_CONTEXT},
        },
        timeout=REQUEST_TIMEOUT,
    )
    _require_ok(response)
    raw = response.json().get("message", {}).get("content", "").strip()
    lines = [" ".join(line.split()) for line in raw.splitlines() if line.strip()]
    title = lines[0] if lines else "Chat summary"
    summary = " ".join(lines[1:]) or title or "Conversation summary unavailable."
    return title[:80], summary[:500]


def _save_generated_title_and_summary(session_id, title, summary):
    return requests.post(
        _url(f"/sessions/{session_id}/generated-title-and-summary"),
        json={"title": title, "summary": summary},
        headers=_headers(),
        timeout=CHAT_HISTORY_TIMEOUT,
    )


def _line(row):
    role = "user" if row.get("mine") else "assistant"
    return f"{role}: {row.get('text', '')}"


def _require_ok(response):
    if response.status_code >= 400:
        raise RuntimeError(f"status_code={response.status_code} body={response.text[:500]}")


def _url(path):
    return CHAT_HISTORY_API_URL.rstrip("/") + path


def _headers():
    return {"X-Tool-Token": CHAT_HISTORY_API_TOKEN} if CHAT_HISTORY_API_TOKEN else {}


def _log(message):
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(f"{stamp} | CHAT_SUMMARY | {message}\n")
