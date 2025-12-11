"""FastMCP server setup for gift recommendations."""

import structlog
from fastmcp import FastMCP

from src.config.settings import Settings

logger = structlog.get_logger()


def create_mcp_server(settings: Settings) -> FastMCP:
    """Create and configure the FastMCP server.

    Args:
        settings: Application settings

    Returns:
        Configured FastMCP server instance
    """
    mcp = FastMCP(
        name=settings.mcp_server_name,
        version="0.1.0",
    )

    log = logger.bind(server=settings.mcp_server_name)
    log.info("mcp_server_created")

    return mcp


# Global server instance (initialized in main.py)
mcp_server: FastMCP | None = None


def get_mcp_server() -> FastMCP:
    """Get the global MCP server instance.

    Returns:
        The configured MCP server

    Raises:
        RuntimeError: If server not initialized
    """
    if mcp_server is None:
        raise RuntimeError("MCP server not initialized. Call create_mcp_server first.")
    return mcp_server
