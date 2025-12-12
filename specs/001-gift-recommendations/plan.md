# Implementation Plan: Gift Recommendation MCP Server

**Branch**: `001-gift-recommendations` | **Date**: 2025-12-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-gift-recommendations/spec.md`

## Summary

Build a stateless MCP server using FastMCP (Python) that provides personalized gift recommendations via semantic search over an embedding-indexed gift catalog stored in AWS S3 Vectors. The server integrates with ChatGPT through OpenAI Apps SDK, rendering an interactive React UI (skybridge) that allows users to star gifts for iterative refinement. All state is passed per-request—no persistence of user data.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastMCP, OpenAI SDK (embeddings), boto3 (AWS S3 Vectors), pydantic (validation)
**UI Framework**: React with skybridge (OpenAI Apps SDK widget runtime)
**Storage**: AWS S3 Vectors for gift embeddings and similarity search
**Testing**: pytest, pytest-asyncio
**Target Platform**: Linux server (containerized deployment)
**Project Type**: Web application (backend MCP server + frontend React widget)
**Performance Goals**: <3s response time for recommendations (SC-001), 100 concurrent requests (SC-003)
**Constraints**: Stateless (no session/user persistence), <500ms vector query latency (S3 Vectors provides ~100ms warm queries)
**Scale/Scope**: Single MCP server instance, S3 Vectors index supports up to 2B vectors

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Status | Notes |
|-----------|-------------|--------|-------|
| I. TDD | Tests before implementation | ✅ PASS | Tasks will enforce Red-Green-Refactor |
| II. API-First | Contracts before code | ✅ PASS | MCP tool schemas defined in Phase 1 |
| III. Clean Architecture | Layered, DI-ready | ✅ PASS | Domain layer isolated from MCP/S3 adapters |
| IV. Observability | Structured logging, health | ✅ PASS | Logging in all tools, health endpoint planned |
| V. Incremental Delivery | Small shippable PRs | ✅ PASS | User stories map to independent increments |

## Project Structure

### Documentation (this feature)

```text
specs/001-gift-recommendations/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (MCP tool schemas)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── domain/
│   │   ├── entities/        # Gift, RecipientProfile, RecommendationRequest
│   │   ├── services/        # RecommendationService, EmbeddingService
│   │   └── ports/           # Interfaces for adapters (VectorStore, EmbeddingProvider)
│   ├── adapters/
│   │   ├── mcp/             # FastMCP server, tool handlers
│   │   ├── embeddings/      # OpenAI embedding adapter
│   │   └── vectors/         # AWS S3 Vectors adapter
│   ├── config/              # Settings, environment
│   └── main.py              # Entry point
└── tests/
    ├── contract/            # MCP tool contract tests
    ├── integration/         # End-to-end recommendation flow
    └── unit/                # Domain logic tests

frontend/
├── src/
│   ├── components/
│   │   ├── GiftCard.tsx     # Individual gift display with star control
│   │   ├── GiftList.tsx     # List of recommendations
│   │   └── GiftDetails.tsx  # Expanded gift view
│   ├── hooks/
│   │   └── useOpenAi.ts     # window.openai integration
│   ├── App.tsx              # Main widget entry
│   └── index.tsx            # Skybridge bootstrap
├── public/
│   └── index.html           # Widget HTML entry (text/html+skybridge)
└── tests/
    └── components/          # React component tests

scripts/
└── seed_catalog.py          # Utility to embed and upload gift catalog to S3 Vectors
```

**Structure Decision**: Web application pattern (backend + frontend) selected because:
1. MCP server (backend) handles tool logic and vector search via S3 Vectors
2. React widget (frontend) renders in ChatGPT iframe via skybridge
3. Clear separation enables independent testing and deployment

## Complexity Tracking

> No constitution violations requiring justification.

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| AWS S3 Vectors | Managed vector storage | Scalable to 2B vectors, sub-second queries, serverless |
| OpenAI embeddings | Using OpenAI text-embedding model | Consistency with ChatGPT ecosystem, high quality |
| No user database | Stateless by design | All context passed per-request as specified |
