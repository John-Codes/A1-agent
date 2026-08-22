from config import (
    DEFAULT_EMBEDDING_API_BASE,
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_EMBEDDING_PROVIDER,
    FALLBACK_EMBEDDING_API_BASE,
    FALLBACK_EMBEDDING_MODEL,
    FALLBACK_EMBEDDING_PROVIDER,
)


def default_embedding_route():
    return _route(
        DEFAULT_EMBEDDING_PROVIDER,
        DEFAULT_EMBEDDING_MODEL,
        DEFAULT_EMBEDDING_API_BASE,
    )


def fallback_embedding_route():
    return _route(
        FALLBACK_EMBEDDING_PROVIDER,
        FALLBACK_EMBEDDING_MODEL,
        FALLBACK_EMBEDDING_API_BASE,
    )


def remember_embedding_route(shared, result):
    shared["active_embedding_provider"] = result.get("provider")
    shared["active_embedding_model"] = result.get("model")
    shared["active_embedding_api_base"] = result.get("api_base")


def embedding_status_text(shared):
    active = shared.get("active_embedding_provider") or DEFAULT_EMBEDDING_PROVIDER
    model = shared.get("active_embedding_model") or DEFAULT_EMBEDDING_MODEL
    api_base = shared.get("active_embedding_api_base") or DEFAULT_EMBEDDING_API_BASE
    fallback = fallback_embedding_route()
    lines = [
        f"default_embedding: {DEFAULT_EMBEDDING_PROVIDER}/{DEFAULT_EMBEDDING_MODEL}",
        f"fallback_embedding: {fallback['provider']}/{fallback['model'] or '(not set)'}",
        f"fallback_auto_use: {shared.get('embedding_fallback_allowed', False)}",
        f"active_embedding_provider: {active}",
        f"active_embedding_model: {model}",
    ]
    if api_base:
        lines.append(f"active_embedding_api_base: {api_base}")
    return "\n".join(lines)


def _route(provider, model, api_base):
    return {"provider": provider, "model": model, "api_base": api_base}
