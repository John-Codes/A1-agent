def embedding_ok(provider, model, api_base, vector):
    return _result(True, provider, model, api_base, len(vector), None)


def embedding_error(provider, model, api_base, exc):
    error = {"type": exc.__class__.__name__, "message": str(exc)}
    return _result(False, provider, model, api_base, None, error)


def format_embedding_attempts(attempts):
    if not attempts:
        return "No embedding attempts recorded."
    lines = ["Embedding status"]
    for attempt in attempts:
        lines.append("")
        lines.append(f"provider: {attempt.get('provider', '')}")
        lines.append(f"model: {attempt.get('model', '')}")
        if attempt.get("api_base"):
            lines.append(f"api_base: {attempt['api_base']}")
        if attempt.get("ok"):
            lines.append(f"dimension: {attempt.get('dimension')}")
            lines.append("status: ok")
        else:
            error = attempt.get("error") or {}
            lines.append(f"error_type: {error.get('type', 'unknown')}")
            lines.append(f"error: {error.get('message', 'unknown error')}")
    return "\n".join(lines)


def _result(ok, provider, model, api_base, dimension, error):
    return {
        "ok": ok,
        "provider": provider,
        "model": model,
        "api_base": api_base,
        "dimension": dimension,
        "error": error,
    }
