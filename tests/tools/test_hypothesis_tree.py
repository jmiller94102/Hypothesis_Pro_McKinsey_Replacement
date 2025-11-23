"""Tests for hypothesis_tree module."""

import pytest

from strategic_consultant_agent.tools.hypothesis_tree import (
    generate_hypothesis_tree,
    _build_custom_framework,
    _generate_l3_leaf,
    _infer_metric_type,
    _generate_target,
    _suggest_data_source,
)


class TestGenerateHypothesisTree:
    """Test generate_hypothesis_tree function."""

    def test_generates_scale_decision_tree(self):
        """Test generating tree for scale_decision framework."""
        tree = generate_hypothesis_tree(
            problem="Should we scale fall detection deployment?",
            framework="scale_decision",
        )

        assert tree["problem"] == "Should we scale fall detection deployment?"
        assert tree["framework"] == "scale_decision"
        assert tree["framework_name"] == "Scale Decision Framework"
        assert "tree" in tree
        assert "metadata" in tree

        # Check L1 categories
        assert "DESIRABILITY" in tree["tree"]
        assert "FEASIBILITY" in tree["tree"]
        assert "VIABILITY" in tree["tree"]

    def test_generates_product_launch_tree(self):
        """Test generating tree for product_launch framework."""
        tree = generate_hypothesis_tree(
            problem="Should we launch telehealth product?",
            framework="product_launch",
        )

        assert tree["framework"] == "product_launch"
        assert tree["framework_name"] == "Product Launch Framework"
        assert "DESIRABILITY" in tree["tree"]
        assert "FEASIBILITY" in tree["tree"]
        assert "VIABILITY" in tree["tree"]

    def test_generates_market_entry_tree(self):
        """Test generating tree for market_entry framework."""
        tree = generate_hypothesis_tree(
            problem="Should we enter European market?", framework="market_entry"
        )

        assert tree["framework"] == "market_entry"
        assert "MARKET_ATTRACTIVENESS" in tree["tree"]
        assert "COMPETITIVE_POSITION" in tree["tree"]
        assert "EXECUTION_CAPABILITY" in tree["tree"]

    def test_tree_has_complete_structure(self):
        """Test that tree has complete L1/L2/L3 structure."""
        tree = generate_hypothesis_tree(
            problem="Test problem", framework="scale_decision"
        )

        # Check L1 has L2 branches
        l1_desirability = tree["tree"]["DESIRABILITY"]
        assert "L2_branches" in l1_desirability
        assert len(l1_desirability["L2_branches"]) > 0

        # Check L2 has L3 leaves
        first_l2_key = list(l1_desirability["L2_branches"].keys())[0]
        l2_branch = l1_desirability["L2_branches"][first_l2_key]
        assert "L3_leaves" in l2_branch
        assert len(l2_branch["L3_leaves"]) > 0

        # Check L3 leaf has required fields
        l3_leaf = l2_branch["L3_leaves"][0]
        assert "id" in l3_leaf
        assert "label" in l3_leaf
        assert "question" in l3_leaf
        assert "metric_type" in l3_leaf
        assert "target" in l3_leaf
        assert "data_source" in l3_leaf
        assert "status" in l3_leaf

    def test_custom_framework_with_categories(self):
        """Test custom framework with user-defined L1 categories."""
        tree = generate_hypothesis_tree(
            problem="Custom analysis",
            framework="custom",
            custom_l1_categories=["Revenue", "Risk", "Operations"],
        )

        assert tree["framework"] == "custom"
        assert tree["framework_name"] == "Custom Framework"

        # Check custom L1 categories exist
        assert "REVENUE" in tree["tree"]
        assert "RISK" in tree["tree"]
        assert "OPERATIONS" in tree["tree"]

    def test_custom_framework_requires_categories(self):
        """Test that custom framework requires custom_l1_categories."""
        with pytest.raises(ValueError, match="custom_l1_categories required"):
            generate_hypothesis_tree(problem="Test", framework="custom")

    def test_invalid_framework_raises_error(self):
        """Test that invalid framework name raises error."""
        with pytest.raises(ValueError, match="Unknown framework"):
            generate_hypothesis_tree(problem="Test", framework="nonexistent")

    def test_all_standard_frameworks(self):
        """Test all standard frameworks can be generated."""
        frameworks = [
            "scale_decision",
            "product_launch",
            "market_entry",
            "investment_decision",
            "operations_improvement",
        ]

        for framework in frameworks:
            tree = generate_hypothesis_tree(problem="Test problem", framework=framework)
            assert tree["framework"] == framework
            assert len(tree["tree"]) > 0


