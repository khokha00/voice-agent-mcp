"""DuckDuckGo web search tool, free and keyless."""
import time
from ddgs import DDGS
from ddgs.exceptions import DuckDuckGoSearchException


def web_search(query: str, max_results: int = 5, retries: int = 2) -> list[dict]:
    """Returns a list of {title, url, snippet} dicts. Returns [] on repeated failure
    rather than raising — a single bad search should degrade gracefully, not crash
    the whole research step."""
    for attempt in range(retries + 1):
        try:
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
        except (DuckDuckGoSearchException, Exception) as e:
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))  # simple backoff
                continue
            print(f"  [search failed after {retries + 1} attempts: {query!r} — {e}]")
            return []