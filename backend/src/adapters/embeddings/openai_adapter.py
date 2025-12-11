"""OpenAI embedding adapter implementing EmbeddingProviderPort."""

import structlog
from openai import AsyncOpenAI

from src.domain.ports.embedding_provider import EmbeddingProviderPort

logger = structlog.get_logger()


class OpenAIEmbeddingAdapter(EmbeddingProviderPort):
    """OpenAI embedding provider using text-embedding-3-small model.

    Implements EmbeddingProviderPort for generating 1536-dimensional embeddings.
    """

    MODEL = "text-embedding-3-small"
    DIMENSIONS = 1536

    def __init__(self, api_key: str) -> None:
        """Initialize the OpenAI client.

        Args:
            api_key: OpenAI API key
        """
        self._client = AsyncOpenAI(api_key=api_key)
        self._log = logger.bind(adapter="openai_embedding")

    async def embed_text(self, text: str) -> list[float]:
        """Generate embedding vector for a single text.

        Args:
            text: Text to embed

        Returns:
            1536-dimensional embedding vector
        """
        self._log.debug("embedding_single_text", text_length=len(text))

        response = await self._client.embeddings.create(
            model=self.MODEL,
            input=text,
        )

        embedding = response.data[0].embedding
        self._log.debug("embedding_complete", dimensions=len(embedding))

        return embedding

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embedding vectors for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of 1536-dimensional embedding vectors
        """
        if not texts:
            return []

        self._log.debug("embedding_batch", count=len(texts))

        response = await self._client.embeddings.create(
            model=self.MODEL,
            input=texts,
        )

        # Sort by index to maintain order
        sorted_data = sorted(response.data, key=lambda x: x.index)
        embeddings = [item.embedding for item in sorted_data]

        self._log.debug("batch_embedding_complete", count=len(embeddings))

        return embeddings

    def get_dimensions(self) -> int:
        """Get the dimensionality of embeddings.

        Returns:
            1536 for text-embedding-3-small
        """
        return self.DIMENSIONS

    async def health_check(self) -> dict[str, object]:
        """Check OpenAI API connectivity.

        Returns:
            Health status with model and connectivity info
        """
        try:
            # Simple embedding to verify connectivity
            await self._client.embeddings.create(
                model=self.MODEL,
                input="health check",
            )
            return {
                "status": "healthy",
                "model": self.MODEL,
                "dimensions": self.DIMENSIONS,
            }
        except Exception as e:
            self._log.error("health_check_failed", error=str(e))
            return {
                "status": "unhealthy",
                "model": self.MODEL,
                "error": str(e),
            }
