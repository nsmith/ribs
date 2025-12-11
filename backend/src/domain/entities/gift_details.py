"""Gift details entity for expanded view."""

from pydantic import BaseModel, Field

from src.domain.entities.price_range import PriceRange


class GiftDetails(BaseModel):
    """Full gift details for expanded view.

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
        has_affiliate_commission: Whether purchase generates affiliate commission
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
    has_affiliate_commission: bool = False

    model_config = {"frozen": True}
