from xml.etree import ElementTree as ET

from llm_env import add_fallback_route, remove_fallback_route, save_llm_default, save_provider_key, set_fallback_route
from llm_runtime import status_text
from store import store


def run_llm_route_config(body):
    data = _parse_xml(body)
    action = data.get("action", "status")
    if action == "status":
        return status_text(store)
    if action == "set_default":
        return save_llm_default(data["provider"], data["model"], data.get("api_base", ""))
    if action == "add_fallback":
        return add_fallback_route(data["provider"], data["model"], data.get("api_base", ""))
    if action == "set_fallback":
        return set_fallback_route(int(data["index"]), data["provider"], data["model"], data.get("api_base", ""))
    if action == "remove_fallback":
        return remove_fallback_route(int(data["index"]))
    if action == "set_key":
        return save_provider_key(data["provider"], data["api_key"])
    raise ValueError(f"Unknown llm_route_config action: {action}")


def _parse_xml(body):
    root = ET.fromstring(f"<root>{body}</root>")
    data = {}
    for child in root:
        data[child.tag.strip()] = (child.text or "").strip()
    return data
