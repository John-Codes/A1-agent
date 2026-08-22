import requests

from config import CHAT_HISTORY_API_TOKEN, CHAT_HISTORY_API_URL, CHAT_HISTORY_TIMEOUT

CLIENT_ID = "A1"
USER_ID = "local"
AGENT_TYPE = "hermes"


def recent(limit=20):
    session_id = _latest_session_id()
    if not session_id:
        return []
    try:
        res = requests.get(
            _url(f"/sessions/{session_id}/messages"),
            headers=_headers(),
            timeout=CHAT_HISTORY_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()[-int(limit):]
    except Exception:
        return []

def format_recent(limit=20):
    rows = recent(limit)
    if not rows:
        return "(history unavailable)"
    return "\n".join(_format(row) for row in rows)

def run_conversation_history(body=""):
    text = (body or "").strip()
    limit = _limit(text)
    return format_recent(limit)


def _latest_session_id():
    params = {"client_id": CLIENT_ID, "user_id": USER_ID, "agent_type": AGENT_TYPE}
    try:
        res = requests.get(_url("/sessions"), params=params, headers=_headers(), timeout=CHAT_HISTORY_TIMEOUT)
        res.raise_for_status()
        sessions = res.json()
        return sessions[0]["id"] if sessions else None
    except Exception:
        return None


def _format(row):
    role = "user" if row.get("mine") else "assistant"
    return f"{role}: {row.get('text', '')}"


def _limit(text):
    for token in text.replace("=", " ").split():
        if token.isdigit():
            return max(1, min(int(token), 100))
    return 20


def _url(path):
    return CHAT_HISTORY_API_URL.rstrip("/") + path


def _headers():
    return {"X-Tool-Token": CHAT_HISTORY_API_TOKEN} if CHAT_HISTORY_API_TOKEN else {}
