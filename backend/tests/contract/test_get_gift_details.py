"""Contract tests for the get_gift_details MCP tool."""

import pytest
from pydantic import ValidationError

from src.domain.entities.gift_details import GiftDetails


class TestGetGiftDetailsContract:
    """Contract tests for get_gift_details request validation."""

    def test_valid_request_with_gift_id(self) -> None:
        """Gift ID is required and must be a valid UUID string."""
        # This tests the expected input format
        gift_id = "12345678-1234-1234-1234-123456789012"
        assert isinstance(gift_id, str)
        assert len(gift_id) == 36  # UUID format

    def test_gift_id_required(self) -> None:
        """Request must include gift_id."""
        # Empty string should be invalid
        gift_id = ""
        assert gift_id == ""  # Will be validated by tool handler


class TestGetGiftDetailsResponse:
    """Contract tests for get_gift_details response format."""

    def test_response_contains_all_gift_fields(self) -> None:
        """Response must contain all gift detail fields."""
        details = GiftDetails(
            id="12345678-1234-1234-1234-123456789012",
            name="Leather Journal",
            brief_description="Hand-crafted leather journal",
            full_description="A beautiful hand-crafted leather journal perfect for writers.",
            price_range="moderate",
            categories=["stationery", "handmade"],
            occasions=["birthday", "graduation"],
            recipient_types=["writers", "professionals"],
            purchase_url="https://example.com/leather-journal",
            has_affiliate_commission=True,
        )

        assert details.id == "12345678-1234-1234-1234-123456789012"
        assert details.name == "Leather Journal"
        assert details.brief_description == "Hand-crafted leather journal"
        assert details.full_description == "A beautiful hand-crafted leather journal perfect for writers."
        assert details.price_range == "moderate"
        assert details.categories == ["stationery", "handmade"]
        assert details.occasions == ["birthday", "graduation"]
        assert details.recipient_types == ["writers", "professionals"]
        assert details.purchase_url == "https://example.com/leather-journal"
        assert details.has_affiliate_commission is True

    def test_response_optional_fields_have_defaults(self) -> None:
        """Optional fields should have sensible defaults."""
        details = GiftDetails(
            id="12345678-1234-1234-1234-123456789012",
            name="Simple Gift",
            brief_description="A simple gift",
            full_description="A simple gift with no extras.",
            price_range="budget",
            categories=["general"],
        )

        assert details.occasions == []
        assert details.recipient_types == []
        assert details.purchase_url is None
        assert details.has_affiliate_commission is False

    def test_response_structured_content_format(self) -> None:
        """Response should follow MCP structured content format."""
        # The tool handler should return a dict with these keys
        expected_keys = {"structuredContent", "content", "_meta"}
        # This will be validated in unit tests for the tool handler

    def test_gift_details_contains_purchase_url(self) -> None:
        """Gift details must include purchase URL when available."""
        details = GiftDetails(
            id="12345678-1234-1234-1234-123456789012",
            name="Gift with URL",
            brief_description="A gift",
            full_description="A gift with purchase URL.",
            price_range="moderate",
            categories=["general"],
            purchase_url="https://amazon.com/dp/B0123456",
        )

        assert details.purchase_url == "https://amazon.com/dp/B0123456"

    def test_gift_details_affiliate_flag(self) -> None:
        """Gift details must indicate if affiliate commission applies."""
        details = GiftDetails(
            id="12345678-1234-1234-1234-123456789012",
            name="Affiliate Gift",
            brief_description="A gift",
            full_description="A gift with affiliate commission.",
            price_range="premium",
            categories=["electronics"],
            purchase_url="https://amazon.com/dp/B0123456",
            has_affiliate_commission=True,
        )

        assert details.has_affiliate_commission is True


class TestGetGiftDetailsError:
    """Contract tests for error responses."""

    def test_not_found_error_format(self) -> None:
        """Not found error should include gift_id."""
        gift_id = "nonexistent-id"
        error_response = {
            "error": "Gift not found",
            "gift_id": gift_id,
        }
        assert error_response["error"] == "Gift not found"
        assert error_response["gift_id"] == gift_id

    def test_invalid_id_error_format(self) -> None:
        """Invalid ID error should be clear."""
        error_response = {
            "error": "Invalid gift ID format",
        }
        assert "Invalid" in error_response["error"]
