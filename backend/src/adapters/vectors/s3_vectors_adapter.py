"""AWS S3 Vectors adapter implementing VectorStorePort."""

from typing import Any
from uuid import UUID

import boto3
import structlog
from botocore.exceptions import ClientError

from src.domain.entities.gift import Gift
from src.domain.entities.price_range import PriceRange
from src.domain.ports.vector_store import VectorStorePort

logger = structlog.get_logger()


class S3VectorsAdapter(VectorStorePort):
    """AWS S3 Vectors storage adapter for gift embeddings.

    Implements VectorStorePort for similarity search and gift retrieval.
    Uses S3 Vectors API for native vector operations.
    """

    def __init__(
        self,
        bucket: str,
        index_name: str,
        region: str = "us-east-1",
    ) -> None:
        """Initialize the S3 Vectors client.

        Args:
            bucket: S3 bucket name with vectors enabled
            index_name: Name of the vector index
            region: AWS region
        """
        self._bucket = bucket
        self._index_name = index_name
        self._region = region
        self._client = boto3.client("s3", region_name=region)
        self._log = logger.bind(adapter="s3_vectors", bucket=bucket, index=index_name)

    async def search_similar(
        self,
        embedding: list[float],
        limit: int = 5,
        threshold: float = 0.5,
    ) -> list[tuple[Gift, float]]:
        """Search for gifts similar to the given embedding.

        Args:
            embedding: Query vector (1536 dimensions)
            limit: Maximum number of results
            threshold: Minimum similarity score

        Returns:
            List of (Gift, similarity_score) tuples
        """
        self._log.debug("search_similar", limit=limit, threshold=threshold)

        try:
            # Note: This is a placeholder for S3 Vectors API
            # The actual API may differ - this follows expected patterns
            response = self._client.query_vectors(
                Bucket=self._bucket,
                IndexName=self._index_name,
                QueryVector=embedding,
                TopK=limit * 2,  # Fetch extra to filter by threshold
            )

            results: list[tuple[Gift, float]] = []
            for match in response.get("Matches", []):
                score = match.get("Score", 0.0)
                if score < threshold:
                    continue

                metadata = match.get("Metadata", {})
                gift = self._metadata_to_gift(
                    gift_id=match["Id"],
                    metadata=metadata,
                    embedding=match.get("Vector", embedding),
                )
                results.append((gift, score))

                if len(results) >= limit:
                    break

            self._log.debug("search_complete", results_count=len(results))
            return results

        except ClientError as e:
            self._log.error("search_failed", error=str(e))
            raise

    async def get_by_id(self, gift_id: str) -> Gift | None:
        """Retrieve a gift by its ID.

        Args:
            gift_id: UUID of the gift

        Returns:
            Gift if found, None otherwise
        """
        self._log.debug("get_by_id", gift_id=gift_id)

        try:
            response = self._client.get_vector(
                Bucket=self._bucket,
                IndexName=self._index_name,
                Id=gift_id,
            )

            if not response.get("Vector"):
                return None

            return self._metadata_to_gift(
                gift_id=gift_id,
                metadata=response.get("Metadata", {}),
                embedding=response["Vector"],
            )

        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return None
            self._log.error("get_by_id_failed", gift_id=gift_id, error=str(e))
            raise

    async def get_by_ids(self, gift_ids: list[str]) -> list[Gift]:
        """Retrieve multiple gifts by their IDs.

        Args:
            gift_ids: List of UUIDs

        Returns:
            List of found gifts
        """
        self._log.debug("get_by_ids", count=len(gift_ids))

        gifts: list[Gift] = []
        for gift_id in gift_ids:
            gift = await self.get_by_id(gift_id)
            if gift:
                gifts.append(gift)

        return gifts

    async def get_popular(self, limit: int = 5) -> list[Gift]:
        """Get popular gifts for fallback recommendations.

        Args:
            limit: Maximum number of results

        Returns:
            List of gifts ordered by popularity
        """
        self._log.debug("get_popular", limit=limit)

        try:
            # Query with popularity score filter
            # This may need adjustment based on actual S3 Vectors API
            response = self._client.list_vectors(
                Bucket=self._bucket,
                IndexName=self._index_name,
                MaxResults=limit,
                SortBy="popularity_score",
                SortOrder="DESCENDING",
            )

            gifts: list[Gift] = []
            for item in response.get("Vectors", []):
                gift = self._metadata_to_gift(
                    gift_id=item["Id"],
                    metadata=item.get("Metadata", {}),
                    embedding=item.get("Vector", [0.0] * 1536),
                )
                gifts.append(gift)

            return gifts

        except ClientError as e:
            self._log.error("get_popular_failed", error=str(e))
            raise

    async def get_total_count(self) -> int:
        """Get total number of gifts in the catalog.

        Returns:
            Total count
        """
        try:
            response = self._client.describe_index(
                Bucket=self._bucket,
                IndexName=self._index_name,
            )
            return response.get("VectorCount", 0)

        except ClientError as e:
            self._log.error("get_total_count_failed", error=str(e))
            raise

    async def upsert(self, gift: Gift) -> None:
        """Insert or update a gift in the vector store.

        Args:
            gift: Gift entity with embedding
        """
        self._log.debug("upsert", gift_id=str(gift.id))

        metadata = {
            "name": gift.name,
            "brief_description": gift.brief_description,
            "full_description": gift.full_description,
            "price_range": gift.price_range.value,
            "categories": gift.categories,
            "occasions": gift.occasions,
            "recipient_types": gift.recipient_types,
            "popularity_score": gift.popularity_score,
        }

        try:
            self._client.put_vector(
                Bucket=self._bucket,
                IndexName=self._index_name,
                Id=str(gift.id),
                Vector=gift.embedding,
                Metadata=metadata,
            )
            self._log.debug("upsert_complete", gift_id=str(gift.id))

        except ClientError as e:
            self._log.error("upsert_failed", gift_id=str(gift.id), error=str(e))
            raise

    async def health_check(self) -> dict[str, Any]:
        """Check S3 Vectors connectivity and status.

        Returns:
            Health status information
        """
        try:
            response = self._client.describe_index(
                Bucket=self._bucket,
                IndexName=self._index_name,
            )
            return {
                "status": "healthy",
                "bucket": self._bucket,
                "index": self._index_name,
                "vector_count": response.get("VectorCount", 0),
            }
        except ClientError as e:
            self._log.error("health_check_failed", error=str(e))
            return {
                "status": "unhealthy",
                "bucket": self._bucket,
                "index": self._index_name,
                "error": str(e),
            }

    def _metadata_to_gift(
        self,
        gift_id: str,
        metadata: dict[str, Any],
        embedding: list[float],
    ) -> Gift:
        """Convert S3 Vectors metadata to Gift entity.

        Args:
            gift_id: Gift UUID string
            metadata: S3 Vectors metadata dict
            embedding: Vector embedding

        Returns:
            Gift entity
        """
        return Gift(
            id=UUID(gift_id),
            name=metadata.get("name", ""),
            brief_description=metadata.get("brief_description", ""),
            full_description=metadata.get("full_description", ""),
            price_range=PriceRange(metadata.get("price_range", "moderate")),
            categories=metadata.get("categories", []),
            occasions=metadata.get("occasions", []),
            recipient_types=metadata.get("recipient_types", []),
            embedding=embedding,
            popularity_score=metadata.get("popularity_score", 0.5),
        )
