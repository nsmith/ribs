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
    Uses the s3vectors boto3 client for native vector operations.

    See: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3vectors.html
    """

    def __init__(
        self,
        bucket: str,
        index_name: str,
        region: str = "us-east-1",
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
    ) -> None:
        """Initialize the S3 Vectors client.

        Args:
            bucket: S3 vector bucket name
            index_name: Name of the vector index
            region: AWS region
            aws_access_key_id: AWS access key (optional, uses default chain if not provided)
            aws_secret_access_key: AWS secret key (optional, uses default chain if not provided)
        """
        self._bucket = bucket
        self._index_name = index_name
        self._region = region

        # Build client with explicit credentials if provided
        client_kwargs: dict[str, Any] = {"region_name": region}
        if aws_access_key_id and aws_secret_access_key:
            client_kwargs["aws_access_key_id"] = aws_access_key_id
            client_kwargs["aws_secret_access_key"] = aws_secret_access_key

        self._client = boto3.client("s3vectors", **client_kwargs)
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
            threshold: Minimum similarity score (cosine: 0-1, higher is more similar)

        Returns:
            List of (Gift, similarity_score) tuples
        """
        self._log.debug("search_similar", limit=limit, threshold=threshold)

        try:
            response = self._client.query_vectors(
                vectorBucketName=self._bucket,
                indexName=self._index_name,
                queryVector={"float32": embedding},
                topK=limit * 2,  # Fetch extra to filter by threshold
                returnDistance=True,
                returnMetadata=True,
            )

            results: list[tuple[Gift, float]] = []
            distance_metric = response.get("distanceMetric", "cosine")

            for match in response.get("vectors", []):
                # Convert distance to similarity score
                # For cosine distance: similarity = 1 - distance
                # For euclidean: we'd need different conversion
                distance = match.get("distance", 1.0)
                if distance_metric == "cosine":
                    score = 1.0 - distance
                else:
                    # For euclidean, use inverse (smaller distance = higher score)
                    score = 1.0 / (1.0 + distance)

                if score < threshold:
                    continue

                metadata = match.get("metadata", {})
                gift = self._metadata_to_gift(
                    gift_key=match["key"],
                    metadata=metadata,
                    embedding=embedding,  # We don't get embedding back from query
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
        """Retrieve a gift by its ID (key).

        Args:
            gift_id: Key of the gift vector

        Returns:
            Gift if found, None otherwise
        """
        self._log.debug("get_by_id", gift_id=gift_id)

        try:
            response = self._client.get_vectors(
                vectorBucketName=self._bucket,
                indexName=self._index_name,
                keys=[gift_id],
                returnData=True,
                returnMetadata=True,
            )

            vectors = response.get("vectors", [])
            if not vectors:
                return None

            vector_data = vectors[0]
            return self._metadata_to_gift(
                gift_key=vector_data["key"],
                metadata=vector_data.get("metadata", {}),
                embedding=vector_data.get("data", {}).get("float32", []),
            )

        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                return None
            self._log.error("get_by_id_failed", gift_id=gift_id, error=str(e))
            raise

    async def get_by_ids(self, gift_ids: list[str]) -> list[Gift]:
        """Retrieve multiple gifts by their IDs.

        Args:
            gift_ids: List of gift keys

        Returns:
            List of found gifts
        """
        self._log.debug("get_by_ids", count=len(gift_ids))

        if not gift_ids:
            return []

        try:
            response = self._client.get_vectors(
                vectorBucketName=self._bucket,
                indexName=self._index_name,
                keys=gift_ids,
                returnData=True,
                returnMetadata=True,
            )

            gifts: list[Gift] = []
            for vector_data in response.get("vectors", []):
                gift = self._metadata_to_gift(
                    gift_key=vector_data["key"],
                    metadata=vector_data.get("metadata", {}),
                    embedding=vector_data.get("data", {}).get("float32", []),
                )
                gifts.append(gift)

            return gifts

        except ClientError as e:
            self._log.error("get_by_ids_failed", error=str(e))
            raise

    async def get_popular(self, limit: int = 5) -> list[tuple[Gift, float]]:
        """Get popular gifts for fallback recommendations.

        Note: S3 Vectors doesn't support sorting by metadata, so we list
        vectors and sort client-side by popularity_score.

        Args:
            limit: Maximum number of results

        Returns:
            List of (Gift, score) tuples ordered by popularity
        """
        self._log.debug("get_popular", limit=limit)

        try:
            # List vectors and fetch their metadata
            response = self._client.list_vectors(
                vectorBucketName=self._bucket,
                indexName=self._index_name,
                maxResults=100,  # Fetch more to sort by popularity
            )

            # Get full metadata for listed vectors
            keys = [v["key"] for v in response.get("vectors", [])]
            if not keys:
                return []

            vectors_response = self._client.get_vectors(
                vectorBucketName=self._bucket,
                indexName=self._index_name,
                keys=keys,
                returnData=True,
                returnMetadata=True,
            )

            # Convert to gifts and sort by popularity
            gifts_with_scores: list[tuple[Gift, float]] = []
            for vector_data in vectors_response.get("vectors", []):
                metadata = vector_data.get("metadata", {})
                gift = self._metadata_to_gift(
                    gift_key=vector_data["key"],
                    metadata=metadata,
                    embedding=vector_data.get("data", {}).get("float32", []),
                )
                score = metadata.get("popularity_score", 0.5)
                gifts_with_scores.append((gift, score))

            # Sort by popularity descending
            gifts_with_scores.sort(key=lambda x: x[1], reverse=True)

            return gifts_with_scores[:limit]

        except ClientError as e:
            self._log.error("get_popular_failed", error=str(e))
            raise

    async def get_total_count(self) -> int:
        """Get total number of gifts in the catalog.

        Returns:
            Total count
        """
        try:
            response = self._client.get_index(
                vectorBucketName=self._bucket,
                indexName=self._index_name,
            )
            return response.get("vectorCount", 0)

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
            "id": str(gift.id),
            "name": gift.name,
            "brief_description": gift.brief_description,
            "full_description": gift.full_description,
            "price_range": gift.price_range.value,
            "categories": gift.categories,
            "occasions": gift.occasions,
            "recipient_types": gift.recipient_types,
            "popularity_score": gift.popularity_score,
            "purchase_url": gift.purchase_url or "",
            "has_affiliate_commission": gift.has_affiliate_commission,
        }

        try:
            self._client.put_vectors(
                vectorBucketName=self._bucket,
                indexName=self._index_name,
                vectors=[
                    {
                        "key": str(gift.id),
                        "data": {"float32": gift.embedding},
                        "metadata": metadata,
                    }
                ],
            )
            self._log.debug("upsert_complete", gift_id=str(gift.id))

        except ClientError as e:
            self._log.error("upsert_failed", gift_id=str(gift.id), error=str(e))
            raise

    async def find_by_name(self, name: str) -> Gift | None:
        """Find a gift by its exact name.

        Note: S3 Vectors requires listing and filtering client-side,
        or using metadata filter in query. We use list + filter approach.

        Args:
            name: Gift name to search for

        Returns:
            Gift if found, None otherwise
        """
        self._log.debug("find_by_name", name=name)

        try:
            # List all vectors and filter by name
            # For large datasets, this would need pagination
            paginator = self._client.get_paginator("list_vectors")

            for page in paginator.paginate(
                vectorBucketName=self._bucket,
                indexName=self._index_name,
            ):
                keys = [v["key"] for v in page.get("vectors", [])]
                if not keys:
                    continue

                # Get metadata for these vectors
                vectors_response = self._client.get_vectors(
                    vectorBucketName=self._bucket,
                    indexName=self._index_name,
                    keys=keys,
                    returnData=True,
                    returnMetadata=True,
                )

                for vector_data in vectors_response.get("vectors", []):
                    metadata = vector_data.get("metadata", {})
                    if metadata.get("name") == name:
                        return self._metadata_to_gift(
                            gift_key=vector_data["key"],
                            metadata=metadata,
                            embedding=vector_data.get("data", {}).get("float32", []),
                        )

            return None

        except ClientError as e:
            self._log.error("find_by_name_failed", name=name, error=str(e))
            raise

    async def ensure_index_exists(self, dimensions: int = 1536) -> bool:
        """Create the vector bucket and index if they don't exist.

        Args:
            dimensions: Vector dimensions (default 1536 for OpenAI embeddings)

        Returns:
            True if created, False if already existed
        """
        self._log.debug("ensure_index_exists", dimensions=dimensions)

        try:
            # Check if index already exists
            self._client.get_index(
                vectorBucketName=self._bucket,
                indexName=self._index_name,
            )
            self._log.debug("index_already_exists")
            return False

        except ClientError as e:
            if e.response["Error"]["Code"] != "NotFoundException":
                raise

        # Try to create the bucket first (may already exist)
        try:
            self._client.create_vector_bucket(
                vectorBucketName=self._bucket,
            )
            self._log.info("created_vector_bucket", bucket=self._bucket)
        except ClientError as e:
            if e.response["Error"]["Code"] != "ConflictException":
                raise
            self._log.debug("bucket_already_exists")

        # Create the index
        self._client.create_index(
            vectorBucketName=self._bucket,
            indexName=self._index_name,
            dataType="float32",
            dimension=dimensions,
            distanceMetric="cosine",
        )
        self._log.info("created_index", index=self._index_name, dimensions=dimensions)
        return True

    async def health_check(self) -> dict[str, Any]:
        """Check S3 Vectors connectivity and status.

        Returns:
            Health status information
        """
        try:
            response = self._client.get_index(
                vectorBucketName=self._bucket,
                indexName=self._index_name,
            )
            return {
                "status": "healthy",
                "bucket": self._bucket,
                "index": self._index_name,
                "vector_count": response.get("vectorCount", 0),
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
        gift_key: str,
        metadata: dict[str, Any],
        embedding: list[float],
    ) -> Gift:
        """Convert S3 Vectors metadata to Gift entity.

        Args:
            gift_key: Vector key (used as ID if not in metadata)
            metadata: S3 Vectors metadata dict
            embedding: Vector embedding

        Returns:
            Gift entity
        """
        # Use ID from metadata if available, otherwise use key
        gift_id = metadata.get("id", gift_key)
        purchase_url = metadata.get("purchase_url", "")

        # Ensure embedding has correct dimensions (pad if needed for queries)
        if not embedding or len(embedding) != 1536:
            embedding = [0.0] * 1536

        return Gift(
            id=UUID(gift_id) if isinstance(gift_id, str) else gift_id,
            name=metadata.get("name", ""),
            brief_description=metadata.get("brief_description", ""),
            full_description=metadata.get("full_description", ""),
            price_range=PriceRange(metadata.get("price_range", "moderate")),
            categories=metadata.get("categories", []),
            occasions=metadata.get("occasions", []),
            recipient_types=metadata.get("recipient_types", []),
            embedding=embedding,
            popularity_score=metadata.get("popularity_score", 0.5),
            purchase_url=purchase_url if purchase_url else None,
            has_affiliate_commission=metadata.get("has_affiliate_commission", False),
        )
