def error_result(provider, model, api_base, exc):
    error = {"type": exc.__class__.__name__, "message": str(exc)}
    return _result(False, "", provider, model, api_base, error)


def ok_result(provider, model, api_base, text):
    return _result(True, text, provider, model, api_base, None)


def format_attempts(attempts):
    if not attempts:
        return "No LLM attempts recorded."
    lines = ["LLM failed"]
    for attempt in attempts:
        label = attempt.get("label", "attempt")
        lines.append("")
        lines.append(f"{label} attempt:")
        lines.append(f"provider: {attempt.get('provider', '')}")
        lines.append(f"model: {attempt.get('model', '')}")
        if attempt.get("api_base"):
            lines.append(f"api_base: {attempt['api_base']}")
        if attempt.get("ok"):
            lines.append("status: ok")
        else:
            error = attempt.get("error") or {}
            lines.append(f"error_type: {error.get('type', 'unknown')}")
            lines.append(f"error: {error.get('message', 'unknown error')}")
    return "\n".join(lines)


def _result(ok, text, provider, model, api_base, error):
    return {
        "ok": ok,
        "text": text,
        "provider": provider,
        "model": model,
        "api_base": api_base,
        "error": error,
    }
