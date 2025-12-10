# Customization Guide

## Example: Healthcare Clinic Vertical

This example shows how to adapt the retail agent for healthcare clinics.

### Step 1: Update IntakeAgent

```python
# app/sub_agents/intake_agent/agent.py

INTAKE_INSTRUCTION = """You are an intake specialist for healthcare location analysis.

Extract:
- target_location: The specific location/neighborhood/city
- business_type: Type of healthcare facility (clinic, dental office,
  urgent care, specialty practice, pharmacy)
- specialty: Medical specialty if mentioned (e.g., dermatology, pediatrics)

Examples:
- "I want to open a dental clinic in downtown Seattle" →
  location: "downtown Seattle", type: "dental clinic"
- "Where should I put my pediatric practice in Austin?" →
  location: "Austin", type: "pediatric practice", specialty: "pediatrics"
"""
```

### Step 2: Update MarketResearchAgent

```python
# app/sub_agents/market_research/agent.py

MARKET_RESEARCH_INSTRUCTION = """Research the healthcare market for {target_location}.

Focus on:
1. Demographics: Age distribution, insurance coverage rates
2. Healthcare access: Existing clinics per capita, hospital proximity
3. Competition: Similar {business_type} facilities in the area
4. Regulations: State/local healthcare licensing requirements
5. Workforce: Availability of medical professionals

Use google_search to find recent data and reports.
"""
```

### Step 3: Update Competitor Analysis

```python
# app/sub_agents/competitor_mapping/agent.py

COMPETITOR_INSTRUCTION = """Map healthcare competitors near {target_location}.

Search for:
- Similar {business_type} facilities
- Hospitals and urgent care centers
- Complementary healthcare services

Evaluate each competitor for:
- Services offered
- Patient ratings
- Insurance networks
- Operating hours
"""
```

### Step 4: Update Analysis Criteria

```python
# app/sub_agents/gap_analysis/agent.py

GAP_ANALYSIS_INSTRUCTION = """Analyze healthcare market opportunity.

Calculate:
- Provider-to-population ratio
- Average wait times for similar services
- Insurance network gaps
- Specialty service availability
- Distance to nearest competitor

Use pandas to create viability scores based on healthcare metrics.
"""
```

### Step 5: Update Output Schema

```python
# app/schemas/report_schema.py

class HealthcareLocationReport(BaseModel):
    location_score: float = Field(description="0-100 viability score")
    provider_ratio: str = Field(description="Providers per 10,000 residents")
    market_gap: str = Field(description="Identified service gaps")
    insurance_landscape: str = Field(description="Major insurance networks")
    regulatory_notes: str = Field(description="Licensing requirements")
    recommendations: list[str] = Field(description="Strategic recommendations")
```

---

## Example: Restaurant Vertical

### Key Changes

```python
# IntakeAgent
- Extract: cuisine_type, price_point, seating_capacity

# MarketResearchAgent
- Focus on: dining trends, food delivery penetration, tourist traffic

# CompetitorMappingAgent
- Evaluate: menu prices, ratings, ambiance, delivery options

# GapAnalysisAgent
- Calculate: cuisine saturation, price point gaps, peak hour traffic

# StrategyAdvisorAgent
- Consider: kitchen requirements, liquor license, parking availability
```

---

## Adding a New Output Type

### Example: Adding a SWOT Analysis Document

#### Step 1: Create the tool

```python
# app/tools/swot_generator.py
from google.adk.tools import ToolContext
from google.genai import types

async def generate_swot_document(
    strengths: str,
    weaknesses: str,
    opportunities: str,
    threats: str,
    tool_context: ToolContext
) -> dict:
    """Generate SWOT analysis document."""
    html = f"""
    <html>
    <head><title>SWOT Analysis</title></head>
    <body>
        <h1>SWOT Analysis</h1>
        <h2>Strengths</h2><p>{strengths}</p>
        <h2>Weaknesses</h2><p>{weaknesses}</p>
        <h2>Opportunities</h2><p>{opportunities}</p>
        <h2>Threats</h2><p>{threats}</p>
    </body>
    </html>
    """

    artifact = types.Part.from_bytes(
        data=html.encode('utf-8'),
        mime_type="text/html"
    )
    await tool_context.save_artifact(
        filename="swot_analysis.html",
        artifact=artifact
    )

    return {"status": "success", "filename": "swot_analysis.html"}
```

#### Step 2: Create the agent

```python
# app/sub_agents/swot_generator/agent.py
from google.adk.agents import LlmAgent
from ...tools import generate_swot_document
from ...config import FAST_MODEL

SWOT_INSTRUCTION = """Create a SWOT analysis based on {strategic_report}.

Extract:
- Strengths: Internal advantages
- Weaknesses: Internal challenges
- Opportunities: External favorable factors
- Threats: External risks

Call generate_swot_document with your analysis.
"""

swot_generator_agent = LlmAgent(
    name="SwotGeneratorAgent",
    model=FAST_MODEL,
    instruction=SWOT_INSTRUCTION,
    tools=[generate_swot_document],
    output_key="swot_result",
)
```

#### Step 3: Add to ParallelAgent

```python
# app/agent.py
from .sub_agents import swot_generator_agent

artifact_generation_pipeline = ParallelAgent(
    name="ArtifactGenerationPipeline",
    sub_agents=[
        report_generator_agent,
        infographic_generator_agent,
        audio_overview_agent,
        swot_generator_agent,  # New!
    ],
)
```

---

## Changing Models

Edit `app/config.py`:

```python
# For cost optimization
FAST_MODEL = "gemini-2.5-flash"
PRO_MODEL = "gemini-2.5-flash"

# For best quality
FAST_MODEL = "gemini-2.5-pro"
PRO_MODEL = "gemini-2.5-pro"

# For latest features (may have availability issues)
FAST_MODEL = "gemini-3-pro-preview"
PRO_MODEL = "gemini-3-pro-preview"
```

---

## Testing Customizations

After making changes:

```bash
# Quick validation
make test-intake

# Full agent tests
make test-agents

# Run with ADK web UI
make dev
```
