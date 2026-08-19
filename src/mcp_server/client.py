"""Sync wrapper around the MCP client, so the rest of the codebase doesn't
need to deal with async sessions directly."""
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_PARAMS = StdioServerParameters(
    command="uv",
    args=["run", "python", "-m", "src.mcp_server.server"],
)


async def _call_tool_async(tool_name: str, arguments: dict):
    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            # MCP tool results come back as a list of content blocks; for our
            # tools (which return JSON-serializable Python values) there's one
            # text block containing the serialized result.
            if result.content and hasattr(result.content[0], "text"):
                return result.content[0].text
            return None


def call_mcp_tool(tool_name: str, arguments: dict):
    """Blocking call to an MCP tool. Spins up a fresh server subprocess per
    call — simple and correct, though not the fastest; fine for our per-question
    call volume. Optimize later if this becomes a bottleneck."""
    return asyncio.run(_call_tool_async(tool_name, arguments))