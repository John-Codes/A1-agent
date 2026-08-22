from llm_catalog import list_models
from llm_env import save_llm_default, save_llm_fallback
from llm_errors import format_attempts
from llm_routes import fallback_routes
from llm_runtime import set_active, status_text, use_default
from store import store


def run_llm_command(body):
    parts = (body or "status").split()
    action = parts[0].lower() if parts else "status"
    if action == "status":
        return status_text(store)
    if action == "errors":
        return format_attempts(store.get("last_llm_attempts", []))
    if action == "list":
        return _list(parts)
    if action == "health":
        return _health()
    if action == "use-default":
        use_default(store)
        return "Active override cleared. Default route will be tried first."
    if action == "use-fallback":
        route = _fallback(parts)
        set_active(
            store,
            route["provider"],
            route["model"],
            route["api_base"],
            True,
            True,
            route["label"],
        )
        return f"Strict active route set to {route['label']}."
    if action == "use":
        return _use(parts)
    if action == "default":
        return _save(parts, save_llm_default, "default")
    if action == "fallback":
        return _save(parts, save_llm_fallback, "fallback")
    return _help()


def _list(parts):
    if len(parts) < 2:
        return "Usage: /llm list ollama|openrouter"
    try:
        return list_models(parts[1])
    except Exception as exc:
        store["last_llm_error"] = {"type": exc.__class__.__name__, "message": str(exc)}
        return f"ERROR | LLM model list failed\n{exc.__class__.__name__}: {exc}"


def _health():
    lines = [status_text(store)]
    attempts = store.get("last_llm_attempts") or []
    if attempts:
        lines.append("")
        lines.append(format_attempts(attempts))
    return "\n".join(lines)


def _use(parts):
    if len(parts) < 3:
        return "Usage: /llm use provider model [api_base]"
    api_base = parts[3] if len(parts) > 3 else ""
    set_active(store, parts[1].lower(), parts[2], api_base)
    return f"Active LLM set to {parts[1].lower()}/{parts[2]}"


def _fallback(parts):
    routes = fallback_routes()
    index = int(parts[1]) - 1 if len(parts) > 1 and parts[1].isdigit() else 0
    if index < 0 or index >= len(routes):
        raise ValueError("Fallback index is out of range.")
    return routes[index]


def _save(parts, saver, label):
    if len(parts) < 3:
        return f"Usage: /llm {label} provider model [api_base]"
    message = saver(parts[1].lower(), parts[2], parts[3] if len(parts) > 3 else "")
    return f"Saved {label} LLM as {parts[1].lower()}/{parts[2]}\n{message}"


def _help():
    return "\n".join([
        "/llm status",
        "/llm errors",
        "/llm health",
        "/llm list ollama",
        "/llm list openrouter",
        "/llm use-default",
        "/llm use-fallback [number]",
        "/llm use provider model [api_base]",
        "/llm default provider model [api_base]",
        "/llm fallback provider model [api_base]",
    ])
