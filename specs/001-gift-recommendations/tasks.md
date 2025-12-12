# Tasks: Gift Recommendation MCP Server

**Input**: Design documents from `/specs/001-gift-recommendations/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: TDD is REQUIRED per constitution Principle I. All tests must be written and fail before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`
- Paths follow plan.md structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create backend project structure per plan.md in backend/
- [x] T002 Initialize Python project with pyproject.toml including fastmcp, openai, boto3, pydantic, pytest dependencies
- [x] T003 [P] Create frontend project structure per plan.md in frontend/
- [x] T004 [P] Initialize React/TypeScript project with package.json in frontend/
- [x] T005 [P] Configure pytest and pytest-asyncio in backend/pyproject.toml
- [x] T006 [P] Configure ESLint and TypeScript in frontend/
- [x] T007 Create backend/.env.example with required environment variables (OPENAI_API_KEY, AWS_REGION, S3_VECTORS_BUCKET)
- [x] T008 [P] Create backend/src/config/settings.py with pydantic Settings class for environment configuration

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T009 Create port interface VectorStorePort in backend/src/domain/ports/vector_store.py
- [x] T010 [P] Create port interface EmbeddingProviderPort in backend/src/domain/ports/embedding_provider.py
- [x] T011 Create Gift entity in backend/src/domain/entities/gift.py per data-model.md
- [x] T012 [P] Create PriceRange enum in backend/src/domain/entities/price_range.py
- [x] T013 [P] Create RecommendationRequest entity in backend/src/domain/entities/recommendation_request.py
- [x] T014 [P] Create RecommendationResponse and GiftRecommendation entities in backend/src/domain/entities/recommendation_response.py
- [x] T015 [P] Create QueryContext entity in backend/src/domain/entities/query_context.py
- [x] T016 Create OpenAI embedding adapter implementing EmbeddingProviderPort in backend/src/adapters/embeddings/openai_adapter.py
- [x] T017 Create S3 Vectors adapter implementing VectorStorePort in backend/src/adapters/vectors/s3_vectors_adapter.py
- [x] T018 Create FastMCP server setup in backend/src/adapters/mcp/server.py
- [x] T019 [P] Create structured logging configuration in backend/src/config/logging.py
- [x] T020 Create main.py entry point in backend/src/main.py
- [x] T021 [P] Create useOpenAi hook for window.openai integration in frontend/src/hooks/useOpenAi.ts
- [x] T022 Create App.tsx main widget entry in frontend/src/App.tsx
- [x] T023 [P] Create index.html skybridge entry point in frontend/public/index.html with text/html+skybridge MIME type

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Get Initial Gift Recommendations (Priority: P1) MVP

**Goal**: User describes a recipient and receives personalized gift recommendations displayed in the UI

**Independent Test**: Provide a recipient description and verify relevant gift recommendations are returned and displayed

### Tests for User Story 1 (TDD - Write First, Must Fail)

- [ ] T024 [P] [US1] Write contract test for get_recommendations tool in backend/tests/contract/test_get_recommendations.py
- [ ] T025 [P] [US1] Write unit test for RecommendationService.get_recommendations in backend/tests/unit/test_recommendation_service.py
- [ ] T026 [P] [US1] Write unit test for embedding generation in backend/tests/unit/test_embedding_service.py
- [ ] T027 [P] [US1] Write integration test for full recommendation flow in backend/tests/integration/test_recommendation_flow.py
- [ ] T028 [P] [US1] Write component test for GiftCard in frontend/tests/components/GiftCard.test.tsx
- [ ] T029 [P] [US1] Write component test for GiftList in frontend/tests/components/GiftList.test.tsx

### Implementation for User Story 1

- [ ] T030 [US1] Create EmbeddingService in backend/src/domain/services/embedding_service.py
- [ ] T031 [US1] Create RecommendationService with get_recommendations method in backend/src/domain/services/recommendation_service.py
- [ ] T032 [US1] Implement get_recommendations MCP tool handler in backend/src/adapters/mcp/tools/get_recommendations.py
- [ ] T033 [US1] Register get_recommendations tool with FastMCP server in backend/src/adapters/mcp/server.py
- [ ] T034 [US1] Implement structured response format (structuredContent, content, _meta) in tool handler
- [ ] T035 [P] [US1] Create GiftCard component with name, brief description, price range in frontend/src/components/GiftCard.tsx
- [ ] T036 [US1] Create GiftList component rendering list of GiftCard in frontend/src/components/GiftList.tsx
- [ ] T037 [US1] Integrate GiftList with window.openai.toolOutput in frontend/src/App.tsx
- [ ] T038 [US1] Add input validation for recipient_description (3-2000 chars) in tool handler
- [ ] T039 [US1] Add error handling for empty/invalid description returning appropriate error response
- [ ] T040 [US1] Add fallback to popular gifts when no matches above threshold
- [ ] T041 [US1] Add structured logging for recommendation requests in RecommendationService

**Checkpoint**: User Story 1 complete - basic recommendations working end-to-end

---

## Phase 4: User Story 2 - Star Gifts to Refine Recommendations (Priority: P2)

**Goal**: User can star gifts and use starred selections to get refined recommendations

**Independent Test**: Make two requests - first to get recommendations, second with starred gift IDs, verify refined results

### Tests for User Story 2 (TDD - Write First, Must Fail)

