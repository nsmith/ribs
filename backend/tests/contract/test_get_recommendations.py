"""Contract tests for get_recommendations MCP tool."""

import pytest

from src.domain.entities.recommendation_request import RecommendationRequest


class TestGetRecommendationsContract:
    """Contract tests for the get_recommendations tool schema."""

    def test_valid_request_with_keywords_only(self) -> None:
        """Test request with just keywords."""
        request = RecommendationRequest(keywords="coffee lover birthday dad")
        assert request.keywords == "coffee lover birthday dad"
        assert request.negative_keywords is None
        assert request.limit == 5

    def test_valid_request_with_all_fields(self) -> None:
        """Test request with all optional fields."""
        request = RecommendationRequest(
            keywords="gardening outdoor mom",
            negative_keywords="tools hardware",
            limit=8,
        )
        assert request.keywords == "gardening outdoor mom"
        assert request.negative_keywords == "tools hardware"
        assert request.limit == 8

    def test_keywords_minimum_length(self) -> None:
        """Test that keywords must be at least 3 characters."""
        with pytest.raises(ValueError):
            RecommendationRequest(keywords="ab")

    def test_keywords_maximum_length(self) -> None:
        """Test that keywords are validated at 500 chars."""
        long_keywords = "a" * 501
        with pytest.raises(ValueError):
            RecommendationRequest(keywords=long_keywords)

    def test_limit_minimum(self) -> None:
        """Test that limit must be at least 3."""
        with pytest.raises(ValueError):
            RecommendationRequest(
                keywords="valid keywords",
                limit=2,
            )

    def test_limit_maximum(self) -> None:
        """Test that limit cannot exceed 10."""
        with pytest.raises(ValueError):
            RecommendationRequest(
                keywords="valid keywords",
                limit=11,
            )

    def test_negative_keywords_optional(self) -> None:
        """Test that negative keywords are optional."""
        request = RecommendationRequest(keywords="tech gadgets")
        assert request.negative_keywords is None

    def test_negative_keywords_maximum_length(self) -> None:
        """Test that negative keywords are validated at 500 chars."""
        long_negative = "a" * 501
        with pytest.raises(ValueError):
            RecommendationRequest(
                keywords="valid keywords",
                negative_keywords=long_negative,
            )


class TestGetRecommendationsResponse:
    """Contract tests for the get_recommendations response format."""

    def test_response_contains_gifts_array(self) -> None:
        """Test that response includes gifts array."""
        # Placeholder - tested in integration tests
        pass

    def test_response_contains_query_context(self) -> None:
        """Test that response includes query context metadata."""
        # Placeholder - internal only, not in MCP response
        pass

    def test_response_structured_content_format(self) -> None:
        """Test OpenAI Apps SDK structured response format."""
        # Placeholder - tested in integration tests
        pass

    def test_gift_contains_required_fields(self) -> None:
        """Test each gift has id, name, brief_description, relevance_score."""
        # Placeholder - tested in integration tests
        pass
