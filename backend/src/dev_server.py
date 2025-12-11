"""Development MCP server with mock adapters for testing with MCP Inspector."""

import random
from typing import Any
from uuid import UUID, uuid4

import structlog

from src.adapters.mcp.server import create_mcp_server
from src.config.logging import configure_logging
from src.config.settings import Settings
from src.domain.entities.gift import Gift
from src.domain.entities.price_range import PriceRange
from src.domain.ports.embedding_provider import EmbeddingProviderPort
from src.domain.ports.vector_store import VectorStorePort
from src.domain.services.recommendation_service import RecommendationService

logger = structlog.get_logger()


# Sample gift data for testing
SAMPLE_GIFTS = [
    Gift(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        name="Leather Journal",
        brief_description="Hand-crafted leather journal for notes and sketches",
        full_description="A beautiful hand-crafted leather journal with 200 pages of acid-free paper. Perfect for writers, artists, or anyone who appreciates fine craftsmanship. Features a wrap-around cover with a leather cord closure.",
        price_range=PriceRange.MODERATE,
        categories=["stationery", "handmade"],
        occasions=["birthday", "graduation", "christmas"],
        recipient_types=["writers", "artists", "professionals"],
        embedding=[0.1] * 1536,
        popularity_score=0.85,
        purchase_url="https://example.com/leather-journal",
        has_affiliate_commission=True,
    ),
    Gift(
        id=UUID("22222222-2222-2222-2222-222222222222"),
        name="Woodworking Kit",
        brief_description="Beginner woodworking tool set with quality tools",
        full_description="Complete starter kit for woodworking enthusiasts. Includes chisels, mallet, marking gauge, and instructional guide. Made with quality hardwood handles and steel blades.",
        price_range=PriceRange.PREMIUM,
        categories=["tools", "crafts", "DIY"],
        occasions=["birthday", "father's day", "retirement"],
        recipient_types=["hobbyists", "DIY enthusiasts", "dads"],
        embedding=[0.2] * 1536,
        popularity_score=0.82,
        purchase_url="https://example.com/woodworking-kit",
        has_affiliate_commission=True,
    ),
    Gift(
        id=UUID("33333333-3333-3333-3333-333333333333"),
        name="Vinyl Record Player",
        brief_description="Retro-style turntable with modern features",
        full_description="Classic vinyl record player combining vintage aesthetics with modern technology. Features built-in speakers, Bluetooth connectivity, and USB recording capability. Plays 33, 45, and 78 RPM records.",
        price_range=PriceRange.PREMIUM,
        categories=["electronics", "music", "retro"],
        occasions=["birthday", "christmas", "housewarming"],
        recipient_types=["music lovers", "audiophiles", "collectors"],
        embedding=[0.3] * 1536,
        popularity_score=0.78,
        purchase_url="https://example.com/vinyl-player",
        has_affiliate_commission=False,
    ),
    Gift(
        id=UUID("44444444-4444-4444-4444-444444444444"),
        name="Gourmet Coffee Subscription",
        brief_description="Monthly delivery of artisan coffee beans",
        full_description="Premium coffee subscription featuring single-origin beans from around the world. Each month receive 12oz of freshly roasted coffee with tasting notes and brewing tips. Choose from light, medium, or dark roasts.",
        price_range=PriceRange.MODERATE,
        categories=["food", "subscription", "coffee"],
        occasions=["birthday", "thank you", "just because"],
        recipient_types=["coffee lovers", "foodies", "remote workers"],
        embedding=[0.4] * 1536,
        popularity_score=0.88,
        purchase_url="https://example.com/coffee-subscription",
        has_affiliate_commission=True,
    ),
    Gift(
        id=UUID("55555555-5555-5555-5555-555555555555"),
        name="Indoor Herb Garden Kit",
        brief_description="Grow fresh herbs year-round with LED lighting",
        full_description="Self-watering indoor garden with LED grow lights. Includes seeds for basil, mint, parsley, and cilantro. Perfect for small spaces - fits on any countertop. Grows herbs 5x faster than soil.",
        price_range=PriceRange.MODERATE,
        categories=["gardening", "kitchen", "home"],
        occasions=["housewarming", "mother's day", "birthday"],
        recipient_types=["home cooks", "plant lovers", "apartment dwellers"],
        embedding=[0.5] * 1536,
        popularity_score=0.75,
        purchase_url="https://example.com/herb-garden",
        has_affiliate_commission=True,
    ),
]


