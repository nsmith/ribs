# Research: Gift Recommendation MCP Server

**Feature**: 001-gift-recommendations
**Date**: 2025-12-11
**Phase**: 0 - Research & Technology Decisions

## Technology Decisions

### 1. MCP Server Framework: FastMCP

**Decision**: Use FastMCP for the Python MCP server implementation.

**Rationale**:
- Minimal boilerplate - decorator-based tool registration (`@mcp.tool`)
- Handles MCP protocol complexity automatically
- Native Python type hints for schema generation
- Active development and good documentation

**Alternatives Considered**:
- Raw `mcp` Python SDK: More control but significantly more boilerplate
- TypeScript MCP SDK: Would require separate backend language from embeddings logic

**Integration Pattern**:
```python
from fastmcp import FastMCP

mcp = FastMCP("Gift Recommendations")

@mcp.tool
def get_recommendations(recipient_description: str, ...) -> dict:
    """Get personalized gift recommendations"""
    ...
```

### 2. Vector Storage: AWS S3 Vectors

**Decision**: Use AWS S3 Vectors for storing and querying gift embeddings.

**Rationale**:
- Native vector similarity search without managing infrastructure
- Scales to 2 billion vectors per index
- Sub-second query latency (~100ms warm queries)
- Cost-effective compared to dedicated vector databases
- Serverless - no provisioning required

**Alternatives Considered**:
- Pinecone: More mature but additional vendor, higher cost
- pgvector (PostgreSQL): Requires database management, overkill for stateless service
- In-memory (numpy): Limited scale, requires catalog reload on restart

**Integration Pattern**:
- Create S3 bucket with vector index for gifts
- Store gift embeddings with metadata (name, description, price range, categories)
- Query by embedding similarity for recommendations

### 3. Embedding Model: OpenAI text-embedding-3-small

**Decision**: Use OpenAI's text-embedding-3-small model for generating embeddings.

**Rationale**:
- Consistent with ChatGPT ecosystem
- High quality semantic representations
- 1536 dimensions, good balance of quality and performance
- Cost-effective for query-time embedding generation

**Alternatives Considered**:
- text-embedding-3-large: Higher quality but more expensive, larger vectors
- Cohere embeddings: Good quality but adds another vendor
- Local models (sentence-transformers): Requires GPU/compute management

**Usage**:
- Embed recipient descriptions at query time
- Embed starred gift characteristics for refinement queries
- Pre-embed gift catalog during seeding

### 4. UI Framework: React with Skybridge

**Decision**: Build the widget UI using React with OpenAI Apps SDK skybridge runtime.

**Rationale**:
- Required for ChatGPT integration via Apps SDK
- Skybridge provides `window.openai` globals for tool communication
- React enables component-based UI with star controls
- Standard tooling (TypeScript, Vite/webpack)

**Key Integration Points**:
- Register widget as MCP resource with `mimeType: "text/html+skybridge"`
- Use `window.openai.toolOutput` to receive recommendation data
- Use `window.openai.callTool()` for component-initiated actions
- Structured content in tool responses for UI rendering

### 5. Structured Response Format

**Decision**: Use OpenAI Apps SDK three-layer response format.

**Rationale**:
- `structuredContent`: JSON for widget + model (gift IDs, names, brief descriptions)
- `content`: Markdown narration for model's response
- `_meta`: Rich data exclusively for widget (full details, styling hints)

**Pattern**:
```python
return {
    "structuredContent": {
        "gifts": [{"id": "...", "name": "...", "brief": "..."}]
    },
    "content": "Here are 5 gift recommendations for your dad...",
    "_meta": {
        "gifts": [{"id": "...", "fullDescription": "...", "priceRange": "..."}]
    }
}
```

## Architecture Decisions

### Clean Architecture Layers

**Domain Layer** (`backend/src/domain/`):
- `entities/`: Gift, RecipientProfile, RecommendationRequest, RecommendationResponse
- `services/`: RecommendationService (core logic), EmbeddingService (embedding operations)
- `ports/`: VectorStorePort, EmbeddingProviderPort (interfaces)

**Adapter Layer** (`backend/src/adapters/`):
- `mcp/`: FastMCP server setup, tool handlers
- `embeddings/`: OpenAI embedding adapter implementing EmbeddingProviderPort
- `vectors/`: S3 Vectors adapter implementing VectorStorePort

**Benefits**:
- Domain logic testable without AWS/OpenAI dependencies
- Adapters swappable (e.g., mock vector store for tests)
- Clear boundaries align with constitution Principle III

### Stateless Request Flow

1. User describes recipient in ChatGPT
2. ChatGPT invokes `get_recommendations` MCP tool with:
   - `recipient_description` (required)
   - `past_gifts` (optional list)
   - `starred_gift_ids` (optional list from previous response)
   - `limit` (optional, default 5)
3. Server embeds the description + starred gift characteristics
4. Server queries S3 Vectors for similar gifts
5. Server returns structured response with gift data
6. Widget renders gifts with star controls
7. User stars gifts → available for next request as input

### Error Handling Strategy

| Scenario | Handling |
|----------|----------|
| Empty/invalid description | Return error in `content`, empty `structuredContent` |
| S3 Vectors unavailable | Return error, log for observability |
| No matches above threshold | Return popular/fallback gifts with explanation |
| Invalid starred IDs | Ignore invalid, process valid ones, continue |
| Rate limiting | Respect OpenAI API limits, queue or retry |

## Security Considerations

- No secrets in `structuredContent` or `_meta` (user-visible)
- AWS credentials via IAM roles, not embedded
- OpenAI API key via environment variable
- Input validation on all tool parameters (pydantic)
- CSP configured via `openai/widgetCSP` resource

## Open Questions Resolved

| Question | Resolution |
|----------|------------|
| How to handle starred gifts? | Pass as `starred_gift_ids` parameter, look up embeddings, blend with description |
| Gift catalog source? | Pre-embedded catalog in S3 Vectors, seeding script provided |
| How does widget communicate stars? | Client tracks locally, passes to next `get_recommendations` call |
| Authentication? | None required (stateless, no user accounts per spec) |
