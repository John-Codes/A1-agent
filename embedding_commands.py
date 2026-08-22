from embedding_client import embed_text_with_diagnostics
from embedding_errors import format_embedding_attempts
from embedding_runtime import embedding_status_text
from store import store


def run_embedding_command(body):
    parts = (body or "status").split()
    action = parts[0].lower() if parts else "status"
    if action == "status":
        return embedding_status_text(store)
    if action == "errors":
        return format_embedding_attempts(store.get("last_embedding_attempts", []))
    if action == "health":
        return _health()
    if action in {"fallback", "use-fallback"}:
        return _fallback_warning()
    return _help()


def _health():
    try:
        vector = embed_text_with_diagnostics("embedding health check")
        return f"{embedding_status_text(store)}\nhealth: ok\ndimension: {len(vector)}"
    except Exception as exc:
        return f"ERROR | Embedding health failed\n{exc}"


def _fallback_warning():
    return (
        "Embedding fallback is intentionally manual-disabled.\n"
        "Reason: different embedding dimensions can break LanceDB tables."
    )


def _help():
    return "\n".join([
        "/embedding status",
        "/embedding errors",
        "/embedding health",
        "/embedding use-fallback",
    ])
