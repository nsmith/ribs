"""Port interface for vector storage operations."""

from abc import ABC, abstractmethod
from typing import Any

from src.domain.entities.gift import Gift


class VectorStorePort(ABC):
    """Abstract interface for vector storage operations.

    Implementations handle the actual vector database interactions
    (e.g., AWS S3 Vectors, Pinecone, etc.).
    """

    @abstractmethod
    async def search_similar(
        self,
        embedding: list[float],
        limit: int = 5,
        threshold: float = 0.5,
    ) -> list[tuple[Gift, float]]:
        """Search for gifts similar to the given embedding.

        Args:
            embedding: Query vector (1536 dimensions for text-embedding-3-small)
            limit: Maximum number of results to return
            threshold: Minimum similarity score (0.0-1.0)

        Returns:
            List of (Gift, similarity_score) tuples, ordered by descending similarity
        """
        ...

    @abstractmethod
    async def get_by_id(self, gift_id: str) -> Gift | None:
        """Retrieve a gift by its ID.

        Args:
            gift_id: UUID of the gift to retrieve

        Returns:
            Gift if found, None otherwise
        """
        ...

    @abstractmethod
    async def get_by_ids(self, gift_ids: list[str]) -> list[Gift]:
        """Retrieve multiple gifts by their IDs.

        Args:
            gift_ids: List of UUIDs to retrieve

        Returns:
            List of found gifts (missing IDs are silently ignored)
        """
        ...

    @abstractmethod
    async def get_popular(self, limit: int = 5) -> list[tuple[Gift, float]]:
        """Get popular gifts for fallback recommendations.

        Args:
            limit: Maximum number of results to return

        Returns:
            List of (Gift, score) tuples ordered by popularity score
        """
        ...

    @abstractmethod
    async def get_total_count(self) -> int:
        """Get total number of gifts in the catalog.

        Returns:
            Total count of gifts
        """
        ...

    @abstractmethod
    async def upsert(self, gift: Gift) -> None:
        """Insert or update a gift in the vector store.

        Args:
            gift: Gift entity with embedding to store
        """
        ...

    @abstractmethod
    async def find_by_name(self, name: str) -> Gift | None:
        """Find a gift by its exact name.

        Args:
            name: Gift name to search for

        Returns:
            Gift if found, None otherwise
        """
        ...

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Check vector store connectivity and status.

        Returns:
            Health status information
        """
        ...
