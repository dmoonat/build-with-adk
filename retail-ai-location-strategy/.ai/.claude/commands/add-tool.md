# Add a New Tool

Guide me through adding a new tool to the retail location strategy agent.

## Steps to Follow

1. **Create the tool file**: `app/tools/NEW_TOOL_NAME.py`

2. **Define the tool function**:
   - Import `ToolContext` from `google.adk.tools`
   - Write docstring explaining when LLM should use it
   - Access state via `tool_context.state`
   - Return dict with `status` key

3. **Export the tool**:
   - Add to `app/tools/__init__.py`

4. **Add to agent**:
   - Import in agent file
   - Add to `tools=[...]` list

## Template

```python
# app/tools/NEW_TOOL_NAME.py
from google.adk.tools import ToolContext

def NEW_TOOL_NAME(query: str, tool_context: ToolContext) -> dict:
    """Description of what this tool does.

    The LLM will read this docstring to decide when to use the tool.

    Args:
        query: What this parameter is for.

    Returns:
        dict with status and results.
    """
    try:
        # Access state if needed
        location = tool_context.state.get("target_location", "")

        # Do the work
        result = perform_operation(query)

        return {
            "status": "success",
            "data": result,
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
        }
```

## For Artifact-Saving Tools

Use `async def` when saving artifacts:

```python
async def generate_artifact(data: str, tool_context: ToolContext) -> dict:
    from google.genai import types

    content = create_content(data)

    artifact = types.Part.from_bytes(
        data=content.encode('utf-8'),
        mime_type="text/html"
    )

    await tool_context.save_artifact(
        filename="my_artifact.html",
        artifact=artifact
    )

    return {"status": "success", "artifact_filename": "my_artifact.html"}
```

Ask me what the new tool should do and I'll help create it.
