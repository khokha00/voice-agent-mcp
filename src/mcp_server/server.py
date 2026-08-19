"""MCP server exposing Notion tools over the MCP protocol.
Run standalone: `uv run python -m src.mcp_server.server`
"""
from mcp.server import MCPServer
from src.mcp_server.notion_tools import search_pages, get_page_content, create_page

mcp = MCPServer("notion-research-tools")


@mcp.tool()
def notion_search(query: str, max_results: int = 5) -> list[dict]:
    """Search Notion pages shared with this integration. Returns a list of
    {id, title, url} for each matching page."""
    return search_pages(query, max_results=max_results)


@mcp.tool()
def notion_read_page(page_id: str) -> str:
    """Fetch the plain-text content of a Notion page by its ID."""
    return get_page_content(page_id)


@mcp.tool()
def notion_create_page(title: str, content: str) -> dict:
    """Create a new Notion page under the configured parent page.
    Returns {id, url} of the created page."""
    return create_page(title=title, content=content)


if __name__ == "__main__":
    mcp.run()