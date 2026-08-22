import json

from config import BROWSER_USE_HEADLESS, BROWSER_USE_MAX_STEPS


def parse_browser_request(body):
    text = body.strip()
    if not text:
        raise ValueError("No browser task provided.")
    if not text.startswith("{"):
        return _defaults(text)

    data = json.loads(text)
    task = str(data.get("task", "")).strip()
    if not task:
        raise ValueError("browser_use JSON requires a task.")

    request = _defaults(task)
    request["headless"] = _bool(data.get("headless"), BROWSER_USE_HEADLESS)
    request["max_steps"] = _positive_int(data.get("max_steps"), BROWSER_USE_MAX_STEPS)
    request["allowed_domains"] = _string_list(data.get("allowed_domains"))
    return request


def _defaults(task):
    return {
        "task": task,
        "headless": BROWSER_USE_HEADLESS,
        "max_steps": BROWSER_USE_MAX_STEPS,
        "allowed_domains": None,
    }


def _bool(value, default):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).lower() in {"1", "true", "yes", "on"}


def _positive_int(value, default):
    if value is None:
        return default
    number = int(value)
    if number < 1:
        raise ValueError("max_steps must be positive.")
    return number


def _string_list(value):
    if value is None:
        return None
    if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
        raise ValueError("allowed_domains must be a list of strings.")
    return value
