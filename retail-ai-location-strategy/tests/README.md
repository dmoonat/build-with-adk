# Testing Guide for Retail AI Location Strategy

This directory contains tests and evaluations for the Retail AI Location Strategy agents built with Google ADK (Agent Development Kit).

## Quick Start

```bash
# Run all tests
make test

# Run only unit tests (fast, no API calls)
make test-unit

# Run IntakeAgent test (quick validation, ~30 seconds)
make test-intake

# Run all individual agent tests (~2-5 minutes)
make test-agents

# Run full pipeline integration tests (~15-30 minutes)
make test-integration
```

---

## Understanding Tests vs Evaluations

When building production AI agent systems, you need two complementary quality assurance approaches: **Tests** and **Evaluations**. Understanding when and why to use each is critical for shipping reliable agents.

### The Key Difference

| Aspect | Tests (pytest) | Evaluations (ADK eval) |
|--------|----------------|------------------------|
| **Purpose** | Verify correctness | Measure quality |
| **Question answered** | "Does it work?" | "How well does it work?" |
| **Output** | Pass/Fail | Scores (0.0-1.0) |
| **Speed** | Fast (seconds) | Slow (minutes) |
| **Scope** | Individual components | End-to-end behavior |
| **When to run** | Every commit | Pre-release, regression |

### Tests: Catching Breakages

Tests answer: **"Did I break something?"**

```
Developer makes change → Run tests → Pass? → Safe to merge
                                   → Fail? → Fix before merging
```

Use tests to verify:
- Agents can be imported without errors
- Schemas validate correctly
- Individual agents produce expected state keys
- Tools return expected data structures
- Pipeline stages execute in correct order

**Example:** After refactoring IntakeAgent, run `make test-intake` to ensure it still extracts `target_location` and `business_type` correctly.

### Evaluations: Measuring Quality

Evaluations answer: **"Is the agent good enough for production?"**

```
Before release → Run evals → Score > threshold? → Ship it
                           → Score < threshold? → Improve agent
```

Use evaluations to measure:
- Response quality and coherence
- Semantic similarity to expected outputs
- Tool selection accuracy
- End-to-end user experience
- Regression in model behavior after updates

**Example:** Before deploying a new model version, run `make eval` to ensure response quality hasn't degraded.

### The Testing Pyramid for AI Agents

```
                    ┌─────────────┐
                    │   Evals     │  ← Slow, comprehensive
                    │  (quality)  │     Run before releases
                    ├─────────────┤
                    │ Integration │  ← Medium speed
                    │   Tests     │     Run on PRs
                    ├─────────────┤
                    │    Unit     │  ← Fast, focused
                    │   Tests     │     Run on every commit
                    └─────────────┘
```

**Bottom (Unit):** Fast, focused tests that catch obvious bugs. Run constantly.

**Middle (Integration):** Test real agent behavior with real APIs. Run on pull requests.

**Top (Evals):** Comprehensive quality measurement. Run before releases or when comparing model versions.

### Production System Benefits

#### 1. Confidence in Deployments

Without tests/evals, deploying agent changes is risky:
- Did I break the intake parsing?
- Does the competitor mapping still work?
- Is the report quality acceptable?

With tests/evals, you have data-driven confidence:
```bash
make test-agents  # All agents work ✓
make eval         # Quality scores meet thresholds ✓
# Safe to deploy
```

#### 2. Regression Detection

LLM behavior can change unexpectedly (model updates, API changes). Regular evals catch regressions:

```
Week 1: response_match_score = 0.85  ← Baseline
Week 2: response_match_score = 0.82  ← Slight drop, investigate
Week 3: response_match_score = 0.71  ← Significant regression!
```

#### 3. A/B Testing Agent Changes

When improving agents, evals provide objective comparison:

```
Current agent:  response_match_score = 0.78
New prompt:     response_match_score = 0.84  ← Better, ship it!
Alternative:    response_match_score = 0.75  ← Worse, discard
```

#### 4. Continuous Integration Pipeline

A production-grade CI pipeline looks like:

```yaml
# On every commit
- make test-unit        # ~2 seconds

# On pull requests
- make test-agents      # ~2-5 minutes

# Before release
- make eval             # ~30-60 minutes
- Compare scores to baseline
- Block release if scores drop significantly
```

