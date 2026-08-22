import json


def parse_json(body):
    try:
        data = json.loads(body or "{}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("JSON body must be an object.")
    return data


def require_text(data, key):
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Missing required text field: {key}")
    return value.strip()


def optional_text(data, key):
    value = data.get(key, "")
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError(f"Field must be text: {key}")
    return value.strip()


def optional_tags(data):
    tags = data.get("tags", [])
    if tags in ("", None):
        return []
    if isinstance(tags, str):
        return [tags.strip()] if tags.strip() else []
    if isinstance(tags, list) and all(isinstance(x, str) for x in tags):
        return [x.strip() for x in tags if x.strip()]
    raise ValueError("Field must be a text list: tags")
