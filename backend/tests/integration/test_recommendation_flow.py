"""Integration tests for full recommendation flow."""

import pytest

from src.domain.entities.gift import Gift
from src.domain.entities.recommendation_request import RecommendationRequest
from src.domain.ports.embedding_provider import EmbeddingProviderPort
from src.domain.ports.vector_store import VectorStorePort


class TestRecommendationFlow:
    """Integration tests for end-to-end recommendation flow."""

    @pytest.mark.asyncio
    async def test_full_recommendation_flow(
        self,
        mock_embedding_provider: EmbeddingProviderPort,
        mock_vector_store: VectorStorePort,
        sample_gifts: list[Gift],
    ) -> None:
        """Test complete flow: request → embed → search → response."""
        from src.domain.services.recommendation_service import RecommendationService

        # Create service
        recommendation_service = RecommendationService(
            embedding_provider=mock_embedding_provider,
            vector_store=mock_vector_store,
        )

        # Create request with keywords
        request = RecommendationRequest(keywords="woodworking dad birthday tools")

        # Get recommendations
        response = await recommendation_service.get_recommendations(request)

        # Verify response structure
        assert response.gifts is not None
        assert len(response.gifts) > 0
        assert response.query_context is not None

        # Verify each gift has required fields
        for gift_rec in response.gifts:
            assert gift_rec.id is not None
            assert gift_rec.name is not None
            assert gift_rec.brief_description is not None
            assert 0.0 <= gift_rec.relevance_score <= 1.0
            assert gift_rec.price_range is not None
            assert len(gift_rec.categories) > 0

    @pytest.mark.asyncio
    async def test_recommendation_with_negative_keywords(
        self,
        mock_embedding_provider: EmbeddingProviderPort,
        mock_vector_store: VectorStorePort,
    ) -> None:
        """Test recommendations with negative keywords."""
        from src.domain.services.recommendation_service import RecommendationService

        service = RecommendationService(
            embedding_provider=mock_embedding_provider,
            vector_store=mock_vector_store,
        )

        request = RecommendationRequest(
            keywords="gardening mom outdoor",
            negative_keywords="tools hardware power",
        )

        response = await service.get_recommendations(request)

        # Negative keywords should steer away from those results
        assert response is not None
        assert response.query_context is not None

    @pytest.mark.asyncio
    async def test_recommendation_empty_results_fallback(
        self,
        mock_embedding_provider: EmbeddingProviderPort,
        mock_vector_store: VectorStorePort,
        sample_gifts: list[Gift],
    ) -> None:
        """Test fallback when no matches found."""
        from src.domain.services.recommendation_service import RecommendationService

        # Configure mock to return no matches initially
        mock_vector_store.search_similar.return_value = []
        mock_vector_store.get_popular.return_value = [
            (sample_gifts[0], 0.5),
        ]

        service = RecommendationService(
            embedding_provider=mock_embedding_provider,
            vector_store=mock_vector_store,
        )

        request = RecommendationRequest(keywords="obscure unique unusual")

        response = await service.get_recommendations(request)

        assert response.query_context.fallback_used is True
        assert len(response.gifts) > 0

    @pytest.mark.asyncio
    async def test_response_format_for_openai_apps_sdk(
        self,
        mock_embedding_provider: EmbeddingProviderPort,
        mock_vector_store: VectorStorePort,
    ) -> None:
        """Test response format matches OpenAI Apps SDK requirements."""
        from src.domain.services.recommendation_service import RecommendationService

        service = RecommendationService(
            embedding_provider=mock_embedding_provider,
            vector_store=mock_vector_store,
        )

        request = RecommendationRequest(keywords="test recipient")

        response = await service.get_recommendations(request)

        # Verify structure can be serialized to expected format
        response_dict = response.model_dump()

        assert "gifts" in response_dict
        assert "query_context" in response_dict
        assert isinstance(response_dict["gifts"], list)
