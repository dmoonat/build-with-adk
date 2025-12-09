# Commands Reference

## Development

```bash
# Install dependencies (uses uv package manager)
make install

# Run agent with ADK web UI at localhost:8501
make dev

# Alias for dev
make playground
```

## Testing

```bash
# Run all tests (unit + integration)
make test

# Unit tests only - fast, no API calls
make test-unit

# Just IntakeAgent - quickest validation (10-30 sec)
make test-intake

# All individual agents (2-5 min)
make test-agents

# Full pipeline integration (15-30 min)
make test-integration
```

## Evaluation

```bash
# Run all ADK evalsets
make eval

# Run intake evalset only (quick)
make eval-intake

# Run pipeline evalset
make eval-pipeline
```

## Code Quality

```bash
# Run linters (ruff, mypy, codespell)
make lint
```

## AG-UI Frontend

```bash
# Install AG-UI dependencies
make ag-ui-install

# Run AG-UI (backend:8000 + frontend:3000)
make ag-ui
```

## Utilities

```bash
# Clean build artifacts
make clean

# Show help
make help
```

## Direct Commands

```bash
# Run ADK web directly
uv run adk web . --port 8501

# Run specific test file
uv run pytest tests/unit/test_schemas.py -v

# Run ADK eval directly
uv run adk eval app tests/evalsets/intake.evalset.json
```

## Environment Setup

```bash
# Create .env file for AI Studio
cat > app/.env << EOF
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your_key
MAPS_API_KEY=your_maps_key
EOF

# Create .env file for Vertex AI
cat > app/.env << EOF
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your_project
GOOGLE_CLOUD_LOCATION=us-central1
MAPS_API_KEY=your_maps_key
EOF
```
