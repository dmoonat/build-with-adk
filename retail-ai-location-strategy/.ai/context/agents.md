# Agents Reference

## IntakeAgent

**Purpose**: Parse natural language request into structured data.

**File**: `app/sub_agents/intake_agent/agent.py`

**Input**: User query (e.g., "coffee shop in Bangalore")

**Output State Keys**:
- `target_location` (str)
- `business_type` (str)

**Tools**: None

**Notes**: Wrapped as `AgentTool` for root agent to call.

---

## MarketResearchAgent

**Purpose**: Research market viability using live web search.

**File**: `app/sub_agents/market_research/agent.py`

**Input State Keys**: `target_location`, `business_type`

**Output State Key**: `market_research_findings`

**Tools**: `google_search` (built-in)

**Callbacks**: `before_market_research`, `after_market_research`

**Notes**: Uses `{variable}` state injection in instruction.

---

## CompetitorMappingAgent

**Purpose**: Map real competitors using Google Maps Places API.

**File**: `app/sub_agents/competitor_mapping/agent.py`

**Input State Keys**: `target_location`, `business_type`

**Output State Key**: `competitor_analysis`

**Tools**: `search_places` (custom)

**Callbacks**: `before_competitor_mapping`, `after_competitor_mapping`

**Notes**: Requires `MAPS_API_KEY` environment variable.

---

## GapAnalysisAgent

**Purpose**: Quantitative analysis using Python code execution.

**File**: `app/sub_agents/gap_analysis/agent.py`

**Input State Keys**: `competitor_analysis`, `market_research_findings`

**Output State Key**: `gap_analysis`

**Tools**: `BuiltInCodeExecutor` (sandboxed Python)

**Callbacks**: `before_gap_analysis`, `after_gap_analysis`

**Notes**: Agent writes and runs pandas code for viability scores.

---

## StrategyAdvisorAgent

**Purpose**: Synthesize all data into strategic recommendations.

**File**: `app/sub_agents/strategy_advisor/agent.py`

**Input State Keys**: All previous stage outputs

**Output State Key**: `strategic_report` (JSON)

**Tools**: None (output_schema disables tools)

**Callbacks**: `before_strategy_advisor`, `after_strategy_advisor`

**Config**: `ThinkingConfig` for extended reasoning

**Output Schema**: `LocationIntelligenceReport` (Pydantic)

---

## ReportGeneratorAgent

**Purpose**: Generate McKinsey/BCG-style HTML executive report.

**File**: `app/sub_agents/report_generator/agent.py`

**Input State Keys**: `strategic_report`

**Output Artifact**: `executive_report.html`

**Tools**: `generate_html_report` (async)

**Callbacks**: `before_report_generator`, `after_report_generator`

---

## InfographicGeneratorAgent

**Purpose**: Generate visual infographic using Gemini image generation.

**File**: `app/sub_agents/infographic_generator/agent.py`

**Input State Keys**: `strategic_report`

**Output Artifact**: `infographic.png`

**Tools**: `generate_infographic` (async)

**Model**: `gemini-3-pro-image-preview`

**Config**: `response_modalities=["TEXT", "IMAGE"]`

---

## AudioOverviewAgent

**Purpose**: Generate podcast-style audio summary.

**File**: `app/sub_agents/audio_overview/agent.py`

**Input State Keys**: `strategic_report`

**Output Artifact**: `audio_overview.wav`

**Tools**: `generate_audio_overview` (async)

**Model**: `gemini-2.5-flash-preview-tts`

**Config**: Multi-speaker (Kore + Puck) in AI Studio, single in Vertex

---

## ArtifactGenerationPipeline

**Purpose**: Run all artifact generators in parallel.

**File**: `app/sub_agents/artifact_generation/agent.py`

**Type**: `ParallelAgent`

**Sub-agents**:
- ReportGeneratorAgent
- InfographicGeneratorAgent
- AudioOverviewAgent

**Notes**: ~40% faster than sequential execution.
