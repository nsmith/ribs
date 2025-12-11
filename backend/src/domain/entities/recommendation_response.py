"""Recommendation response entities."""

from pydantic import BaseModel, Field

from src.domain.entities.price_range import PriceRange
from src.domain.entities.query_context import QueryContext


class GiftRecommendation(BaseModel):
    """A single gift in the recommendation response.

    Attributes:
        id: Gift identifier (for starring)
        name: Display name
        brief_description: Short description
        relevance_score: Similarity score (0.0-1.0)
        price_range: Price bracket
        categories: Category tags
    """

    id: str
    name: str
    brief_description: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    price_range: PriceRange
    categories: list[str]

    model_config = {"frozen": True}


class RecommendationResponse(BaseModel):
    """Output structure from the get_recommendations tool.

    Attributes:
        gifts: Ordered list of recommended gifts
        query_context: Metadata about the search
    """

    gifts: list[GiftRecommendation]
    query_context: QueryContext

    model_config = {"frozen": True}
