from config import ROOT_DIR
from llm_route_rows import format_route_row, load_fallback_rows

KEY_NAMES = {
    "groq": "GROQ_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "nvidia_nim": "NVIDIA_API_KEY",
}


def save_llm_default(provider, model, api_base=""):
    return _rewrite({"LLM_DEFAULT": format_route_row(provider, model, api_base)})


def save_llm_fallback(provider, model, api_base=""):
    return set_fallback_route(1, provider, model, api_base)


def add_fallback_route(provider, model, api_base=""):
    rows = load_fallback_rows() + [format_route_row(provider, model, api_base)]
    return _rewrite_repeated("LLM_FALLBACKS", rows)


def set_fallback_route(index, provider, model, api_base=""):
    rows = load_fallback_rows()
    while len(rows) < index:
        rows.append("||")
    rows[index - 1] = format_route_row(provider, model, api_base)
    return _rewrite_repeated("LLM_FALLBACKS", rows)


def remove_fallback_route(index):
    rows = load_fallback_rows()
    if index < 1 or index > len(rows):
        raise ValueError("Fallback index is out of range.")
    del rows[index - 1]
    return _rewrite_repeated("LLM_FALLBACKS", rows)


def save_provider_key(provider, api_key):
    key_name = KEY_NAMES.get(provider)
    if not key_name:
        raise ValueError(f"No key name configured for provider: {provider}")
    return _rewrite({key_name: api_key})


def _rewrite(updates):
    return _write_lines(_updated_lines(updates))


def _rewrite_repeated(key, values):
    lines = [line for line in _read_lines() if not line.startswith(f"{key}=")]
    lines.extend(f"{key}={value}" for value in values if value and value != "||")
    return _write_lines(lines)


def _updated_lines(updates):
    seen = set()
    output = []
    for line in _read_lines():
        key = line.split("=", 1)[0] if "=" in line else ""
        if key in updates:
            output.append(f"{key}={updates[key]}")
            seen.add(key)
        else:
            output.append(line)
    output.extend(f"{key}={value}" for key, value in updates.items() if key not in seen)
    return output


def _read_lines():
    path = ROOT_DIR / ".env"
    return path.read_text(encoding="utf-8").splitlines() if path.exists() else []


def _write_lines(lines):
    (ROOT_DIR / ".env").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return "Saved to .env."
