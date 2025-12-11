"""MCP tool handler for get_recommendations."""

from typing import Any

import structlog
from pydantic import ValidationError

from src.domain.entities.recommendation_request import RecommendationRequest
from src.domain.services.recommendation_service import RecommendationService

logger = structlog.get_logger(__name__)


async def get_recommendations_handler(
    recipient_description: str,
    service: RecommendationService,
    past_gifts: list[str] | None = None,
    starred_gift_ids: list[str] | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """Handle get_recommendations MCP tool call.

    Args:
        recipient_description: Description of the gift recipient.
        service: The recommendation service instance.
        past_gifts: Optional list of previously given gifts.
        starred_gift_ids: Optional list of starred gift IDs for refinement.
        limit: Optional limit on number of recommendations.

    Returns:
        MCP structured response with gifts and metadata.
    """
    log = logger.bind(
        tool="get_recommendations",
        description_length=len(recipient_description),
        has_past_gifts=bool(past_gifts),
        has_starred=bool(starred_gift_ids),
        limit=limit,
    )

    try:
        # Build request with validation
        request = RecommendationRequest(
            recipient_description=recipient_description,
            past_gifts=past_gifts or [],
            starred_gift_ids=starred_gift_ids or [],
            limit=limit or 5,
        )

        log.info("processing_recommendation_request")

        # Get recommendations from service
        response = await service.get_recommendations(request)

        log.info(
            "recommendation_request_complete",
            num_gifts=len(response.gifts),
            fallback_used=response.query_context.fallback_used,
        )

        # Build MCP structured response
        return _build_structured_response(response)

    except ValidationError as e:
        log.warning("validation_error", errors=e.errors())
        return _build_error_response(str(e))

    except Exception as e:
        log.error("recommendation_error", error=str(e))
        return _build_error_response(f"Failed to get recommendations: {e}")


def _build_structured_response(response: Any) -> dict[str, Any]:
    """Build MCP structured content response.

    Args:
        response: The RecommendationResponse from the service.

    Returns:
        MCP-formatted response with structuredContent, content, and _meta.
    """
    # Structured content for programmatic access (UI rendering)
    structured_content = {
        "gifts": [
            {
                "id": gift.id,
                "name": gift.name,
                "brief_description": gift.brief_description,
                "relevance_score": gift.relevance_score,
                "price_range": gift.price_range.value,
                "categories": gift.categories,
            }
            for gift in response.gifts
        ],
        "query_context": {
            "total_searched": response.query_context.total_searched,
            "above_threshold": response.query_context.above_threshold,
            "starred_boost_applied": response.query_context.starred_boost_applied,
            "fallback_used": response.query_context.fallback_used,
        },
    }

    # Human-readable content for LLM/text display
    if response.gifts:
        gift_lines = [
            f"- {gift.name}: {gift.brief_description} ({gift.price_range.value})"
            for gift in response.gifts[:5]
        ]
        content = f"Found {len(response.gifts)} gift recommendations:\n" + "\n".join(gift_lines)
    else:
        content = "No gift recommendations found matching the description."

    # Metadata for debugging/analytics
    meta = {
        "total_searched": response.query_context.total_searched,
        "above_threshold": response.query_context.above_threshold,
        "starred_boost_applied": response.query_context.starred_boost_applied,
        "fallback_used": response.query_context.fallback_used,
    }

    return {
        "structuredContent": structured_content,
        "content": content,
        "_meta": meta,
    }


def _build_error_response(error_message: str) -> dict[str, Any]:
    """Build MCP error response.

    Args:
        error_message: The error message to include.

    Returns:
        MCP-formatted error response.
    """
    return {
        "structuredContent": {"error": error_message, "gifts": []},
        "content": f"Error: {error_message}",
        "_meta": {"error": error_message},
    }
