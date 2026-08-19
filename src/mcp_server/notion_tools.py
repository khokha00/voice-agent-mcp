# src/mcp_server/notion_tools.py
"""Raw Notion API calls. No MCP protocol code here — kept separately testable."""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_API_KEY = os.environ["NOTION_API_KEY"]
PARENT_PAGE_ID = os.environ["NOTION_PARENT_PAGE_ID"]
NOTION_VERSION = "2022-06-28"
BASE_URL = "https://api.notion.com/v1"

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json",
}


def search_pages(query: str, max_results: int = 5) -> list[dict]:
    """Search all pages/databases shared with the integration."""
    resp = requests.post(
        f"{BASE_URL}/search",
        headers=HEADERS,
        json={"query": query, "page_size": max_results},
        timeout=30,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])

    out = []
    for r in results:
        title = _extract_title(r)
        out.append({"id": r["id"], "title": title, "url": r.get("url", "")})
    return out


def get_page_content(page_id: str) -> str:
    """Fetch a page's block children and flatten to plain text."""
    resp = requests.get(
        f"{BASE_URL}/blocks/{page_id}/children",
        headers=HEADERS,
        timeout=30,
    )
    resp.raise_for_status()
    blocks = resp.json().get("results", [])

    lines = []
    for block in blocks:
        block_type = block.get("type")
        text_obj = block.get(block_type, {})
        rich_text = text_obj.get("rich_text", [])
        text = "".join(t.get("plain_text", "") for t in rich_text)
        if text:
            lines.append(text)
    return "\n".join(lines)


def create_page(title: str, content: str) -> dict:
    """Create a new page under the configured parent page."""
    resp = requests.post(
        f"{BASE_URL}/pages",
        headers=HEADERS,
        json={
            "parent": {"page_id": PARENT_PAGE_ID},
            "properties": {
                "title": {"title": [{"text": {"content": title}}]}
            },
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"text": {"content": content}}]},
                }
            ],
        },
        timeout=30,
    )
    if not resp.ok:
       print("Notion error:", resp.text)
    resp.raise_for_status()
    data = resp.json()
    return {"id": data["id"], "url": data.get("url", "")}


def _extract_title(page_obj: dict) -> str:
    """Notion buries the title in different places depending on object type."""
    props = page_obj.get("properties", {})
    for prop in props.values():
        if prop.get("type") == "title":
            title_parts = prop.get("title", [])
            return "".join(t.get("plain_text", "") for t in title_parts)
    return page_obj.get("id", "untitled")

def get_page(page_id: str) -> dict:
    """Retrieve a Notion page by ID."""
    resp = requests.get(
        f"{BASE_URL}/pages/{page_id}",
        headers=HEADERS,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()