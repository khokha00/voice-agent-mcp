# src/tools/search.py
"""DuckDuckGo web search tool, free and keyless."""
from ddgs import DDGS


def web_search(query: str, max_results: int = 5) -> list[dict]:
    """Returns a list of {title, url, snippet} dicts."""
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))

    return [
        {
            "title": r.get("title", ""),
            "url": r.get("href", ""),
            "snippet": r.get("body", ""),
        }
        for r in results
    ]