# Common Errors Reference

## Authentication Errors

### GOOGLE_API_KEY not set

**Error**:
```
ValueError: GOOGLE_API_KEY environment variable not set
```

**Cause**: Missing or incorrectly placed `.env` file.

**Fix**:
```bash
# Create .env in app/ folder (NOT project root!)
cat > app/.env << EOF
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your_ai_studio_key
MAPS_API_KEY=your_maps_api_key
EOF
```

### Invalid API Key

**Error**:
```
google.api_core.exceptions.InvalidArgument: API key not valid
```

**Cause**: Incorrect or revoked API key.

**Fix**:
1. Verify key at [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Check no extra spaces/newlines in `.env`
3. Regenerate key if necessary

### Vertex AI Authentication

**Error**:
```
google.auth.exceptions.DefaultCredentialsError
```

**Cause**: Not authenticated with gcloud.

**Fix**:
```bash
gcloud auth application-default login
```

---

## Model Errors

### Model Overloaded (503)

**Error**:
```
503 UNAVAILABLE - model overloaded
```

**Cause**: Gemini 3 models can hit capacity limits.

**Fix**: Switch to stable models in `app/config.py`:
```python
# Option 1: Use Gemini 2.5 Pro (recommended)
FAST_MODEL = "gemini-2.5-pro"
PRO_MODEL = "gemini-2.5-pro"

# Option 2: Add retry configuration
from google.genai import types

generate_content_config=types.GenerateContentConfig(
    http_options=types.HttpOptions(
        retry_options=types.HttpRetryOptions(
            initial_delay=2.0,
            attempts=5,
        ),
    ),
)
```

### Model Not Found

**Error**:
```
404 NOT_FOUND - Model not found
```

**Cause**: Invalid model name or not available in region.

**Fix**: Use valid model names:
```python
# Valid model names (December 2025)
FAST_MODEL = "gemini-2.5-pro"
PRO_MODEL = "gemini-2.5-pro"
IMAGE_MODEL = "gemini-3-pro-image-preview"
TTS_MODEL = "gemini-2.5-flash-preview-tts"
```

---

## Tool Errors

### Tool Not Called

**Symptom**: Agent ignores tools and responds with text.

**Cause**: `output_schema` disables tool calling.

**Fix**:
```python
# WRONG: output_schema + tools conflicts
agent = LlmAgent(
    tools=[my_tool],
    output_schema=MySchema,  # This disables tools!
)

# CORRECT: Choose one
tool_agent = LlmAgent(tools=[my_tool], ...)
schema_agent = LlmAgent(output_schema=MySchema, ...)
```

### ToolContext Not Available

**Error**:
```
TypeError: my_tool() missing required argument: 'tool_context'
```

**Cause**: Not including ToolContext in function signature.

**Fix**:
```python
from google.adk.tools import ToolContext

def my_tool(query: str, tool_context: ToolContext) -> dict:
    #                   ^^^^^^^^^^^^^^^^^^^^^^^^^^
    # Always include tool_context as last parameter!
    ...
```

### Async Tool Error

**Error**:
```
RuntimeError: cannot call save_artifact from synchronous context
```

**Cause**: Using `save_artifact()` in sync function.

**Fix**:
```python
# WRONG
def my_tool(data: str, tool_context: ToolContext):
    await tool_context.save_artifact(...)  # Error!

# CORRECT
async def my_tool(data: str, tool_context: ToolContext):
    await tool_context.save_artifact(...)  # Works!
```

---

## State Errors

### State Variable Empty

**Symptom**: `{variable}` in instruction shows empty.

**Cause**: Mismatch between `output_key` and placeholder.

**Fix**:
```python
# Agent 1: Sets state
agent1 = LlmAgent(
    output_key="market_research_findings",  # Key name
    ...
)

# Agent 2: Must use EXACT same name
INSTRUCTION = """
Use this research: {market_research_findings}
"""  #               ^^^^^^^^^^^^^^^^^^^^^^^^ Must match!
```

### State Not Persisting

**Symptom**: State changes don't carry to next agent.

**Cause**: Using wrong state prefix or not using shared state.

**Fix**: Use state correctly in callbacks:
```python
def after_my_agent(callback_context: CallbackContext):
    # Access state
    value = callback_context.state.get("key", "default")

    # Modify state
    callback_context.state["my_key"] = "my_value"
```

---

## TTS/Audio Errors

### Multi-Speaker TTS Fails

**Error**:
```
multi_speaker_voice_config not supported
```

**Cause**: Multi-speaker only works in AI Studio, not Vertex AI.

**Fix**: For multi-speaker podcast audio:
```bash
# app/.env
GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

Or use single-speaker fallback for Vertex AI (automatic).

---

## Pipeline Errors

### Agent Not in Pipeline

**Symptom**: New agent doesn't run.

**Cause**: Not added to `sub_agents` list.

**Fix**: Add to `app/agent.py`:
```python
location_strategy_pipeline = SequentialAgent(
    sub_agents=[
        intake_agent,
        market_research_agent,
        my_new_agent,  # Add here!
        ...
    ],
)
```

### Import Error

**Error**:
```
ImportError: cannot import name 'my_agent'
```

**Cause**: Missing exports.

**Fix**: Export in both `__init__.py` files:
```python
# app/sub_agents/my_agent/__init__.py
from .agent import my_agent

# app/sub_agents/__init__.py
from .my_agent import my_agent
__all__ = [..., "my_agent"]
```

---

## Debugging Commands

```bash
# Quick validation
make test-intake

# Run all agent tests
make test-agents

# Check environment
cat app/.env

# View logs (verbose)
ADK_LOG_LEVEL=DEBUG make dev
```
