"""Contract tests for get_recommendations MCP tool."""

import pytest

from src.domain.entities.recommendation_request import RecommendationRequest


class TestGetRecommendationsContract:
    """Contract tests for the get_recommendations tool schema."""

    def test_valid_request_with_description_only(self) -> None:
        """Test request with just recipient description."""
        request = RecommendationRequest(
            recipient_description="My dad who loves woodworking and classic rock"
        )
        assert request.recipient_description == "My dad who loves woodworking and classic rock"
        assert request.past_gifts == []
        assert request.starred_gift_ids == []
        assert request.limit == 5

    def test_valid_request_with_all_fields(self) -> None:
        """Test request with all optional fields."""
        request = RecommendationRequest(
            recipient_description="My mom who enjoys gardening",
            past_gifts=["flower seeds", "gardening gloves"],
            starred_gift_ids=["abc123", "def456"],
            limit=8,
        )
        assert request.recipient_description == "My mom who enjoys gardening"
        assert len(request.past_gifts) == 2
        assert len(request.starred_gift_ids) == 2
        assert request.limit == 8

    def test_description_minimum_length(self) -> None:
        """Test that description must be at least 3 characters."""
        with pytest.raises(ValueError):
            RecommendationRequest(recipient_description="ab")

    def test_description_maximum_length(self) -> None:
        """Test that description is truncated or validated at 2000 chars."""
        long_description = "a" * 2001
        with pytest.raises(ValueError):
            RecommendationRequest(recipient_description=long_description)

    def test_limit_minimum(self) -> None:
        """Test that limit must be at least 3."""
        with pytest.raises(ValueError):
            RecommendationRequest(
                recipient_description="Valid description",
                limit=2,
            )

    def test_limit_maximum(self) -> None:
        """Test that limit cannot exceed 10."""
        with pytest.raises(ValueError):
            RecommendationRequest(
                recipient_description="Valid description",
                limit=11,
            )

    def test_past_gifts_truncated(self) -> None:
        """Test that past gifts are limited to 20 items."""
        many_gifts = [f"gift {i}" for i in range(25)]
        request = RecommendationRequest(
            recipient_description="Test recipient",
            past_gifts=many_gifts,
        )
        assert len(request.past_gifts) == 20

    def test_starred_gift_ids_truncated(self) -> None:
        """Test that starred gift IDs are limited to 20."""
        many_ids = [f"id-{i}" for i in range(25)]
        request = RecommendationRequest(
            recipient_description="Test recipient",
            starred_gift_ids=many_ids,
        )
        assert len(request.starred_gift_ids) == 20


class TestGetRecommendationsResponse:
    """Contract tests for the get_recommendations response format."""

    def test_response_contains_gifts_array(self) -> None:
        """Test that response includes gifts array."""
        # This will test the actual tool handler response
        # Placeholder until implementation
        pass

    def test_response_contains_query_context(self) -> None:
        """Test that response includes query context metadata."""
        # Placeholder until implementation
        pass

    def test_response_structured_content_format(self) -> None:
        """Test OpenAI Apps SDK structured response format."""
        # Placeholder until implementation
        pass

    def test_gift_contains_required_fields(self) -> None:
        """Test each gift has id, name, brief_description, relevance_score."""
        # Placeholder until implementation
        pass
