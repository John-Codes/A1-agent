import requests

from config import OLLAMA_HOST, REQUEST_TIMEOUT


def summarize(prompt, model):
    response = requests.post(
        f"{OLLAMA_HOST.rstrip('/')}/api/chat",
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt + "\n/no_think"}],
            "stream": False,
            "think": False,
            "options": {"num_ctx": 8192, "num_predict": 256},
        },
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    text = response.json().get("message", {}).get("content", "")
    text = text.rsplit("</think>", 1)[-1].strip()
    if not text:
        raise ValueError("Local summary model returned no text.")
    return text
