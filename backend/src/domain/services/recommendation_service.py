"""Recommendation service for gift suggestions."""

from src.domain.entities.gift import Gift
from src.domain.entities.query_context import QueryContext
from src.domain.entities.recommendation_request import RecommendationRequest
from src.domain.entities.recommendation_response import (
    GiftRecommendation,
    RecommendationResponse,
)
from src.domain.ports.embedding_provider import EmbeddingProviderPort
from src.domain.ports.vector_store import VectorStorePort
from src.domain.services.embedding_service import EmbeddingService


class RecommendationService:
    """Service for generating gift recommendations."""

    def __init__(
        self,
        embedding_provider: EmbeddingProviderPort,
        vector_store: VectorStorePort,
    ) -> None:
        """Initialize the recommendation service.

        Args:
            embedding_provider: Provider for text embeddings.
            vector_store: Vector store for similarity search.
        """
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store
        self._embedding_service = EmbeddingService(provider=embedding_provider)

    async def get_recommendations(
        self,
        request: RecommendationRequest,
    ) -> RecommendationResponse:
        """Get gift recommendations based on the request.

        Args:
            request: The recommendation request with keywords.

        Returns:
            A response containing gift recommendations and query context.
        """
        # Embed the search keywords
        query_embedding = await self._embedding_provider.embed_text(request.keywords)

        # Apply negative keywords if provided
        if request.negative_keywords:
            negative_embedding = await self._embedding_provider.embed_text(
                request.negative_keywords
            )
            query_embedding = self._embedding_service.subtract_embedding(
                positive=query_embedding,
                negative=negative_embedding,
                negative_weight=0.3,
            )

        # Search for similar gifts
        limit = request.limit or 5

        search_results = await self._vector_store.search_similar(
            embedding=query_embedding,
            limit=limit * 2,  # Get extra to account for low scores
            threshold=0.3,  # Lower threshold for keyword search
        )

        # Track query context
        total_searched = await self._vector_store.get_total_count()
        fallback_used = False

        # If no results above threshold, fall back to popular gifts
        if not search_results:
            fallback_used = True
            search_results = await self._vector_store.get_popular(limit=limit)

        # Convert results to recommendations
        gifts = [
            self._gift_to_recommendation(gift, score)
            for gift, score in search_results
        ]

        # Sort by relevance score descending
        gifts.sort(key=lambda g: g.relevance_score, reverse=True)

        # Respect the limit
        gifts = gifts[:limit]

        query_context = QueryContext(
            total_searched=total_searched,
            above_threshold=len([g for g in gifts if g.relevance_score >= 0.3]),
            starred_boost_applied=False,
            fallback_used=fallback_used,
        )

        return RecommendationResponse(
            gifts=gifts,
            query_context=query_context,
        )

    def _gift_to_recommendation(
        self,
        gift: Gift,
        score: float,
    ) -> GiftRecommendation:
        """Convert a Gift entity to a GiftRecommendation.

        Args:
            gift: The gift entity.
            score: The relevance score.

        Returns:
            A GiftRecommendation with the gift data.
        """
        return GiftRecommendation(
            id=str(gift.id),
            name=gift.name,
            brief_description=gift.brief_description,
            relevance_score=score,
            price_range=gift.price_range,
            categories=gift.categories,
        )
