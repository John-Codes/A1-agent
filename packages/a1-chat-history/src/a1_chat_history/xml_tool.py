"""The XML tool endpoint A1 agents call: POST /tools/chat_history_api {"body": "<action>..."}."""
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

from .models import MessageIn, SessionIn, UpdateChatSessionRequest
from .rows import session_summary
from .workspace_ids import clean_workspace_id

MENU = (
    "chat_history_api actions: menu | health | list_sessions | list_session_summaries | "
    "create_session | update_session | delete_session | list_messages | add_message | "
    "delete_message | clear_messages | set_feedback. "
    "Session tags: workspace_id, client_id, user_id, agent_type, agent_id, model_name, "
    "title, summary. Message tags: session_id, message_id, text, mine, feedback."
)

SESSION_FILTER_FIELDS = ("workspace_id", "client_id", "user_id", "agent_type", "agent_id")
CREATE_FIELDS = SESSION_FILTER_FIELDS + ("model_name", "title", "summary")
MESSAGE_FIELDS = ("text", "mine", "timestamp", "image_data", "has_image")


class MissingTag(ValueError):
    def __init__(self, key):
        super().__init__(f"Missing required tag: {key}")
        self.key = key


class UnknownAction(ValueError):
    pass


def run_chat_history_xml_action(store, body):
    data, parse_error = parse_xml_tool_body(body)
    if parse_error:
        return xml_result(parse_error)
    try:
        response = _run_action(store, data.get("action", "menu"), data)
    except MissingTag as exc:
        response = error_result("missing_required_tag", str(exc))
    except UnknownAction as exc:
        response = error_result("unknown_action", str(exc))
    except ValueError as exc:
        response = error_result("invalid_request", str(exc))
    return xml_result(response)


def _run_action(store, action, data):
    if action == "menu":
        return ok_result(MENU)
    if action == "health":
        return ok_result({"status": "ok"})
    if action == "list_sessions":
        return ok_result(store.sessions(**_filters(data)))
    if action == "list_session_summaries":
        return ok_result([session_summary(item) for item in store.sessions(**_filters(data))])
    if action == "create_session":
        return ok_result(store.create_session(SessionIn(**_pick(data, CREATE_FIELDS))))
    if action == "update_session":
        session = store.update_chat_session(
            _required(data, "session_id"),
            UpdateChatSessionRequest(**_pick(data, ("title", "summary"))),
        )
        return ok_result(session) if session else status_error(404, "session not found")
    if action == "delete_session":
        store.delete_session(_required(data, "session_id"))
        return ok_result({"status_code": 204})
    if action == "list_messages":
        return ok_result(store.messages(_required(data, "session_id"), data.get("workspace_id")))
    if action == "add_message":
        return ok_result(store.add_message(_required(data, "session_id"), _message_payload(data)))
    if action == "delete_message":
        store.delete_message(_required(data, "session_id"), _required(data, "message_id"))
        return ok_result({"status_code": 204})
    if action == "clear_messages":
        store.clear_messages(_required(data, "session_id"))
        return ok_result({"status_code": 204})
    if action == "set_feedback":
        message = store.set_feedback(
            _required(data, "session_id"),
            _required(data, "message_id"),
            _optional_none(data.get("feedback")),
        )
        return ok_result(message) if message else status_error(404, "message not found")
    raise UnknownAction(f"Unknown action: {action}")


def parse_xml_tool_body(body):
    try:
        root = ET.fromstring(f"<root>{body or ''}</root>")
    except ET.ParseError as exc:
        return None, error_result("invalid_xml", str(exc))
    data = {}
    for child in root:
        if list(child):
            return None, error_result("invalid_xml", f"Nested tag not allowed: {child.tag}")
        data[child.tag.strip()] = (child.text or "").strip()
    return data, None


def xml_result(response):
    return "<chat_history_result>\n" + _nodes(response) + "</chat_history_result>"


def ok_result(body):
    return {"ok": True, "body": body}


def error_result(code, message):
    return {"ok": False, "error_code": code, "body": message}


def status_error(status_code, message):
    return {"ok": False, "status_code": status_code, "body": message}


def _filters(data):
    picked = _pick(data, SESSION_FILTER_FIELDS)
    if "workspace_id" in picked:
        picked["workspace_id"] = clean_workspace_id(picked["workspace_id"])
    return picked


def _message_payload(data):
    payload = _pick(data, MESSAGE_FIELDS)
    payload["mine"] = str(payload.get("mine", "")).lower() in {"true", "1", "yes"}
    if "has_image" in payload:
        payload["has_image"] = str(payload["has_image"]).lower() in {"true", "1", "yes"}
    return MessageIn(**payload)


def _optional_none(value):
    return None if value in (None, "", "none", "null") else value


def _required(data, key):
    value = data.get(key, "")
    if value == "":
        raise MissingTag(key)
    return value


def _pick(data, fields):
    return {key: data[key] for key in fields if key in data}


def _nodes(data):
    if isinstance(data, dict):
        return "".join(_tag(key, value) for key, value in data.items())
    return _tag("body", data)


def _tag(key, value):
    if isinstance(value, dict):
        return f"  <{key}>\n{_nodes(value)}  </{key}>\n"
    if isinstance(value, list):
        inner = "".join(_tag("item", item) for item in value)
        return f"  <{key}>\n{inner}  </{key}>\n"
    text = "true" if value is True else "false" if value is False else value
    return f"  <{key}>{'' if text is None else escape(str(text))}</{key}>\n"
