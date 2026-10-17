from config import (
    DEFAULT_LLM_API_BASE,
    DEFAULT_LLM_MODEL,
    DEFAULT_LLM_PROVIDER,
    LITELLM_ENABLED,
)
from llm_routes import default_route, fallback_routes, route, route_key


def all_routes():
    return _dedupe([default_route()] + fallback_routes())


def skipped_fallback_routes(shared):
    """Return fallbacks filtered out by heartbeat model reservation."""
    from heartbeat.settings import MODEL, PROVIDER
    reserved_set = {(PROVIDER, MODEL)}
    return [r for r in fallback_routes() if (r["provider"], r["model"]) in reserved_set]


def active_routes(shared):
    active = _active_route(shared)
    from heartbeat.settings import MODEL, PROVIDER
    reserved = lambda item: (item["provider"], item["model"]) == (PROVIDER, MODEL)
    if active and active.get("label") == "heartbeat" and shared.get("active_llm_strict"):
        return [active]
    primary = active or default_route()
    if reserved(primary):
        raise ValueError("This model is reserved for heartbeat; select a different main model.")
    if active and shared.get("active_llm_strict"):
        return [active]
    return _dedupe([primary] + [r for r in fallback_routes() if not reserved(r)])


def set_active(shared, provider, model, api_base="", override=True, strict=False, label=None):
    shared["active_llm_provider"] = provider
    shared["active_llm_model"] = model
    shared["active_llm_api_base"] = api_base
    shared["active_llm_label"] = label
    shared["active_llm_override"] = override
    shared["active_llm_strict"] = strict


def use_default(shared):
    route = default_route()
    set_active(shared, route["provider"], route["model"], route["api_base"], False)


def remember_active(shared, result):
    set_active(
        shared,
        result.get("provider"),
        result.get("model"),
        result.get("api_base"),
        False,
        False,
        result.get("label"),
    )


def status_text(shared):
    from heartbeat.settings import MODEL, PROVIDER
    has_active = bool(shared.get("active_llm_provider") and shared.get("active_llm_model"))
    provider = shared.get("active_llm_provider") if has_active else DEFAULT_LLM_PROVIDER
    model = shared.get("active_llm_model") if has_active else DEFAULT_LLM_MODEL
    api_base = shared.get("active_llm_api_base") if has_active else DEFAULT_LLM_API_BASE
    lines = [
        f"backend: {'litellm' if LITELLM_ENABLED else 'ollama-direct'}",
        f"default: {DEFAULT_LLM_PROVIDER}/{DEFAULT_LLM_MODEL}",
    ]
    lines.append(f"heartbeat (reserved, excluded from main fallbacks): {PROVIDER}/{MODEL}")
    skipped = skipped_fallback_routes(shared)
    if skipped:
        for r in skipped:
            lines.append(f"skipped (heartbeat reserved): {r['label']} {r['provider']}/{r['model']}")
    for item in fallback_routes():
        lines.append(f"{item['label']}: {item['provider']}/{item['model']}")
    lines.extend([f"active_provider: {provider}", f"active_model: {model}"])
    if api_base:
        lines.append(f"active_api_base: {api_base}")
    return "\n".join(lines)


def _active_route(shared):
    if not shared.get("active_llm_override"):
        return None
    provider = shared.get("active_llm_provider")
    model = shared.get("active_llm_model")
    if not provider or not model:
        return None
    label = shared.get("active_llm_label") or "active"
    return route(label, provider, model, shared.get("active_llm_api_base") or "")


def _dedupe(routes):
    seen = set()
    output = []
    for item in routes:
        key = route_key(item)
        if key not in seen:
            output.append(item)
            seen.add(key)
    return output
