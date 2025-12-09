# State Keys Reference

## Overview

State is shared across all agents in a session. Each agent reads from and writes to the state dictionary.

## Core State Keys

| Key | Type | Set By | Used By |
|-----|------|--------|---------|
| `target_location` | str | IntakeAgent | All pipeline agents |
| `business_type` | str | IntakeAgent | All pipeline agents |
| `current_date` | str | before_market_research | MarketResearch, CompetitorMapping |
| `market_research_findings` | str | MarketResearchAgent | GapAnalysis, StrategyAdvisor |
| `competitor_analysis` | str | CompetitorMappingAgent | GapAnalysis, StrategyAdvisor |
| `gap_analysis` | str | GapAnalysisAgent | StrategyAdvisor |
| `strategic_report` | JSON | StrategyAdvisorAgent | All artifact generators |

## Pipeline Tracking Keys

| Key | Type | Purpose |
|-----|------|---------|
| `pipeline_stage` | str | Current stage name |
| `pipeline_start_time` | str | ISO timestamp |
| `stages_completed` | list[str] | Completed stage names |

## API Keys in State

| Key | Source |
|-----|--------|
| `maps_api_key` | Environment or user input |

## Accessing State

### In Agent Instruction

Use `{variable}` syntax for automatic injection:

```python
instruction = """
TARGET LOCATION: {target_location}
BUSINESS TYPE: {business_type}
CURRENT DATE: {current_date}
"""
```

### In Tool

Use `tool_context.state`:

```python
def my_tool(query: str, tool_context: ToolContext) -> dict:
    location = tool_context.state.get("target_location", "")
    api_key = tool_context.state.get("maps_api_key", "")
    return {"status": "success"}
```

### In Callback

Use `callback_context.state`:

```python
def before_agent(callback_context: CallbackContext):
    # Read
    location = callback_context.state.get("target_location")

    # Write
    callback_context.state["current_date"] = datetime.now().isoformat()

    return None
```

## State Flow Example

```
1. User: "coffee shop in Bangalore"

2. IntakeAgent writes:
   state["target_location"] = "Bangalore"
   state["business_type"] = "coffee shop"

3. before_market_research writes:
   state["current_date"] = "2025-12-10"
   state["pipeline_stage"] = "market_research"

4. MarketResearchAgent writes:
   state["market_research_findings"] = "Demographics analysis..."

5. after_market_research writes:
   state["stages_completed"] = ["market_research"]

6. CompetitorMappingAgent writes:
   state["competitor_analysis"] = "15 competitors found..."

7. GapAnalysisAgent writes:
   state["gap_analysis"] = "Zone viability scores..."

8. StrategyAdvisorAgent writes:
   state["strategic_report"] = {JSON with recommendations}

9. Artifact generators read strategic_report
   and save files as artifacts.
```

## Best Practices

1. Use descriptive snake_case names
2. Check for key existence with `.get()` and defaults
3. Don't mutate nested objects without re-assigning
4. Keep values serializable (str, int, list, dict)
5. Use callbacks to set derived state (like current_date)
