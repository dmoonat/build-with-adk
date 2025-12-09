# Copilot Instructions

## Project Overview

This is a multi-agent AI pipeline for retail location analysis, built with Google ADK (Agent Development Kit).

## Architecture

8-agent pipeline using SequentialAgent + ParallelAgent:

```
IntakeAgent → MarketResearch → CompetitorMapping → GapAnalysis →
StrategyAdvisor → ParallelAgent(Report, Infographic, Audio)
```

## Key Files

- `app/agent.py` - Root agent and pipeline definition
- `app/sub_agents/*/agent.py` - Individual agent definitions
- `app/tools/*.py` - Custom tools
- `app/callbacks/pipeline_callbacks.py` - Lifecycle hooks
- `app/config.py` - Model configuration

## Commands

```bash
make install        # Install dependencies
make dev            # Run at localhost:8501
make test-unit      # Fast unit tests
make test-agents    # Integration tests
```

## Code Patterns

### Agent Definition
```python
from google.adk.agents import LlmAgent

agent = LlmAgent(
    name="MyAgent",
    model=FAST_MODEL,
    instruction="...",
    tools=[my_tool],
    output_key="my_output",
)
```

### Tool Definition
```python
from google.adk.tools import ToolContext

def my_tool(query: str, tool_context: ToolContext) -> dict:
    return {"status": "success", "data": result}
```

### Callback Definition
```python
from google.adk.agents.callback_context import CallbackContext

def before_agent(callback_context: CallbackContext):
    callback_context.state["key"] = "value"
    return None
```

## Style Guide

- Use type hints for all function parameters
- Tools return dict with "status" key
- Callbacks return None to continue, Content to override
- State keys use snake_case
- Async tools when using save_artifact()

## Testing

- Unit tests: `tests/unit/` - No API calls
- Integration: `tests/integration/` - Real APIs

## State Keys

| Key | Type | Set By |
|-----|------|--------|
| `target_location` | str | IntakeAgent |
| `business_type` | str | IntakeAgent |
| `market_research_findings` | str | MarketResearchAgent |
| `competitor_analysis` | str | CompetitorMappingAgent |
| `gap_analysis` | str | GapAnalysisAgent |
| `strategic_report` | JSON | StrategyAdvisorAgent |

## Common Tasks

### Add new agent
1. Create `app/sub_agents/my_agent/agent.py`
2. Add callbacks in `pipeline_callbacks.py`
3. Export in `__init__.py`
4. Add to pipeline in `agent.py`

### Add new tool
1. Create `app/tools/my_tool.py`
2. Export in `__init__.py`
3. Add to agent's `tools=[]`

## Boundaries

- Don't modify model names without asking
- Keep tools async when using save_artifact()
- Don't remove callbacks - they track pipeline state
