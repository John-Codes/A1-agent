import json

from tools.agentmail.client import AgentMailClient

INBOX_FIELDS = {"username", "domain", "display_name", "client_id"}
SEND_FIELDS = {"to", "cc", "bcc", "reply_to", "subject", "text", "html", "labels", "attachments", "headers"}
REPLY_FIELDS = SEND_FIELDS | {"reply_all"}
UPDATE_FIELDS = {"add_labels", "remove_labels"}
LIST_FIELDS = {"limit", "page_token", "labels", "before", "after", "ascending"}


def run_agentmail(body):
    data = _load(body)
    action = data.pop("action", "").strip()
    client = AgentMailClient()
    if action == "create_inbox":
        result = client.create_inbox(_pick(data, INBOX_FIELDS))
    elif action == "list_inboxes":
        result = client.list_inboxes(_pick(data, {"limit", "page_token", "ascending"}))
    elif action == "get_inbox":
        result = client.get_inbox(_required(data, "inbox_id"))
    elif action == "send":
        result = client.send(_required(data, "inbox_id"), _pick(data, SEND_FIELDS))
    elif action == "list_messages":
        result = client.list_messages(_required(data, "inbox_id"), _pick(data, LIST_FIELDS))
    elif action == "get_message":
        result = client.get_message(_required(data, "inbox_id"), _required(data, "message_id"))
    elif action == "reply":
        result = client.reply(
            _required(data, "inbox_id"),
            _required(data, "message_id"),
            _pick(data, REPLY_FIELDS),
        )
    elif action == "update_message":
        result = client.update_message(
            _required(data, "inbox_id"),
            _required(data, "message_id"),
            _pick(data, UPDATE_FIELDS),
        )
    else:
        raise ValueError("Unknown AgentMail action")
    return json.dumps(result, indent=2, sort_keys=True)


def _load(body):
    try:
        data = json.loads(body)
    except json.JSONDecodeError as exc:
        raise ValueError(f"AgentMail body must be JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("AgentMail body must be a JSON object")
    return data


def _pick(data, fields):
    return {key: value for key, value in data.items() if key in fields and value is not None}


def _required(data, key):
    value = data.get(key)
    if not value:
        raise ValueError(f"Missing required field: {key}")
    return value
