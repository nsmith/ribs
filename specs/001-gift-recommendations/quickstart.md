# Quickstart: Gift Recommendation MCP Server

**Feature**: 001-gift-recommendations
**Date**: 2025-12-11

## Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- AWS account with S3 access
- OpenAI API key

## Setup

### 1. Clone and Install Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### 2. Configure Environment

Create `backend/.env`:

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# AWS S3 Vectors
AWS_REGION=us-east-1
S3_VECTORS_BUCKET=ribs-gift-recommendations
S3_VECTORS_INDEX=gifts

# Server
MCP_SERVER_NAME=gift-recommendations
LOG_LEVEL=INFO
```

### 3. Seed Gift Catalog (Development)

```bash
# Generate embeddings and upload to S3 Vectors
python scripts/seed_catalog.py --source data/sample-gifts.json
```

### 4. Install Frontend

```bash
cd frontend
npm install
```

### 5. Run Development Servers

**Terminal 1 - Backend (MCP Server)**:
```bash
cd backend
source .venv/bin/activate
python -m src.main
```

**Terminal 2 - Frontend (Widget)**:
```bash
cd frontend
npm run dev
```

## Testing Locally

### Run Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Run Frontend Tests

```bash
cd frontend
npm test
```

### Test MCP Tools (via MCP Inspector)

```bash
# Install MCP Inspector
npx @anthropic-ai/mcp-inspector

# Connect to local server
# Navigate to http://localhost:5173 (Inspector UI)
# Add server: stdio, command: python -m src.main
```

## ChatGPT Integration (Development)

### 1. Expose Server via ngrok

```bash
ngrok http 8000
```

### 2. Register in ChatGPT Developer Console

1. Go to ChatGPT Apps settings
2. Add new MCP server
3. Enter ngrok URL as server endpoint
4. Configure widget resource URI

### 3. Test in ChatGPT

```
User: "I need gift ideas for my dad who loves woodworking and classic rock"
```

Expected: Widget displays gift cards with star controls.

## Common Commands

| Command | Description |
|---------|-------------|
| `pytest tests/unit/` | Run unit tests only |
| `pytest tests/contract/` | Run MCP contract tests |
| `pytest tests/integration/` | Run integration tests |
| `python scripts/seed_catalog.py --dry-run` | Preview catalog seeding |
| `npm run build` | Build frontend for production |
| `npm run lint` | Lint frontend code |

## Project Structure

```
ribs/
├── backend/
│   ├── src/
│   │   ├── domain/          # Business logic
│   │   ├── adapters/        # MCP, S3, OpenAI integrations
│   │   ├── config/          # Settings
│   │   └── main.py          # Entry point
│   ├── tests/
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   └── hooks/           # OpenAI integration hooks
│   ├── public/
│   └── package.json
├── scripts/
│   └── seed_catalog.py      # Catalog seeding utility
└── specs/
    └── 001-gift-recommendations/
        ├── spec.md
        ├── plan.md
        ├── research.md
        ├── data-model.md
        ├── quickstart.md    # This file
        └── contracts/
```

## Troubleshooting

### "No gifts found" on every query

- Verify S3 Vectors bucket and index exist
- Check AWS credentials have read access
- Confirm catalog was seeded: `python scripts/seed_catalog.py --check`

### Widget not rendering in ChatGPT

- Verify ngrok tunnel is active
- Check MCP server is running and accessible
- Confirm widget resource is registered with correct MIME type

### Embedding errors

- Verify OPENAI_API_KEY is set and valid
- Check API quota/rate limits
- Ensure network connectivity to OpenAI

### S3 Vectors timeout

- Verify AWS_REGION matches bucket region
- Check S3 endpoint connectivity
- Review CloudWatch logs for S3 errors
