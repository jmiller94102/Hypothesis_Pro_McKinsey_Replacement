"""Tests for matrix_2x2 module."""

import pytest

from strategic_consultant_agent.tools.matrix_2x2 import (
    generate_2x2_matrix,
    _get_quadrant_definitions,
    _auto_assess_items,
    _place_items_in_quadrants,
    _generate_recommendations,
)


class TestGenerate2x2Matrix:
    """Test generate_2x2_matrix function."""

    def test_generates_prioritization_matrix(self):
        """Test generating a prioritization matrix."""
        items = [
            "Validate fall detection accuracy",
            "Assess staff workflow impact",
            "Calculate full ROI model",
        ]

        result = generate_2x2_matrix(items, matrix_type="prioritization")

        assert result["matrix_type"] == "prioritization"
        assert result["x_axis"] == "Effort"
        assert result["y_axis"] == "Impact"
        assert "quadrants" in result
        assert "Q1" in result["quadrants"]
        assert result["quadrants"]["Q1"]["name"] == "Quick Wins"
        assert "items" in result
        assert len(result["items"]) == 3
        assert "assessments" in result
        assert "placements" in result
        assert "recommendations" in result

    def test_generates_bcg_matrix(self):
        """Test generating a BCG matrix."""
        items = ["Product A", "Product B"]

        result = generate_2x2_matrix(
            items, x_axis="Market Share", y_axis="Growth", matrix_type="bcg"
        )

        assert result["matrix_type"] == "bcg"
        assert result["quadrants"]["Q1"]["name"] == "Stars"
        assert result["quadrants"]["Q4"]["name"] == "Cash Cows"

    def test_generates_risk_matrix(self):
        """Test generating a risk matrix."""
        items = ["Privacy breach", "System downtime"]

        result = generate_2x2_matrix(
            items, x_axis="Likelihood", y_axis="Impact", matrix_type="risk"
        )

        assert result["matrix_type"] == "risk"
        assert result["quadrants"]["Q1"]["name"] == "Mitigate"
        assert result["quadrants"]["Q3"]["name"] == "Accept"

    def test_generates_eisenhower_matrix(self):
        """Test generating an Eisenhower matrix."""
        items = ["Critical bug fix", "Documentation update"]

        result = generate_2x2_matrix(
            items, x_axis="Urgency", y_axis="Importance", matrix_type="eisenhower"
        )

        assert result["matrix_type"] == "eisenhower"
        assert result["quadrants"]["Q1"]["name"] == "Do First"
        assert result["quadrants"]["Q4"]["name"] == "Eliminate"

    def test_generates_custom_matrix(self):
        """Test generating a custom matrix."""
        items = ["Item 1", "Item 2"]

        result = generate_2x2_matrix(
            items, x_axis="Complexity", y_axis="Value", matrix_type="custom"
        )

        assert result["matrix_type"] == "custom"
        assert "Complexity" in result["quadrants"]["Q1"]["name"]
        assert "Value" in result["quadrants"]["Q1"]["name"]

    def test_uses_provided_assessments(self):
        """Test using provided assessments instead of auto-assessment."""
        items = ["Item A", "Item B"]
        assessments = {
            "Item A": {"x": "high", "y": "high"},
            "Item B": {"x": "low", "y": "low"},
        }

        result = generate_2x2_matrix(items, assessments=assessments)

        assert result["assessments"] == assessments
        assert "Item A" in result["placements"]["Q2"]  # High Y, High X
        assert "Item B" in result["placements"]["Q3"]  # Low Y, Low X

    def test_handles_empty_items_list(self):
        """Test handling empty items list."""
        result = generate_2x2_matrix([])

        assert result["items"] == []
        assert all(len(items) == 0 for items in result["placements"].values())

    def test_returns_all_required_fields(self):
        """Test that result has all required fields."""
        items = ["Test item"]
        result = generate_2x2_matrix(items)

        assert "matrix_type" in result
        assert "x_axis" in result
        assert "y_axis" in result
        assert "quadrants" in result
        assert "items" in result
        assert "assessments" in result
        assert "placements" in result
        assert "recommendations" in result


