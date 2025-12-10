# Tool Patterns Reference

## Complete Tool Template

```python
# app/tools/my_tool.py
from google.adk.tools import ToolContext
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def my_tool(
    query: str,
    max_results: int = 10,
    tool_context: ToolContext = None
) -> dict:
    """Search for information based on query.

    This tool searches external sources and returns structured results.
    Use when you need to find specific data or verify information.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return (default: 10).

    Returns:
        dict containing:
        - status: "success" or "error"
        - results: List of result objects
        - count: Number of results found
        - error_message: Error details if status is "error"
    """
    try:
        # Access session state
        location = tool_context.state.get("target_location", "")
        business = tool_context.state.get("business_type", "")

        logger.info(f"Searching: {query} for {location}")

        # Perform the operation
        results = perform_search(query, location, max_results)

        return {
            "status": "success",
            "results": results,
            "count": len(results),
        }
    except Exception as e:
        logger.error(f"Tool error: {e}")
        return {
            "status": "error",
            "error_message": str(e),
            "results": [],
        }
```

---

## Export Pattern

```python
# app/tools/__init__.py
from .my_tool import my_tool

__all__ = [
    "search_places",
    "generate_html_report",
    # ... existing tools
    "my_tool",  # Add new tool
]
```

---

## Using Tools in Agents

```python
# app/sub_agents/my_agent/agent.py
from ...tools import my_tool, another_tool

my_agent = LlmAgent(
    name="MyAgent",
    model=FAST_MODEL,
    instruction=INSTRUCTION,
    tools=[my_tool, another_tool],
    output_key="my_output",
)
```

---

## Async Tool for Artifacts

```python
# app/tools/artifact_generator.py
from google.adk.tools import ToolContext
from google.genai import types

async def generate_artifact(
    content: str,
    filename: str,
    tool_context: ToolContext
) -> dict:
    """Generate and save an artifact file.

    Args:
        content: The content to save.
        filename: Output filename (e.g., "report.html").

    Returns:
        dict with status and filename.
    """
    try:
        # Determine MIME type
        mime_types = {
            ".html": "text/html",
            ".png": "image/png",
            ".wav": "audio/wav",
            ".json": "application/json",
        }
        ext = "." + filename.split(".")[-1]
        mime_type = mime_types.get(ext, "application/octet-stream")

        # Create artifact Part
        if isinstance(content, bytes):
            artifact = types.Part.from_bytes(data=content, mime_type=mime_type)
        else:
            artifact = types.Part.from_bytes(
                data=content.encode('utf-8'),
                mime_type=mime_type
            )

        # Save artifact (async!)
        await tool_context.save_artifact(
            filename=filename,
            artifact=artifact
        )

        return {
            "status": "success",
            "artifact_filename": filename,
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
        }
```

---

## External API Integration

```python
# app/tools/api_client.py
import os
import requests
from google.adk.tools import ToolContext

def call_external_api(
    endpoint: str,
    params: dict,
    tool_context: ToolContext
) -> dict:
    """Call an external API.

    Args:
        endpoint: API endpoint path.
        params: Query parameters.

    Returns:
        dict with API response or error.
    """
    api_key = os.environ.get("API_KEY")
    if not api_key:
        return {
            "status": "error",
            "error_message": "API_KEY not configured",
        }

    try:
        response = requests.get(
            f"https://api.example.com/{endpoint}",
            params={**params, "key": api_key},
            timeout=30
        )
        response.raise_for_status()

        return {
            "status": "success",
            "data": response.json(),
        }
    except requests.RequestException as e:
        return {
            "status": "error",
            "error_message": str(e),
        }
```

---

## Built-in Tools

ADK provides built-in tools you can use directly:

```python
from google.adk.tools import google_search

agent = LlmAgent(
    name="SearchAgent",
    tools=[google_search],  # Built-in, no API key needed
    ...
)
```

---

## Tool with State Modification

```python
def update_state_tool(
    key: str,
    value: str,
    tool_context: ToolContext
) -> dict:
    """Update a value in session state.

    Args:
        key: State key to update.
        value: New value.

    Returns:
        dict with status.
    """
    tool_context.state[key] = value
    return {
        "status": "success",
        "message": f"Updated {key}",
    }
```

---

## Docstring Best Practices

The LLM uses docstrings to understand when and how to use tools:

```python
def search_competitors(
    location: str,
    business_type: str,
    radius_meters: int = 1000,
    tool_context: ToolContext = None
) -> dict:
    """Find competitor businesses near a location using Google Maps.

    Use this tool when you need to:
    - Identify existing competitors in an area
    - Map the competitive landscape
    - Find similar businesses nearby

    Args:
        location: Address or place name to search near.
        business_type: Type of business (e.g., "coffee shop", "gym").
        radius_meters: Search radius in meters (default: 1000).

    Returns:
        dict containing:
        - status: "success" or "error"
        - competitors: List of competitor objects with name, address, rating
        - count: Total competitors found
    """
    ...
```
