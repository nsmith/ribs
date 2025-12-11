"""Price range enumeration for gifts."""

from enum import Enum


class PriceRange(str, Enum):
    """Price bracket for gift items.

    Values are string-based for JSON serialization compatibility.
    """

    BUDGET = "budget"  # Under $25
    MODERATE = "moderate"  # $25 - $75
    PREMIUM = "premium"  # $75 - $200
    LUXURY = "luxury"  # Over $200

    @property
    def display_range(self) -> str:
        """Get human-readable price range."""
        ranges = {
            PriceRange.BUDGET: "Under $25",
            PriceRange.MODERATE: "$25 - $75",
            PriceRange.PREMIUM: "$75 - $200",
            PriceRange.LUXURY: "Over $200",
        }
        return ranges[self]
