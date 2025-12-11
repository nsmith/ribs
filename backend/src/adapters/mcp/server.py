"""FastMCP server setup for gift recommendations."""

from typing import Annotated

import structlog
from fastmcp import FastMCP

from src.adapters.mcp.tools.get_recommendations import get_recommendations_handler
from src.config.settings import Settings
from src.domain.services.recommendation_service import RecommendationService

logger = structlog.get_logger()

# Global service instance (set during server creation)
_recommendation_service: RecommendationService | None = None


def create_mcp_server(
    settings: Settings,
    recommendation_service: RecommendationService,
) -> FastMCP:
    """Create and configure the FastMCP server.

    Args:
        settings: Application settings
        recommendation_service: The recommendation service instance

    Returns:
        Configured FastMCP server instance
    """
    global _recommendation_service
    _recommendation_service = recommendation_service

    mcp = FastMCP(
        name=settings.mcp_server_name,
        version="0.1.0",
    )

    # Register the get_recommendations tool
    @mcp.tool()
    async def get_recommendations(
        recipient_description: Annotated[str, "Description of the gift recipient (3-2000 chars)"],
        past_gifts: Annotated[list[str] | None, "Previously given gifts to avoid"] = None,
        starred_gift_ids: Annotated[list[str] | None, "IDs of starred gifts for refinement"] = None,
        limit: Annotated[int | None, "Number of recommendations (3-10)"] = None,
    ) -> dict:
        """Get personalized gift recommendations based on recipient description.

        Analyzes the recipient description and returns relevant gift suggestions
        using semantic similarity search. Optionally refine results by starring
        gifts from previous results.
        """
        return await get_recommendations_handler(
            recipient_description=recipient_description,
            past_gifts=past_gifts,
            starred_gift_ids=starred_gift_ids,
            limit=limit,
            service=_recommendation_service,
        )

    log = logger.bind(server=settings.mcp_server_name)
    log.info("mcp_server_created", tools=["get_recommendations"])

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