class TestGetQuadrantDefinitions:
    """Test _get_quadrant_definitions function."""

    def test_returns_prioritization_quadrants(self):
        """Test prioritization quadrant definitions."""
        quadrants = _get_quadrant_definitions("prioritization", "Effort", "Impact")

        assert len(quadrants) == 4
        assert quadrants["Q1"]["name"] == "Quick Wins"
        assert quadrants["Q2"]["name"] == "Strategic Bets"
        assert quadrants["Q3"]["name"] == "Fill Later"
        assert quadrants["Q4"]["name"] == "Hard Slogs"
        assert "action" in quadrants["Q1"]

    def test_returns_bcg_quadrants(self):
        """Test BCG quadrant definitions."""
        quadrants = _get_quadrant_definitions("bcg", "Market Share", "Growth")

        assert quadrants["Q1"]["name"] == "Stars"
        assert quadrants["Q2"]["name"] == "Question Marks"
        assert quadrants["Q3"]["name"] == "Dogs"
        assert quadrants["Q4"]["name"] == "Cash Cows"

    def test_returns_risk_quadrants(self):
        """Test risk quadrant definitions."""
        quadrants = _get_quadrant_definitions("risk", "Likelihood", "Impact")

        assert quadrants["Q1"]["name"] == "Mitigate"
        assert quadrants["Q2"]["name"] == "Monitor"
        assert quadrants["Q3"]["name"] == "Accept"
        assert quadrants["Q4"]["name"] == "Reduce"

    def test_returns_eisenhower_quadrants(self):
        """Test Eisenhower quadrant definitions."""
        quadrants = _get_quadrant_definitions("eisenhower", "Urgency", "Importance")

        assert quadrants["Q1"]["name"] == "Do First"
        assert quadrants["Q2"]["name"] == "Schedule"
        assert quadrants["Q3"]["name"] == "Delegate"
        assert quadrants["Q4"]["name"] == "Eliminate"

    def test_returns_custom_quadrants(self):
        """Test custom quadrant definitions."""
        quadrants = _get_quadrant_definitions("custom", "Cost", "Benefit")

        assert "Benefit" in quadrants["Q1"]["name"]
        assert "Cost" in quadrants["Q1"]["name"]
        assert all("position" in q for q in quadrants.values())


class TestAutoAssessItems:
    """Test _auto_assess_items function."""

    def test_generates_assessments_for_all_items(self):
        """Test generating assessments for all items."""
        items = ["Item 1", "Item 2", "Item 3"]

        assessments = _auto_assess_items(items, "Effort", "Impact")

        assert len(assessments) == 3
        assert all(item in assessments for item in items)

    def test_assessment_has_x_and_y_values(self):
        """Test that each assessment has x and y values."""
        items = ["Item 1", "Item 2"]

        assessments = _auto_assess_items(items, "Effort", "Impact")

        for item in items:
            assert "x" in assessments[item]
            assert "y" in assessments[item]
            assert assessments[item]["x"] in ["low", "high"]
            assert assessments[item]["y"] in ["low", "high"]

    def test_distributes_items_across_quadrants(self):
        """Test that items are distributed across quadrants."""
        items = [f"Item {i}" for i in range(10)]

        assessments = _auto_assess_items(items, "Effort", "Impact")

        # Should have mix of high/low values
        x_values = [assessments[item]["x"] for item in items]
        y_values = [assessments[item]["y"] for item in items]

        assert "high" in x_values
        assert "low" in x_values
        assert "high" in y_values
        assert "low" in y_values


class TestPlaceItemsInQuadrants:
    """Test _place_items_in_quadrants function."""

    def test_places_items_in_correct_quadrants(self):
        """Test placing items in correct quadrants based on assessments."""
        items = ["Item A", "Item B", "Item C", "Item D"]
        assessments = {
            "Item A": {"x": "low", "y": "high"},  # Q1
            "Item B": {"x": "high", "y": "high"},  # Q2
            "Item C": {"x": "low", "y": "low"},  # Q3
            "Item D": {"x": "high", "y": "low"},  # Q4
        }
        quadrants = _get_quadrant_definitions("prioritization", "Effort", "Impact")

        placements = _place_items_in_quadrants(items, assessments, quadrants)

        assert "Item A" in placements["Q1"]
        assert "Item B" in placements["Q2"]
        assert "Item C" in placements["Q3"]
        assert "Item D" in placements["Q4"]

    def test_handles_numeric_assessments(self):
        """Test handling numeric assessments (0-1 scale)."""
        items = ["Item X", "Item Y"]
        assessments = {
            "Item X": {"x": 0.3, "y": 0.8},  # Low X, High Y -> Q1
            "Item Y": {"x": 0.7, "y": 0.2},  # High X, Low Y -> Q4
        }
        quadrants = _get_quadrant_definitions("prioritization", "Effort", "Impact")

        placements = _place_items_in_quadrants(items, assessments, quadrants)

        assert "Item X" in placements["Q1"]
        assert "Item Y" in placements["Q4"]

    def test_handles_missing_assessments(self):
        """Test handling items with missing assessments."""
        items = ["Item 1", "Item 2"]
        assessments = {"Item 1": {"x": "high", "y": "high"}}
        quadrants = _get_quadrant_definitions("prioritization", "Effort", "Impact")

        placements = _place_items_in_quadrants(items, assessments, quadrants)

        # Item 2 should default to Q3
        assert "Item 2" in placements["Q3"]

    def test_all_items_placed_exactly_once(self):
        """Test that all items are placed exactly once."""
        items = [f"Item {i}" for i in range(5)]
        assessments = {item: {"x": "low", "y": "high"} for item in items}
        quadrants = _get_quadrant_definitions("prioritization", "Effort", "Impact")

        placements = _place_items_in_quadrants(items, assessments, quadrants)

        # Count total placements
        total_placed = sum(len(items) for items in placements.values())
        assert total_placed == len(items)


