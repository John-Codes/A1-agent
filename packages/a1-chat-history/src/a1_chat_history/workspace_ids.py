import re

from .settings import DEFAULT_WORKSPACE_ID

WORKSPACE_ID_PATTERN = r"^[A-Za-z0-9_.-]{1,64}$"
WORKSPACE_ID_RULES = "Use letters, numbers, dash, underscore, or dot. Max 64 chars."


def default_workspace_id():
    return clean_workspace_id(DEFAULT_WORKSPACE_ID)


def clean_workspace_id(value):
    text = (value or DEFAULT_WORKSPACE_ID).strip() or DEFAULT_WORKSPACE_ID
    if not re.fullmatch(WORKSPACE_ID_PATTERN, text):
        raise ValueError(f"Invalid workspace_id. {WORKSPACE_ID_RULES}")
    return text
