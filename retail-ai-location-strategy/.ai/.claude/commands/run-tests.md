# Run Tests

Run the test suite for the retail location strategy agent.

## Available Test Commands

### Quick Tests (No API)
```bash
make test-unit
```
Runs schema validation tests. Fast, no API calls needed.

### IntakeAgent Only (~30 sec)
```bash
make test-intake
```
Quick validation that the agent parses requests correctly.

### All Agents (~5 min)
```bash
make test-agents
```
Tests each agent individually with real API calls.

### Full Pipeline (~15-30 min)
```bash
make test-integration
```
Runs complete end-to-end pipeline tests.

### ADK Evaluations
```bash
make eval           # All evalsets
make eval-intake    # Just intake evalset
make eval-pipeline  # Just pipeline evalset
```

## What to Run

- **Before committing**: `make test-unit`
- **After changing agent**: `make test-intake` or specific agent test
- **Before PR**: `make test-agents`
- **For full validation**: `make test-integration`

## Running Specific Tests

```bash
# Single test file
uv run pytest tests/unit/test_schemas.py -v

# Single test class
uv run pytest tests/integration/test_agents.py::TestIntakeAgent -v

# With output
uv run pytest tests/integration/test_agents.py -v -s
```

Which tests should I run?
