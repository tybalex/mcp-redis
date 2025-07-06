from mcp.server.fastmcp import FastMCP

from src.common.config import MCP_PORT, MCP_HOST

# Initialize FastMCP server
mcp = FastMCP(
    "Redis MCP Server",
    host=MCP_HOST,
    port=MCP_PORT,
    dependencies=["redis", "dotenv", "numpy"]
)

