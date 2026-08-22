from config import DEFAULT_LLM_API_BASE, DEFAULT_LLM_MODEL, DEFAULT_LLM_PROVIDER, ROOT_DIR

DEFAULT_FALLBACKS = [
    "groq|qwen/qwen3.6-27b|",
    "openrouter|nvidia/nemotron-3-ultra-550b-a55b:free|",
    "nvidia_nim|deepseek-ai/deepseek-v4-pro|https://integrate.api.nvidia.com/v1",
]


def load_default_row():
    row = _last_value("LLM_DEFAULT")
    if row:
        return row
    return f"{DEFAULT_LLM_PROVIDER}|{DEFAULT_LLM_MODEL}|{DEFAULT_LLM_API_BASE}"


def load_fallback_rows():
    rows = _all_values("LLM_FALLBACKS")
    return rows or DEFAULT_FALLBACKS


def parse_route_row(row):
    parts = (row or "").split("|")
    parts = (parts + ["", "", ""])[:3]
    return {"provider": parts[0].strip(), "model": parts[1].strip(), "api_base": parts[2].strip()}


def format_route_row(provider, model, api_base=""):
    return f"{provider}|{model}|{api_base or ''}"


def _all_values(key):
    rows = []
    for line in _env_lines():
        if line.startswith(f"{key}="):
            rows.append(line.split("=", 1)[1].strip())
    return rows


def _last_value(key):
    values = _all_values(key)
    return values[-1] if values else ""


def _env_lines():
    path = ROOT_DIR / ".env"
    if not path.exists():
        path = ROOT_DIR / ".env.sample"
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8").splitlines()