class MockEmbeddingProvider(EmbeddingProviderPort):
    """Mock embedding provider for development."""

    async def embed_text(self, text: str) -> list[float]:
        """Return a deterministic mock embedding based on text."""
        # Create a simple deterministic embedding based on text hash
        seed = hash(text) % 10000
        random.seed(seed)
        return [random.random() for _ in range(1536)]

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts."""
        return [await self.embed_text(t) for t in texts]

    def get_dimensions(self) -> int:
        """Return embedding dimensions."""
        return 1536

    async def health_check(self) -> dict[str, Any]:
        """Return health status."""
        return {"status": "healthy", "provider": "mock"}


class MockVectorStore(VectorStorePort):
    """Mock vector store with sample gifts for development."""

    def __init__(self, gifts: list[Gift]) -> None:
        self._gifts = {str(g.id): g for g in gifts}

    async def search_similar(
        self,
        embedding: list[float],
        limit: int = 5,
        threshold: float = 0.5,
    ) -> list[tuple[Gift, float]]:
        """Return sample gifts with mock similarity scores."""
        gifts = list(self._gifts.values())
        # Shuffle to simulate different results
        random.shuffle(gifts)
        results = []
        for i, gift in enumerate(gifts[:limit]):
            score = 0.95 - (i * 0.05)  # Decreasing scores
            results.append((gift, score))
        return results

    async def get_by_id(self, gift_id: str) -> Gift | None:
        """Get a gift by ID."""
        return self._gifts.get(gift_id)

    async def get_by_ids(self, gift_ids: list[str]) -> list[Gift]:
        """Get multiple gifts by ID."""
        return [self._gifts[gid] for gid in gift_ids if gid in self._gifts]

    async def get_popular(self, limit: int = 5) -> list[tuple[Gift, float]]:
        """Get popular gifts."""
        sorted_gifts = sorted(
            self._gifts.values(),
            key=lambda g: g.popularity_score,
            reverse=True,
        )
        return [(g, g.popularity_score) for g in sorted_gifts[:limit]]

    async def get_total_count(self) -> int:
        """Get total gift count."""
        return len(self._gifts)

    async def upsert(self, gift: Gift) -> None:
        """Add or update a gift."""
        self._gifts[str(gift.id)] = gift

    async def find_by_name(self, name: str) -> Gift | None:
        """Find a gift by name."""
        for gift in self._gifts.values():
            if gift.name == name:
                return gift
        return None

    async def health_check(self) -> dict[str, Any]:
        """Return health status."""
        return {"status": "healthy", "store": "mock", "count": len(self._gifts)}


def main() -> None:
    """Run the development MCP server with mock adapters."""
    configure_logging("DEBUG")

    log = logger.bind(server="gift-recommendations-dev")
    log.info("starting_dev_server")

    # Create mock adapters
    embedding_adapter = MockEmbeddingProvider()
    vector_adapter = MockVectorStore(SAMPLE_GIFTS)

    # Create service with mock adapters
    recommendation_service = RecommendationService(
        embedding_provider=embedding_adapter,
        vector_store=vector_adapter,
    )

    # Create mock settings
    settings = Settings(
        mcp_server_name="gift-recommendations-dev",
        openai_api_key="mock-key",
        s3_vectors_bucket="mock-bucket",
        s3_vectors_index="mock-index",
    )

    # Create and run MCP server
    mcp = create_mcp_server(
        settings=settings,
        recommendation_service=recommendation_service,
        vector_store=vector_adapter,
    )

    log.info(
        "dev_server_configured",
        adapters=["mock_embedding", "mock_vector_store"],
        sample_gifts=len(SAMPLE_GIFTS),
    )

    # Run with SSE transport on port 3001
    mcp.run(transport="sse", host="127.0.0.1", port=3001)


if __name__ == "__main__":
    main()
