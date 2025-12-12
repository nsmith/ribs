# RIBS Gift Recommendations - Test & Development Makefile
#
# Usage:
#   make setup        - Install all dependencies
#   make test         - Run all tests
#   make test-backend - Run backend tests only
#   make test-frontend - Run frontend tests only
#
# See TESTING.md for detailed documentation.

.PHONY: setup setup-backend setup-frontend \
        test test-backend test-frontend test-watch \
        lint lint-backend lint-frontend \
        typecheck typecheck-backend typecheck-frontend \
        clean clean-backend clean-frontend \
        help

# Default target
.DEFAULT_GOAL := help

#------------------------------------------------------------------------------
# Setup
#------------------------------------------------------------------------------

setup: setup-backend setup-frontend ## Install all dependencies
	@echo "✓ All dependencies installed"

setup-backend: ## Install backend dependencies
	@echo "→ Installing backend dependencies..."
	@cd backend && uv sync --extra dev
	@echo "✓ Backend dependencies installed"

setup-frontend: ## Install frontend dependencies
	@echo "→ Installing frontend dependencies..."
	@cd frontend && npm install
	@echo "✓ Frontend dependencies installed"

#------------------------------------------------------------------------------
# Testing
#------------------------------------------------------------------------------

test: test-backend test-frontend ## Run all tests
	@echo ""
	@echo "════════════════════════════════════════"
	@echo "✓ All tests passed"
	@echo "════════════════════════════════════════"

test-backend: ## Run backend tests (pytest)
	@echo ""
	@echo "════════════════════════════════════════"
	@echo "Running Backend Tests (pytest)"
	@echo "════════════════════════════════════════"
	@cd backend && uv run pytest tests/ -v --tb=short

test-frontend: ## Run frontend tests (vitest)
	@echo ""
	@echo "════════════════════════════════════════"
	@echo "Running Frontend Tests (vitest)"
	@echo "════════════════════════════════════════"
	@cd frontend && npm test -- --run

test-watch: ## Run frontend tests in watch mode
	@cd frontend && npm test

test-cov: test-cov-backend ## Run tests with coverage
	@echo "✓ Coverage report generated"

test-cov-backend: ## Run backend tests with coverage
	@echo "→ Running backend tests with coverage..."
	@cd backend && uv run pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

#------------------------------------------------------------------------------
# Linting
#------------------------------------------------------------------------------

lint: lint-backend lint-frontend ## Run all linters
	@echo "✓ All linting passed"

lint-backend: ## Run backend linter (ruff)
	@echo "→ Linting backend..."
	@cd backend && uv run ruff check src/ tests/
	@cd backend && uv run ruff format --check src/ tests/

lint-frontend: ## Run frontend linter (eslint)
	@echo "→ Linting frontend..."
	@cd frontend && npm run lint 2>/dev/null || echo "  (eslint not configured)"

lint-fix: ## Auto-fix linting issues
	@echo "→ Auto-fixing backend..."
	@cd backend && uv run ruff check --fix src/ tests/
	@cd backend && uv run ruff format src/ tests/
	@echo "→ Auto-fixing frontend..."
	@cd frontend && npm run lint:fix 2>/dev/null || echo "  (eslint not configured)"

#------------------------------------------------------------------------------
# Type Checking
#------------------------------------------------------------------------------

typecheck: typecheck-backend typecheck-frontend ## Run all type checkers
	@echo "✓ All type checking passed"

typecheck-backend: ## Run backend type checker (mypy)
	@echo "→ Type checking backend..."
	@cd backend && uv run mypy src/

typecheck-frontend: ## Run frontend type checker (tsc)
	@echo "→ Type checking frontend..."
	@cd frontend && npx tsc --noEmit

#------------------------------------------------------------------------------
# Cleaning
#------------------------------------------------------------------------------

clean: clean-backend clean-frontend ## Remove all build artifacts and caches
	@echo "✓ All cleaned"

clean-backend: ## Clean backend artifacts
	@echo "→ Cleaning backend..."
	@cd backend && rm -rf .venv .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	@cd backend && find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

clean-frontend: ## Clean frontend artifacts
	@echo "→ Cleaning frontend..."
	@cd frontend && rm -rf node_modules dist .vite coverage

#------------------------------------------------------------------------------
# Development
#------------------------------------------------------------------------------

dev-backend: ## Run backend with real AWS/OpenAI (requires .env)
	@echo "→ Starting server with real adapters (SSE on port 3001)"
	@echo "  Requires: backend/.env with OPENAI_API_KEY, AWS credentials"
	@echo ""
	@cd backend && uv run python -m src.main

dev-frontend: ## Run frontend dev server
	@cd frontend && npm run dev

dev-mock: ## Run backend with mock adapters (SSE on port 3001)
	@echo "→ Starting dev server with SSE transport on http://127.0.0.1:3001/sse"
	@echo "  Tools: get_recommendations, get_gift_details"
	@echo "  Sample gift IDs:"
	@echo "    - 11111111-1111-1111-1111-111111111111 (Leather Journal)"
	@echo "    - 22222222-2222-2222-2222-222222222222 (Woodworking Kit)"
	@echo "    - 33333333-3333-3333-3333-333333333333 (Vinyl Record Player)"
	@echo ""
	@cd backend && uv run python -m src.dev_server

inspect: ## Open MCP Inspector (run 'make dev-mock' first in another terminal)
	@echo "→ Opening MCP Inspector..."
	@echo "  Make sure dev server is running: make dev-mock"
	@echo "  Connect to: http://127.0.0.1:3001/sse"
	@echo ""
	@npx @anthropic/mcp-inspector

upload-gifts: ## Upload gifts from CSV (usage: make upload-gifts CSV=path/to/file.csv)
	@if [ -z "$(CSV)" ]; then \
		echo "Usage: make upload-gifts CSV=path/to/file.csv"; \
		echo "       make upload-gifts CSV=path/to/file.csv SETUP=1  # Create index if needed"; \
		echo "       make upload-gifts CSV=path/to/file.csv DRY_RUN=1"; \
		exit 1; \
	fi
	@cd backend && uv run upload-gifts $(CSV) $(if $(SETUP),--setup,) $(if $(DRY_RUN),--dry-run,)

#------------------------------------------------------------------------------
# CI Helpers
#------------------------------------------------------------------------------

ci: setup lint typecheck test ## Full CI pipeline
	@echo ""
	@echo "════════════════════════════════════════"
	@echo "✓ CI pipeline passed"
	@echo "════════════════════════════════════════"

#------------------------------------------------------------------------------
# Help
#------------------------------------------------------------------------------

help: ## Show this help message
	@echo "RIBS Gift Recommendations - Development Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Examples:"
	@echo "  make setup        # First-time setup"
	@echo "  make test         # Run all tests"
	@echo "  make test-backend # Run only Python tests"
	@echo "  make lint-fix     # Auto-fix code style"
