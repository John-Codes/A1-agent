import requests

from config import EMBEDDING_TIMEOUT
from embedding_errors import embedding_error, embedding_ok
from embedding_runtime import default_embedding_route, remember_embedding_route
from store import store


def embed_text_with_diagnostics(text):
    route = default_embedding_route()
    store["last_embedding_error"] = None
    store["last_embedding_attempts"] = []
    result = _try_default_embedding(text, route)
    store["last_embedding_attempts"] = [result]
    if result["ok"]:
        remember_embedding_route(store, result)
        return result["vector"]
    store["last_embedding_error"] = result
    raise RuntimeError(_format_error(result))


def _try_default_embedding(text, route):
    try:
        vector = _call_ollama_embed(text, route)
        result = embedding_ok(route["provider"], route["model"], route["api_base"], vector)
        result["vector"] = vector
        return result
    except Exception as exc:
        return embedding_error(route["provider"], route["model"], route["api_base"], exc)


def _call_ollama_embed(text, route):
    if route["provider"] != "ollama":
        raise ValueError("Only Ollama embeddings are enabled by default.")
    payload = {"model": route["model"], "input": text}
    url = f"{route['api_base'].rstrip('/')}/api/embed"
    response = requests.post(url, json=payload, timeout=EMBEDDING_TIMEOUT)
    response.raise_for_status()
    return _first_embedding(response.json())


def _first_embedding(data):
    vectors = data.get("embeddings") or data.get("embedding")
    if not vectors:
        raise ValueError("Embedding provider returned no embedding.")
    if isinstance(vectors[0], list):
        return vectors[0]
    return vectors


def _format_error(result):
    error = result.get("error") or {}
    return (
        "Embedding failed\n"
        f"provider: {result.get('provider')}\n"
        f"model: {result.get('model')}\n"
        f"error_type: {error.get('type')}\n"
        f"error: {error.get('message')}"
    )
