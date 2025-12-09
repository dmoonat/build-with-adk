# Troubleshooting

## API Key Issues

### "API key not found"

**Symptom**: Agent fails with API key error.

**Fix**: Ensure `.env` file is in `app/` folder (not project root).

```bash
# Correct location
app/.env

# Create it
cat > app/.env << EOF
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your_key
MAPS_API_KEY=your_maps_key
EOF
```

### "Maps API key not found"

**Symptom**: CompetitorMappingAgent fails.

**Fix**: Add `MAPS_API_KEY` to `app/.env`.

---

## Model Errors

### "Model overloaded" (503)

**Symptom**: Requests fail with 503 errors.

**Fix**:
1. Switch to stable model in `app/config.py`:
   ```python
   FAST_MODEL = "gemini-2.5-pro"  # More stable
   # FAST_MODEL = "gemini-3-pro-preview"  # May have availability issues
   ```
2. Increase retry settings:
   ```python
   RETRY_ATTEMPTS = 5
   RETRY_INITIAL_DELAY = 5
   ```

### "Model not found"

**Symptom**: Model name not recognized.

**Fix**: Check model availability for your API type (AI Studio vs Vertex AI).

---

## Agent Issues

### "output_schema disables tool calling"

**Symptom**: Agent with `output_schema` doesn't call tools.

**Explanation**: This is expected behavior. When you set `output_schema`, the agent outputs structured JSON directly without using tools.

**Fix**: Remove `output_schema` if you need tool calling, or use tools before setting output_schema.

### State variable not found

**Symptom**: `{variable}` in instruction shows literal text.

**Fix**: Ensure previous agent wrote to state with that key name.

```python
# Check the output_key of previous agent
previous_agent = LlmAgent(
    ...,
    output_key="my_state_key",  # This becomes state["my_state_key"]
)

# Use in next agent
next_agent = LlmAgent(
    instruction="Use {my_state_key} to...",
)
```

---

## Tool Issues

### Tool not being called

**Symptom**: Agent describes what it would do but doesn't call tool.

**Fix**:
1. Make tool docstring clear about when to use it
2. Add explicit instruction to use the tool
3. Check that `output_schema` is not set (disables tools)

### ToolContext attribute error

**Symptom**: `AttributeError: 'ToolContext' has no attribute 'state'`

**Fix**: Ensure you're using `ToolContext` from the correct import:
```python
from google.adk.tools import ToolContext
```

---

## Audio/TTS Issues

### "Multi-speaker not supported"

**Symptom**: TTS fails with multi-speaker config.

**Explanation**: Multi-speaker TTS only works in AI Studio mode.

**Fix**: The code automatically falls back to single speaker in Vertex AI mode.

### Audio file won't play

**Symptom**: Generated audio file is silent or corrupted.

**Fix**: The audio tool wraps raw audio in WAV headers. If still not working, check:
1. Audio data is being extracted from response correctly
2. Correct sample rate (24000 Hz for Gemini TTS)

---

## Image Generation Issues

### "No image generated"

**Symptom**: Infographic tool returns error.

**Fix**:
1. Ensure `response_modalities=["TEXT", "IMAGE"]` is set
2. Check model supports image generation (`gemini-3-pro-image-preview`)
3. Check prompt isn't triggering content filters

---

## Testing Issues

### Tests timing out

**Symptom**: Integration tests exceed timeout.

**Fix**:
1. Use `--timeout` flag: `pytest tests/ -v --timeout=300`
2. Run individual agent tests: `make test-intake`
3. Mock external APIs for unit tests

### Import errors in tests

**Symptom**: `ModuleNotFoundError` when running tests.

**Fix**:
```bash
# Ensure dev dependencies installed
uv sync --dev

# Run from project root
cd retail-ai-location-strategy
make test-unit
```

---

## Common Mistakes

### 1. Wrong .env location
Put `.env` in `app/` folder, not project root.

### 2. Forgetting to export
Always add to `__all__` in `__init__.py` files.

### 3. Sync vs Async tools
Use `async def` when calling `tool_context.save_artifact()`.

### 4. Missing callbacks export
Add both before_ and after_ callbacks to `__init__.py`.

### 5. State key typos
Use consistent naming. Check `output_key` matches what you reference.

---

## Getting Help

1. **Tutorial**: `blog/` - Step-by-step guide
2. **Dev Guide**: `DEVELOPER_GUIDE.md` - Architecture details
3. **ADK Docs**: https://google.github.io/adk-docs/
4. **Issues**: https://github.com/google/adk-python/issues
