import re
from html import unescape
from urllib.parse import parse_qs, unquote, urlparse


def search_item(title, snippet, url, date=""):
    return {
        "title": _clean(title),
        "snippet": _clean(snippet),
        "url": _clean_url(url),
        "date": _clean(date),
    }


def format_results(backend, query, results, answer=""):
    if not results:
        return f"Backend: {backend}\nQuery: {query}\nNo results."
    lines = [f"Backend: {backend}", f"Query: {query}"]
    if answer:
        lines += ["", f"Answer: {_clean(answer)}"]
    for result in results:
        lines += ["", f"Title: {result['title']}"]
        lines += [f"Snippet: {result['snippet']}", f"URL: {result['url']}"]
        if result["date"]:
            lines.append(f"Date: {result['date']}")
    return "\n".join(lines)


def _clean(text):
    return unescape(re.sub(r"<.*?>", "", text or "")).strip()


def _clean_url(url):
    parsed = urlparse(unescape(url or ""))
    target = parse_qs(parsed.query).get("url", [""])[0]
    return unquote(target) if target else unescape(url or "")