### When to Use What

| Scenario | Use |
|----------|-----|
| "I changed a Pydantic schema" | `make test-unit` |
| "I modified an agent's prompt" | `make test-agents` + `make eval` |
| "I'm upgrading the model version" | `make eval` (compare before/after) |
| "I fixed a bug in a tool" | `make test-agents` |
| "I'm preparing a release" | Full test suite + evals |
| "CI/CD on every commit" | `make test-unit` |
| "CI/CD on pull requests" | `make test-agents` |

### Cost Considerations

Tests and evals have different cost profiles:

| Type | API Calls | LLM Tokens | Time | Cost |
|------|-----------|------------|------|------|
| Unit tests | 0 | 0 | ~2s | Free |
| Integration (1 agent) | 1-3 | ~1K | ~30s | ~$0.01 |
| Integration (all agents) | 10-20 | ~10K | ~5m | ~$0.10 |
| Eval (1 case, full pipeline) | 50+ | ~100K | ~10m | ~$1.00 |
| Eval (5 cases) | 250+ | ~500K | ~50m | ~$5.00 |

**Tip:** Run expensive evals selectively (pre-release, weekly) rather than on every commit.

---

## Prerequisites

Before running integration tests, ensure you have API keys configured in `app/.env`:

```bash
# For AI Studio (default)
GOOGLE_API_KEY=your_api_key
MAPS_API_KEY=your_maps_key
GOOGLE_GENAI_USE_VERTEXAI=FALSE

# For Vertex AI
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your_project
GOOGLE_CLOUD_LOCATION=us-central1
MAPS_API_KEY=your_maps_key
```

## Directory Structure

```
tests/
├── README.md              # This file
├── conftest.py            # Shared pytest fixtures
├── __init__.py
├── unit/                  # Unit tests (no API calls)
│   ├── __init__.py
│   └── test_schemas.py    # Pydantic schema validation tests
├── integration/           # Integration tests (requires API keys)
│   ├── __init__.py
│   └── test_agents.py     # Individual agent tests using Runner
└── evalsets/              # ADK evaluation datasets
    ├── intake.evalset.json
    └── pipeline.evalset.json
```

## Test Types

### 1. Unit Tests (`tests/unit/`)

Fast tests that don't require API keys. Run in ~2 seconds.

| File | Description |
|------|-------------|
| `test_schemas.py` | Validates Pydantic schemas for report generation |

**Run unit tests:**
```bash
make test-unit
```

### 2. Integration Tests (`tests/integration/`)

Tests that use real APIs to validate agent behavior. Each test uses ADK's `Runner` to execute individual agents in isolation.

| Test Class | Agent | Description | Time |
|------------|-------|-------------|------|
| `TestIntakeAgent` | IntakeAgent | Validates request parsing (location, business type) | ~10-30s |
| `TestMarketResearchAgent` | MarketResearchAgent | Tests market research with Google Search | ~30-60s |
| `TestCompetitorMappingAgent` | CompetitorMappingAgent | Tests competitor mapping with Maps API | ~30-60s |
| `TestAgentModuleImport` | All | Verifies all agents can be imported | ~2s |

**Run integration tests:**
```bash
# Quick test - just IntakeAgent
make test-intake

# All individual agents
make test-agents

# Full pipeline (all agents in sequence)
make test-integration
```

### 3. ADK Evaluations (`tests/evalsets/`)

Evaluation datasets for ADK's built-in `AgentEvaluator`. These run the full agent pipeline and measure response quality.

| File | Description |
|------|-------------|
| `intake.evalset.json` | Tests IntakeAgent parsing accuracy |
| `pipeline.evalset.json` | End-to-end pipeline evaluation |

**Run evaluations:**
```bash
# Run all evalsets
make eval

# Run specific evalset
make eval-intake
```

---

## How to Add New Tests

### Adding a Unit Test

Unit tests validate logic without API calls. Great for schemas, utilities, and data transformations.

**Step 1:** Create a test file in `tests/unit/`:

