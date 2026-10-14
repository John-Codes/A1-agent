import os

from config import BROWSER_USE_OLLAMA_MODEL, LLM_GENERATION_TIMEOUT, OLLAMA_HOST
from llm_routes import default_route


def browser_model():
    provider = os.environ.get("BROWSER_USE_PROVIDER", "ollama")
    if provider == "ollama":
        from tools.browser_use_tool.local_model import BrowserChatOllama
        return BrowserChatOllama(
            model=BROWSER_USE_OLLAMA_MODEL, host=OLLAMA_HOST, timeout=LLM_GENERATION_TIMEOUT,
            ollama_options={"num_ctx": 16384, "num_predict": 1024},
        )
    if provider == "openrouter":
        from browser_use.llm.openrouter.chat import ChatOpenRouter
        route = default_route()
        model = os.environ.get("BROWSER_USE_MODEL") or (route["model"] if route["provider"] == provider else "")
        key = os.environ.get("OPENROUTER_API_KEY")
        if not model or not key:
            raise ValueError("Browser OpenRouter model and API key must be configured.")
        return ChatOpenRouter(model=model, api_key=key, timeout=LLM_GENERATION_TIMEOUT, max_retries=1,
                              extra_body={"max_tokens": 2048, "extra_body": {"reasoning": {"enabled": False}}})
    raise ValueError(f"Unsupported browser provider: {provider}")
