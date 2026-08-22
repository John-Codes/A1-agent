import os

import requests

from config import DEFAULT_LLM_API_BASE, LLM_HEALTHCHECK_TIMEOUT


def list_models(provider):
    provider = (provider or "").lower()
    if provider == "ollama":
        return _list_ollama()
    if provider == "openrouter":
        return _list_openrouter()
    return f"Unknown LLM provider: {provider}"


def _list_ollama():
    url = f"{DEFAULT_LLM_API_BASE.rstrip('/')}/api/tags"
    data = _get_json(url)
    names = [item.get("name", "") for item in data.get("models", [])]
    return "\n".join(name for name in names if name) or "No Ollama models found."


def _list_openrouter():
    headers = {}
    if os.environ.get("OPENROUTER_API_KEY"):
        headers["Authorization"] = f"Bearer {os.environ['OPENROUTER_API_KEY']}"
    data = _get_json("https://openrouter.ai/api/v1/models", headers)
    ids = [item.get("id", "") for item in data.get("data", [])]
    free = [model for model in ids if model.endswith(":free")]
    return "\n".join((free or ids)[:40]) or "No OpenRouter models found."


def _get_json(url, headers=None):
    response = requests.get(url, headers=headers or {}, timeout=LLM_HEALTHCHECK_TIMEOUT)
    response.raise_for_status()
    return response.json()
