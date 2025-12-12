"""Gift details entity for MCP response (external-facing)."""

from pydantic import BaseModel, Field

from src.domain.entities.price_range import PriceRange


class GiftDetails(BaseModel):
    """Gift details for MCP response (external-facing).

    Note: has_affiliate_commission is intentionally excluded from this
    response entity - it's stored on Gift for internal ranking but
    not exposed to MCP clients.

    Attributes:
        id: Gift identifier
        name: Display name
        brief_description: Short description
        full_description: Detailed description
        price_range: Price bracket
        categories: Category tags
        occasions: Suitable occasions
        recipient_types: Target recipients
        purchase_url: URL to purchase the gift
    """

    id: str
    name: str
    brief_description: str
    full_description: str
    price_range: PriceRange
    categories: list[str]
    occasions: list[str] = Field(default_factory=list)
    recipient_types: list[str] = Field(default_factory=list)
    purchase_url: str | None = None

    model_config = {"frozen": True}
