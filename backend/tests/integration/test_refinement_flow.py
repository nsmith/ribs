"""Integration tests for refinement flow with starred gifts."""

import pytest
from unittest.mock import AsyncMock
from uuid import UUID

from src.domain.entities.gift import Gift
from src.domain.entities.price_range import PriceRange
from src.domain.entities.recommendation_request import RecommendationRequest
from src.domain.ports.embedding_provider import EmbeddingProviderPort
from src.domain.ports.vector_store import VectorStorePort

# Fixed UUIDs for testing
STARRED_UUID = UUID("33333333-3333-3333-3333-333333333333")
STARRED_UUID_1 = UUID("44444444-4444-4444-4444-444444444444")
STARRED_UUID_2 = UUID("55555555-5555-5555-5555-555555555555")


class TestRefinementFlow:
    """Integration tests for the starred gift refinement flow."""

    @pytest.fixture
    def starred_gift(self) -> Gift:
        """Create a sample starred gift."""
        return Gift(
            id=STARRED_UUID,
            name="Woodworking Kit",
            brief_description="Beginner woodworking tools",
            full_description="Complete starter kit for woodworking",
            price_range=PriceRange.PREMIUM,
            categories=["tools", "crafts"],
            embedding=[0.7] * 1536,
            popularity_score=0.85,
        )

    @pytest.mark.asyncio
    async def test_refinement_with_starred_gifts(
        self,
        mock_embedding_provider: EmbeddingProviderPort,
        mock_vector_store: VectorStorePort,
        starred_gift: Gift,
        sample_gifts: list[Gift],
    ) -> None:
        """Test full refinement flow: initial request → star → refined request."""
        from src.domain.services.recommendation_service import RecommendationService

        # Setup mock to return starred gift when requested
        mock_vector_store.get_by_ids = AsyncMock(return_value=[starred_gift])

        service = RecommendationService(
            embedding_provider=mock_embedding_provider,
            vector_store=mock_vector_store,
        )

        # Step 1: Initial request
        initial_request = RecommendationRequest(
            recipient_description="My dad who loves building things"
        )

        initial_response = await service.get_recommendations(initial_request)
        assert initial_response.gifts is not None
        assert initial_response.query_context.starred_boost_applied is False

        # Step 2: Refined request with starred gift
        refined_request = RecommendationRequest(
            recipient_description="My dad who loves building things",
            starred_gift_ids=[str(STARRED_UUID)],
        )

        refined_response = await service.get_recommendations(refined_request)

        # Verify refinement was applied
        assert refined_response.query_context.starred_boost_applied is True
        assert refined_response.gifts is not None

    @pytest.mark.asyncio
    async def test_multiple_starred_gifts_blending(
        self,
        mock_embedding_provider: EmbeddingProviderPort,
        mock_vector_store: VectorStorePort,
    ) -> None:
        """Test blending multiple starred gift embeddings."""
        from src.domain.services.recommendation_service import RecommendationService

        starred_gifts = [
            Gift(
                id=STARRED_UUID_1,
                name="Gift 1",
                brief_description="Description 1",
                full_description="Full description 1",
                price_range=PriceRange.MODERATE,
                categories=["cat1"],
                embedding=[0.3] * 1536,
                popularity_score=0.7,
            ),
            Gift(
                id=STARRED_UUID_2,
                name="Gift 2",
                brief_description="Description 2",
                full_description="Full description 2",
                price_range=PriceRange.PREMIUM,
                categories=["cat2"],
                embedding=[0.9] * 1536,
                popularity_score=0.8,
            ),
        ]

        mock_vector_store.get_by_ids = AsyncMock(return_value=starred_gifts)

        service = RecommendationService(
            embedding_provider=mock_embedding_provider,
            vector_store=mock_vector_store,
        )

        request = RecommendationRequest(
            recipient_description="Test recipient",
            starred_gift_ids=[str(STARRED_UUID_1), str(STARRED_UUID_2)],
        )

        response = await service.get_recommendations(request)

        # Should complete without error and indicate boost was applied
        assert response.query_context.starred_boost_applied is True
        assert response.gifts is not None

    @pytest.mark.asyncio
    async def test_refinement_excludes_starred_from_results(
        self,
        mock_embedding_provider: EmbeddingProviderPort,
        mock_vector_store: VectorStorePort,
        starred_gift: Gift,
        sample_gifts: list[Gift],
    ) -> None:
        """Test that starred gifts are excluded from new results."""
        from src.domain.services.recommendation_service import RecommendationService

        # Setup: starred gift is also in search results
        results_with_starred = sample_gifts + [(starred_gift, 0.95)]
        mock_vector_store.search_similar = AsyncMock(
            return_value=[(g, 0.8) for g in sample_gifts] + [(starred_gift, 0.95)]
        )
        mock_vector_store.get_by_ids = AsyncMock(return_value=[starred_gift])

        service = RecommendationService(
            embedding_provider=mock_embedding_provider,
            vector_store=mock_vector_store,
        )

        request = RecommendationRequest(
            recipient_description="Test description",
            starred_gift_ids=[str(starred_gift.id)],
        )

        response = await service.get_recommendations(request)

        # Starred gifts should be excluded from results
        result_ids = [g.id for g in response.gifts]
        assert str(starred_gift.id) not in result_ids
