# Architecture Reference

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    LocationStrategyPipeline                      │
│                      (SequentialAgent)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────────┐    ┌───────────────┐  │
│  │ IntakeAgent  │───▶│MarketResearchAgent│───▶│CompetitorMapping│ │
│  │              │    │                  │    │    Agent      │  │
│  │ Extracts:    │    │ Uses:            │    │ Uses:         │  │
│  │ • location   │    │ • google_search  │    │ • Places API  │  │
│  │ • business   │    │                  │    │               │  │
│  └──────────────┘    └──────────────────┘    └───────────────┘  │
│         │                    │                      │           │
│         ▼                    ▼                      ▼           │
│   target_location    market_research_     competitor_analysis   │
│   business_type          findings                               │
│                                                                  │
│  ┌──────────────┐    ┌──────────────────┐                       │
│  │GapAnalysisAgent│───▶│StrategyAdvisor  │                       │
│  │              │    │     Agent        │                       │
│  │ Uses:        │    │ Uses:            │                       │
│  │ • code exec  │    │ • extended       │                       │
│  │ • pandas     │    │   thinking       │                       │
│  └──────────────┘    └──────────────────┘                       │
│         │                    │                                  │
│         ▼                    ▼                                  │
│    gap_analysis       strategic_report                          │
│                              │                                  │
│  ┌───────────────────────────▼─────────────────────────────────┐│
│  │              ArtifactGenerationPipeline                     ││
│  │                   (ParallelAgent)                           ││
│  ├─────────────────────────────────────────────────────────────┤│
│  │  ┌─────────────┐  ┌─────────────────┐  ┌─────────────────┐ ││
│  │  │   Report    │  │   Infographic   │  │  AudioOverview  │ ││
│  │  │  Generator  │  │    Generator    │  │     Agent       │ ││
│  │  │             │  │                 │  │                 │ ││
│  │  │ Outputs:    │  │ Outputs:        │  │ Outputs:        │ ││
│  │  │ report.html │  │ infographic.png │  │ audio_overview  │ ││
│  │  │             │  │                 │  │    .wav         │ ││
│  │  └─────────────┘  └─────────────────┘  └─────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## State Flow

```
User Input: "I want to open a coffee shop in Indiranagar, Bangalore"
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                         IntakeAgent                              │
│  Extracts structured data from natural language                  │
├─────────────────────────────────────────────────────────────────┤
│  OUTPUT:                                                         │
│    state["target_location"] = "Indiranagar, Bangalore"          │
│    state["business_type"] = "coffee shop"                       │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                     MarketResearchAgent                          │
│  Instruction: "Research {target_location} for {business_type}"   │
├─────────────────────────────────────────────────────────────────┤
│  INPUT: target_location, business_type                          │
│  TOOL: google_search                                             │
│  OUTPUT: state["market_research_findings"]                       │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CompetitorMappingAgent                        │
│  Instruction: "Find competitors near {target_location}"         │
├─────────────────────────────────────────────────────────────────┤
│  INPUT: target_location, business_type                          │
│  TOOL: search_places (Google Maps API)                          │
│  OUTPUT: state["competitor_analysis"]                           │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      GapAnalysisAgent                            │
│  Instruction: "Analyze: {market_research_findings},             │
│               {competitor_analysis}"                             │
├─────────────────────────────────────────────────────────────────┤
│  INPUT: market_research_findings, competitor_analysis           │
│  TOOL: BuiltInCodeExecutor (Python/pandas)                      │
│  OUTPUT: state["gap_analysis"]                                  │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    StrategyAdvisorAgent                          │
│  Instruction: "Synthesize: {gap_analysis}, {market_research}"   │
├─────────────────────────────────────────────────────────────────┤
│  INPUT: gap_analysis, market_research_findings, competitor_     │
│         analysis                                                 │
│  FEATURE: ThinkingConfig (extended reasoning)                   │
│  OUTPUT: state["strategic_report"] (Pydantic schema)            │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                 ArtifactGenerationPipeline                       │
│                      (ParallelAgent)                             │
├─────────────────────────────────────────────────────────────────┤
│  INPUT: strategic_report                                         │
│  OUTPUTS (concurrent):                                           │
│    • report.html (executive HTML report)                        │
│    • infographic.png (visual summary)                           │
│    • audio_overview.wav (podcast-style audio)                   │
└─────────────────────────────────────────────────────────────────┘
```

## Key Files

| File | Purpose |
|------|---------|
| `app/agent.py` | Root agent, pipeline definition |
| `app/config.py` | Model names, retry settings |
| `app/sub_agents/*/agent.py` | Individual agent definitions |
| `app/tools/*.py` | Custom tool implementations |
| `app/callbacks/pipeline_callbacks.py` | Lifecycle hooks |
| `app/schemas/report_schema.py` | Pydantic output schema |
