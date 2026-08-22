from tools.life_idea_log.client import LifeIdeaLogClient
from tools.life_idea_log.menu import menu
from tools.life_idea_log.xml_body import parse_body
from tools.life_idea_log.xml_result import result


def run_life_idea_log(body):
    data, parse_error = parse_body(body)
    if parse_error:
        return result(parse_error)
    action = data.pop("action", "menu")
    client = LifeIdeaLogClient()
    try:
        response = _run_action(client, action, data)
        return result({"ok": True, "response": response})
    except Exception as exc:
        return result({"ok": False, "error_code": "tool_error", "message": str(exc)})


def _run_action(client, action, data):
    if action == "menu":
        return menu()
    if action == "health":
        return client.health()
    if action == "create":
        return client.create(_entry_payload(data))
    if action == "list":
        return client.list(_list_params(data))
    if action == "get":
        return client.get(_required(data, "entry_id"))
    if action == "update":
        return client.update(_required(data, "entry_id"), _update_payload(data))
    if action == "delete":
        return client.delete(_required(data, "entry_id"))
    raise ValueError(f"Unknown life_idea_log action: {action}")


def _entry_payload(data):
    return {
        "workspace_id": data.get("workspace_id", "default"),
        "entry_type": data.get("entry_type", "life"),
        "title": _required(data, "title"),
        "body": _required(data, "body"),
        "tags": _tags(data.get("tags", "")),
    }


def _update_payload(data):
    allowed = {"workspace_id", "entry_type", "title", "body"}
    payload = {key: data[key] for key in allowed if data.get(key)}
    if data.get("tags"):
        payload["tags"] = _tags(data["tags"])
    return payload


def _list_params(data):
    keys = ["workspace_id", "entry_type", "limit", "skip", "sort"]
    return {key: data[key] for key in keys if data.get(key)}


def _required(data, key):
    value = data.get(key, "").strip()
    if not value:
        raise ValueError(f"Missing required tag: {key}")
    return value


def _tags(raw):
    return [tag.strip() for tag in raw.split(",") if tag.strip()]
