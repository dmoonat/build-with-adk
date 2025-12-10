---
name: adk-tool-builder
description: Guide for creating custom ADK tools. Use when adding new function tools, working with ToolContext, saving artifacts, or integrating external APIs into the agent pipeline.
---

# ADK Tool Builder

## Quick Start

1. Create `app/tools/my_tool.py`
2. Use signature: `def my_tool(param: str, tool_context: ToolContext) -> dict`
3. Export in `app/tools/__init__.py`
4. Add to agent's `tools=[my_tool]` list

## Basic Tool Template

```python
from google.adk.tools import ToolContext

def my_tool(query: str, tool_context: ToolContext) -> dict:
    """Search for relevant information.

    Args:
        query: The search query.

    Returns:
        dict with status and results.
    """
    try:
        # Access state if needed
        location = tool_context.state.get("target_location", "")

        # Perform the operation
        results = do_something(query, location)

        return {
            "status": "success",
            "results": results,
            "count": len(results),
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
        }
```

## Key Patterns

| Pattern | Usage |
|---------|-------|
| **ToolContext** | Always include as last parameter |
| **State access** | `tool_context.state.get("key")` |
| **Return format** | Always return dict with "status" key |
| **Async tools** | Use `async def` for `save_artifact()` |
| **Docstrings** | LLM uses these to understand the tool |

## Async Tool (for Artifacts)

```python
async def save_report(html: str, tool_context: ToolContext) -> dict:
    """Save HTML report as artifact."""
    artifact = types.Part.from_bytes(
        data=html.encode('utf-8'),
        mime_type="text/html"
    )
    await tool_context.save_artifact(
        filename="report.html",
        artifact=artifact
    )
    return {"status": "success", "filename": "report.html"}
```

## Common Mistakes

- Forgetting `tool_context: ToolContext` parameter
- Not handling exceptions properly
- Missing docstring (LLM needs it!)
- Using sync for `save_artifact()` (must be async)

[See references/tool-patterns.md for API examples and advanced patterns]
