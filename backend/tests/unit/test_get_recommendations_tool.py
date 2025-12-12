"""Unit tests for get_recommendations MCP tool handler."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.domain.entities.query_context import QueryContext
from src.domain.entities.recommendation_response import (
    GiftRecommendation,
    RecommendationResponse,
)
from src.domain.entities.price_range import PriceRange


class TestGetRecommendationsTool:
    """Unit tests for get_recommendations tool handler."""

    @pytest.fixture
    def mock_recommendation_service(self) -> MagicMock:
        """Create a mock recommendation service."""
        service = MagicMock()
        service.get_recommendations = AsyncMock(
            return_value=RecommendationResponse(
                gifts=[
                    GiftRecommendation(
                        id="gift-1",
                        name="Test Gift",
                        brief_description="A test gift",
                        relevance_score=0.9,
                        price_range=PriceRange.MODERATE,
                        categories=["test"],
                    )
                ],
                query_context=QueryContext(
                    total_searched=100,
                    above_threshold=10,
                    starred_boost_applied=False,
                    fallback_used=False,
                ),
            )
        )
        return service

    @pytest.mark.asyncio
    async def test_tool_returns_structured_response(
        self,
        mock_recommendation_service: MagicMock,
    ) -> None:
        """Test that tool returns MCP structured content format."""
        from src.adapters.mcp.tools.get_recommendations import get_recommendations_handler

        result = await get_recommendations_handler(
            keywords="woodworking dad birthday",
            service=mock_recommendation_service,
        )

        # MCP structured content format
        assert "structuredContent" in result
        assert "content" in result

    @pytest.mark.asyncio
    async def test_tool_structured_content_contains_gifts(
        self,
        mock_recommendation_service: MagicMock,
    ) -> None:
        """Test that structured content contains gift data."""
        from src.adapters.mcp.tools.get_recommendations import get_recommendations_handler

        result = await get_recommendations_handler(
            keywords="woodworking dad birthday",
            service=mock_recommendation_service,
        )

        structured = result["structuredContent"]
        assert "gifts" in structured
        assert len(structured["gifts"]) > 0
        assert structured["gifts"][0]["name"] == "Test Gift"

    @pytest.mark.asyncio
    async def test_tool_content_is_human_readable(
        self,
        mock_recommendation_service: MagicMock,
    ) -> None:
        """Test that content field is human-readable summary."""
        from src.adapters.mcp.tools.get_recommendations import get_recommendations_handler

        result = await get_recommendations_handler(
            keywords="woodworking dad birthday",
            service=mock_recommendation_service,
        )

        content = result["content"]
        assert isinstance(content, str)
        assert "Test Gift" in content or "recommendation" in content.lower()

    @pytest.mark.asyncio
    async def test_tool_calls_service_with_request(
        self,
        mock_recommendation_service: MagicMock,
    ) -> None:
        """Test that tool passes correct request to service."""
        from src.adapters.mcp.tools.get_recommendations import get_recommendations_handler

        await get_recommendations_handler(
            keywords="gardening mom outdoor",
            negative_keywords="tools hardware",
            limit=5,
            service=mock_recommendation_service,
        )

        mock_recommendation_service.get_recommendations.assert_called_once()
        call_args = mock_recommendation_service.get_recommendations.call_args
        request = call_args[0][0]

        assert request.keywords == "gardening mom outdoor"
        assert request.negative_keywords == "tools hardware"
        assert request.limit == 5

    @pytest.mark.asyncio
    async def test_tool_handles_validation_error(
        self,
        mock_recommendation_service: MagicMock,
    ) -> None:
        """Test that tool returns error for invalid input."""
        from src.adapters.mcp.tools.get_recommendations import get_recommendations_handler

        result = await get_recommendations_handler(
            keywords="ab",  # Too short (min 3 chars)
            service=mock_recommendation_service,
        )

        # Error should be in structuredContent
        assert "error" in result["structuredContent"]
