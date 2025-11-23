"""Tests for mece_validator module."""

import pytest

from strategic_consultant_agent.tools.mece_validator import (
    validate_mece_structure,
    _check_l1_overlaps,
    _check_l1_gaps,
    _check_level_consistency,
)


class TestValidateMeceStructure:
    """Test validate_mece_structure function."""

    def test_validates_clean_structure(self):
        """Test validating a clean MECE structure."""
        structure = {
            "problem": "Should we scale?",
            "tree": {
                "DESIRABILITY": {"label": "Desirability"},
                "FEASIBILITY": {"label": "Feasibility"},
                "VIABILITY": {"label": "Viability"},
            },
        }

        result = validate_mece_structure(structure)

        assert result["is_mece"] is True
        assert len(result["suggestions"]) > 0

    def test_detects_overlaps(self):
        """Test detecting overlapping categories."""
        structure = {
            "problem": "Test",
            "tree": {
                "COST": {"label": "Cost Analysis"},
                "FINANCIAL": {"label": "Financial Impact"},
            },
        }

        result = validate_mece_structure(structure)

        assert result["is_mece"] is False
        assert len(result["issues"]["overlaps"]) > 0

    def test_detects_gaps(self):
        """Test detecting gaps in coverage."""
        structure = {
            "problem": "Should we enter healthcare market?",
            "tree": {
                "MARKET": {"label": "Market Size"},
            },
        }

        result = validate_mece_structure(structure)

        # Should suggest adding regulatory/compliance for healthcare
        assert len(result["issues"]["gaps"]) > 0 or not result["is_mece"]

    def test_detects_level_inconsistencies(self):
        """Test detecting level inconsistencies."""
        structure = {
            "problem": "Test",
            "tree": {
                "STRATEGIC": {"label": "Strategic Vision"},
                "DEPLOYMENT": {"label": "Deployment Details"},
            },
        }

        result = validate_mece_structure(structure)

        assert result["is_mece"] is False
        assert len(result["issues"]["level_inconsistencies"]) > 0

    def test_returns_all_fields(self):
        """Test that result has all required fields."""
        structure = {
            "problem": "Test",
            "tree": {
                "CAT1": {"label": "Category 1"},
            },
        }

        result = validate_mece_structure(structure)

        assert "is_mece" in result
        assert "issues" in result
        assert "suggestions" in result
        assert "overlaps" in result["issues"]
        assert "gaps" in result["issues"]
        assert "level_inconsistencies" in result["issues"]


class TestCheckL1Overlaps:
    """Test _check_l1_overlaps function."""

    def test_detects_keyword_overlaps(self):
        """Test detecting overlaps via shared keywords."""
        tree = {
            "COST": {"label": "Cost Analysis"},
            "FINANCIAL": {"label": "Financial Impact"},
        }

        overlaps = _check_l1_overlaps(tree)

        assert len(overlaps) > 0

    def test_detects_semantic_overlaps(self):
        """Test detecting semantic overlaps."""
        tree = {
            "RISK": {"label": "Risk Assessment"},
            "COMPLIANCE": {"label": "Regulatory Compliance"},
        }

        overlaps = _check_l1_overlaps(tree)

        assert len(overlaps) > 0

    def test_no_overlaps_for_distinct_categories(self):
        """Test no overlaps for distinct categories."""
        tree = {
            "DESIRABILITY": {"label": "Desirability"},
            "FEASIBILITY": {"label": "Feasibility"},
            "VIABILITY": {"label": "Viability"},
        }

        overlaps = _check_l1_overlaps(tree)

        assert len(overlaps) == 0


class TestCheckL1Gaps:
    """Test _check_l1_gaps function."""

    def test_suggests_regulatory_for_healthcare(self):
        """Test suggesting regulatory dimension for healthcare."""
        tree = {
            "MARKET": {"label": "Market Size"},
        }
        problem = "Should we launch healthcare product?"

        gaps = _check_l1_gaps(tree, problem)

        # Should suggest regulatory
        assert any("regulatory" in gap.lower() for gap in gaps)

    def test_suggests_competitive_for_market_entry(self):
        """Test suggesting competitive dimension for market entry."""
        tree = {
            "OPERATIONS": {"label": "Operations"},
        }
        problem = "Should we enter new market?"

        gaps = _check_l1_gaps(tree, problem)

        assert any(
            "competitive" in gap.lower() or "market" in gap.lower() for gap in gaps
        )

    def test_no_gaps_for_comprehensive_structure(self):
        """Test no gaps for comprehensive structure."""
        tree = {
            "MARKET": {"label": "Market Dynamics"},
            "COMPETITIVE": {"label": "Competitive Position"},
            "FINANCIAL": {"label": "Financial Viability"},
            "REGULATORY": {"label": "Regulatory Environment"},
        }
        problem = "Should we enter healthcare market?"

        gaps = _check_l1_gaps(tree, problem)

        # May have few or no gaps
        assert len(gaps) < 3


class TestCheckLevelConsistency:
    """Test _check_level_consistency function."""

    def test_detects_strategic_tactical_mix(self):
        """Test detecting mix of strategic and tactical levels."""
        tree = {
            "STRATEGIC": {"label": "Strategic Vision"},
            "DEPLOYMENT": {"label": "Deployment Process"},
        }

        inconsistencies = _check_level_consistency(tree)

        assert len(inconsistencies) > 0
        assert any("strategic" in issue.lower() for issue in inconsistencies)

    def test_detects_too_many_categories(self):
        """Test detecting too many L1 categories."""
        tree = {f"CAT{i}": {"label": f"Category {i}"} for i in range(1, 8)}

        inconsistencies = _check_level_consistency(tree)

        assert any("categories" in issue.lower() for issue in inconsistencies)

    def test_accepts_reasonable_structure(self):
        """Test accepting reasonable structure."""
        tree = {
            "DESIRABILITY": {"label": "Desirability"},
            "FEASIBILITY": {"label": "Feasibility"},
            "VIABILITY": {"label": "Viability"},
        }

        inconsistencies = _check_level_consistency(tree)

        # Should have few or no inconsistencies
        assert len(inconsistencies) == 0


class TestIntegration:
    """Integration tests."""

    def test_validates_real_hypothesis_tree(self):
        """Test validating a real hypothesis tree structure."""
        from strategic_consultant_agent.tools.hypothesis_tree import (
            generate_hypothesis_tree,
        )

        tree = generate_hypothesis_tree(
            problem="Should we scale deployment?", framework="scale_decision"
        )

        result = validate_mece_structure(tree)

        # Should pass MECE validation
        assert "is_mece" in result
        assert "issues" in result
        assert "suggestions" in result

    def test_full_workflow(self):
        """Test full workflow from generation to validation."""
        from strategic_consultant_agent.tools.hypothesis_tree import (
            generate_hypothesis_tree,
        )

        # Generate tree
        tree = generate_hypothesis_tree(
            problem="Should we launch product?", framework="product_launch"
        )

        # Validate it
        result = validate_mece_structure(tree)

        # Should have structure
        assert isinstance(result, dict)
        assert isinstance(result["is_mece"], bool)
        assert isinstance(result["issues"], dict)
        assert isinstance(result["suggestions"], list)
