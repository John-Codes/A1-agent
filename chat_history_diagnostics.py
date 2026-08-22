from xml.etree import ElementTree as ET

from config import CHAT_HISTORY_API_URL, CHAT_HISTORY_WORKSPACE_ID
from chat_history_auto_save import save_chat_turn_to_history
from tools.chat_history.client import ChatHistoryClient


def chat_history_diagnostics():
    client = ChatHistoryClient()
    health = _require_ok(client.get("/health"), "health")
    catalog = _require_ok(client.get("/tools/chat_history_api"), "catalog")
    shared = {"active_llm_model": "diagnostic"}
    session_id = save_chat_turn_to_history(
        shared,
        "diagnostic user message",
        "diagnostic assistant message",
    )
    if not session_id:
        raise RuntimeError("auto-save returned no session_id")
    messages = _require_ok(client.get(f"/sessions/{session_id}/messages"), "messages")
    summary = {
        "api_url": CHAT_HISTORY_API_URL,
        "workspace_id": CHAT_HISTORY_WORKSPACE_ID,
        "health": health,
        "tool_name": catalog.get("name"),
        "tool_actions": catalog.get("actions", []),
        "session_id": session_id,
        "shared_session_id": shared.get("chat_history_session_id"),
        "message_count": len(messages),
        "messages": [_message_summary(row) for row in messages[-2:]],
    }
    _cleanup_session(client, session_id)
    return summary


def _require_ok(response, label):
    if not response.get("ok"):
        raise RuntimeError(f"{label} failed: {response}")
    return response.get("body")


def _message_summary(row):
    return {
        "id": row.get("id", ""),
        "workspace_id": row.get("workspace_id", ""),
        "mine": row.get("mine"),
        "text": row.get("text", "")[:120],
    }


def _cleanup_session(client, session_id):
    body = f"<action>delete_session</action><session_id>{session_id}</session_id>"
    response = client.post("/tools/chat_history_api", {"body": body})
    result = _require_ok(response, "cleanup")
    root = ET.fromstring(result)
    if (root.findtext(".//ok") or "").strip() != "true":
        raise RuntimeError(f"cleanup XML failed: {result}")
