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
        recipient_description: Annotated[
            str,
            "A description of the person you're buying a gift for. Include details like their interests, hobbies, age, relationship to you, and the occasion. Example: 'My 30-year-old sister who loves gardening and cooking, for her birthday'",
        ],
        past_gifts: Annotated[
            list[str] | None,
            "List of gifts you've already given this person, so we can suggest something different. Example: ['cookbook', 'plant pot', 'kitchen knife set']",
        ] = None,
        starred_gift_ids: Annotated[
            list[str] | None,
            "IDs of gifts from previous results that you liked. Pass these to refine recommendations toward similar items. Get IDs from the 'id' field in previous results.",
        ] = None,
        limit: Annotated[
            int | None,
            "Number of recommendations to return (default: 5, min: 3, max: 10)",
        ] = None,
    ) -> dict:
        """Search for personalized gift recommendations based on who you're shopping for.

        Returns a ranked list of gift ideas with names, descriptions, price ranges, and
        categories. Each gift has a unique ID you can use with get_gift_details for more
        info, or pass to starred_gift_ids to find similar items.

        Each gift in the response includes:
        - id: Unique identifier (use with get_gift_details or starred_gift_ids)
        - name: Gift name
        - brief_description: Short summary
        - price_range: budget, moderate, premium, or luxury
        - categories: Tags like 'electronics', 'handmade', 'outdoor'
        - relevance_score: How well it matches (0.0-1.0)
        """
        return await get_recommendations_handler(
            recipient_description=recipient_description,
            past_gifts=past_gifts,
            starred_gift_ids=starred_gift_ids,
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
