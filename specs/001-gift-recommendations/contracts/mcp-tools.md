# MCP Tool Contracts: Gift Recommendation Server

**Feature**: 001-gift-recommendations
**Date**: 2025-12-11
**Protocol**: Model Context Protocol (MCP)

## Tools

### get_recommendations

Get personalized gift recommendations based on recipient description.

**Tool Name**: `get_recommendations`

**Description**: Returns gift recommendations based on who the recipient is, optionally refined by starred gifts from previous results.

**Input Schema** (JSON Schema):
```json
{
  "type": "object",
  "properties": {
    "recipient_description": {
      "type": "string",
      "description": "Description of the gift recipient including interests, age, relationship, etc.",
      "minLength": 3,
      "maxLength": 2000
    },
    "past_gifts": {
      "type": "array",
      "items": {
        "type": "string",
        "maxLength": 200
      },
      "maxItems": 20,
      "description": "List of gifts previously given to this person (to avoid duplicates)",
      "default": []
    },
    "starred_gift_ids": {
      "type": "array",
      "items": {
        "type": "string",
        "format": "uuid"
      },
      "maxItems": 20,
      "description": "IDs of gifts starred from previous recommendations (to refine results)",
      "default": []
    },
    "limit": {
      "type": "integer",
      "minimum": 3,
      "maximum": 10,
      "default": 5,
      "description": "Number of recommendations to return"
    }
  },
  "required": ["recipient_description"],
  "additionalProperties": false
}
```

**Output Format** (OpenAI Apps SDK structured response):

```json
{
  "structuredContent": {
    "gifts": [
      {
        "id": "uuid-string",
        "name": "Gift Name",
        "brief_description": "Short description for display",
        "relevance_score": 0.85,
        "price_range": "moderate",
        "categories": ["category1", "category2"]
      }
    ],
    "query_context": {
      "total_searched": 5000,
      "above_threshold": 23,
      "starred_boost_applied": true,
      "fallback_used": false
    }
  },
  "content": "Here are 5 gift recommendations for your dad who loves woodworking...",
  "_meta": {
    "openai/outputTemplate": "ui://widget/gift-list.html",
    "gifts": [
      {
        "id": "uuid-string",
        "name": "Gift Name",
        "full_description": "Complete detailed description...",
        "price_range": "moderate",
        "categories": ["category1", "category2"],
        "occasions": ["birthday"],
        "purchasing_guidance": "Available at craft stores..."
      }
    ]
  }
}
```

**Tool Metadata**:
```json
{
  "_meta": {
    "openai/outputTemplate": "ui://widget/gift-list.html",
    "openai/widgetAccessible": true,
    "openai/invocationMessage": "Finding gift recommendations..."
  }
}
```

**Error Responses**:

| Condition | structuredContent | content |
|-----------|-------------------|---------|
| Empty/invalid description | `{"error": "invalid_input", "gifts": []}` | "Please provide a description of the gift recipient." |
| No matches found | `{"gifts": [], "fallback": true}` | "No strong matches found. Here are some popular gift ideas..." |
| Service unavailable | `{"error": "service_error", "gifts": []}` | "Unable to fetch recommendations. Please try again." |

---

### get_gift_details

Get extended details for a specific gift.

**Tool Name**: `get_gift_details`

**Description**: Returns full details for a gift by ID, including extended description and purchasing guidance.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "gift_id": {
      "type": "string",
      "format": "uuid",
      "description": "The ID of the gift to get details for"
    }
  },
  "required": ["gift_id"],
  "additionalProperties": false
}
```

**Output Format**:
```json
{
  "structuredContent": {
    "gift": {
      "id": "uuid-string",
      "name": "Gift Name",
      "full_description": "Complete detailed description...",
      "price_range": "moderate",
      "categories": ["category1", "category2"],
      "occasions": ["birthday", "holiday"],
      "recipient_types": ["parent", "hobbyist"],
      "purchasing_guidance": "Available at specialty stores and online retailers..."
    }
  },
  "content": "**Gift Name** ($25-75)\n\nComplete detailed description...\n\n*Where to find*: Available at...",
  "_meta": {
    "openai/outputTemplate": "ui://widget/gift-details.html"
  }
}
```

**Tool Metadata**:
```json
{
  "_meta": {
    "openai/outputTemplate": "ui://widget/gift-details.html",
    "openai/widgetAccessible": true,
    "openai/invocationMessage": "Loading gift details..."
  }
}
```

**Error Responses**:

| Condition | structuredContent | content |
|-----------|-------------------|---------|
| Gift not found | `{"error": "not_found", "gift": null}` | "Gift not found. It may have been removed from our catalog." |
| Invalid ID format | `{"error": "invalid_input", "gift": null}` | "Invalid gift ID format." |

---

## Resources

### gift-list-widget

The main recommendation list UI widget.

**Resource URI**: `ui://widget/gift-list.html`
**MIME Type**: `text/html+skybridge`

**Description**: Renders a list of gift recommendations with star controls. Receives data via `window.openai.toolOutput`.

**Widget Capabilities**:
- Display gift cards with name, brief description, price range
- Star/unstar controls for each gift
- Track starred gift IDs in local state
- Provide starred IDs to next tool call via `window.openai.callTool()`

---

### gift-details-widget

The expanded gift details UI widget.

**Resource URI**: `ui://widget/gift-details.html`
**MIME Type**: `text/html+skybridge`

**Description**: Renders full details for a single gift. Used when user requests more information.

**Widget Capabilities**:
- Display full description, price range, occasions
- Show purchasing guidance
- Star control for the gift
- Back navigation to list view

---

## Widget Data Flow

```text
┌─────────────────────────────────────────────────────────────┐
│                        ChatGPT                              │
│                                                             │
│  User: "Gift ideas for my dad who loves woodworking"        │
│                           │                                 │
│                           ▼                                 │
│              ┌────────────────────────┐                     │
│              │ Invoke get_recommendations                   │
│              │ recipient_description: "..."                 │
│              └────────────┬───────────┘                     │
│                           │                                 │
└───────────────────────────┼─────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────┐
│                    MCP Server (FastMCP)                   │
│                                                           │
│  1. Embed recipient_description                           │
│  2. Query S3 Vectors                                      │
│  3. Build response with structuredContent + _meta         │
│                                                           │
└───────────────────────────┬───────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────┐
│                  Widget (gift-list.html)                  │
│                                                           │
│  window.openai.toolOutput → gift data                     │
│                                                           │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐                      │
│  │ Gift 1  │ │ Gift 2  │ │ Gift 3  │  ...                 │
│  │ ☆ Star  │ │ ★ Star  │ │ ☆ Star  │                      │
│  └─────────┘ └─────────┘ └─────────┘                      │
│                                                           │
│  [Refine Recommendations] button                          │
│      │                                                    │
│      └──► window.openai.callTool("get_recommendations", { │
│             recipient_description: "...",                 │
│             starred_gift_ids: ["gift-2-id"]               │
│           })                                              │
│                                                           │
└───────────────────────────────────────────────────────────┘
```
