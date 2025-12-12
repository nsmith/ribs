<!--
================================================================================
SYNC IMPACT REPORT
================================================================================
Version Change: N/A → 1.0.0 (initial ratification)

Modified Principles: N/A (initial creation)

Added Sections:
  - Core Principles (5 principles)
  - Development Workflow
  - Quality Gates
  - Governance

Removed Sections: N/A

Templates Requiring Updates:
  - .specify/templates/plan-template.md: ✅ No updates needed (generic Constitution Check section)
  - .specify/templates/spec-template.md: ✅ No updates needed (generic structure)
  - .specify/templates/tasks-template.md: ✅ No updates needed (generic structure)
  - .specify/templates/checklist-template.md: ✅ No updates needed (generic structure)
  - .specify/templates/agent-file-template.md: ✅ No updates needed (generic structure)

Follow-up TODOs: None
================================================================================
-->

# ribs Constitution

## Core Principles

### I. Test-Driven Development (NON-NEGOTIABLE)

All production code MUST be written following the TDD discipline:

- Tests MUST be written before implementation code
- Tests MUST fail before any implementation begins (Red phase)
- Implementation MUST be the minimum code required to pass tests (Green phase)
- Refactoring MUST only occur with passing tests (Refactor phase)
- No production code changes without corresponding test coverage

**Rationale**: TDD ensures correctness, provides living documentation, and enables
confident refactoring. Skipping TDD creates technical debt that compounds over time.

### II. API-First Design

All interfaces MUST be designed and documented before implementation:

- API contracts (OpenAPI/Swagger specifications) MUST be defined before coding endpoints
- Contract changes MUST be versioned and backward-compatible unless explicitly breaking
- Internal service boundaries MUST have clearly defined interfaces
- External integrations MUST have contract tests validating expected behavior

**Rationale**: API-first design forces clear thinking about system boundaries,
enables parallel development, and prevents integration surprises.

### III. Clean Architecture

Code organization MUST follow separation of concerns and dependency inversion:

- Business logic MUST NOT depend on infrastructure (databases, HTTP, external services)
- Dependencies MUST point inward: Frameworks → Adapters → Use Cases → Entities
- Each layer MUST be independently testable via dependency injection
- Infrastructure details MUST be isolated in adapter modules

**Rationale**: Clean architecture enables technology changes without business logic
rewrites, simplifies testing, and improves long-term maintainability.

### IV. Observability

All components MUST be observable in production:

- Structured logging MUST be used for all significant operations
- Request tracing MUST propagate correlation IDs across service boundaries
- Health endpoints MUST expose service status and dependencies
- Error conditions MUST include sufficient context for debugging

**Rationale**: Systems that cannot be observed cannot be operated reliably.
Observability is a first-class requirement, not an afterthought.

### V. Incremental Delivery

Work MUST be delivered in small, independently valuable increments:

- Each PR SHOULD represent a complete, shippable unit of functionality
- Feature branches MUST be short-lived (merge within days, not weeks)
- Breaking changes MUST use feature flags or versioned APIs
- Each increment MUST pass all tests and quality gates before merge

**Rationale**: Small increments reduce risk, enable faster feedback, and keep
the codebase in a continuously deployable state.

## Development Workflow

### Code Review Requirements

- All changes MUST be reviewed before merge
- Reviews MUST verify principle compliance (TDD, Clean Architecture, etc.)
- Reviewers MUST check for test coverage and contract adherence

### Branch Strategy

- Feature branches from `main`
- PRs target `main` with required CI passing
- Hotfixes follow the same process with expedited review

## Quality Gates

### Pre-Merge Requirements

All PRs MUST satisfy these gates before merge:

1. All tests pass (unit, integration, contract)
2. Code coverage meets minimum threshold (if configured)
3. API contracts validated against implementation
4. No linting or formatting violations
5. At least one approving review

### Continuous Integration

- Tests run on every push
- Contract validation runs on API changes
- Build artifacts generated for deployment verification

## Governance

### Amendment Process

1. Propose amendment via PR to this constitution file
2. Document rationale for the change
3. Obtain team review and approval
4. Update version according to semantic versioning:
   - MAJOR: Principle removal or fundamental redefinition
   - MINOR: New principle added or material expansion
   - PATCH: Clarifications, wording, non-semantic changes
5. Update `LAST_AMENDED_DATE` to amendment date

### Compliance

- All PRs and code reviews MUST verify constitution compliance
- Constitution violations MUST be documented in Complexity Tracking if justified
- Unjustified violations block merge

### Precedence

This constitution supersedes all other development practices and guidelines.
When conflicts arise, constitution principles take priority.

**Version**: 1.0.0 | **Ratified**: 2025-12-11 | **Last Amended**: 2025-12-11
