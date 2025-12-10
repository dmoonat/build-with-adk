# ADK Concepts Deep Dive

## What is ADK?

**Agent Development Kit (ADK)** is Google's framework for building AI agents with Gemini. It provides:

- **Agent abstractions**: LlmAgent, SequentialAgent, ParallelAgent
- **Tool system**: Function calling with ToolContext
- **State management**: Session state for data flow
- **Built-in tools**: google_search, code execution
- **Deployment**: Cloud Run, Vertex AI Agent Engine

Documentation: https://google.github.io/adk-docs/

---

## Agent Types

### LlmAgent

The fundamental building block. Wraps a single LLM call.

```python
from google.adk.agents import LlmAgent

agent = LlmAgent(
    name="MyAgent",
    model="gemini-2.5-pro",
    instruction="You are a helpful assistant.",
    tools=[my_tool],
    output_key="agent_output",
)
```

**Key properties**:
- `name`: Identifier for the agent
- `model`: Gemini model to use
- `instruction`: System prompt (supports `{state_vars}`)
- `tools`: List of callable functions
- `output_key`: Where to store output in state

### SequentialAgent

Runs sub-agents one after another in order.

```python
from google.adk.agents import SequentialAgent

pipeline = SequentialAgent(
    name="Pipeline",
    sub_agents=[agent1, agent2, agent3],
)
```

Each agent can access state set by previous agents.

### ParallelAgent

Runs sub-agents concurrently for performance.

```python
from google.adk.agents import ParallelAgent

parallel = ParallelAgent(
    name="ParallelOutputs",
    sub_agents=[report_agent, image_agent, audio_agent],
)
```

All sub-agents receive the same initial state.

---

## State Management

### Session State

Shared dictionary that persists across agents:

```python
# In tool
def my_tool(query: str, tool_context: ToolContext) -> dict:
    # Read state
    location = tool_context.state.get("target_location")

    # Write state
    tool_context.state["my_key"] = "my_value"
```

### State Injection

Use `{variable}` in instructions to inject state values:

```python
INSTRUCTION = """
Location: {target_location}
Business: {business_type}
Previous Analysis: {market_research_findings}
"""
```

### Output Keys

Agent output is stored in state under `output_key`:

```python
agent = LlmAgent(
    output_key="my_output",  # State key
    ...
)
# After execution: state["my_output"] contains agent response
```

---

## Tools

### Basic Tool

```python
from google.adk.tools import ToolContext

def my_tool(query: str, tool_context: ToolContext) -> dict:
    """Search for information.

    Args:
        query: Search query.

    Returns:
        dict with results.
    """
    return {"status": "success", "results": [...]}
```

### Built-in Tools

```python
from google.adk.tools import google_search

agent = LlmAgent(
    tools=[google_search],  # No API key needed
    ...
)
```

### Code Execution

```python
from google.adk.code_executors import BuiltInCodeExecutor

agent = LlmAgent(
    tools=[BuiltInCodeExecutor()],
    ...
)
```

Agent can write and execute Python code with pandas, numpy, etc.

---

## Callbacks

Lifecycle hooks for agents:

```python
from google.adk.agents.callback_context import CallbackContext

def before_agent(callback_context: CallbackContext):
    """Runs before agent executes."""
    callback_context.state["stage"] = "starting"
    return None  # Continue normally

def after_agent(callback_context: CallbackContext):
    """Runs after agent completes."""
    output = callback_context.state.get("output_key")
    return None  # Continue normally
```

Usage:
```python
agent = LlmAgent(
    before_agent_callback=before_agent,
    after_agent_callback=after_agent,
    ...
)
```

---

## Extended Thinking

Enable reasoning for complex tasks:

```python
from google.genai import types

agent = LlmAgent(
    model="gemini-2.5-pro",
    generate_content_config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_budget_tokens=10000,
        ),
    ),
    ...
)
```

---

## Structured Output

Use Pydantic for typed responses:

```python
from pydantic import BaseModel

class Report(BaseModel):
    title: str
    score: float
    recommendations: list[str]

agent = LlmAgent(
    output_schema=Report,  # Note: Disables tools!
    ...
)
```

**Warning**: `output_schema` disables tool calling.

---

## Artifacts

Save files from tools:

```python
async def save_report(html: str, tool_context: ToolContext):
    artifact = types.Part.from_bytes(
        data=html.encode(),
        mime_type="text/html"
    )
    await tool_context.save_artifact(
        filename="report.html",
        artifact=artifact
    )
```

---

## Running Agents

### Local Development

```bash
# Install
make install

# Run ADK web UI
make dev
# Opens http://localhost:8501
```

### Testing

```python
from google.adk.testing import AdkTestClient

client = AdkTestClient(agent=my_agent)
response = client.send_message("test query")
assert "expected" in response.text
```

### Deployment

- **Cloud Run**: `make deploy`
- **Agent Engine**: Use Agent Starter Pack
