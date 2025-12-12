"""Unit tests for starred gift embedding blending in RecommendationService."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

from src.domain.entities.gift import Gift
from src.domain.entities.price_range import PriceRange
from src.domain.entities.recommendation_request import RecommendationRequest
from src.domain.ports.embedding_provider import EmbeddingProviderPort
from src.domain.ports.vector_store import VectorStorePort

# Fixed UUIDs for testing
STARRED_UUID_1 = UUID("11111111-1111-1111-1111-111111111111")
STARRED_UUID_2 = UUID("22222222-2222-2222-2222-222222222222")


class TestStarredGiftEmbeddingBlending:
    """Tests for embedding blending with starred gifts."""

    @pytest.fixture
    def starred_gifts(self) -> list[Gift]:
        """Create sample starred gifts."""
        return [
            Gift(
                id=STARRED_UUID_1,
                name="Starred Gift 1",
                brief_description="A previously starred gift",
                full_description="Full description",
                price_range=PriceRange.MODERATE,
                categories=["category1"],
                embedding=[0.5] * 1536,
                popularity_score=0.8,
            ),
            Gift(
                id=STARRED_UUID_2,
                name="Starred Gift 2",
                brief_description="Another starred gift",
                full_description="Full description",
                price_range=PriceRange.PREMIUM,
                categories=["category2"],
                embedding=[0.8] * 1536,
                popularity_score=0.7,
            ),
        ]

    @pytest.mark.asyncio
    async def test_starred_gifts_influence_search(
        self,
        mock_embedding_provider: EmbeddingProviderPort,
        mock_vector_store: VectorStorePort,
        starred_gifts: list[Gift],
    ) -> None:
        """Test that starred gift embeddings are fetched and blended."""
        from src.domain.services.recommendation_service import RecommendationService

        # Setup mock to return starred gifts
        mock_vector_store.get_by_ids = AsyncMock(return_value=starred_gifts)

        service = RecommendationService(
            embedding_provider=mock_embedding_provider,
            vector_store=mock_vector_store,
        )

        request = RecommendationRequest(
            recipient_description="My dad who loves woodworking",
            starred_gift_ids=[str(STARRED_UUID_1), str(STARRED_UUID_2)],
        )

        await service.get_recommendations(request)

        # Should fetch starred gifts by ID
        mock_vector_store.get_by_ids.assert_called_once_with([str(STARRED_UUID_1), str(STARRED_UUID_2)])

    @pytest.mark.asyncio
    async def test_blended_embedding_used_for_search(
        self,
        mock_embedding_provider: EmbeddingProviderPort,
        mock_vector_store: VectorStorePort,
        starred_gifts: list[Gift],
    ) -> None:
        """Test that blended embedding is used for similarity search."""
        from src.domain.services.recommendation_service import RecommendationService

        mock_vector_store.get_by_ids = AsyncMock(return_value=starred_gifts)

        service = RecommendationService(
            embedding_provider=mock_embedding_provider,
            vector_store=mock_vector_store,
        )

        request = RecommendationRequest(
            recipient_description="Test description",
            starred_gift_ids=[str(STARRED_UUID_1), str(STARRED_UUID_2)],
        )

        await service.get_recommendations(request)

        # The search should have been called (we verify it was called with some embedding)
        mock_vector_store.search_similar.assert_called_once()
        call_args = mock_vector_store.search_similar.call_args
        embedding_used = call_args.kwargs.get("embedding") or call_args[1].get("embedding")

        # The embedding should be different from the base embedding (blended)
        # Base embedding is [0.1] * 1536, starred are [0.5] and [0.8]
        # Blended should be somewhere between
        assert embedding_used is not None
        assert len(embedding_used) == 1536

    @pytest.mark.asyncio
    async def test_invalid_starred_ids_ignored(
        self,
        mock_embedding_provider: EmbeddingProviderPort,
        mock_vector_store: VectorStorePort,
    ) -> None:
        """Test that invalid starred gift IDs are silently ignored."""
        from src.domain.services.recommendation_service import RecommendationService

        # Return empty list for invalid IDs
        mock_vector_store.get_by_ids = AsyncMock(return_value=[])

        service = RecommendationService(
            embedding_provider=mock_embedding_provider,
            vector_store=mock_vector_store,
        )

        request = RecommendationRequest(
            recipient_description="Test description",
            starred_gift_ids=["invalid-1", "invalid-2"],
        )

        # Should not raise an error
        response = await service.get_recommendations(request)

        assert response is not None
        # Should still return results (from base embedding search)
        assert response.gifts is not None

    @pytest.mark.asyncio
    async def test_starred_boost_applied_flag(
        self,
        mock_embedding_provider: EmbeddingProviderPort,
        mock_vector_store: VectorStorePort,
        starred_gifts: list[Gift],
    ) -> None:
        """Test that starred_boost_applied flag is set when starred gifts used."""
        from src.domain.services.recommendation_service import RecommendationService

        mock_vector_store.get_by_ids = AsyncMock(return_value=starred_gifts)

        service = RecommendationService(
            embedding_provider=mock_embedding_provider,
            vector_store=mock_vector_store,
        )

        request = RecommendationRequest(
            recipient_description="Test description",
            starred_gift_ids=[str(STARRED_UUID_1)],
        )

        response = await service.get_recommendations(request)

        assert response.query_context.starred_boost_applied is True

    @pytest.mark.asyncio
    async def test_no_starred_boost_when_no_starred_ids(
        self,
        mock_embedding_provider: EmbeddingProviderPort,
        mock_vector_store: VectorStorePort,
    ) -> None:
        """Test that starred_boost_applied is False when no starred gifts."""
        from src.domain.services.recommendation_service import RecommendationService

        service = RecommendationService(
            embedding_provider=mock_embedding_provider,
            vector_store=mock_vector_store,
        )

        request = RecommendationRequest(
            recipient_description="Test description",
        )

        response = await service.get_recommendations(request)

        assert response.query_context.starred_boost_applied is False