```python
# tests/unit/test_my_feature.py

import pytest
from app.my_module import my_function

class TestMyFeature:
    """Tests for my_feature module."""

    def test_basic_functionality(self):
        """Test the happy path."""
        result = my_function("input")
        assert result == "expected_output"

    def test_edge_case(self):
        """Test edge case handling."""
        result = my_function("")
        assert result is None
```

**Step 2:** Run your test:
```bash
uv run pytest tests/unit/test_my_feature.py -v
```

### Adding an Integration Test for a Sub-Agent

Integration tests validate real agent behavior. Use the `run_agent_test` helper function.

**Step 1:** Add a test class to `tests/integration/test_agents.py`:

```python
@pytest.mark.integration
class TestMyNewAgent:
    """Test MyNewAgent in isolation."""

    @pytest.mark.asyncio
    @pytest.mark.timeout(120)  # Adjust timeout as needed
    async def test_my_agent_basic(self):
        """Test basic functionality of MyNewAgent."""
        from app.sub_agents.my_new_agent import my_new_agent

        result = await run_agent_test(
            agent=my_new_agent,
            query="Test query for the agent",
            session_state={
                # Pre-populate state if needed by the agent
                "target_location": "San Francisco, CA",
                "business_type": "restaurant",
            },
        )

        # Verify the agent produced expected output in state
        state = result["state"]
        assert "my_output_key" in state
        assert len(state["my_output_key"]) > 50  # Ensure substantial output
```

**Step 2:** Run your test:
```bash
uv run pytest tests/integration/test_agents.py::TestMyNewAgent -v -s --timeout=120
```

### Understanding the `run_agent_test` Helper

The `run_agent_test` function is the core of our integration testing approach:

```python
async def run_agent_test(
    agent: Any,           # The ADK agent to test
    query: str,           # User query to send
    session_state: dict | None = None,  # Initial session state
) -> dict[str, Any]:
    """
    Run a single agent with a query and return results.

    Returns:
        dict with:
        - 'response': The agent's text response (str)
        - 'state': The updated session state (dict)
    """
```

**Key concepts:**
- Uses `InMemorySessionService` for isolated sessions
- Uses ADK's `Runner` to execute the agent
- Returns both the response text and updated session state
- Each test runs in a fresh session (no state pollution)

---

## How to Add ADK Evaluations

ADK evaluations use the `AgentEvaluator` to run your agent against test cases and measure quality metrics.

### EvalSet Format (Pydantic Schema)

Each evalset is a JSON file following the ADK `EvalSet` Pydantic schema:

```json
{
  "eval_set_id": "unique_identifier",
  "name": "Human-readable name",
  "description": "Description of what this evalset tests",
  "eval_cases": [
    {
      "eval_id": "case_unique_id",
      "conversation": [
        {
          "invocation_id": "invocation-uuid",
          "user_content": {
            "parts": [{"text": "User input message"}],
            "role": "user"
          },
          "final_response": {
            "parts": [{"text": "Expected response pattern"}],
            "role": "model"
          },
          "intermediate_data": {
            "tool_uses": [
              {"name": "tool_name", "args": {}}
            ],
            "intermediate_responses": []
          }
        }
      ],
      "session_input": {
        "app_name": "retail_location_strategy",
        "user_id": "test_user",
        "state": {}
      }
    }
  ]
}
```

| Field | Description |
|-------|-------------|
| `eval_set_id` | Unique identifier for the evalset |
| `name` | Human-readable name |
| `description` | What this evalset tests |
| `eval_cases` | List of evaluation cases |
| `eval_id` | Unique identifier for each case |
| `conversation` | List of conversation turns (invocations) |
| `user_content` | The user's input message |
| `final_response` | Expected response for semantic comparison |
| `intermediate_data.tool_uses` | Expected tools to be called |
| `session_input` | Initial session configuration |

### Example: Adding an Evalset for a New Scenario

**Step 1:** Create `tests/evalsets/my_scenario.evalset.json`:

