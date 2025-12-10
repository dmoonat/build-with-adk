---
name: adk-debugger
description: Troubleshoot ADK errors and issues. Use when encountering API errors, model overloaded errors, state issues, tool failures, authentication problems, or unexpected agent behavior.
---

# ADK Debugger

## Quick Diagnosis

| Symptom | Likely Cause | Quick Fix |
|---------|--------------|-----------|
| `GOOGLE_API_KEY not set` | Missing .env | Create `app/.env` |
| `503 model overloaded` | Gemini 3 rate limit | Switch to Gemini 2.5 Pro |
| Tool not being called | `output_schema` set | Remove output_schema |
| State variable empty | Key mismatch | Check output_key names |
| TTS fails | Vertex AI mode | Use AI Studio for multi-speaker |

## Common Errors & Fixes

### API Key Issues

**Error**: `GOOGLE_API_KEY not set` or `Invalid API key`

**Fix**: Create `.env` file in `app/` folder (not project root):
```bash
echo "GOOGLE_API_KEY=your_key" >> app/.env
echo "MAPS_API_KEY=your_maps_key" >> app/.env
```

### Model Overloaded (503)

**Error**: `503 UNAVAILABLE - model overloaded`

**Fix**: Edit `app/config.py`:
```python
# Switch from Gemini 3 to 2.5
FAST_MODEL = "gemini-2.5-pro"  # More stable
PRO_MODEL = "gemini-2.5-pro"
```

### Tool Not Called

**Cause**: Using `output_schema` disables tool calling.

**Fix**: Remove `output_schema` or use separate agent:
```python
# DON'T: This disables tools
agent = LlmAgent(
    tools=[my_tool],
    output_schema=MySchema,  # Conflicts!
)

# DO: Separate concerns
tool_agent = LlmAgent(tools=[my_tool], ...)
schema_agent = LlmAgent(output_schema=MySchema, ...)
```

### State Variable Empty

**Cause**: `output_key` doesn't match instruction placeholder.

**Fix**: Ensure names match exactly:
```python
# Agent 1
agent1 = LlmAgent(output_key="market_data", ...)

# Agent 2 instruction must use same key
INSTRUCTION = "Use this data: {market_data}"  # Must match!
```

## Debugging Steps

1. **Check environment**: `cat app/.env`
2. **Run quick test**: `make test-intake`
3. **Check logs**: Look for callback messages
4. **Verify state flow**: Check output_key → instruction placeholders

[See references/common-errors.md for complete error catalog]
