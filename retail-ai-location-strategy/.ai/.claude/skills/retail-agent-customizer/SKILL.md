---
name: retail-agent-customizer
description: Customize the retail agent for different use cases. Use when adapting for different business types, industries, or output formats, or when modifying prompts, adding verticals, or changing the analysis focus.
---

# Retail Agent Customizer

## Common Customizations

| Goal | What to Modify |
|------|----------------|
| Different business type | IntakeAgent + MarketResearchAgent prompts |
| New industry vertical | All agent prompts + StrategyAdvisor criteria |
| Additional output format | Add new agent to ParallelAgent |
| Different analysis criteria | GapAnalysisAgent + report schema |
| Change AI model | `app/config.py` |

## Quick Customizations

### Change Business Vertical

Edit IntakeAgent to recognize new business types:

```python
# app/sub_agents/intake_agent/agent.py
INSTRUCTION = """Extract:
- target_location: The location/city/neighborhood
- business_type: Type of business (e.g., restaurant, gym,
  salon, clinic, coworking space, YOUR_NEW_TYPE)
"""
```

### Modify Research Focus

Edit MarketResearchAgent for industry-specific research:

```python
# app/sub_agents/market_research/agent.py
INSTRUCTION = """Research the following for {target_location}:
- Demographics and foot traffic
- [ADD YOUR CRITERIA HERE]
- Industry-specific trends for {business_type}
"""
```

### Change Output Schema

Edit the Pydantic schema for different report structure:

```python
# app/schemas/report_schema.py
class LocationIntelligenceReport(BaseModel):
    location_score: float
    market_opportunity: str
    # Add your custom fields
    your_custom_field: str
```

### Add New Output Format

Create new artifact agent and add to ParallelAgent:

```python
# app/agent.py
artifact_generation_pipeline = ParallelAgent(
    name="ArtifactGenerationPipeline",
    sub_agents=[
        report_generator_agent,
        infographic_generator_agent,
        audio_overview_agent,
        your_new_output_agent,  # Add here
    ],
)
```

## Key Files to Modify

| Customization | Primary Files |
|---------------|---------------|
| Business types | `app/sub_agents/intake_agent/agent.py` |
| Research focus | `app/sub_agents/market_research/agent.py` |
| Competitor criteria | `app/sub_agents/competitor_mapping/agent.py` |
| Analysis logic | `app/sub_agents/gap_analysis/agent.py` |
| Recommendations | `app/sub_agents/strategy_advisor/agent.py` |
| Report structure | `app/schemas/report_schema.py` |
| Model selection | `app/config.py` |
| Output artifacts | `app/sub_agents/artifact_generation/agent.py` |

[See references/customization-guide.md for detailed examples]
