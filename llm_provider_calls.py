import requests
import json

from config import AONE_MODEL_CONTEXT, LLM_GENERATION_TIMEOUT, OLLAMA_HOST
from llm_http_providers import call_groq, call_nvidia_nim, call_openrouter


def call_provider(prompt, provider, model, api_base, image_data=""):
    if provider == "ollama":
        return call_ollama_direct(prompt, model, api_base, image_data)
    if image_data:
        raise ValueError(f"Images require an Ollama route, not {provider}.")
    if provider == "groq":
        return call_groq(prompt, model)
    if provider == "openrouter":
        return call_openrouter(prompt, model)
    if provider == "nvidia_nim":
        return call_nvidia_nim(prompt, model, api_base)
    return _call_litellm(prompt, provider, model, api_base)


def call_ollama_direct(prompt, model, api_base="", image_data=""):
    base = (api_base or OLLAMA_HOST).rstrip("/")
    message = {"role": "user", "content": prompt}
    if image_data:
        message["images"] = [image_data]
    thinking = model == "qwen3:4b"
    payload = {
        "model": model,
        "messages": [message],
        "stream": True,
        "think": thinking,
        "options": {
            "num_ctx": min(AONE_MODEL_CONTEXT, 4096),
            "num_predict": 2048,
        },
    }
    response = requests.post(
        f"{base}/api/chat",
        json=payload,
        timeout=LLM_GENERATION_TIMEOUT,
        stream=True,
    )
    response.raise_for_status()
    return _read_ollama_stream(response, thinking)


def _read_ollama_stream(response, thinking):
    thoughts, content = [], []
    for raw in response.iter_lines(decode_unicode=True):
        if not raw:
            continue
        item = json.loads(raw)
        message = item.get("message") or {}
        if message.get("thinking"):
            thoughts.append(message["thinking"])
        if message.get("content"):
            content.append(message["content"])
    text = "".join(content).strip()
    if thinking and thoughts:
        text = f"<think>{''.join(thoughts).strip()}</think>\n{text}"
    return text


def _call_litellm(prompt, provider, model, api_base):
    from litellm import completion

    kwargs = {
        "model": _litellm_model(provider, model),
        "messages": [{"role": "user", "content": prompt}],
        "timeout": LLM_GENERATION_TIMEOUT,
    }
    if api_base and provider in {"ollama", "openai_compatible"}:
        kwargs["api_base"] = api_base
    response = completion(**kwargs)
    return response.choices[0].message.content or ""


def _litellm_model(provider, model):
    model = model.strip()
    if model.startswith(f"{provider}/"):
        return model
    if provider == "ollama":
        return f"ollama/{model}"
    if provider == "openrouter":
        return f"openrouter/{model}"
    if provider == "openai_compatible":
        return model
    return model if "/" in model else f"{provider}/{model}"
