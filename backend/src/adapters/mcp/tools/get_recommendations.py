"""MCP tool handler for get_recommendations."""

from typing import Any

import structlog
from pydantic import ValidationError

from src.domain.entities.recommendation_request import RecommendationRequest
from src.domain.services.recommendation_service import RecommendationService

logger = structlog.get_logger(__name__)


async def get_recommendations_handler(
    keywords: str,
    service: RecommendationService,
    negative_keywords: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """Handle get_recommendations MCP tool call.

    Args:
        keywords: Search keywords for gift matching.
        service: The recommendation service instance.
        negative_keywords: Optional keywords to avoid in results.
        limit: Optional limit on number of recommendations.

    Returns:
        MCP structured response with gifts and metadata.
    """
    log = logger.bind(
        tool="get_recommendations",
        keywords_length=len(keywords),
        has_negative=bool(negative_keywords),
        limit=limit,
    )

    try:
        # Build request with validation
        request = RecommendationRequest(
            keywords=keywords,
            negative_keywords=negative_keywords,
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
        MCP-formatted response with structuredContent and content.
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

    return {
        "structuredContent": structured_content,
        "content": content,
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
    }
