"""Embedding service for text vectorization."""

from src.domain.ports.embedding_provider import EmbeddingProviderPort


class EmbeddingService:
    """Service for creating and manipulating text embeddings."""

    def __init__(self, provider: EmbeddingProviderPort) -> None:
        """Initialize the embedding service.

        Args:
            provider: The embedding provider port implementation.
        """
        self._provider = provider

    async def embed_text(self, text: str) -> list[float]:
        """Embed a single text string.

        Args:
            text: The text to embed.

        Returns:
            A 1536-dimensional embedding vector.
        """
        return await self._provider.embed_text(text)

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple text strings.

        Args:
            texts: The texts to embed.

        Returns:
            List of 1536-dimensional embedding vectors.
        """
        return await self._provider.embed_texts(texts)

    def blend_embeddings(
        self,
        embeddings: list[list[float]],
        weights: list[float] | None = None,
    ) -> list[float]:
        """Blend multiple embeddings into a single vector.

        Args:
            embeddings: List of embedding vectors to blend.
            weights: Optional weights for each embedding. If None, uses equal weights.

        Returns:
            A blended embedding vector.
        """
        if len(embeddings) == 1:
            return embeddings[0]

        if weights is None:
            weights = [1.0 / len(embeddings)] * len(embeddings)

        dimension = len(embeddings[0])
        blended = [0.0] * dimension

        for embedding, weight in zip(embeddings, weights):
            for i in range(dimension):
                blended[i] += embedding[i] * weight

        return blended
