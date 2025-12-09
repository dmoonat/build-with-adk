# Retail AI Location Strategy Agent

Multi-agent AI pipeline for retail site selection, built with Google ADK.

## Quick Start

```bash
make install        # Install dependencies with uv
make dev            # Run at localhost:8501
make test-unit      # Fast schema tests
make test-agents    # Integration tests
```

## Architecture

@context/architecture.md

## Agents Reference

@context/agents.md

## Tools Reference

@context/tools.md

## State Keys

@context/state-keys.md

## Common Tasks

@context/common-tasks.md

## Troubleshooting

@context/troubleshooting.md

## Commands Reference

@context/commands.md

## Key Files

| Path | Purpose |
|------|---------|
| `app/agent.py` | Root agent and pipeline definition |
| `app/sub_agents/*/agent.py` | Individual agent definitions |
| `app/tools/*.py` | Custom tools |
| `app/callbacks/pipeline_callbacks.py` | Lifecycle hooks |
| `app/config.py` | Model names, retry config |

## ADK Patterns Used

### SequentialAgent
Pipeline orchestration - agents run in order, sharing state.

### ParallelAgent
Concurrent execution for artifact generation (Report + Infographic + Audio).

### LlmAgent
Core agent type with tools, callbacks, and output_key.

### AgentTool
Wraps an agent as a callable tool for the root agent.

### BuiltInCodeExecutor
Sandboxed Python execution for GapAnalysisAgent.

## Environment Setup

### AI Studio (Local Development)
```bash
# app/.env
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your_key
MAPS_API_KEY=your_maps_key
```

### Vertex AI (Production)
```bash
# app/.env
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your_project
GOOGLE_CLOUD_LOCATION=us-central1
MAPS_API_KEY=your_maps_key
```

## Learning Resources

- **Tutorial**: `blog/` directory - 9-part progressive guide
- **Dev Guide**: `DEVELOPER_GUIDE.md`
- **ADK Docs**: https://google.github.io/adk-docs/

## Models Configuration

In `app/config.py`:
- `FAST_MODEL` = gemini-2.5-pro
- `PRO_MODEL` = gemini-2.5-pro
- `IMAGE_MODEL` = gemini-3-pro-image-preview
- `TTS_MODEL` = gemini-2.5-flash-preview-tts

## Testing Commands

```bash
make test-unit      # Unit tests, no API
make test-intake    # IntakeAgent only
make test-agents    # All agents
make eval           # ADK evalsets
```
