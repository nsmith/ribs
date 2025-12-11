# Testing Guide

This document covers the test setup, dependencies, and common pitfalls for the RIBS gift recommendation system.

## Prerequisites

- **mise** - Runtime version manager (manages Python, Node.js versions)
- **uv** - Fast Python package manager (replaces pip/venv)
- **Node.js 18+** - For frontend development
- **npm** - Node package manager

## Project Structure

```
ribs/
├── backend/           # Python FastMCP server
│   ├── src/          # Source code
│   ├── tests/        # Python tests (pytest)
│   └── pyproject.toml
├── frontend/         # React/TypeScript widget
│   ├── src/          # Source code
│   ├── tests/        # Frontend tests (vitest)
│   └── package.json
└── Makefile          # Unified test commands
```

## Quick Start

```bash
# Install all dependencies and run all tests
make setup
make test

# Or run backend/frontend separately
make test-backend
make test-frontend
```

## Backend Setup (Python)

### Installing Dependencies

```bash
cd backend

# Sync dependencies including dev tools (pytest, mypy, ruff)
uv sync --extra dev
```

**Important**: Use `uv sync --extra dev` to install test dependencies. Without `--extra dev`, pytest won't be available.

### Running Backend Tests

```bash
cd backend
uv run pytest tests/ -v
```

### Common Pitfalls

#### 1. "Failed to spawn: pytest" or "No such file or directory"

**Cause**: Dev dependencies not installed.

**Fix**: Run `uv sync --extra dev` to install pytest and other dev tools.

#### 2. "Readme file does not exist: README.md"

**Cause**: Hatchling build backend requires README.md when specified in pyproject.toml.

**Fix**: Ensure `backend/README.md` exists, even if minimal.

#### 3. "Unable to determine which files to ship inside the wheel"

**Cause**: Hatchling can't find the source package directory.

**Fix**: Add to `pyproject.toml`:
```toml
[tool.hatch.build.targets.wheel]
packages = ["src"]
```

#### 4. "python: command not found"

**Cause**: System Python not available or not in PATH.

**Fix**: Use `uv run` prefix for all Python commands. This uses the project's virtual environment automatically.

```bash
# Wrong
python -m pytest tests/

# Correct
uv run pytest tests/
```

### Test Organization

```
backend/tests/
├── conftest.py                    # Shared fixtures
├── contract/                      # API contract tests
│   └── test_get_recommendations.py
├── unit/                          # Unit tests
│   ├── test_embedding_service.py
│   └── test_recommendation_service.py
└── integration/                   # Integration tests
    └── test_recommendation_flow.py
```

## Frontend Setup (TypeScript/React)

### Installing Dependencies

```bash
cd frontend
npm install
```

### Running Frontend Tests

```bash
cd frontend
npm test -- --run
```

The `--run` flag runs tests once and exits (vs. watch mode).

### Common Pitfalls

#### 1. "vitest: command not found"

**Cause**: Node modules not installed.

**Fix**: Run `npm install` in the frontend directory.

#### 2. "Failed to resolve import" errors

**Cause**: Component files don't exist yet (expected during TDD red phase).

**Fix**: Implement the missing components. This is the expected TDD workflow.

#### 3. Running npm from wrong directory

**Cause**: Running `npm test` from backend or root directory.

**Fix**: Always `cd frontend` before running npm commands.

### Test Organization

```
frontend/tests/
├── components/
│   ├── GiftCard.test.tsx
│   └── GiftList.test.tsx
└── setup.ts                       # Test setup (jsdom, etc.)
```

## TDD Workflow

This project follows strict Test-Driven Development:

1. **Red Phase**: Write tests first, run them to see failures
   ```bash
   make test  # Expect failures
   ```

2. **Green Phase**: Implement code to make tests pass
   ```bash
   make test  # All should pass
   ```

3. **Refactor Phase**: Clean up code while keeping tests green
   ```bash
   make test  # Still passing
   ```

## Makefile Commands

| Command | Description |
|---------|-------------|
| `make setup` | Install all dependencies (backend + frontend) |
| `make test` | Run all tests (backend + frontend) |
| `make test-backend` | Run only backend tests |
| `make test-frontend` | Run only frontend tests |
| `make test-watch` | Run frontend tests in watch mode |
| `make lint` | Run linters (ruff, eslint) |
| `make typecheck` | Run type checkers (mypy, tsc) |
| `make clean` | Remove build artifacts and caches |

## CI/CD Considerations

For CI environments, ensure:

1. **Python version**: Set via mise or explicitly install Python 3.11+
2. **uv installation**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
3. **Node.js version**: Set via mise or use Node 18+

Example CI setup:
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Backend
cd backend
uv sync --extra dev
uv run pytest tests/ -v --tb=short

# Frontend
cd ../frontend
npm ci
npm test -- --run
```

## Troubleshooting

### Reset Everything

If you encounter persistent issues:

```bash
make clean
make setup
make test
```

### Check Versions

```bash
# Python (via uv)
uv run python --version

# Node
node --version

# npm
npm --version
```

### Verbose Test Output

```bash
# Backend - show full tracebacks
cd backend && uv run pytest tests/ -v --tb=long

# Frontend - show console output
cd frontend && npm test -- --run --reporter=verbose
```
