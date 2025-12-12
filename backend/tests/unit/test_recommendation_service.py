"""Unit tests for RecommendationService."""

import pytest

from src.domain.entities.gift import Gift
from src.domain.entities.recommendation_request import RecommendationRequest
from src.domain.ports.embedding_provider import EmbeddingProviderPort
from src.domain.ports.vector_store import VectorStorePort


class TestRecommendationServiceGetRecommendations:
    """Unit tests for RecommendationService.get_recommendations."""

    @pytest.mark.asyncio
    async def test_get_recommendations_returns_gifts(
        self,
        mock_embedding_provider: EmbeddingProviderPort,
        mock_vector_store: VectorStorePort,
        sample_gifts: list[Gift],
    ) -> None:
        """Test that get_recommendations returns gift list."""
        from src.domain.services.recommendation_service import RecommendationService

        service = RecommendationService(
            embedding_provider=mock_embedding_provider,
            vector_store=mock_vector_store,
        )

        request = RecommendationRequest(keywords="woodworking dad tools")

        response = await service.get_recommendations(request)

        assert len(response.gifts) > 0
        assert response.query_context.total_searched > 0

    @pytest.mark.asyncio
    async def test_get_recommendations_respects_limit(
        self,
        mock_embedding_provider: EmbeddingProviderPort,
        mock_vector_store: VectorStorePort,
    ) -> None:
        """Test that response respects the requested limit."""
        from src.domain.services.recommendation_service import RecommendationService

        service = RecommendationService(
            embedding_provider=mock_embedding_provider,
            vector_store=mock_vector_store,
        )

        request = RecommendationRequest(keywords="test recipient", limit=3)

        response = await service.get_recommendations(request)

        assert len(response.gifts) <= 3

    @pytest.mark.asyncio
    async def test_get_recommendations_embeds_keywords(
        self,
        mock_embedding_provider: EmbeddingProviderPort,
        mock_vector_store: VectorStorePort,
    ) -> None:
        """Test that keywords are embedded."""
        from src.domain.services.recommendation_service import RecommendationService

        service = RecommendationService(
            embedding_provider=mock_embedding_provider,
            vector_store=mock_vector_store,
        )

        request = RecommendationRequest(keywords="gardening mom outdoor")

        await service.get_recommendations(request)

        mock_embedding_provider.embed_text.assert_called_with("gardening mom outdoor")

    @pytest.mark.asyncio
    async def test_get_recommendations_searches_vector_store(
        self,
        mock_embedding_provider: EmbeddingProviderPort,
        mock_vector_store: VectorStorePort,
    ) -> None:
        """Test that vector store is searched with embedding."""
        from src.domain.services.recommendation_service import RecommendationService

        service = RecommendationService(
            embedding_provider=mock_embedding_provider,
            vector_store=mock_vector_store,
        )

        request = RecommendationRequest(keywords="test recipient")

        await service.get_recommendations(request)

        mock_vector_store.search_similar.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_recommendations_returns_sorted_by_relevance(
        self,
        mock_embedding_provider: EmbeddingProviderPort,
        mock_vector_store: VectorStorePort,
    ) -> None:
        """Test that gifts are sorted by relevance score descending."""
        from src.domain.services.recommendation_service import RecommendationService

        service = RecommendationService(
            embedding_provider=mock_embedding_provider,
            vector_store=mock_vector_store,
        )

        request = RecommendationRequest(keywords="test recipient")

        response = await service.get_recommendations(request)

        if len(response.gifts) > 1:
            for i in range(len(response.gifts) - 1):
                assert response.gifts[i].relevance_score >= response.gifts[i + 1].relevance_score

    @pytest.mark.asyncio
    async def test_fallback_to_popular_when_no_matches(
        self,
        mock_embedding_provider: EmbeddingProviderPort,
        mock_vector_store: VectorStorePort,
    ) -> None:
        """Test fallback to popular gifts when no matches above threshold."""
        from src.domain.services.recommendation_service import RecommendationService

        # Configure mock to return no matches
        mock_vector_store.search_similar.return_value = []

        service = RecommendationService(
            embedding_provider=mock_embedding_provider,
            vector_store=mock_vector_store,
        )

        request = RecommendationRequest(keywords="obscure unusual")

        response = await service.get_recommendations(request)

        assert response.query_context.fallback_used is True
        mock_vector_store.get_popular.assert_called_once()

    @pytest.mark.asyncio
    async def test_negative_keywords_creates_two_embeddings(
        self,
        mock_embedding_provider: EmbeddingProviderPort,
        mock_vector_store: VectorStorePort,
    ) -> None:
        """Test that negative keywords result in two embedding calls."""
        from src.domain.services.recommendation_service import RecommendationService

        service = RecommendationService(
            embedding_provider=mock_embedding_provider,
            vector_store=mock_vector_store,
        )

        request = RecommendationRequest(
            keywords="coffee lover",
            negative_keywords="espresso machine",
        )

        await service.get_recommendations(request)

        # Should embed both keywords and negative keywords
        assert mock_embedding_provider.embed_text.call_count == 2
