"""Recommendation request entity."""

from pydantic import BaseModel, Field, field_validator


class RecommendationRequest(BaseModel):
    """Input structure for the get_recommendations MCP tool.

    Attributes:
        recipient_description: Description of gift recipient (3-2000 chars)
        past_gifts: Previously given gifts to avoid (optional, truncated to max 20)
        starred_gift_ids: IDs of starred gifts from previous results (optional, truncated to max 20)
        limit: Number of recommendations (3-10, default 5)
    """

    recipient_description: str = Field(..., min_length=3, max_length=2000)
    past_gifts: list[str] = Field(default_factory=list)
    starred_gift_ids: list[str] = Field(default_factory=list)
    limit: int = Field(default=5, ge=3, le=10)

    @field_validator("past_gifts", mode="before")
    @classmethod
    def truncate_past_gifts(cls, v: list[str]) -> list[str]:
        """Truncate past gifts to max 20 items."""
        if not isinstance(v, list):
            return v
        truncated = v[:20]
        return [gift[:200] for gift in truncated]  # Truncate individual items too

    @field_validator("starred_gift_ids", mode="before")
    @classmethod
    def truncate_starred_gift_ids(cls, v: list[str]) -> list[str]:
        """Truncate starred gift IDs to max 20 items."""
        if not isinstance(v, list):
            return v
        return v[:20]

    model_config = {"frozen": True}
