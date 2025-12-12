"""Unit tests for embedding operations in EmbeddingService."""

import pytest

from src.domain.services.embedding_service import EmbeddingService


class TestEmbeddingSubtraction:
    """Tests for negative embedding subtraction."""

    def test_subtract_embedding_basic(self) -> None:
        """Test basic embedding subtraction."""
        from unittest.mock import MagicMock

        provider = MagicMock()
        service = EmbeddingService(provider=provider)

        positive = [1.0, 0.5, 0.0]
        negative = [0.5, 0.5, 0.5]

        result = service.subtract_embedding(positive, negative, negative_weight=0.5)

        # 1.0 - 0.5*0.5 = 0.75
        # 0.5 - 0.5*0.5 = 0.25
        # 0.0 - 0.5*0.5 = -0.25
        assert result[0] == pytest.approx(0.75)
        assert result[1] == pytest.approx(0.25)
        assert result[2] == pytest.approx(-0.25)

    def test_subtract_embedding_default_weight(self) -> None:
        """Test embedding subtraction with default weight (0.3)."""
        from unittest.mock import MagicMock

        provider = MagicMock()
        service = EmbeddingService(provider=provider)

        positive = [1.0] * 3
        negative = [1.0] * 3

        result = service.subtract_embedding(positive, negative)

        # 1.0 - 0.3*1.0 = 0.7
        assert all(v == pytest.approx(0.7) for v in result)

    def test_subtract_embedding_zero_weight(self) -> None:
        """Test that zero weight returns original embedding."""
        from unittest.mock import MagicMock

        provider = MagicMock()
        service = EmbeddingService(provider=provider)

        positive = [0.5, 0.3, 0.8]
        negative = [1.0, 1.0, 1.0]

        result = service.subtract_embedding(positive, negative, negative_weight=0.0)

        assert result[0] == pytest.approx(0.5)
        assert result[1] == pytest.approx(0.3)
        assert result[2] == pytest.approx(0.8)

    def test_subtract_embedding_preserves_dimensions(self) -> None:
        """Test that subtraction preserves embedding dimensions."""
        from unittest.mock import MagicMock

        provider = MagicMock()
        service = EmbeddingService(provider=provider)

        positive = [0.1] * 1536
        negative = [0.2] * 1536

        result = service.subtract_embedding(positive, negative)

        assert len(result) == 1536


class TestEmbeddingBlending:
    """Tests for embedding blending."""

    def test_blend_single_embedding_returns_same(self) -> None:
        """Test that blending a single embedding returns it unchanged."""
        from unittest.mock import MagicMock

        provider = MagicMock()
        service = EmbeddingService(provider=provider)

        embedding = [0.5, 0.3, 0.8]
        result = service.blend_embeddings([embedding])

        assert result == embedding

    def test_blend_equal_weights(self) -> None:
        """Test blending with equal weights."""
        from unittest.mock import MagicMock

        provider = MagicMock()
        service = EmbeddingService(provider=provider)

        emb1 = [1.0, 0.0]
        emb2 = [0.0, 1.0]

        result = service.blend_embeddings([emb1, emb2])

        # Equal weights: (1+0)/2=0.5, (0+1)/2=0.5
        assert result[0] == pytest.approx(0.5)
        assert result[1] == pytest.approx(0.5)

    def test_blend_custom_weights(self) -> None:
        """Test blending with custom weights."""
        from unittest.mock import MagicMock

        provider = MagicMock()
        service = EmbeddingService(provider=provider)

        emb1 = [1.0, 0.0]
        emb2 = [0.0, 1.0]

        result = service.blend_embeddings([emb1, emb2], weights=[0.75, 0.25])

        # Weighted: 1*0.75+0*0.25=0.75, 0*0.75+1*0.25=0.25
        assert result[0] == pytest.approx(0.75)
        assert result[1] == pytest.approx(0.25)
