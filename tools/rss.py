import xml.etree.ElementTree as ET

import requests

from config import BING_NEWS_URL, BING_SEARCH_URL, WEB_SEARCH_TIMEOUT
from tools.format import format_results, search_item


def bing_news(query):
    return _bing_rss("bing_news_rss", BING_NEWS_URL, query)


def bing_web(query):
    return _bing_rss("bing_web_rss", BING_SEARCH_URL, query)


def _bing_rss(name, url, query):
    response = requests.get(
        url,
        params={"q": query, "format": "rss"},
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=WEB_SEARCH_TIMEOUT,
    )
    response.raise_for_status()
    root = ET.fromstring(response.text)
    results = []
    for item in root.findall(".//item")[:5]:
        results.append(search_item(
            item.findtext("title", ""),
            item.findtext("description", ""),
            item.findtext("link", ""),
            item.findtext("pubDate", ""),
        ))
    return format_results(name, query, results)
