"""Shared test fixtures for Gift Recommendations tests."""

from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.domain.entities.gift import Gift
from src.domain.entities.price_range import PriceRange
from src.domain.ports.embedding_provider import EmbeddingProviderPort
from src.domain.ports.vector_store import VectorStorePort


@pytest.fixture
def sample_embedding() -> list[float]:
    """Generate a sample 1536-dimensional embedding."""
    return [0.1] * 1536


@pytest.fixture
def sample_gift(sample_embedding: list[float]) -> Gift:
    """Create a sample gift for testing."""
    return Gift(
        id=uuid4(),
        name="Leather Journal",
        brief_description="Hand-crafted leather journal for notes and sketches",
        full_description="A beautiful hand-crafted leather journal...",
        price_range=PriceRange.MODERATE,
        categories=["stationery", "handmade"],
        occasions=["birthday", "graduation"],
        recipient_types=["friend", "creative"],
        embedding=sample_embedding,
        popularity_score=0.75,
    )


@pytest.fixture
def sample_gifts(sample_embedding: list[float]) -> list[Gift]:
    """Create multiple sample gifts for testing."""
    return [
        Gift(
            id=uuid4(),
            name="Leather Journal",
            brief_description="Hand-crafted leather journal",
            full_description="A beautiful hand-crafted leather journal...",
            price_range=PriceRange.MODERATE,
            categories=["stationery", "handmade"],
            embedding=sample_embedding,
            popularity_score=0.75,
        ),
        Gift(
            id=uuid4(),
            name="Woodworking Kit",
            brief_description="Beginner woodworking tool set",
            full_description="Complete starter kit for woodworking...",
            price_range=PriceRange.PREMIUM,
            categories=["tools", "crafts"],
            embedding=sample_embedding,
            popularity_score=0.8,
        ),
        Gift(
            id=uuid4(),
            name="Vinyl Record Player",
            brief_description="Retro-style turntable",
            full_description="Classic vinyl record player...",
            price_range=PriceRange.PREMIUM,
            categories=["electronics", "music"],
            embedding=sample_embedding,
            popularity_score=0.7,
        ),
    ]


@pytest.fixture
def mock_embedding_provider() -> EmbeddingProviderPort:
    """Create a mock embedding provider."""
    mock = MagicMock(spec=EmbeddingProviderPort)
    mock.embed_text = AsyncMock(return_value=[0.1] * 1536)
    mock.embed_texts = AsyncMock(return_value=[[0.1] * 1536])
    mock.get_dimensions.return_value = 1536
    mock.health_check = AsyncMock(return_value={"status": "healthy"})
    return mock


@pytest.fixture
def mock_vector_store(sample_gifts: list[Gift]) -> VectorStorePort:
    """Create a mock vector store."""
    mock = MagicMock(spec=VectorStorePort)
    mock.search_similar = AsyncMock(
        return_value=[(gift, 0.9 - i * 0.1) for i, gift in enumerate(sample_gifts)]
    )
    mock.get_by_id = AsyncMock(return_value=sample_gifts[0])
    mock.get_by_ids = AsyncMock(return_value=sample_gifts)
    mock.get_popular = AsyncMock(
        return_value=[(gift, 0.5) for gift in sample_gifts]
    )
    mock.get_total_count = AsyncMock(return_value=100)
    mock.health_check = AsyncMock(return_value={"status": "healthy"})
    return mock
