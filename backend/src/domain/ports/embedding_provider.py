"""Port interface for embedding generation operations."""

from abc import ABC, abstractmethod
from typing import Any


class EmbeddingProviderPort(ABC):
    """Abstract interface for generating text embeddings.

    Implementations handle the actual embedding model interactions
    (e.g., OpenAI, Cohere, local models, etc.).
    """

    @abstractmethod
    async def embed_text(self, text: str) -> list[float]:
        """Generate embedding vector for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (1536 dimensions for text-embedding-3-small)
        """
        ...

    @abstractmethod
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embedding vectors for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        ...

    @abstractmethod
    def get_dimensions(self) -> int:
        """Get the dimensionality of embeddings produced by this provider.

        Returns:
            Number of dimensions in embedding vectors
        """
        ...

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Check embedding provider connectivity and status.

        Returns:
            Health status information
        """
        ...
