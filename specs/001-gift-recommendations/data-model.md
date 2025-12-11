# Data Model: Gift Recommendation MCP Server

**Feature**: 001-gift-recommendations
**Date**: 2025-12-11
**Phase**: 1 - Design

## Entity Definitions

### Gift

The core recommendation item stored in S3 Vectors with its embedding.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string (UUID) | Yes | Unique identifier for the gift |
| `name` | string | Yes | Display name (max 100 chars) |
| `brief_description` | string | Yes | Short description for list view (max 200 chars) |
| `full_description` | string | Yes | Detailed description for expanded view (max 2000 chars) |
| `price_range` | PriceRange | Yes | Typical price bracket |
| `categories` | list[string] | Yes | Category tags (e.g., "electronics", "handmade", "experiences") |
| `occasions` | list[string] | No | Suitable occasions (e.g., "birthday", "holiday", "anniversary") |
| `recipient_types` | list[string] | No | Target recipients (e.g., "parent", "friend", "coworker") |
| `embedding` | list[float] | Yes | 1536-dimensional vector from text-embedding-3-small |
| `popularity_score` | float | No | Fallback ranking metric (0.0-1.0) |

**Validation Rules**:
- `id` must be valid UUID v4
- `name` must be non-empty, max 100 characters
- `brief_description` must be non-empty, max 200 characters
- `categories` must contain at least one tag
- `embedding` must have exactly 1536 dimensions

**Embedding Source**: Concatenation of `name`, `brief_description`, and `categories` for semantic matching.

---

### PriceRange (Enum)

| Value | Description | Approximate Range |
|-------|-------------|-------------------|
| `budget` | Budget-friendly | Under $25 |
| `moderate` | Mid-range | $25 - $75 |
| `premium` | Higher-end | $75 - $200 |
| `luxury` | Luxury items | Over $200 |

---

### RecipientProfile (Transient)

Constructed at query time from the user's description. Not persisted.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `description` | string | Yes | Raw user input (3-2000 chars) |
| `embedding` | list[float] | Yes | Generated embedding of description |
| `past_gifts` | list[string] | No | Descriptions of previously given gifts |
| `past_gift_embeddings` | list[list[float]] | No | Embeddings of past gifts (for exclusion) |

**Validation Rules**:
- `description` minimum 3 characters, maximum 2000 characters
- `past_gifts` maximum 20 items, each max 200 characters

---

### RecommendationRequest

Input structure for the `get_recommendations` MCP tool.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `recipient_description` | string | Yes | - | Description of gift recipient |
| `past_gifts` | list[string] | No | [] | Previously given gifts to avoid |
| `starred_gift_ids` | list[string] | No | [] | IDs of starred gifts from previous results |
| `limit` | int | No | 5 | Number of recommendations (3-10) |

**Validation Rules**:
- `recipient_description` must be 3-2000 characters
- `limit` must be between 3 and 10 inclusive
- `starred_gift_ids` maximum 20 items
- Invalid `starred_gift_ids` silently ignored

---

### RecommendationResponse

Output structure from the `get_recommendations` tool.

| Field | Type | Description |
|-------|------|-------------|
| `gifts` | list[GiftRecommendation] | Ordered list of recommended gifts |
| `query_context` | QueryContext | Metadata about the search |

---

### GiftRecommendation

A single gift in the recommendation response.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Gift identifier (for starring) |
| `name` | string | Display name |
| `brief_description` | string | Short description |
| `relevance_score` | float | Similarity score (0.0-1.0) |
| `price_range` | PriceRange | Price bracket |
| `categories` | list[string] | Category tags |

**Note**: `full_description` and additional details available via `get_gift_details` tool.

---

### QueryContext

Metadata about the recommendation query.

| Field | Type | Description |
|-------|------|-------------|
| `total_searched` | int | Number of gifts in catalog |
| `above_threshold` | int | Gifts meeting relevance threshold |
| `starred_boost_applied` | bool | Whether starred gifts influenced results |
| `fallback_used` | bool | Whether popular fallbacks were included |

---

### GiftDetails

Extended information for a single gift (returned by `get_gift_details` tool).

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Gift identifier |
| `name` | string | Display name |
| `full_description` | string | Detailed description |
| `price_range` | PriceRange | Price bracket |
| `categories` | list[string] | Category tags |
| `occasions` | list[string] | Suitable occasions |
| `recipient_types` | list[string] | Target recipient types |
| `purchasing_guidance` | string | General advice on where to find |

---

## Relationships

```text
┌─────────────────────┐
│ RecommendationRequest│
│                     │
│ recipient_description├──────► RecipientProfile (transient)
│ past_gifts          │              │
│ starred_gift_ids────┼──────────────┼───► Gift (lookup in S3 Vectors)
│ limit               │              │
└─────────────────────┘              │
                                     ▼
                              ┌─────────────┐
                              │ S3 Vectors  │
                              │ Similarity  │
                              │ Search      │
                              └──────┬──────┘
                                     │
                                     ▼
                        ┌────────────────────────┐
                        │ RecommendationResponse │
                        │                        │
                        │ gifts: [GiftRec...]    │
                        │ query_context          │
                        └────────────────────────┘
```

## State Transitions

This system is stateless. Each request is independent:

1. **Request Received** → Validate inputs
2. **Profile Created** → Generate embeddings for description
3. **Starred Lookup** → Fetch starred gift embeddings (if any)
4. **Vector Search** → Query S3 Vectors with combined embedding
5. **Filter & Rank** → Apply past gift exclusion, relevance threshold
6. **Response Built** → Format as structured content

No state persists between requests. Starred gift IDs reference gifts that exist in S3 Vectors; the client is responsible for tracking which gifts were starred.

## Storage Mapping (S3 Vectors)

**Index Configuration**:
- Bucket: `ribs-gift-recommendations` (configurable)
- Index: `gifts`
- Dimensions: 1536
- Metric: Cosine similarity

**Vector Record Structure**:
```json
{
  "id": "uuid-here",
  "vector": [0.123, -0.456, ...],
  "metadata": {
    "name": "Leather Journal",
    "brief_description": "Hand-crafted leather journal...",
    "full_description": "...",
    "price_range": "moderate",
    "categories": ["stationery", "handmade"],
    "occasions": ["birthday", "graduation"],
    "recipient_types": ["friend", "creative"],
    "popularity_score": 0.75
  }
}
```