```json
{
  "eval_set_id": "my_scenario_eval",
  "name": "My Scenario Evaluation",
  "description": "Tests for my specific scenario",
  "eval_cases": [
    {
      "eval_id": "gym_seattle",
      "conversation": [
        {
          "invocation_id": "inv-001",
          "user_content": {
            "parts": [{"text": "I want to open a gym in downtown Seattle"}],
            "role": "user"
          },
          "final_response": {
            "parts": [{"text": "Based on my analysis of downtown Seattle for your gym"}],
            "role": "model"
          },
          "intermediate_data": {
            "tool_uses": [
              {"name": "IntakeAgent", "args": {}},
              {"name": "google_search", "args": {}}
            ],
            "intermediate_responses": []
          }
        }
      ],
      "session_input": {
        "app_name": "retail_location_strategy",
        "user_id": "test_user",
        "state": {}
      }
    }
  ]
}
```

**Step 2:** Run the evaluation:
```bash
uv run adk eval app tests/evalsets/my_scenario.evalset.json
```

### Evaluation Metrics

The ADK evaluator computes:

| Metric | Description |
|--------|-------------|
| `response_match_score` | Semantic similarity to reference (0.0-1.0) |
| `tool_trajectory_avg_score` | Accuracy of tool usage patterns |
| State validation | Checks expected values in session state |

**Tips:**
- Start with `response_match_score` threshold of 0.6 and adjust
- Use `tool_trajectory_avg_score` to validate correct tool selection
- For long-running tests, use `--timeout=600`

---

## Testing Best Practices

### 1. Test Agents in Isolation First

Test each sub-agent independently before testing the full pipeline:

```
IntakeAgent → MarketResearchAgent → CompetitorMappingAgent → ...
```

This makes debugging easier and tests run faster.

### 2. Use Appropriate Timeouts

| Agent Type | Recommended Timeout |
|------------|---------------------|
| Simple parsing (IntakeAgent) | 60s |
| API-dependent (MarketResearch, Competitor) | 120s |
| Complex reasoning (GapAnalysis, Strategy) | 180s |
| Full pipeline | 600-1800s |

### 3. Validate State, Not Just Response

Agents communicate through session state. Always verify the state contains expected keys:

```python
# Good: Check state structure
state = result["state"]
parsed = state.get("parsed_request", {})
assert "target_location" in parsed

# Also good: Check response exists
assert result["response"] is not None
assert len(result["response"]) > 10
```

### 4. Use Fixtures for Common State

Define reusable state in `conftest.py`:

```python
@pytest.fixture
def sample_intake_state() -> dict[str, Any]:
    return {
        "target_location": "Indiranagar, Bangalore",
        "business_type": "coffee shop",
    }
```

Then use in tests:

```python
async def test_market_research(self, sample_intake_state):
    result = await run_agent_test(
        agent=market_research_agent,
        query="Research the market",
        session_state=sample_intake_state,
    )
```

### 5. Mark Tests Appropriately

```python
@pytest.mark.integration  # Requires API keys
@pytest.mark.asyncio       # Async test
@pytest.mark.timeout(120)  # Timeout in seconds
async def test_my_agent(self):
    ...
```

---

## Troubleshooting

### Tests Timing Out

If tests are timing out, check:
1. API keys are valid in `app/.env`
2. Network connectivity to Google APIs
3. Increase timeout: `@pytest.mark.timeout(300)`

### Import Errors

If you see import errors:
```bash
# Reinstall dependencies
make install

# Or with uv directly
uv sync --dev
```

### State Not Found

If session state is empty or missing keys:
1. Check the agent's `output_key` configuration
2. Verify the agent is actually storing to state (not just responding)
3. Print the full state for debugging: `print(f"State: {result['state']}")`

### Running Specific Tests

```bash
# Run a specific test class
uv run pytest tests/integration/test_agents.py::TestIntakeAgent -v

# Run a specific test method
uv run pytest tests/integration/test_agents.py::TestIntakeAgent::test_parse_coffee_shop_bangalore -v

# Run with print output
uv run pytest tests/integration/test_agents.py -v -s
```

---

## Summary

| What to Test | Where | Command |
|--------------|-------|---------|
| Schemas, utilities | `tests/unit/` | `make test-unit` |
| Individual agents | `tests/integration/` | `make test-agents` |
| Full pipeline | `tests/integration/` | `make test-integration` |
| Response quality | `tests/evalsets/` | `make eval` |

Start with unit tests, then IntakeAgent, then build up to more complex agents. This incremental approach makes debugging much easier.
