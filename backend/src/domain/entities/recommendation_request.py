"""Recommendation request entity."""

from pydantic import BaseModel, Field, field_validator


class RecommendationRequest(BaseModel):
    """Input structure for the get_recommendations MCP tool.

    Attributes:
        keywords: Search keywords for gift matching (3-500 chars)
        negative_keywords: Keywords to avoid in results (optional, max 500 chars)
        limit: Number of recommendations (3-10, default 5)
    """

    keywords: str = Field(..., min_length=3, max_length=500)
    negative_keywords: str | None = Field(default=None, max_length=500)
    limit: int = Field(default=5, ge=3, le=10)

    model_config = {"frozen": True}
