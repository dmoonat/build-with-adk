# Tools Reference

## Built-in Tools

### google_search

**Import**: `from google.adk.tools import google_search`

**Purpose**: Search the web using Gemini's integrated search.

**Usage**: Add to agent's `tools=[google_search]`

**Notes**: No API key needed. Uses Gemini's built-in search.

---

## Custom Tools

### search_places

**File**: `app/tools/places_search.py`

**Signature**:
```python
def search_places(query: str, tool_context: ToolContext) -> dict:
```

**Purpose**: Search for businesses using Google Maps Places API.

**Parameters**:
- `query`: Search query (e.g., "coffee shop near Indiranagar, Bangalore")
- `tool_context`: Access to session state

**Returns**:
```python
{
    "status": "success" | "error",
    "results": [
        {
            "name": "Business Name",
            "address": "Full address",
            "rating": 4.5,
            "user_ratings_total": 1234,
            "price_level": 2,
            "business_status": "OPERATIONAL",
            "location": {"lat": 12.97, "lng": 77.63}
        }
    ],
    "count": 15
}
```

**Requires**: `MAPS_API_KEY` environment variable.

---

### generate_html_report

**File**: `app/tools/html_report_generator.py`

**Signature**:
```python
async def generate_html_report(report_data: str, tool_context: ToolContext) -> dict:
```

**Purpose**: Generate McKinsey/BCG-style HTML executive report.

**Notes**:
- Uses `tool_context.save_artifact()` to save HTML
- Async function for non-blocking execution
- Returns artifact filename and status

---

### generate_infographic

**File**: `app/tools/image_generator.py`

**Signature**:
```python
async def generate_infographic(data_summary: str, tool_context: ToolContext) -> dict:
```

**Purpose**: Generate infographic using Gemini native image generation.

**Config**:
```python
response_modalities=["TEXT", "IMAGE"]
```

**Notes**:
- Uses `gemini-3-pro-image-preview` model
- Saves PNG artifact via `tool_context.save_artifact()`

---

### generate_audio_overview

**File**: `app/tools/audio_generator.py`

**Signature**:
```python
async def generate_audio_overview(podcast_script: str, tool_context: ToolContext) -> dict:
```

**Purpose**: Generate podcast-style audio using Gemini TTS.

**Config**:
```python
response_modalities=["AUDIO"]
speech_config=SpeechConfig(multi_speaker_voice_config=...)
```

**Voices**:
- AI Studio: Kore (Host A) + Puck (Host B)
- Vertex AI: Kore only (single speaker)

**Notes**:
- Audio is wrapped in WAV headers for compatibility
- Multi-speaker only works in AI Studio mode

---

## Creating a New Tool

1. Create function in `app/tools/my_tool.py`:

```python
from google.adk.tools import ToolContext

def my_tool(param: str, tool_context: ToolContext) -> dict:
    """Description for LLM to understand when to use this tool.

    Args:
        param: What this parameter is for.

    Returns:
        dict with status and results.
    """
    # Access state
    value = tool_context.state.get("key")

    # Do work
    result = ...

    return {
        "status": "success",
        "data": result
    }
```

2. Export in `app/tools/__init__.py`:

```python
from .my_tool import my_tool

__all__ = [..., "my_tool"]
```

3. Add to agent's tools list:

```python
agent = LlmAgent(
    ...,
    tools=[my_tool],
)
```

## Tool Context

`ToolContext` provides:

| Attribute | Purpose |
|-----------|---------|
| `tool_context.state` | Session state (dict) |
| `tool_context.save_artifact()` | Save file artifact |
| `tool_context.actions` | Control agent flow |
