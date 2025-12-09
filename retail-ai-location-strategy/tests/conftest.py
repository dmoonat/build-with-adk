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

"""Shared pytest fixtures for retail-ai-location-strategy tests."""

import os
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from dotenv import load_dotenv

# Load environment variables from app/.env for integration tests
env_path = Path(__file__).parent.parent / "app" / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)


@pytest.fixture
def mock_env_vars():
    """Mock API keys for testing without real credentials.

    Use this fixture explicitly in tests that need mocked environment variables.
    For integration tests with real APIs, don't use this fixture.
    """
    with patch.dict(os.environ, {
        "GOOGLE_API_KEY": "test-api-key",
        "MAPS_API_KEY": "test-maps-key",
        "GOOGLE_GENAI_USE_VERTEXAI": "FALSE",
    }):
        yield


@pytest.fixture
def sample_intake_state() -> dict[str, Any]:
    """Sample session state after IntakeAgent processing."""
    return {
        "target_location": "Indiranagar, Bangalore",
        "business_type": "coffee shop",
        "maps_api_key": "test-maps-key",
    }


@pytest.fixture
def sample_market_research_state(sample_intake_state: dict[str, Any]) -> dict[str, Any]:
    """Sample session state after MarketResearchAgent processing."""
    return {
        **sample_intake_state,
        "market_research_findings": """
        ## Market Research Findings for Indiranagar, Bangalore

        ### Demographics
        - Population: High-density residential and commercial area
        - Income Level: Upper-middle to high income
        - Age Group: Predominantly 25-45 years old professionals

        ### Coffee Market Trends
        - Growing specialty coffee culture
        - High demand for third-wave coffee shops
        - Premium pricing accepted by target demographic
        """,
    }


@pytest.fixture
def sample_competitor_state(sample_market_research_state: dict[str, Any]) -> dict[str, Any]:
    """Sample session state after CompetitorMappingAgent processing."""
    return {
        **sample_market_research_state,
        "competitor_analysis": """
        ## Competitor Analysis for Coffee Shops in Indiranagar

        ### Direct Competitors Found: 12

        1. **Third Wave Coffee** - Rating: 4.5, Reviews: 1200
        2. **Blue Tokai Coffee** - Rating: 4.4, Reviews: 890
        3. **Starbucks** - Rating: 4.2, Reviews: 2100
        4. **Cafe Coffee Day** - Rating: 3.8, Reviews: 1500

        ### Market Saturation: Moderate
        - Chain presence: 40%
        - Independent cafes: 60%
        - Average rating: 4.2
        """,
    }


@pytest.fixture
def sample_full_pipeline_state(sample_competitor_state: dict[str, Any]) -> dict[str, Any]:
    """Sample session state with all pipeline stages completed."""
    return {
        **sample_competitor_state,
        "gap_analysis": """
        ## Gap Analysis Results

        ### Viability Score: 72/100

        | Factor | Score | Weight | Weighted Score |
        |--------|-------|--------|----------------|
        | Market Demand | 85 | 0.3 | 25.5 |
        | Competition | 65 | 0.25 | 16.25 |
        | Demographics | 80 | 0.25 | 20.0 |
        | Location | 70 | 0.2 | 14.0 |

        ### Key Findings
        - Strong market demand for specialty coffee
        - Moderate competition with room for differentiation
        - High foot traffic areas available
        """,
        "strategic_report": {
            "target_location": "Indiranagar, Bangalore",
            "business_type": "coffee shop",
            "analysis_date": "2025-12-09",
            "market_validation": "Strong market potential with growing demand",
            "total_competitors_found": 12,
            "zones_analyzed": 3,
            "top_recommendation": {
                "location_name": "100 Feet Road",
                "area": "Indiranagar",
                "overall_score": 85,
                "opportunity_type": "High Traffic Corridor",
                "strengths": [],
                "concerns": [],
                "competition": {
                    "total_competitors": 5,
                    "density_per_km2": 2.5,
                    "chain_dominance_pct": 40.0,
                    "avg_competitor_rating": 4.2,
                    "high_performers_count": 2,
                },
                "market": {
                    "population_density": "High",
                    "income_level": "High",
                    "infrastructure_access": "Excellent metro connectivity",
                    "foot_traffic_pattern": "High throughout the day",
                    "rental_cost_tier": "Premium",
                },
                "best_customer_segment": "Young professionals",
                "estimated_foot_traffic": "High",
                "next_steps": ["Secure lease", "Obtain permits"],
            },
            "alternative_locations": [],
            "key_insights": ["Strong demand for specialty coffee"],
            "methodology_summary": "Analysis based on Google Maps and web research",
        },
    }
