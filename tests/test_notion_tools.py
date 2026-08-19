"""Standalone tests for Notion tools — no LangGraph, no LLM, just the raw API calls."""
from src.mcp_server.notion_tools import search_pages, create_page, get_page_content

if __name__ == "__main__":
    print("1. Creating a test page...")
    created = create_page(
        title="MCP Server Test Note",
        content="This page was created automatically to verify the custom MCP server works.",
    )
    print(f"   Created: {created['url']}")

    print("\n2. Searching for it...")
    results = search_pages("MCP Server Test Note")
    for r in results:
        print(f"   - {r['title']} ({r['id']})")
    assert any(r["id"] == created["id"] for r in results), "FAIL: created page not found in search"

    print("\n3. Reading its content back...")
    content = get_page_content(created["id"])
    print(f"   Content: {content!r}")
    assert "verify" in content, "FAIL: content mismatch"

    print("\n✅ All Notion tool checks passed.")