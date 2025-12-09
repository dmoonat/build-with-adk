# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Integration tests using Runner to test individual sub-agents.

This approach tests each agent in isolation, which is faster and more
debuggable than running the full pipeline for each test case.

Run with:
    make test-intake     # Quick test - just IntakeAgent (10-30 seconds)
    make test-agents     # Test all individual agents (2-5 minutes)
"""

from typing import Any

import pytest
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

APP_NAME = "retail_location_strategy_test"
USER_ID = "test_user"


async def run_agent_test(
    agent: Any,
    query: str,
    session_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Helper to run a single agent with a query and return results.

    Args:
        agent: The ADK agent to test
        query: User query to send to the agent
        session_state: Optional initial session state

    Returns:
        dict with 'response' (str) and 'state' (dict)
    """
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state=session_state or {},
    )

    runner = Runner(
        agent=agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    content = types.Content(role="user", parts=[types.Part(text=query)])

    final_response = None
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session.id,
        new_message=content,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_response = event.content.parts[0].text
            break

    # Get updated session state
    updated_session = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=session.id
    )

    return {
        "response": final_response,
        "state": updated_session.state if updated_session else {},
    }


# =============================================================================
# IntakeAgent Tests - Test request parsing in isolation
# =============================================================================


@pytest.mark.integration
class TestIntakeAgent:
    """Test IntakeAgent in isolation.

    IntakeAgent parses user requests and extracts:
    - target_location: The geographic location to analyze
    - business_type: The type of business to open
    """

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_parse_coffee_shop_bangalore(self):
        """Test parsing a coffee shop request in Bangalore."""
        from app.sub_agents.intake_agent import intake_agent

        result = await run_agent_test(
            agent=intake_agent,
            query="I want to open a coffee shop in Indiranagar, Bangalore",
        )

        # Verify the agent extracted the correct values to state
        # IntakeAgent stores data in parsed_request dict
        state = result["state"]
        parsed = state.get("parsed_request", {})
        assert "target_location" in parsed, f"Missing target_location in state: {state}"
        assert "business_type" in parsed, f"Missing business_type in state: {state}"

        # Check values (case-insensitive for flexibility)
        assert "indiranagar" in parsed["target_location"].lower()
        assert "bangalore" in parsed["target_location"].lower()
        assert "coffee" in parsed["business_type"].lower()

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_parse_fitness_austin(self):
        """Test parsing a fitness studio request in Austin."""
        from app.sub_agents.intake_agent import intake_agent

        result = await run_agent_test(
            agent=intake_agent,
            query="Where should I open a fitness studio in Austin, Texas?",
        )

        state = result["state"]
        parsed = state.get("parsed_request", {})
        assert "target_location" in parsed
        assert "business_type" in parsed

        assert "austin" in parsed["target_location"].lower()
        assert "fitness" in parsed["business_type"].lower()

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_parse_bakery_dubai(self):
        """Test parsing a bakery request in Dubai."""
        from app.sub_agents.intake_agent import intake_agent

        result = await run_agent_test(
            agent=intake_agent,
            query="I'm planning to open a bakery in Dubai Marina",
        )

        state = result["state"]
        parsed = state.get("parsed_request", {})
        assert "dubai" in parsed.get("target_location", "").lower()
        assert "bakery" in parsed.get("business_type", "").lower()


# =============================================================================
# MarketResearchAgent Tests - Requires google_search tool
# =============================================================================


@pytest.mark.integration
class TestMarketResearchAgent:
    """Test MarketResearchAgent in isolation.

    MarketResearchAgent uses Google Search to research market conditions.
    It reads target_location and business_type from session state.
    """

    @pytest.mark.asyncio
    @pytest.mark.timeout(120)
    async def test_market_research_bangalore_coffee(self):
        """Test market research for coffee shop in Bangalore."""
        from app.sub_agents.market_research import market_research_agent

        result = await run_agent_test(
            agent=market_research_agent,
            query="Research the market for this location",
            session_state={
                "target_location": "Indiranagar, Bangalore",
                "business_type": "coffee shop",
            },
        )

        # Verify market research findings were stored
        findings = result["state"].get("market_research_findings", "")
        assert len(findings) > 50, f"Expected substantial findings, got: {findings[:100]}"


# =============================================================================
# CompetitorMappingAgent Tests - Requires Maps API
# =============================================================================


@pytest.mark.integration
class TestCompetitorMappingAgent:
    """Test CompetitorMappingAgent in isolation.

    CompetitorMappingAgent uses Google Maps Places API to find competitors.
    It reads target_location and business_type from session state.
    """

    @pytest.mark.asyncio
    @pytest.mark.timeout(120)
    async def test_competitor_mapping_bangalore_coffee(self):
        """Test competitor mapping for coffee shops in Bangalore."""
        from app.sub_agents.competitor_mapping import competitor_mapping_agent

        result = await run_agent_test(
            agent=competitor_mapping_agent,
            query="Map the competitors in this area",
            session_state={
                "target_location": "Indiranagar, Bangalore",
                "business_type": "coffee shop",
                "market_research_findings": "Growing specialty coffee market.",
            },
        )

        # Verify competitor analysis was stored
        analysis = result["state"].get("competitor_analysis", "")
        assert len(analysis) > 50, f"Expected competitor analysis, got: {analysis[:100]}"


