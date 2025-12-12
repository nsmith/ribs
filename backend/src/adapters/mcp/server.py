"""FastMCP server setup for gift recommendations."""

from typing import Annotated

import structlog
from fastmcp import FastMCP
from mcp.types import ToolAnnotations

from src.adapters.mcp.tools.get_gift_details import get_gift_details_handler
from src.adapters.mcp.tools.get_recommendations import get_recommendations_handler
from src.config.settings import Settings
from src.domain.ports.vector_store import VectorStorePort
from src.domain.services.recommendation_service import RecommendationService

logger = structlog.get_logger()

# Global service instances (set during server creation)
_recommendation_service: RecommendationService | None = None
_vector_store: VectorStorePort | None = None


def create_mcp_server(
    settings: Settings,
    recommendation_service: RecommendationService,
    vector_store: VectorStorePort | None = None,
) -> FastMCP:
    """Create and configure the FastMCP server.

    Args:
        settings: Application settings
        recommendation_service: The recommendation service instance
        vector_store: Vector store for gift details lookup

    Returns:
        Configured FastMCP server instance
    """
    global _recommendation_service, _vector_store
    _recommendation_service = recommendation_service
    _vector_store = vector_store

    mcp = FastMCP(
        name=settings.mcp_server_name,
        version="0.1.0",
    )

    # Register the get_recommendations tool
    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def get_recommendations(
        keywords: Annotated[
            str,
            "Search keywords for finding gifts. Include recipient interests, occasion, or gift type. Examples: 'coffee lover birthday', 'outdoor camping dad', 'tech gadgets christmas', 'cooking kitchen mom'",
        ],
        negative_keywords: Annotated[
            str | None,
            "Keywords to avoid in results. Use for past gifts or things to steer away from. Examples: 'coffee maker espresso' (if they already have coffee gear), 'electronics gadgets' (if you want non-tech gifts)",
        ] = None,
        limit: Annotated[
            int | None,
            "Number of recommendations to return (default: 5, min: 3, max: 10)",
        ] = None,
    ) -> dict:
        """Search for gift recommendations using keywords.

        Pass keywords about the recipient's interests, the occasion, or gift categories.
        Use negative_keywords to avoid certain types of gifts (e.g., past gifts).

        Each gift in the response includes:
        - id: Unique identifier (use with get_gift_details to learn more)
        - name: Gift name
        - brief_description: Short summary
        - price_range: budget, moderate, premium, or luxury
        - categories: Tags like 'electronics', 'handmade', 'outdoor'
        - relevance_score: How well it matches (0.0-1.0)
        """
        return await get_recommendations_handler(
            keywords=keywords,
            negative_keywords=negative_keywords,
            limit=limit,
            service=_recommendation_service,
        )

    # Register the get_gift_details tool (only if vector_store provided)
    if _vector_store is not None:
        @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
        async def get_gift_details(
            gift_id: Annotated[
                str,
                "The unique ID of a gift from get_recommendations results. Example: '12345678-1234-1234-1234-123456789012'",
            ],
        ) -> dict:
            """Get full details about a specific gift idea.

            Use this to learn more about a gift before recommending it. Returns the complete
            description, suggested occasions (birthday, christmas, etc.), ideal recipient types,
            and a purchase link when available.

            The response includes:
            - id, name, brief_description, full_description
            - price_range: budget, moderate, premium, or luxury
            - categories: Tags like 'electronics', 'handmade', 'outdoor'
            - occasions: When to give it (birthday, anniversary, christmas, etc.)
            - recipient_types: Who it's good for (tech enthusiast, home cook, etc.)
            - purchase_url: Where to buy it (when available)
            """
            return await get_gift_details_handler(
                gift_id=gift_id,
                vector_store=_vector_store,
            )

        tools = ["get_recommendations", "get_gift_details"]
    else:
        tools = ["get_recommendations"]

    log = logger.bind(server=settings.mcp_server_name)
    log.info("mcp_server_created", tools=tools)

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
