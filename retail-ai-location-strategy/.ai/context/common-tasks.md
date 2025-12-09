# Common Tasks

## Add a New Agent

### Step 1: Create the agent file

```bash
mkdir -p app/sub_agents/my_agent
touch app/sub_agents/my_agent/__init__.py
touch app/sub_agents/my_agent/agent.py
```

### Step 2: Define the agent

```python
# app/sub_agents/my_agent/agent.py
from google.adk.agents import LlmAgent
from google.genai import types

from ...config import FAST_MODEL, RETRY_INITIAL_DELAY, RETRY_ATTEMPTS
from ...callbacks import before_my_agent, after_my_agent

MY_AGENT_INSTRUCTION = """You are a specialized agent for...

TARGET LOCATION: {target_location}
BUSINESS TYPE: {business_type}

Your task is to...
"""

my_agent = LlmAgent(
    name="MyAgent",
    model=FAST_MODEL,
    description="What this agent does (for orchestrator)",
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
    output_key="my_agent_output",  # State key for output
    before_agent_callback=before_my_agent,
    after_agent_callback=after_my_agent,
)
```

### Step 3: Add callbacks

```python
# app/callbacks/pipeline_callbacks.py

def before_my_agent(callback_context: CallbackContext):
    logger.info("MY AGENT: Starting")
    callback_context.state["pipeline_stage"] = "my_agent"
    return None

def after_my_agent(callback_context: CallbackContext):
    output = callback_context.state.get("my_agent_output", "")
    logger.info(f"MY AGENT: Complete - {len(output)} chars")
    stages = callback_context.state.get("stages_completed", [])
    stages.append("my_agent")
    callback_context.state["stages_completed"] = stages
    return None
```

### Step 4: Export the agent

```python
# app/sub_agents/my_agent/__init__.py
from .agent import my_agent

# app/sub_agents/__init__.py
from .my_agent import my_agent
__all__ = [..., "my_agent"]
```

### Step 5: Add to pipeline

```python
# app/agent.py
from .sub_agents.my_agent import my_agent

location_strategy_pipeline = SequentialAgent(
    ...,
    sub_agents=[
        ...,
        my_agent,  # Add in correct order
        ...,
    ],
)
```

---

## Add a New Tool

### Step 1: Create the tool file

```python
# app/tools/my_tool.py
from google.adk.tools import ToolContext

def my_tool(query: str, tool_context: ToolContext) -> dict:
    """Search for something specific.

    Args:
        query: The search query.

    Returns:
        dict with status and results.
    """
    try:
        # Access state if needed
        location = tool_context.state.get("target_location", "")

        # Do the work
        results = perform_search(query, location)

        return {
            "status": "success",
            "results": results,
            "count": len(results),
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
            "results": [],
        }
```

### Step 2: Export the tool

```python
# app/tools/__init__.py
from .my_tool import my_tool

__all__ = [..., "my_tool"]
```

### Step 3: Add to agent

```python
# In agent definition
from ...tools import my_tool

agent = LlmAgent(
    ...,
    tools=[my_tool],
)
```

---

## Add a New Callback

### Step 1: Define the callback

```python
# app/callbacks/pipeline_callbacks.py
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

def before_my_stage(callback_context: CallbackContext) -> Optional[types.Content]:
    """Run before the agent executes."""
    logger.info("Starting my stage")

    # Set state
    callback_context.state["my_key"] = "value"

    # Return None to continue normally
    return None

def after_my_stage(callback_context: CallbackContext) -> Optional[types.Content]:
    """Run after the agent completes."""
    result = callback_context.state.get("output_key", "")
    logger.info(f"Completed: {len(result)} chars")

    # Track completion
    stages = callback_context.state.get("stages_completed", [])
    stages.append("my_stage")
    callback_context.state["stages_completed"] = stages

    return None
```

### Step 2: Export the callback

```python
# app/callbacks/__init__.py
from .pipeline_callbacks import before_my_stage, after_my_stage

__all__ = [..., "before_my_stage", "after_my_stage"]
```

### Step 3: Use in agent

```python
from ...callbacks import before_my_stage, after_my_stage

agent = LlmAgent(
    ...,
    before_agent_callback=before_my_stage,
    after_agent_callback=after_my_stage,
)
```

---

## Add a New Artifact Output

### Step 1: Create async tool

```python
# app/tools/my_artifact.py
from google.adk.tools import ToolContext
from google.genai import types

async def generate_my_artifact(data: str, tool_context: ToolContext) -> dict:
    """Generate my artifact."""
    # Create the content
    content = create_content(data)

    # Create Part object
    artifact = types.Part.from_bytes(
        data=content.encode('utf-8'),
        mime_type="text/html"  # or image/png, audio/wav, etc.
    )

    # Save artifact
    await tool_context.save_artifact(
        filename="my_artifact.html",
        artifact=artifact
    )

    return {
        "status": "success",
        "artifact_filename": "my_artifact.html",
    }
```

### Step 2: Create agent

```python
my_artifact_agent = LlmAgent(
    name="MyArtifactAgent",
    model=FAST_MODEL,
    instruction="Generate artifact from {strategic_report}",
    tools=[generate_my_artifact],
    output_key="my_artifact_result",
)
```

### Step 3: Add to ParallelAgent (optional)

```python
artifact_generation_pipeline = ParallelAgent(
    name="ArtifactGenerationPipeline",
    sub_agents=[
        ...,
        my_artifact_agent,
    ],
)
```

---

## Add a Test

### Unit Test

```python
# tests/unit/test_my_feature.py
import pytest

def test_my_function():
    result = my_function("input")
    assert result == expected

def test_my_schema():
    from app.schemas.my_schema import MySchema
    data = MySchema(field="value")
    assert data.field == "value"
```

### Integration Test

```python
# tests/integration/test_my_agent.py
import pytest
from google.adk.testing import AdkTestClient

@pytest.mark.integration
class TestMyAgent:
    @pytest.fixture
    def client(self):
        from app.sub_agents.my_agent import my_agent
        return AdkTestClient(agent=my_agent)

    def test_my_agent_response(self, client):
        response = client.send_message("test query")
        assert "expected" in response.text
```

Run tests:
```bash
make test-unit
make test-agents
```