# =============================================================================
# AudioOverviewAgent Tests - Requires Gemini TTS
# =============================================================================


@pytest.mark.integration
class TestAudioOverviewAgent:
    """Test AudioOverviewAgent in isolation.

    AudioOverviewAgent generates a podcast-style audio summary using Gemini TTS.
    It reads strategic_report from session state.

    Note: Audio generation takes ~60-120 seconds depending on script length.
    """

    @pytest.mark.asyncio
    @pytest.mark.timeout(180)
    async def test_audio_overview_with_strategic_report(self):
        """Test audio generation with pre-populated strategic report."""
        import json

        from app.sub_agents.audio_overview import audio_overview_agent

        # Mock strategic report data (simplified for testing)
        strategic_report = {
            "target_location": "Indiranagar, Bangalore",
            "business_type": "coffee shop",
            "market_validation": "Proceed with confidence",
            "total_competitors_found": 47,
            "top_recommendation": {
                "location_name": "Central Indiranagar",
                "overall_score": 82,
                "opportunity_type": "Premium positioning",
            },
            "key_insights": [
                "High foot traffic area",
                "Growing specialty coffee culture",
                "Young professional demographic",
            ],
        }

        result = await run_agent_test(
            agent=audio_overview_agent,
            query="Generate an audio overview of the analysis",
            session_state={
                "target_location": "Indiranagar, Bangalore",
                "business_type": "coffee shop",
                "strategic_report": json.dumps(strategic_report),
            },
        )

        # Verify audio was generated - check for audio result in state
        state = result["state"]

        # The agent should produce audio_overview_result or store base64 audio
        has_audio_result = "audio_overview_result" in state
        has_audio_base64 = "audio_overview_base64" in state

        assert (
            has_audio_result or has_audio_base64
        ), f"Expected audio output in state. Got keys: {list(state.keys())}"

        # If audio_overview_result exists, verify it has expected structure
        if has_audio_result:
            audio_result = state["audio_overview_result"]
            if isinstance(audio_result, dict):
                assert audio_result.get("status") == "success", f"Audio generation failed: {audio_result}"


# =============================================================================
# Agent Module Import Tests - No API calls, fast
# =============================================================================


class TestAgentModuleImport:
    """Basic tests to verify agent module can be imported correctly.

    These tests don't require API keys and run quickly.
    """

    def test_root_agent_import(self):
        """Test that root_agent can be imported from app module."""
        from app import root_agent

        assert root_agent is not None
        assert hasattr(root_agent, "name")

    def test_sub_agents_import(self):
        """Test that all sub-agents can be imported."""
        from app.sub_agents.artifact_generation import artifact_generation_pipeline
        from app.sub_agents.audio_overview import audio_overview_agent
        from app.sub_agents.competitor_mapping import competitor_mapping_agent
        from app.sub_agents.gap_analysis import gap_analysis_agent
        from app.sub_agents.infographic_generator import infographic_generator_agent
        from app.sub_agents.intake_agent import intake_agent
        from app.sub_agents.market_research import market_research_agent
        from app.sub_agents.report_generator import report_generator_agent
        from app.sub_agents.strategy_advisor import strategy_advisor_agent

        agents = [
            intake_agent,
            market_research_agent,
            competitor_mapping_agent,
            gap_analysis_agent,
            strategy_advisor_agent,
            report_generator_agent,
            infographic_generator_agent,
            audio_overview_agent,
            artifact_generation_pipeline,
        ]

        for agent in agents:
            assert agent is not None
            assert hasattr(agent, "name")

    def test_tools_import(self):
        """Test that all custom tools can be imported."""
        from app.tools.audio_generator import generate_audio_overview
        from app.tools.html_report_generator import generate_html_report
        from app.tools.image_generator import generate_infographic
        from app.tools.places_search import search_places

        tools = [search_places, generate_html_report, generate_infographic, generate_audio_overview]

        for tool in tools:
            assert callable(tool)

    def test_schemas_import(self):
        """Test that all Pydantic schemas can be imported."""
        from app.schemas.report_schema import (
            AlternativeLocation,
            CompetitionProfile,
            ConcernAnalysis,
            LocationIntelligenceReport,
            LocationRecommendation,
            MarketCharacteristics,
            StrengthAnalysis,
        )

        schemas = [
            StrengthAnalysis,
            ConcernAnalysis,
            CompetitionProfile,
            MarketCharacteristics,
            LocationRecommendation,
            AlternativeLocation,
            LocationIntelligenceReport,
        ]

        for schema in schemas:
            assert schema is not None
