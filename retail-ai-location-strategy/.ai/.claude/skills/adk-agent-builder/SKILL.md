---
name: adk-agent-builder
description: Guide for adding new agents to the ADK pipeline. Use when creating a new LlmAgent, SequentialAgent, or ParallelAgent, or when extending the pipeline with additional processing stages.
---

# ADK Agent Builder

## Quick Start

Create a new agent in 5 steps:

1. Create `app/sub_agents/my_agent/agent.py`
2. Define LlmAgent with instruction, tools, output_key
3. Add callbacks in `app/callbacks/pipeline_callbacks.py`
4. Export in `app/sub_agents/__init__.py`
5. Add to pipeline in `app/agent.py`

## Agent Types

| Type | Purpose | Example |
|------|---------|---------|
| **LlmAgent** | Single LLM call with tools | IntakeAgent, MarketResearchAgent |
| **SequentialAgent** | Run sub-agents in order | Main pipeline |
| **ParallelAgent** | Run sub-agents concurrently | ArtifactGenerationPipeline |

## Minimal Template

```python
from google.adk.agents import LlmAgent
from ...config import FAST_MODEL
from ...callbacks import before_my_agent, after_my_agent

INSTRUCTION = """You are a specialized agent.

TARGET LOCATION: {target_location}
BUSINESS TYPE: {business_type}

Your task is to analyze the data and provide insights.
"""

my_agent = LlmAgent(
    name="MyAgent",
    model=FAST_MODEL,
    description="What this agent does (for orchestrator)",
    instruction=INSTRUCTION,
    tools=[],
    output_key="my_agent_output",
    before_agent_callback=before_my_agent,
    after_agent_callback=after_my_agent,
)
```

## Key Patterns

- **State injection**: Use `{variable}` in instructions to inject state values
- **Output storage**: Set `output_key` to store agent output in session state
- **Callbacks**: Add `before_agent_callback` and `after_agent_callback` for logging
- **Retry config**: Use `generate_content_config` for API retry settings

## Common Mistakes

- Forgetting to export in `__init__.py` files
- Using `output_schema` with tools (disables tool calling)
- Not adding agent to pipeline's `sub_agents` list
- Mismatched state key names between agents

[See references/agent-patterns.md for complete templates and examples]
