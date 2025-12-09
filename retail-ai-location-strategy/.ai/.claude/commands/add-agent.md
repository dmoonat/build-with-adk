# Add a New Agent

Guide me through adding a new agent to the retail location strategy pipeline.

## Steps to Follow

1. **Create the agent directory and files**:
   ```bash
   mkdir -p app/sub_agents/NEW_AGENT_NAME
   touch app/sub_agents/NEW_AGENT_NAME/__init__.py
   touch app/sub_agents/NEW_AGENT_NAME/agent.py
   ```

2. **Define the agent** in `app/sub_agents/NEW_AGENT_NAME/agent.py`:
   - Import `LlmAgent` from `google.adk.agents`
   - Define instruction with `{state_variable}` placeholders
   - Set `output_key` for state storage
   - Add `before_agent_callback` and `after_agent_callback`

3. **Add callbacks** in `app/callbacks/pipeline_callbacks.py`:
   - `before_NEW_AGENT_NAME` - Initialize state, log start
   - `after_NEW_AGENT_NAME` - Track completion, log output

4. **Export the agent**:
   - In `app/sub_agents/NEW_AGENT_NAME/__init__.py`
   - In `app/sub_agents/__init__.py`

5. **Add to pipeline** in `app/agent.py`:
   - Import the agent
   - Add to `sub_agents` list in correct position

## Template

```python
# app/sub_agents/NEW_AGENT_NAME/agent.py
from google.adk.agents import LlmAgent
from google.genai import types

from ...config import FAST_MODEL, RETRY_INITIAL_DELAY, RETRY_ATTEMPTS
from ...callbacks import before_NEW_AGENT_NAME, after_NEW_AGENT_NAME

INSTRUCTION = """You are a specialized agent for...

TARGET LOCATION: {target_location}
BUSINESS TYPE: {business_type}

Your task is to...
"""

NEW_AGENT_NAME_agent = LlmAgent(
    name="NewAgentName",
    model=FAST_MODEL,
    description="Description for orchestrator",
    instruction=INSTRUCTION,
    tools=[],
    output_key="new_agent_output",
    before_agent_callback=before_NEW_AGENT_NAME,
    after_agent_callback=after_NEW_AGENT_NAME,
)
```

Ask me what the new agent should do and I'll help create it.
