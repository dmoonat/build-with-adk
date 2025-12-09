# AGENTS.md

Universal context file for AI coding assistants (OpenAI Codex, GitHub Copilot, Cursor, Jules).

## Identity

You are working on a multi-agent AI pipeline for retail location analysis, built with Google ADK (Agent Development Kit). The agent helps businesses find optimal physical locations by analyzing demographics, competition, and market viability.

## Commands

```bash
make install        # Install dependencies
make dev            # Start development server at :8501
make test-unit      # Run unit tests (fast, no API)
make test-agents    # Run integration tests
make lint           # Run linters
```

## Project Structure

```
retail-ai-location-strategy/
├── app/
│   ├── agent.py              # Root agent and pipeline
│   ├── config.py             # Model configuration
│   ├── sub_agents/           # Individual agents
│   │   ├── intake_agent/
│   │   ├── market_research/
│   │   ├── competitor_mapping/
│   │   ├── gap_analysis/
│   │   ├── strategy_advisor/
│   │   ├── report_generator/
│   │   ├── infographic_generator/
│   │   └── audio_overview/
│   ├── tools/                # Custom tools
│   │   ├── places_search.py
│   │   ├── html_report_generator.py
│   │   ├── image_generator.py
│   │   └── audio_generator.py
│   ├── callbacks/            # Lifecycle hooks
│   └── schemas/              # Pydantic models
├── tests/
│   ├── unit/
│   └── integration/
└── blog/                     # Tutorial series
```

## Pipeline Flow

```
User Query
    ↓
IntakeAgent (parse location + business type)
    ↓
LocationStrategyPipeline (SequentialAgent)
    ├── MarketResearchAgent (google_search tool)
    ├── CompetitorMappingAgent (search_places tool)
    ├── GapAnalysisAgent (code execution)
    ├── StrategyAdvisorAgent (extended reasoning)
    └── ArtifactGenerationPipeline (ParallelAgent)
        ├── ReportGeneratorAgent → HTML
        ├── InfographicGeneratorAgent → PNG
        └── AudioOverviewAgent → WAV
```

## Code Style

- Use type hints for all function parameters
- Tools return `dict` with `status` key ("success" or "error")
- Callbacks return `None` to continue, `Content` to override
- Async tools use `async def` when calling `tool_context.save_artifact()`
- State keys use snake_case

## Key Patterns

### Creating an Agent
```python
from google.adk.agents import LlmAgent

agent = LlmAgent(
    name="MyAgent",
    model=FAST_MODEL,
    instruction="...",
    tools=[my_tool],
    output_key="my_output",
    before_agent_callback=before_my_agent,
    after_agent_callback=after_my_agent,
)
```

### Creating a Tool
```python
from google.adk.tools import ToolContext

def my_tool(query: str, tool_context: ToolContext) -> dict:
    """Tool description for LLM."""
    # Access state
    value = tool_context.state.get("key")

    return {"status": "success", "data": result}
```

### Creating a Callback
```python
from google.adk.agents.callback_context import CallbackContext

def before_agent(callback_context: CallbackContext):
    callback_context.state["key"] = "value"
    return None  # Continue execution
```

## Testing

- Unit tests: `tests/unit/` - Schema validation, no API calls
- Integration: `tests/integration/` - Real API calls
- Evalsets: `tests/evalsets/` - ADK evaluation files

Run before committing:
```bash
make test-unit
```

## Boundaries

- Don't modify model names in `app/config.py` without asking
- Don't change API key handling patterns
- Keep tools async when using `tool_context.save_artifact()`
- Don't remove callbacks - they track pipeline state

## Learning Resources

- Tutorial: `blog/` directory (9 parts)
- Architecture: `DEVELOPER_GUIDE.md`
- ADK Docs: https://google.github.io/adk-docs/
