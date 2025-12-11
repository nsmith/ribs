"""Unit tests for EmbeddingService."""

import pytest

from src.domain.ports.embedding_provider import EmbeddingProviderPort


class TestEmbeddingService:
    """Unit tests for EmbeddingService."""

    @pytest.mark.asyncio
    async def test_embed_text_returns_vector(
        self,
        mock_embedding_provider: EmbeddingProviderPort,
    ) -> None:
        """Test that embed_text returns a 1536-dimensional vector."""
        from src.domain.services.embedding_service import EmbeddingService

        service = EmbeddingService(provider=mock_embedding_provider)

        embedding = await service.embed_text("Test text")

        assert len(embedding) == 1536
        mock_embedding_provider.embed_text.assert_called_once_with("Test text")

    @pytest.mark.asyncio
    async def test_embed_texts_returns_vectors(
        self,
        mock_embedding_provider: EmbeddingProviderPort,
    ) -> None:
        """Test that embed_texts returns list of vectors."""
        from src.domain.services.embedding_service import EmbeddingService

        mock_embedding_provider.embed_texts.return_value = [[0.1] * 1536, [0.2] * 1536]

        service = EmbeddingService(provider=mock_embedding_provider)

        embeddings = await service.embed_texts(["Text 1", "Text 2"])

        assert len(embeddings) == 2
        assert all(len(e) == 1536 for e in embeddings)

    @pytest.mark.asyncio
    async def test_blend_embeddings_returns_averaged_vector(
        self,
        mock_embedding_provider: EmbeddingProviderPort,
    ) -> None:
        """Test that blend_embeddings averages multiple vectors."""
        from src.domain.services.embedding_service import EmbeddingService

        service = EmbeddingService(provider=mock_embedding_provider)

        embedding1 = [1.0] * 1536
        embedding2 = [0.0] * 1536

        blended = service.blend_embeddings([embedding1, embedding2])

        # Average should be 0.5 for each dimension
        assert len(blended) == 1536
        assert abs(blended[0] - 0.5) < 0.001

    @pytest.mark.asyncio
    async def test_blend_embeddings_with_single_vector(
        self,
        mock_embedding_provider: EmbeddingProviderPort,
    ) -> None:
        """Test blending with single vector returns that vector."""
        from src.domain.services.embedding_service import EmbeddingService

        service = EmbeddingService(provider=mock_embedding_provider)

        embedding = [0.5] * 1536

        blended = service.blend_embeddings([embedding])

        assert blended == embedding

    @pytest.mark.asyncio
    async def test_blend_embeddings_with_weights(
        self,
        mock_embedding_provider: EmbeddingProviderPort,
    ) -> None:
        """Test weighted blending of embeddings."""
        from src.domain.services.embedding_service import EmbeddingService

        service = EmbeddingService(provider=mock_embedding_provider)

        embedding1 = [1.0] * 1536
        embedding2 = [0.0] * 1536

        # Weight first embedding higher (0.75) than second (0.25)
        blended = service.blend_embeddings(
            [embedding1, embedding2],
            weights=[0.75, 0.25],
        )

        # Weighted average: 1.0 * 0.75 + 0.0 * 0.25 = 0.75
        assert len(blended) == 1536
        assert abs(blended[0] - 0.75) < 0.001
