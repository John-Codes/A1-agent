from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

from config import CHAT_HISTORY_SESSION_TITLE, CHAT_HISTORY_WORKSPACE_ID, OLLAMA_MODEL
from tools.chat_history.client import ChatHistoryClient

CLIENT_ID = "A1"
USER_ID = "local"
AGENT_TYPE = "hermes"


def save_user_message_before_generation(shared, user_text):
    session_id = ensure_chat_history_session(shared)
    if not session_id:
        return None
    saved = save_chat_message_to_history(session_id, user_text, True)
    return session_id if saved else None


def save_assistant_message_after_generation(shared, assistant_text):
    session_id = ensure_chat_history_session(shared)
    if not session_id:
        return None
    saved = save_chat_message_to_history(session_id, assistant_text, False)
    return session_id if saved else None


def save_chat_turn_to_history(shared, user_text, assistant_text):
    session_id = save_user_message_before_generation(shared, user_text)
    if not session_id:
        return None
    saved = save_chat_message_to_history(session_id, assistant_text, False)
    return session_id if saved else None


def ensure_chat_history_session(shared):
    if shared.get("chat_history_session_id"):
        return shared["chat_history_session_id"]
    session_id = _create_chat_history_session(shared)
    if session_id:
        shared["chat_history_session_id"] = session_id
    return session_id


def save_chat_message_to_history(session_id, text, mine):
    result = _call_chat_history_xml(
        "<action>add_message</action>"
        f"<session_id>{_xml(session_id)}</session_id>"
        f"<text>{_xml(text or '')}</text>"
        f"<mine>{str(bool(mine)).lower()}</mine>"
    )
    return _xml_ok(result)


def _create_chat_history_session(shared):
    model_name = shared.get("active_llm_model") or OLLAMA_MODEL
    result = _call_chat_history_xml(
        "<action>create_session</action>"
        f"<workspace_id>{_xml(CHAT_HISTORY_WORKSPACE_ID)}</workspace_id>"
        f"<client_id>{CLIENT_ID}</client_id>"
        f"<user_id>{USER_ID}</user_id>"
        f"<agent_type>{AGENT_TYPE}</agent_type>"
        f"<model_name>{_xml(model_name)}</model_name>"
        f"<title>{_xml(CHAT_HISTORY_SESSION_TITLE)}</title>"
        "<summary></summary>"
    )
    if not _xml_ok(result):
        return None
    return _first_xml_text(result, "id")


def _call_chat_history_xml(body):
    try:
        response = ChatHistoryClient().post("/tools/chat_history_api", {"body": body})
    except Exception:
        return ""
    return str(response.get("body") or "") if response.get("ok") else ""


def _xml_ok(text):
    return _first_xml_text(text, "ok") == "true"


def _first_xml_text(text, tag):
    try:
        root = ET.fromstring(text or "")
    except ET.ParseError:
        return ""
    node = root.find(f".//{tag}")
    return (node.text or "").strip() if node is not None else ""


def _xml(value):
    return escape(str(value))
