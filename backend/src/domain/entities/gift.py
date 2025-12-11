"""Gift entity representing a recommendation item."""

from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from src.domain.entities.price_range import PriceRange


class Gift(BaseModel):
    """Core gift entity stored in S3 Vectors with its embedding.

    Attributes:
        id: Unique identifier (UUID v4)
        name: Display name (max 100 chars)
        brief_description: Short description for list view (max 200 chars)
        full_description: Detailed description for expanded view (max 2000 chars)
        price_range: Typical price bracket
        categories: Category tags (at least one required)
        occasions: Suitable occasions (optional)
        recipient_types: Target recipients (optional)
        embedding: 1536-dimensional vector from text-embedding-3-small
        popularity_score: Fallback ranking metric (0.0-1.0)
    """

    id: UUID
    name: str = Field(..., min_length=1, max_length=100)
    brief_description: str = Field(..., min_length=1, max_length=200)
    full_description: str = Field(..., min_length=1, max_length=2000)
    price_range: PriceRange
    categories: list[str] = Field(..., min_length=1)
    occasions: list[str] = Field(default_factory=list)
    recipient_types: list[str] = Field(default_factory=list)
    embedding: list[float] = Field(..., min_length=1536, max_length=1536)
    popularity_score: float = Field(default=0.5, ge=0.0, le=1.0)

    @field_validator("categories")
    @classmethod
    def validate_categories(cls, v: list[str]) -> list[str]:
        """Ensure at least one category is provided."""
        if not v:
            raise ValueError("At least one category is required")
        return v

    @field_validator("embedding")
    @classmethod
    def validate_embedding(cls, v: list[float]) -> list[float]:
        """Ensure embedding has exactly 1536 dimensions."""
        if len(v) != 1536:
            raise ValueError(f"Embedding must have 1536 dimensions, got {len(v)}")
        return v

    def get_embedding_text(self) -> str:
        """Get concatenated text used for embedding generation."""
        return f"{self.name}. {self.brief_description}. Categories: {', '.join(self.categories)}"

    model_config = {"frozen": True}
