"""Unit tests for the get_gift_details MCP tool handler."""

import pytest
from unittest.mock import AsyncMock
from uuid import UUID

from src.domain.entities.gift import Gift
from src.domain.entities.price_range import PriceRange
from src.domain.ports.vector_store import VectorStorePort

# Fixed UUID for testing
TEST_UUID = UUID("12345678-1234-1234-1234-123456789012")


class TestGetGiftDetailsTool:
    """Tests for the get_gift_details tool handler."""

    @pytest.fixture
    def sample_gift(self) -> Gift:
        """Create a sample gift with full details."""
        return Gift(
            id=TEST_UUID,
            name="Leather Journal",
            brief_description="Hand-crafted leather journal",
            full_description="A beautiful hand-crafted leather journal with 200 pages of acid-free paper. Perfect for writers, artists, or anyone who appreciates fine craftsmanship.",
            price_range=PriceRange.MODERATE,
            categories=["stationery", "handmade"],
            occasions=["birthday", "graduation", "christmas"],
            recipient_types=["writers", "professionals", "students"],
            embedding=[0.1] * 1536,
            popularity_score=0.85,
            purchase_url="https://example.com/leather-journal",
            has_affiliate_commission=True,
        )

    @pytest.mark.asyncio
    async def test_tool_returns_gift_details(
        self,
        mock_vector_store: VectorStorePort,
        sample_gift: Gift,
    ) -> None:
        """Tool should return full gift details."""
        from src.adapters.mcp.tools.get_gift_details import get_gift_details_handler

        mock_vector_store.get_by_id = AsyncMock(return_value=sample_gift)

        result = await get_gift_details_handler(
            gift_id=str(TEST_UUID),
            vector_store=mock_vector_store,
        )

        assert "structuredContent" in result
        details = result["structuredContent"]
        assert details["id"] == str(TEST_UUID)
        assert details["name"] == "Leather Journal"
        assert details["full_description"] == sample_gift.full_description
        assert details["purchase_url"] == "https://example.com/leather-journal"
        assert details["has_affiliate_commission"] is True

    @pytest.mark.asyncio
    async def test_tool_includes_occasions_and_recipient_types(
        self,
        mock_vector_store: VectorStorePort,
        sample_gift: Gift,
    ) -> None:
        """Tool should include occasions and recipient types."""
        from src.adapters.mcp.tools.get_gift_details import get_gift_details_handler

        mock_vector_store.get_by_id = AsyncMock(return_value=sample_gift)

        result = await get_gift_details_handler(
            gift_id=str(TEST_UUID),
            vector_store=mock_vector_store,
        )

        details = result["structuredContent"]
        assert details["occasions"] == ["birthday", "graduation", "christmas"]
        assert details["recipient_types"] == ["writers", "professionals", "students"]

    @pytest.mark.asyncio
    async def test_tool_content_is_human_readable(
        self,
        mock_vector_store: VectorStorePort,
        sample_gift: Gift,
    ) -> None:
        """Tool should provide human-readable content."""
        from src.adapters.mcp.tools.get_gift_details import get_gift_details_handler

        mock_vector_store.get_by_id = AsyncMock(return_value=sample_gift)

        result = await get_gift_details_handler(
            gift_id=str(TEST_UUID),
            vector_store=mock_vector_store,
        )

        assert "content" in result
        content = result["content"]
        assert "Leather Journal" in content
        assert "hand-crafted" in content.lower()

    @pytest.mark.asyncio
    async def test_tool_returns_not_found_error(
        self,
        mock_vector_store: VectorStorePort,
    ) -> None:
        """Tool should return error when gift not found."""
        from src.adapters.mcp.tools.get_gift_details import get_gift_details_handler

        mock_vector_store.get_by_id = AsyncMock(return_value=None)

        result = await get_gift_details_handler(
            gift_id="nonexistent-id",
            vector_store=mock_vector_store,
        )

        assert "error" in result
        assert result["error"] == "Gift not found"
        assert result["gift_id"] == "nonexistent-id"

    @pytest.mark.asyncio
    async def test_tool_calls_vector_store_with_id(
        self,
        mock_vector_store: VectorStorePort,
        sample_gift: Gift,
    ) -> None:
        """Tool should call vector store with the gift ID."""
        from src.adapters.mcp.tools.get_gift_details import get_gift_details_handler

        mock_vector_store.get_by_id = AsyncMock(return_value=sample_gift)

        await get_gift_details_handler(
            gift_id=str(TEST_UUID),
            vector_store=mock_vector_store,
        )

        mock_vector_store.get_by_id.assert_called_once_with(str(TEST_UUID))

    @pytest.mark.asyncio
    async def test_tool_handles_empty_optional_fields(
        self,
        mock_vector_store: VectorStorePort,
    ) -> None:
        """Tool should handle gifts with empty optional fields."""
        from src.adapters.mcp.tools.get_gift_details import get_gift_details_handler

        gift_without_extras = Gift(
            id=TEST_UUID,
            name="Simple Gift",
            brief_description="A simple gift",
            full_description="A simple gift without many extras.",
            price_range=PriceRange.BUDGET,
            categories=["general"],
            embedding=[0.1] * 1536,
        )

        mock_vector_store.get_by_id = AsyncMock(return_value=gift_without_extras)

        result = await get_gift_details_handler(
            gift_id=str(TEST_UUID),
            vector_store=mock_vector_store,
        )

        details = result["structuredContent"]
        assert details["occasions"] == []
        assert details["recipient_types"] == []
        assert details["purchase_url"] is None
        assert details["has_affiliate_commission"] is False