- [ ] T042 [P] [US2] Write unit test for starred gift embedding blending in backend/tests/unit/test_recommendation_service.py
- [ ] T043 [P] [US2] Write contract test for get_recommendations with starred_gift_ids in backend/tests/contract/test_get_recommendations.py
- [ ] T044 [P] [US2] Write integration test for refinement flow in backend/tests/integration/test_refinement_flow.py
- [ ] T045 [P] [US2] Write component test for star toggle in GiftCard in frontend/tests/components/GiftCard.test.tsx

### Implementation for User Story 2

- [ ] T046 [US2] Add starred_gift_ids parameter handling to get_recommendations tool in backend/src/adapters/mcp/tools/get_recommendations.py
- [ ] T047 [US2] Implement starred gift embedding lookup in RecommendationService
- [ ] T048 [US2] Implement embedding blending (recipient + starred gifts) in RecommendationService
- [ ] T049 [US2] Add star toggle control to GiftCard component in frontend/src/components/GiftCard.tsx
- [ ] T050 [US2] Add starred state management to GiftList component in frontend/src/components/GiftList.tsx
- [ ] T051 [US2] Implement "Refine Recommendations" button calling window.openai.callTool with starred IDs in frontend/src/components/GiftList.tsx
- [ ] T052 [US2] Add validation for starred_gift_ids (max 20, ignore invalid) in tool handler
- [ ] T053 [US2] Add starred_boost_applied flag to QueryContext in response

**Checkpoint**: User Story 2 complete - starring and refinement working

---

## Phase 5: User Story 3 - View Gift Details (Priority: P3)

**Goal**: User can view extended details for any recommended gift

**Independent Test**: Request details for a specific gift ID and verify extended information returned

### Tests for User Story 3 (TDD - Write First, Must Fail)

- [ ] T054 [P] [US3] Write contract test for get_gift_details tool in backend/tests/contract/test_get_gift_details.py
- [ ] T055 [P] [US3] Write unit test for gift detail retrieval in backend/tests/unit/test_recommendation_service.py
- [ ] T056 [P] [US3] Write component test for GiftDetails in frontend/tests/components/GiftDetails.test.tsx

### Implementation for User Story 3

- [ ] T057 [US3] Create GiftDetails entity in backend/src/domain/entities/gift_details.py per data-model.md
- [ ] T058 [US3] Add get_gift_details method to RecommendationService in backend/src/domain/services/recommendation_service.py
- [ ] T059 [US3] Implement get_gift_details MCP tool handler in backend/src/adapters/mcp/tools/get_gift_details.py
- [ ] T060 [US3] Register get_gift_details tool with FastMCP server in backend/src/adapters/mcp/server.py
- [ ] T061 [US3] Create GiftDetails component with full description, price, occasions, purchasing guidance in frontend/src/components/GiftDetails.tsx
- [ ] T062 [US3] Add detail view toggle/modal to GiftCard or GiftList in frontend/src/components/
- [ ] T063 [US3] Add error handling for gift not found in tool handler
- [ ] T064 [US3] Add structured logging for detail requests

**Checkpoint**: User Story 3 complete - all user stories functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T065 [P] Create seed_catalog.py script for embedding and uploading gift catalog to S3 Vectors in scripts/seed_catalog.py
- [ ] T066 [P] Create sample-gifts.json seed data file in data/sample-gifts.json
- [ ] T067 [P] Add health check endpoint to MCP server in backend/src/adapters/mcp/server.py
- [ ] T068 [P] Configure CORS and CSP for widget in backend/src/adapters/mcp/server.py
- [ ] T069 Add correlation ID propagation to all request handlers
- [ ] T070 [P] Create Dockerfile for backend in backend/Dockerfile
- [ ] T071 [P] Create Dockerfile for frontend in frontend/Dockerfile
- [ ] T072 Run full test suite and verify all tests pass
- [ ] T073 Run quickstart.md validation - verify setup steps work end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - US1 must complete before US2 (starred gifts depend on basic recommendations)
  - US3 can run in parallel with US2 after US1 complete
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Depends on US1 (needs working recommendations to star)
- **User Story 3 (P3)**: Can start after US1 (needs gift data, independent of starring)

### Within Each User Story (TDD Flow)

1. Tests MUST be written and FAIL before implementation
2. Entities/models before services
3. Services before tool handlers
4. Backend before frontend integration
5. Core implementation before error handling
6. Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 Setup**:
```
T001 (backend structure) ──┐
T003 (frontend structure) ─┼── All can run in parallel
T005 (pytest config) ──────┤
T006 (eslint config) ──────┘
```

**Phase 2 Foundational**:
```
T009 (VectorStorePort) ────┐
T010 (EmbeddingPort) ──────┼── Ports in parallel
T011-T015 (entities) ──────┼── Entities in parallel after ports
T016-T017 (adapters) ──────┘   Adapters after entities
```

**Phase 3 US1 Tests**:
```
T024 (contract test) ──────┐
T025 (unit test service) ──┼── All tests in parallel
T026 (unit test embedding)─┤
T027 (integration test) ───┤
T028 (GiftCard test) ──────┤
T029 (GiftList test) ──────┘
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test US1 independently with MCP Inspector
5. Deploy/demo basic recommendations

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy (MVP!)
3. Add User Story 2 → Test independently → Deploy
4. Add User Story 3 → Test independently → Deploy
5. Polish phase → Production ready

### TDD Discipline (Constitution Principle I)

For each user story:
1. Write ALL tests first (T024-T029 for US1)
2. Run tests → ALL MUST FAIL (Red phase)
3. Implement minimum code to pass (Green phase)
4. Refactor only with passing tests

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **TDD is NON-NEGOTIABLE** per constitution - verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