class TestGenerateRecommendations:
    """Test _generate_recommendations function."""

    def test_generates_prioritization_recommendations(self):
        """Test generating recommendations for prioritization matrix."""
        placements = {
            "Q1": ["Quick item 1", "Quick item 2"],
            "Q2": ["Strategic item"],
            "Q3": ["Low priority"],
            "Q4": ["Hard slog"],
        }

        recommendations = _generate_recommendations(placements, "prioritization")

        assert len(recommendations) > 0
        assert any("Quick Win" in rec for rec in recommendations)
        assert any("Strategic Bet" in rec for rec in recommendations)

    def test_generates_risk_recommendations(self):
        """Test generating recommendations for risk matrix."""
        placements = {
            "Q1": ["Critical risk"],
            "Q2": ["Monitor this"],
            "Q3": [],
            "Q4": [],
        }

        recommendations = _generate_recommendations(placements, "risk")

        assert any("Mitigate" in rec or "URGENT" in rec for rec in recommendations)

    def test_includes_quadrant_counts(self):
        """Test that recommendations include item counts."""
        placements = {
            "Q1": ["Item 1", "Item 2", "Item 3"],
            "Q2": ["Item 4"],
            "Q3": [],
            "Q4": [],
        }

        recommendations = _generate_recommendations(placements, "prioritization")

        # Should mention the count (3 Quick Wins)
        assert any("3" in rec for rec in recommendations)

    def test_handles_empty_placements(self):
        """Test handling empty placements."""
        placements = {"Q1": [], "Q2": [], "Q3": [], "Q4": []}

        recommendations = _generate_recommendations(placements, "prioritization")

        # Should still return some recommendations
        assert len(recommendations) > 0

    def test_suggests_sequence_for_prioritization(self):
        """Test that prioritization includes suggested sequence."""
        placements = {
            "Q1": ["Quick item"],
            "Q2": ["Strategic item"],
            "Q3": [],
            "Q4": [],
        }

        recommendations = _generate_recommendations(placements, "prioritization")

        # Should suggest sequence
        assert any("sequence" in rec.lower() for rec in recommendations)


class TestIntegration:
    """Integration tests."""

    def test_full_prioritization_workflow(self):
        """Test full workflow for prioritization matrix."""
        items = [
            "Quick validation test",
            "Full integration implementation",
            "Nice-to-have feature",
            "Complex low-value task",
        ]

        result = generate_2x2_matrix(items, matrix_type="prioritization")

        # Should have all components
        assert result["matrix_type"] == "prioritization"
        assert len(result["items"]) == 4
        assert all(item in result["assessments"] for item in items)

        # All items should be placed
        total_placed = sum(len(items) for items in result["placements"].values())
        assert total_placed == 4

        # Should have recommendations
        assert len(result["recommendations"]) > 0

    def test_custom_assessments_workflow(self):
        """Test workflow with custom assessments."""
        items = ["High impact easy task", "High impact hard task", "Low impact task"]
        assessments = {
            "High impact easy task": {"x": "low", "y": "high"},
            "High impact hard task": {"x": "high", "y": "high"},
            "Low impact task": {"x": "low", "y": "low"},
        }

        result = generate_2x2_matrix(
            items, matrix_type="prioritization", assessments=assessments
        )

        # Should use provided assessments
        assert result["assessments"] == assessments

        # Should place correctly
        assert "High impact easy task" in result["placements"]["Q1"]  # Quick Win
        assert "High impact hard task" in result["placements"]["Q2"]  # Strategic Bet
        assert "Low impact task" in result["placements"]["Q3"]  # Fill Later

    def test_json_serializable_output(self):
        """Test that output is JSON serializable."""
        import json

        items = ["Item 1", "Item 2"]
        result = generate_2x2_matrix(items)

        # Should not raise exception
        json_str = json.dumps(result, indent=2)
        assert len(json_str) > 0

        # Should be deserializable
        parsed = json.loads(json_str)
        assert parsed["matrix_type"] == result["matrix_type"]
