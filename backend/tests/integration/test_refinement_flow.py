"""Integration tests for negative keyword functionality."""

import pytest

from src.domain.entities.gift import Gift
from src.domain.entities.recommendation_request import RecommendationRequest
from src.domain.ports.embedding_provider import EmbeddingProviderPort
from src.domain.ports.vector_store import VectorStorePort


class TestNegativeKeywordsFlow:
    """Integration tests for negative keywords steering results away."""

    @pytest.mark.asyncio
    async def test_negative_keywords_adjusts_embedding(
        self,
        mock_embedding_provider: EmbeddingProviderPort,
        mock_vector_store: VectorStorePort,
        sample_gifts: list[Gift],
    ) -> None:
        """Test that negative keywords adjust the search embedding."""
        from src.domain.services.recommendation_service import RecommendationService

        service = RecommendationService(
            embedding_provider=mock_embedding_provider,
            vector_store=mock_vector_store,
        )

        request = RecommendationRequest(
            keywords="coffee lover morning",
            negative_keywords="espresso machine maker",
        )

        response = await service.get_recommendations(request)

        # Embedding provider should be called twice: keywords and negative
        assert mock_embedding_provider.embed_text.call_count == 2
        assert response is not None

    @pytest.mark.asyncio
    async def test_without_negative_keywords_single_embedding(
        self,
        mock_embedding_provider: EmbeddingProviderPort,
        mock_vector_store: VectorStorePort,
        sample_gifts: list[Gift],
    ) -> None:
        """Test that without negative keywords, only one embedding is made."""
        from src.domain.services.recommendation_service import RecommendationService

        service = RecommendationService(
            embedding_provider=mock_embedding_provider,
            vector_store=mock_vector_store,
        )

        request = RecommendationRequest(keywords="coffee lover morning")

        response = await service.get_recommendations(request)

        # Only keywords should be embedded
        assert mock_embedding_provider.embed_text.call_count == 1
        assert response is not None
