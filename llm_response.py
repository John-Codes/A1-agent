def response_text(response, provider):
    try:
        data = response.json()
    except ValueError as exc:
        raise ValueError(f"{provider} returned invalid JSON (HTTP {response.status_code}).") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{provider} returned an invalid response object.")
    if data.get("error"):
        error = data["error"]
        if isinstance(error, dict):
            detail = f"{error.get('code', 'unknown')}: {error.get('message', 'Unknown provider error')}"
        else:
            detail = str(error)
        raise RuntimeError(f"{provider} error (HTTP {response.status_code}): {detail[:1000]}")
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError(f"{provider} returned no completion choices/message content.") from exc
    if not isinstance(content, str) or not content.strip():
        raise ValueError(f"{provider} returned an empty text completion.")
    return content
