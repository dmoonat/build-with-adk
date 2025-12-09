# Explain the Agent Pipeline

The Retail AI Location Strategy Agent uses a multi-agent pipeline to analyze locations for retail businesses.

## Pipeline Flow

```
User: "I want to open a coffee shop in Indiranagar, Bangalore"
                    │
                    ▼
┌──────────────────────────────────────────────────────────────┐
│                    Root Agent                                 │
│  - Greets user, asks clarifying questions                     │
│  - Calls IntakeAgent to parse request                         │
│  - Delegates to LocationStrategyPipeline                      │
└──────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────────────────┐
│              IntakeAgent (AgentTool)                          │
│  Extracts: target_location, business_type                     │
└──────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────────────────┐
│         LocationStrategyPipeline (SequentialAgent)            │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Stage 1: MarketResearchAgent                                 │
│  └─ Uses google_search to find demographics, trends           │
│  └─ Output: market_research_findings                          │
│                          │                                    │
│                          ▼                                    │
│  Stage 2A: CompetitorMappingAgent                             │
│  └─ Uses search_places (Google Maps API)                      │
│  └─ Output: competitor_analysis                               │
│                          │                                    │
│                          ▼                                    │
│  Stage 2B: GapAnalysisAgent                                   │
│  └─ Uses BuiltInCodeExecutor (Python sandbox)                 │
│  └─ Calculates viability scores with pandas                   │
│  └─ Output: gap_analysis                                      │
│                          │                                    │
│                          ▼                                    │
│  Stage 3: StrategyAdvisorAgent                                │
│  └─ Uses ThinkingConfig for extended reasoning                │
│  └─ Outputs structured JSON via output_schema                 │
│  └─ Output: strategic_report (Pydantic)                       │
│                          │                                    │
│                          ▼                                    │
│  Stage 4: ArtifactGenerationPipeline (ParallelAgent)          │
│  ├─ ReportGeneratorAgent → executive_report.html              │
│  ├─ InfographicGeneratorAgent → infographic.png               │
│  └─ AudioOverviewAgent → audio_overview.wav                   │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

## Agent Types

| Type | Purpose | Used For |
|------|---------|----------|
| `LlmAgent` | Core agent with LLM | All individual agents |
| `SequentialAgent` | Run in order | LocationStrategyPipeline |
| `ParallelAgent` | Run concurrently | ArtifactGenerationPipeline |
| `AgentTool` | Wrap as tool | IntakeAgent |

## Key Files

- `app/agent.py` - Root agent and pipeline definition
- `app/sub_agents/*/agent.py` - Individual agents
- `app/tools/*.py` - Custom tools
- `app/callbacks/pipeline_callbacks.py` - Lifecycle hooks

## Learning More

- Tutorial: `blog/` directory (9 parts)
- Architecture: `DEVELOPER_GUIDE.md`
- ADK Docs: https://google.github.io/adk-docs/

What aspect would you like me to explain in more detail?