class TestBuildCustomFramework:
    """Test _build_custom_framework function."""

    def test_builds_framework_from_categories(self):
        """Test building custom framework from categories."""
        framework = _build_custom_framework(["Revenue", "Cost", "Risk"])

        assert "REVENUE" in framework["L1_categories"]
        assert "COST" in framework["L1_categories"]
        assert "RISK" in framework["L1_categories"]

    def test_custom_framework_has_l2_branches(self):
        """Test custom framework has L2 branches."""
        framework = _build_custom_framework(["Revenue"])

        revenue_cat = framework["L1_categories"]["REVENUE"]
        assert "L2_branches" in revenue_cat
        assert len(revenue_cat["L2_branches"]) > 0


class TestGenerateL3Leaf:
    """Test _generate_l3_leaf function."""

    def test_generates_complete_leaf(self):
        """Test generating complete L3 leaf."""
        leaf = _generate_l3_leaf(
            label="Cost Reduction",
            l1_context="Desirability",
            l2_context="Financial Impact",
            problem="Test problem",
            index=1,
        )

        assert leaf["id"] == "L3_001"
        assert leaf["label"] == "Cost Reduction"
        assert "question" in leaf
        assert leaf["metric_type"] in ["quantitative", "qualitative", "binary"]
        assert "target" in leaf
        assert "data_source" in leaf
        assert leaf["status"] == "UNTESTED"


class TestInferMetricType:
    """Test _infer_metric_type function."""

    def test_infers_binary(self):
        """Test inferring binary metric type."""
        assert _infer_metric_type("System Integration Possible") == "binary"
        assert _infer_metric_type("Compliance Ready") == "binary"
        assert _infer_metric_type("Capability Exists") == "binary"

    def test_infers_quantitative(self):
        """Test inferring quantitative metric type."""
        assert _infer_metric_type("Cost Reduction") == "quantitative"
        assert _infer_metric_type("Growth Rate") == "quantitative"
        assert _infer_metric_type("Response Time Improvement") == "quantitative"
        assert _infer_metric_type("Revenue Impact") == "quantitative"

    def test_infers_qualitative_as_default(self):
        """Test inferring qualitative as default."""
        assert _infer_metric_type("Stakeholder Satisfaction") == "qualitative"
        assert _infer_metric_type("Brand Alignment") == "qualitative"
        assert _infer_metric_type("User Experience") == "qualitative"


class TestGenerateTarget:
    """Test _generate_target function."""

    def test_generates_binary_target(self):
        """Test generating target for binary metrics."""
        target = _generate_target("Compliance Ready", "binary")
        assert "Yes" in target or "Confirmed" in target

    def test_generates_quantitative_target(self):
        """Test generating target for quantitative metrics."""
        target = _generate_target("Cost Reduction", "quantitative")
        assert "%" in target or "ROI" in target or "days" in target

    def test_generates_qualitative_target(self):
        """Test generating target for qualitative metrics."""
        target = _generate_target("User Satisfaction", "qualitative")
        assert "positive" in target.lower()


class TestSuggestDataSource:
    """Test _suggest_data_source function."""

    def test_suggests_financial_source(self):
        """Test suggesting financial data source."""
        source = _suggest_data_source("Cost Savings", "Financial Impact")
        assert "financial" in source.lower() or "budget" in source.lower()

    def test_suggests_technical_source(self):
        """Test suggesting technical data source."""
        source = _suggest_data_source("System Integration", "Technical")
        assert "technical" in source.lower() or "specification" in source.lower()

    def test_suggests_user_source(self):
        """Test suggesting user data source."""
        source = _suggest_data_source("User Satisfaction", "Experience")
        assert (
            "survey" in source.lower()
            or "feedback" in source.lower()
            or "interview" in source.lower()
        )

    def test_suggests_market_source(self):
        """Test suggesting market data source."""
        source = _suggest_data_source("Market Growth", "Market Analysis")
        assert "market" in source.lower() or "industry" in source.lower()


class TestIntegration:
    """Integration tests for full workflow."""

    def test_full_workflow_generates_valid_tree(self):
        """Test complete workflow generates valid tree."""
        tree = generate_hypothesis_tree(
            problem="Should we scale deployment of fall detection?",
            framework="scale_decision",
        )

        # Validate structure
        assert isinstance(tree, dict)
        assert "tree" in tree
        assert "metadata" in tree

        # Validate all L3 leaves have required fields
        for l1_key, l1_value in tree["tree"].items():
            for l2_key, l2_value in l1_value["L2_branches"].items():
                for l3_leaf in l2_value["L3_leaves"]:
                    assert "id" in l3_leaf
                    assert "label" in l3_leaf
                    assert "question" in l3_leaf
                    assert "metric_type" in l3_leaf
                    assert l3_leaf["metric_type"] in [
                        "quantitative",
                        "qualitative",
                        "binary",
                    ]
                    assert "target" in l3_leaf
                    assert "data_source" in l3_leaf

    def test_tree_json_serializable(self):
        """Test that generated tree is JSON serializable."""
        import json

        tree = generate_hypothesis_tree(problem="Test", framework="scale_decision")

        # Should not raise exception
        json_str = json.dumps(tree)
        assert len(json_str) > 0
