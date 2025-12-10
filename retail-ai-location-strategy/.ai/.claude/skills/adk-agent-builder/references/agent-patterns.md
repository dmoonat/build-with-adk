# Agent Patterns Reference

## Complete Agent Template

```python
# app/sub_agents/my_agent/agent.py
from google.adk.agents import LlmAgent
from google.genai import types

from ...config import FAST_MODEL, RETRY_INITIAL_DELAY, RETRY_ATTEMPTS
from ...callbacks import before_my_agent, after_my_agent

MY_AGENT_INSTRUCTION = """You are a specialized agent for [PURPOSE].

## Context
TARGET LOCATION: {target_location}
BUSINESS TYPE: {business_type}
PREVIOUS ANALYSIS: {previous_output}

## Task
[Describe what this agent should do]

## Output Format
[Specify expected output structure]
"""

my_agent = LlmAgent(
    name="MyAgent",
    model=FAST_MODEL,
    description="Performs [task] for the pipeline orchestrator",
    instruction=MY_AGENT_INSTRUCTION,
    generate_content_config=types.GenerateContentConfig(
        http_options=types.HttpOptions(
            retry_options=types.HttpRetryOptions(
                initial_delay=RETRY_INITIAL_DELAY,
                attempts=RETRY_ATTEMPTS,
            ),
        ),
    ),
    tools=[],  # Add tools here
    output_key="my_agent_output",
    before_agent_callback=before_my_agent,
    after_agent_callback=after_my_agent,
)
```

---

## Callback Template

```python
# app/callbacks/pipeline_callbacks.py
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def before_my_agent(callback_context: CallbackContext) -> Optional[types.Content]:
    """Run before MyAgent executes."""
    logger.info("MY AGENT: Starting")
    callback_context.state["pipeline_stage"] = "my_agent"
    return None  # Return None to continue normally

def after_my_agent(callback_context: CallbackContext) -> Optional[types.Content]:
    """Run after MyAgent completes."""
    output = callback_context.state.get("my_agent_output", "")
    logger.info(f"MY AGENT: Complete - {len(output)} chars")

    # Track stage completion
    stages = callback_context.state.get("stages_completed", [])
    stages.append("my_agent")
    callback_context.state["stages_completed"] = stages

    return None
```

---

## Export Pattern

```python
# app/sub_agents/my_agent/__init__.py
from .agent import my_agent

__all__ = ["my_agent"]

# app/sub_agents/__init__.py
from .my_agent import my_agent

__all__ = [
    "intake_agent",
    "market_research_agent",
    # ... existing agents
    "my_agent",  # Add new agent
]
```

---

## Adding to Pipeline

```python
# app/agent.py
from .sub_agents import my_agent

location_strategy_pipeline = SequentialAgent(
    name="LocationStrategyPipeline",
    description="Multi-stage analysis pipeline",
    sub_agents=[
        intake_agent,
        market_research_agent,
        competitor_mapping_agent,
        gap_analysis_agent,
        my_agent,  # Insert in correct position
        strategy_advisor_agent,
        artifact_generation_pipeline,
    ],
)
```

---

## SequentialAgent Pattern

```python
from google.adk.agents import SequentialAgent

my_pipeline = SequentialAgent(
    name="MyPipeline",
    description="Runs agents in sequence",
    sub_agents=[
        agent_1,
        agent_2,
        agent_3,
    ],
)
```

---

## ParallelAgent Pattern

```python
from google.adk.agents import ParallelAgent

parallel_outputs = ParallelAgent(
    name="ParallelOutputs",
    description="Runs agents concurrently",
    sub_agents=[
        report_agent,
        infographic_agent,
        audio_agent,
    ],
)
```

---

## Agent with Tools

```python
from ...tools import my_custom_tool, another_tool

my_agent = LlmAgent(
    name="MyAgent",
    model=FAST_MODEL,
    instruction=INSTRUCTION,
    tools=[my_custom_tool, another_tool],
    output_key="my_agent_output",
)
```

---

## Agent with Structured Output

**Warning**: Using `output_schema` disables tool calling!

```python
from ...schemas.my_schema import MyOutputSchema

# Option 1: Structured output (no tools)
structured_agent = LlmAgent(
    name="StructuredAgent",
    model=FAST_MODEL,
    instruction=INSTRUCTION,
    output_schema=MyOutputSchema,  # Disables tools!
    output_key="structured_output",
)

# Option 2: Tools + manual parsing (recommended)
tool_agent = LlmAgent(
    name="ToolAgent",
    model=FAST_MODEL,
    instruction=INSTRUCTION,
    tools=[my_tool],  # Works!
    output_key="tool_output",
)
```

---

## Agent with Extended Thinking

```python
from google.genai import types

thinking_agent = LlmAgent(
    name="ThinkingAgent",
    model=PRO_MODEL,
    instruction=INSTRUCTION,
    generate_content_config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_budget_tokens=10000,
        ),
    ),
    output_key="thinking_output",
)
```

---

## State Injection Examples

```python
# Basic injection
INSTRUCTION = """
Location: {target_location}
Business: {business_type}
"""

# Multi-source injection
INSTRUCTION = """
## Market Research
{market_research_findings}

## Competitors
{competitor_analysis}

## Gap Analysis
{gap_analysis}
"""
```
