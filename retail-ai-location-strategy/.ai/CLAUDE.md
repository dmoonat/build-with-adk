# Retail AI Location Strategy Agent

Multi-agent AI pipeline for retail site selection, built with Google ADK.

## Quick Start

```bash
make install        # Install dependencies with uv
make dev            # Run at localhost:8501
make test-unit      # Fast schema tests (no API calls)
make test-agents    # Integration tests (2-5 min)
```

## Architecture

8-agent pipeline using SequentialAgent + ParallelAgent:

```
IntakeAgent → MarketResearch → CompetitorMapping → GapAnalysis →
StrategyAdvisor → ParallelAgent(Report, Infographic, Audio)
```

### Key Files

| Path | Purpose |
|------|---------|
| `app/agent.py` | Root agent and pipeline definition |
| `app/sub_agents/*/agent.py` | Individual agent definitions |
| `app/tools/*.py` | Custom tools (Places API, image gen, etc.) |
| `app/callbacks/pipeline_callbacks.py` | Lifecycle hooks for each stage |
| `app/config.py` | Model names, retry settings |
| `app/schemas/report_schema.py` | Pydantic output schema |

## State Keys

| Key | Set By | Type |
|-----|--------|------|
| `target_location` | IntakeAgent | str |
| `business_type` | IntakeAgent | str |
| `market_research_findings` | MarketResearchAgent | str |
| `competitor_analysis` | CompetitorMappingAgent | str |
| `gap_analysis` | GapAnalysisAgent | str |
| `strategic_report` | StrategyAdvisorAgent | JSON (Pydantic) |

## Common Tasks

### Add a new agent

1. Create `app/sub_agents/my_agent/agent.py`
2. Define `LlmAgent` with `instruction`, `tools`, `output_key`
3. Add callbacks in `app/callbacks/pipeline_callbacks.py`
4. Export in `app/sub_agents/__init__.py`
5. Add to pipeline in `app/agent.py`

### Add a new tool

1. Create function in `app/tools/my_tool.py`
2. Use signature: `def my_tool(arg: str, tool_context: ToolContext) -> dict`
3. Export in `app/tools/__init__.py`
4. Add to agent's `tools=[my_tool]` list

### Add a callback

1. Add `before_*` and `after_*` functions in `pipeline_callbacks.py`
2. Signature: `def before_*(callback_context: CallbackContext) -> Optional[Content]`
3. Return `None` to continue, `Content` to override
4. Export in `app/callbacks/__init__.py`

## Gotchas

- `.env` file must be in `app/` folder, not project root
- Use `ToolContext` parameter for state access in tools
- `output_schema` on LlmAgent disables tool calling
- TTS multi-speaker (Kore + Puck) only works in AI Studio, not Vertex AI
- State injection uses `{variable}` syntax in instructions
- `google_search` is a built-in tool, no API key needed

## Testing

```bash
make test-unit      # Schema validation, no API calls
make test-intake    # Just IntakeAgent (~30 sec)
make test-agents    # All agents (~5 min)
make eval           # ADK evalsets
```

## Models

Defined in `app/config.py`:
- `FAST_MODEL` = gemini-2.5-pro (main processing)
- `IMAGE_MODEL` = gemini-3-pro-image-preview (infographic)
- `TTS_MODEL` = gemini-2.5-flash-preview-tts (audio)

## Learning Resources

- **Tutorial**: `blog/` - 9-part progressive guide
- **Dev Guide**: `DEVELOPER_GUIDE.md` - Deep architecture docs
- **ADK Docs**: https://google.github.io/adk-docs/

## Slash Commands

Slash commands are available in `.ai/.claude/commands/`:
- `/add-agent` - Guide for adding a new agent
- `/add-tool` - Guide for adding a new tool
- `/run-tests` - Run test commands
- `/explain-pipeline` - Explain the agent pipeline

To use: symlink or copy `.ai/.claude/` to your project root as `.claude/`

## File Patterns

- `app/sub_agents/*/agent.py` - Agent definitions
- `app/sub_agents/*/instructions.py` - Prompt templates
- `app/tools/*.py` - Tool implementations
- `tests/unit/test_*.py` - Unit tests
- `tests/integration/test_*.py` - Integration tests
