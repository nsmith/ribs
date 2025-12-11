"""MCP tool handler for getting gift details."""

from typing import Any

from src.domain.entities.gift import Gift
from src.domain.entities.gift_details import GiftDetails
from src.domain.ports.vector_store import VectorStorePort


def _gift_to_details(gift: Gift) -> GiftDetails:
    """Convert a Gift entity to GiftDetails."""
    return GiftDetails(
        id=str(gift.id),
        name=gift.name,
        brief_description=gift.brief_description,
        full_description=gift.full_description,
        price_range=gift.price_range,
        categories=gift.categories,
        occasions=gift.occasions,
        recipient_types=gift.recipient_types,
        purchase_url=gift.purchase_url,
        has_affiliate_commission=gift.has_affiliate_commission,
    )


def _format_human_readable(details: GiftDetails) -> str:
    """Format gift details as human-readable text."""
    lines = [
        f"**{details.name}**",
        "",
        details.full_description,
        "",
        f"**Price:** {details.price_range.value}",
        f"**Categories:** {', '.join(details.categories)}",
    ]

    if details.occasions:
        lines.append(f"**Great for:** {', '.join(details.occasions)}")

    if details.recipient_types:
        lines.append(f"**Perfect for:** {', '.join(details.recipient_types)}")

    if details.purchase_url:
        lines.append(f"**Where to buy:** {details.purchase_url}")

    return "\n".join(lines)


async def get_gift_details_handler(
    gift_id: str,
    vector_store: VectorStorePort,
) -> dict[str, Any]:
    """Get detailed information about a specific gift.

    Args:
        gift_id: The unique identifier of the gift.
        vector_store: Vector store for retrieving gift data.

    Returns:
        MCP-formatted response with gift details or error.
    """
    gift = await vector_store.get_by_id(gift_id)

    if gift is None:
        return {
            "error": "Gift not found",
            "gift_id": gift_id,
        }

    details = _gift_to_details(gift)

    return {
        "structuredContent": details.model_dump(),
        "content": _format_human_readable(details),
        "_meta": {
            "gift_id": gift_id,
        },
    }
