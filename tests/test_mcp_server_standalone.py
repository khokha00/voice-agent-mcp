"""Verify the MCP server starts and correctly lists its tools via the MCP
client protocol — not just that the underlying Notion functions work."""
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_PARAMS = StdioServerParameters(
    command="uv",
    args=["run", "python", "-m", "src.mcp_server.server"],
)


async def main():
    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Tools exposed by the server:")
            for t in tools.tools:
                print(f"  - {t.name}: {t.description}")

            expected = {"notion_search", "notion_read_page", "notion_create_page"}
            found = {t.name for t in tools.tools}
            assert expected.issubset(found), f"FAIL: missing tools {expected - found}"
            print("\n✅ MCP server exposes all expected tools.")


if __name__ == "__main__":
    asyncio.run(main())