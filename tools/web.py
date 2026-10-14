import re
import requests

from config import TAVILY_API_KEY, TAVILY_SEARCH_URL, WEB_SEARCH_TIMEOUT
from tools.format import format_results, search_item
from tools.log import log_tool_event
from tools.rss import bing_news, bing_web

NEWS_WORDS = ("news", "latest", "today", "recent", "breaking", "2026")


def run_web_search(query):
    query = re.sub(r"</?tool\b[^>]*>", "", query).strip()
    if not query:
        return "No search query provided."
    backends = [_tavily, bing_news, bing_web] if _looks_news(query) else [_tavily, bing_web]
    errors = []
    for backend in backends:
        result = _try_backend(backend, query)
        if result.startswith("Backend:"):
            return result
        errors.append(result)
    return "No useful web results found. Details: gateway.log"


def _try_backend(backend, query):
    log_tool_event("web_search.backend", "start", f"{backend.__name__} | {query}")
    try:
        result = backend(query)
        count = result.count("\nTitle:")
        log_tool_event("web_search.backend", "done", f"{backend.__name__} returned {count} results")
        return result if count else f"{backend.__name__}: no results"
    except Exception as exc:
        detail = f"{backend.__name__}: {exc}"
        log_tool_event("web_search.backend", "error", detail)
        return detail


def _tavily(query):
    if not TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY is not set")
    response = requests.post(
        TAVILY_SEARCH_URL,
        json=_tavily_payload(query),
        headers={"Authorization": f"Bearer {TAVILY_API_KEY}"},
        timeout=WEB_SEARCH_TIMEOUT,
    )
    response.raise_for_status()
    data = response.json()
    results = [
        search_item(item.get("title"), item.get("content"), item.get("url"))
        for item in data.get("results", [])
    ]
    return format_results("tavily_api", query, results, data.get("answer", ""))


def _tavily_payload(query):
    return {
        "query": query,
        "topic": "news" if _looks_news(query) else "general",
        "search_depth": "basic",
        "include_answer": "basic",
        "max_results": 5,
    }


def _looks_news(query):
    return any(word in query.lower() for word in NEWS_WORDS)
