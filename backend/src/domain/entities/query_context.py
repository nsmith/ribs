"""Query context entity for recommendation metadata."""

from pydantic import BaseModel


class QueryContext(BaseModel):
    """Metadata about the recommendation query.

    Attributes:
        total_searched: Number of gifts in catalog
        above_threshold: Gifts meeting relevance threshold
        starred_boost_applied: Whether starred gifts influenced results
        fallback_used: Whether popular fallbacks were included
    """

    total_searched: int
    above_threshold: int
    starred_boost_applied: bool = False
    fallback_used: bool = False

    model_config = {"frozen": True}
