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

"""Unit tests for Pydantic output schemas.

These tests validate the schema definitions without making any LLM calls,
ensuring that the structured output models work correctly.
"""

import pytest
from pydantic import ValidationError

from app.schemas.report_schema import (
    AlternativeLocation,
    CompetitionProfile,
    ConcernAnalysis,
    LocationIntelligenceReport,
    LocationRecommendation,
    MarketCharacteristics,
    StrengthAnalysis,
)


class TestStrengthAnalysis:
    """Tests for StrengthAnalysis schema."""

    def test_valid_strength(self):
        """Test creating a valid StrengthAnalysis."""
        strength = StrengthAnalysis(
            factor="High Foot Traffic",
            description="Located near metro station with high pedestrian flow",
            evidence_from_analysis="Google Maps data shows 2000+ daily visitors",
        )
        assert strength.factor == "High Foot Traffic"
        assert "metro station" in strength.description

    def test_missing_required_field(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            StrengthAnalysis(
                factor="High Foot Traffic",
                description="Missing evidence field",
                # evidence_from_analysis is missing
            )


class TestConcernAnalysis:
    """Tests for ConcernAnalysis schema."""

    def test_valid_concern(self):
        """Test creating a valid ConcernAnalysis."""
        concern = ConcernAnalysis(
            risk="High Rent",
            description="Premium location demands high rental costs",
            mitigation_strategy="Negotiate long-term lease for better rates",
        )
        assert concern.risk == "High Rent"
        assert "negotiate" in concern.mitigation_strategy.lower()


class TestCompetitionProfile:
    """Tests for CompetitionProfile schema."""

    def test_valid_competition_profile(self):
        """Test creating a valid CompetitionProfile."""
        profile = CompetitionProfile(
            total_competitors=15,
            density_per_km2=3.5,
            chain_dominance_pct=40.0,
            avg_competitor_rating=4.2,
            high_performers_count=5,
        )
        assert profile.total_competitors == 15
        assert profile.avg_competitor_rating == 4.2

    def test_negative_competitors(self):
        """Test that negative competitor count works (no constraint in schema)."""
        # Note: Schema doesn't constrain negative values - this is a documentation
        # of current behavior, not necessarily desired behavior
        profile = CompetitionProfile(
            total_competitors=-1,
            density_per_km2=0.0,
            chain_dominance_pct=0.0,
            avg_competitor_rating=0.0,
            high_performers_count=0,
        )
        assert profile.total_competitors == -1


class TestMarketCharacteristics:
    """Tests for MarketCharacteristics schema."""

    def test_valid_market_characteristics(self):
        """Test creating valid MarketCharacteristics."""
        market = MarketCharacteristics(
            population_density="High",
            income_level="High",
            infrastructure_access="Excellent metro and bus connectivity",
            foot_traffic_pattern="High during morning and evening rush hours",
            rental_cost_tier="Premium",
        )
        assert market.population_density == "High"
        assert "metro" in market.infrastructure_access.lower()


class TestLocationRecommendation:
    """Tests for LocationRecommendation schema."""

    @pytest.fixture
    def valid_recommendation_data(self):
        """Fixture providing valid recommendation data."""
        return {
            "location_name": "Indiranagar 100 Feet Road",
            "area": "Indiranagar",
            "overall_score": 85,
            "opportunity_type": "High Traffic Corridor",
            "strengths": [
                StrengthAnalysis(
                    factor="Location",
                    description="Prime location",
                    evidence_from_analysis="Near metro",
                )
            ],
            "concerns": [
                ConcernAnalysis(
                    risk="Competition",
                    description="Many cafes nearby",
                    mitigation_strategy="Differentiate with specialty offerings",
                )
            ],
            "competition": CompetitionProfile(
                total_competitors=5,
                density_per_km2=2.5,
                chain_dominance_pct=40.0,
                avg_competitor_rating=4.2,
                high_performers_count=2,
            ),
            "market": MarketCharacteristics(
                population_density="High",
                income_level="High",
                infrastructure_access="Excellent",
                foot_traffic_pattern="High",
                rental_cost_tier="Premium",
            ),
            "best_customer_segment": "Young professionals and tech workers",
            "estimated_foot_traffic": "2000+ daily visitors",
            "next_steps": ["Secure lease", "Obtain permits", "Hire staff"],
        }

    def test_valid_recommendation(self, valid_recommendation_data):
        """Test creating a valid LocationRecommendation."""
        rec = LocationRecommendation(**valid_recommendation_data)
        assert rec.overall_score == 85
        assert rec.location_name == "Indiranagar 100 Feet Road"
        assert len(rec.strengths) == 1
        assert len(rec.next_steps) == 3

    def test_score_range_valid_min(self, valid_recommendation_data):
        """Test that score of 0 is valid."""
        valid_recommendation_data["overall_score"] = 0
        rec = LocationRecommendation(**valid_recommendation_data)
        assert rec.overall_score == 0

    def test_score_range_valid_max(self, valid_recommendation_data):
        """Test that score of 100 is valid."""
        valid_recommendation_data["overall_score"] = 100
        rec = LocationRecommendation(**valid_recommendation_data)
        assert rec.overall_score == 100

    def test_score_range_invalid_too_high(self, valid_recommendation_data):
        """Test that score above 100 raises ValidationError."""
        valid_recommendation_data["overall_score"] = 101
        with pytest.raises(ValidationError) as exc_info:
            LocationRecommendation(**valid_recommendation_data)
        assert "overall_score" in str(exc_info.value)

    def test_score_range_invalid_negative(self, valid_recommendation_data):
        """Test that negative score raises ValidationError."""
        valid_recommendation_data["overall_score"] = -1
        with pytest.raises(ValidationError) as exc_info:
            LocationRecommendation(**valid_recommendation_data)
        assert "overall_score" in str(exc_info.value)


class TestAlternativeLocation:
    """Tests for AlternativeLocation schema."""

    def test_valid_alternative(self):
        """Test creating a valid AlternativeLocation."""
        alt = AlternativeLocation(
            location_name="Koramangala 4th Block",
            area="Koramangala",
            overall_score=75,
            opportunity_type="Startup Hub",
            key_strength="High concentration of tech companies",
            key_concern="Parking availability",
            why_not_top="Higher competition from established players",
        )
        assert alt.overall_score == 75
        assert "tech" in alt.key_strength.lower()

    def test_score_range_validation(self):
        """Test that score must be between 0-100."""
        with pytest.raises(ValidationError):
            AlternativeLocation(
                location_name="Test",
                area="Test",
                overall_score=150,  # Invalid
                opportunity_type="Test",
                key_strength="Test",
                key_concern="Test",
                why_not_top="Test",
            )


class TestLocationIntelligenceReport:
    """Tests for the complete LocationIntelligenceReport schema."""

    @pytest.fixture
    def valid_report_data(self):
        """Fixture providing valid full report data."""
        return {
            "target_location": "Indiranagar, Bangalore",
            "business_type": "coffee shop",
            "analysis_date": "2025-12-09",
            "market_validation": "Strong market potential with growing specialty coffee demand",
            "total_competitors_found": 15,
            "zones_analyzed": 3,
            "top_recommendation": LocationRecommendation(
                location_name="100 Feet Road",
                area="Indiranagar",
                overall_score=85,
                opportunity_type="High Traffic Corridor",
                strengths=[],
                concerns=[],
                competition=CompetitionProfile(
                    total_competitors=5,
                    density_per_km2=2.5,
                    chain_dominance_pct=40.0,
                    avg_competitor_rating=4.2,
                    high_performers_count=2,
                ),
                market=MarketCharacteristics(
                    population_density="High",
                    income_level="High",
                    infrastructure_access="Excellent",
                    foot_traffic_pattern="High",
                    rental_cost_tier="Premium",
                ),
                best_customer_segment="Young professionals",
                estimated_foot_traffic="High",
                next_steps=["Secure lease", "Obtain permits"],
            ),
            "alternative_locations": [
                AlternativeLocation(
                    location_name="Koramangala",
                    area="Koramangala",
                    overall_score=72,
                    opportunity_type="Startup Hub",
                    key_strength="Tech crowd",
                    key_concern="Competition",
                    why_not_top="More saturated market",
                )
            ],
            "key_insights": [
                "Strong demand for specialty coffee",
                "Premium pricing accepted",
                "Morning rush hour peak demand",
            ],
            "methodology_summary": "Analysis based on Google Maps Places API and web research",
        }

    def test_valid_full_report(self, valid_report_data):
        """Test creating a complete valid report."""
        report = LocationIntelligenceReport(**valid_report_data)
        assert report.target_location == "Indiranagar, Bangalore"
        assert report.business_type == "coffee shop"
        assert report.total_competitors_found == 15
        assert report.zones_analyzed == 3
        assert report.top_recommendation.overall_score == 85
        assert len(report.alternative_locations) == 1
        assert len(report.key_insights) == 3

    def test_empty_alternatives_allowed(self, valid_report_data):
        """Test that empty alternative locations list is valid."""
        valid_report_data["alternative_locations"] = []
        report = LocationIntelligenceReport(**valid_report_data)
        assert report.alternative_locations == []

    def test_empty_insights_allowed(self, valid_report_data):
        """Test that empty insights list is valid."""
        valid_report_data["key_insights"] = []
        report = LocationIntelligenceReport(**valid_report_data)
        assert report.key_insights == []

    def test_report_serialization(self, valid_report_data):
        """Test that report can be serialized to JSON."""
        report = LocationIntelligenceReport(**valid_report_data)
        json_str = report.model_dump_json()
        assert "Indiranagar" in json_str
        assert "coffee shop" in json_str

    def test_report_dict_conversion(self, valid_report_data):
        """Test that report can be converted to dict."""
        report = LocationIntelligenceReport(**valid_report_data)
        report_dict = report.model_dump()
        assert isinstance(report_dict, dict)
        assert report_dict["target_location"] == "Indiranagar, Bangalore"
        assert isinstance(report_dict["top_recommendation"], dict)
