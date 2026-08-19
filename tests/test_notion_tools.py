"""Standalone tests for Notion tools — no LangGraph, no LLM, just the raw API calls."""

from src.mcp_server.notion_tools import (
    PARENT_PAGE_ID,
    create_page,
    get_page,
    get_page_content,
    search_pages,
)


if __name__ == "__main__":
    # ---------------------------------------------------------
    # 1. Create a test page
    # ---------------------------------------------------------
    print("1. Creating a test page...")

    created = create_page(
        title="MCP Server Test Note",
        content=(
            "This page was created automatically to verify "
            "the custom MCP server works."
        ),
    )

    print(f"   Created: {created['url']}")

    assert created["id"], "FAIL: create_page() did not return a page ID"
    assert created["url"], "FAIL: create_page() did not return a page URL"

    # ---------------------------------------------------------
    # 2. Retrieve the created page by ID
    # ---------------------------------------------------------
    print("\n2. Retrieving the created page...")

    page = get_page(created["id"])

    print(f"   Retrieved: {page['id']}")

    assert page["id"] == created["id"], (
        "FAIL: retrieved page ID does not match created page ID"
    )

    print("   Page retrieved successfully.")

    # ---------------------------------------------------------
    # 3. Search for an existing page
    # ---------------------------------------------------------
    print("\n3. Searching for the parent page...")

    results = search_pages("Research Notes")

    for r in results:
        print(f"   - {r['title']} ({r['id']})")

    assert any(
        r["id"] == PARENT_PAGE_ID
        for r in results
    ), "FAIL: parent page not found in search"

    print("   Search works successfully.")

    # ---------------------------------------------------------
    # 4. Read the created page content
    # ---------------------------------------------------------
    print("\n4. Reading the created page content...")

    content = get_page_content(created["id"])

    print(f"   Content: {content!r}")

    assert "verify" in content.lower(), (
        "FAIL: created page content does not contain expected text"
    )

    print("   Content read successfully.")

    # ---------------------------------------------------------
    # Final result
    # ---------------------------------------------------------
    print("\n✅ All Notion tool checks passed.")