# Architecture

## Pipeline Flow

```
User: "I want to open a coffee shop in Indiranagar, Bangalore"
                    │
                    ▼
┌──────────────────────────────────────────────────────────────┐
│                    Root Agent (LlmAgent)                      │
│  - Greets user                                                │
│  - Asks clarifying questions if needed                        │
│  - Calls IntakeAgent tool                                     │
│  - Delegates to LocationStrategyPipeline                      │
└──────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────────────────┐
│              IntakeAgent (AgentTool)                          │
│  Input: Natural language query                                │
│  Output: target_location, business_type                       │
│  File: app/sub_agents/intake_agent/agent.py                   │
└──────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────────────────┐
│         LocationStrategyPipeline (SequentialAgent)            │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Stage 1: MarketResearchAgent                            │ │
│  │   Tool: google_search (built-in)                        │ │
│  │   Output: market_research_findings                      │ │
│  └─────────────────────────────────────────────────────────┘ │
│                          │                                    │
│                          ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Stage 2A: CompetitorMappingAgent                        │ │
│  │   Tool: search_places (custom, Maps API)                │ │
│  │   Output: competitor_analysis                           │ │
│  └─────────────────────────────────────────────────────────┘ │
│                          │                                    │
│                          ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Stage 2B: GapAnalysisAgent                              │ │
│  │   Tool: BuiltInCodeExecutor (Python sandbox)            │ │
│  │   Output: gap_analysis                                  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                          │                                    │
│                          ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Stage 3: StrategyAdvisorAgent                           │ │
│  │   Config: ThinkingConfig (extended reasoning)           │ │
│  │   Output: strategic_report (Pydantic JSON)              │ │
│  └─────────────────────────────────────────────────────────┘ │
│                          │                                    │
│                          ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Stage 4: ArtifactGenerationPipeline (ParallelAgent)     │ │
│  │                                                         │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │ │
│  │  │   Report    │ │ Infographic │ │    Audio    │       │ │
│  │  │  Generator  │ │  Generator  │ │  Overview   │       │ │
│  │  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘       │ │
│  │         │               │               │               │ │
│  │         ▼               ▼               ▼               │ │
│  │   report.html    infographic.png  audio_overview.wav    │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

## Agent Types Used

| Type | Purpose | Example |
|------|---------|---------|
| `LlmAgent` | Core agent with LLM, tools, callbacks | All individual agents |
| `SequentialAgent` | Run agents in order | LocationStrategyPipeline |
| `ParallelAgent` | Run agents concurrently | ArtifactGenerationPipeline |
| `AgentTool` | Wrap agent as callable tool | IntakeAgent |

## State Flow

```
Initial State
    │
    ├── target_location (from IntakeAgent)
    ├── business_type (from IntakeAgent)
    │
    ├── market_research_findings (from MarketResearchAgent)
    │
    ├── competitor_analysis (from CompetitorMappingAgent)
    │
    ├── gap_analysis (from GapAnalysisAgent)
    │
    └── strategic_report (from StrategyAdvisorAgent)
            │
            └── Used by all artifact generators
```

## Files Structure

```
app/
├── agent.py              # Root agent + pipeline
├── config.py             # Models, retry settings
├── sub_agents/
│   ├── intake_agent/
│   │   └── agent.py      # IntakeAgent definition
│   ├── market_research/
│   │   └── agent.py      # MarketResearchAgent
│   ├── competitor_mapping/
│   │   └── agent.py      # CompetitorMappingAgent
│   ├── gap_analysis/
│   │   └── agent.py      # GapAnalysisAgent
│   ├── strategy_advisor/
│   │   └── agent.py      # StrategyAdvisorAgent
│   ├── report_generator/
│   │   └── agent.py      # ReportGeneratorAgent
│   ├── infographic_generator/
│   │   └── agent.py      # InfographicGeneratorAgent
│   ├── audio_overview/
│   │   └── agent.py      # AudioOverviewAgent
│   └── artifact_generation/
│       └── agent.py      # ParallelAgent wrapper
├── tools/
│   ├── places_search.py
│   ├── html_report_generator.py
│   ├── image_generator.py
│   └── audio_generator.py
├── callbacks/
│   └── pipeline_callbacks.py
└── schemas/
    └── report_schema.py
```
