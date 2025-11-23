"""Tests for evaluation setup."""

import json
from pathlib import Path

import pytest


class TestEvaluationSetup:
    """Test evaluation configuration and test cases."""

    def test_evalset_exists(self):
        """Test that evalset.json file exists."""
        evalset_path = Path("evaluation/strategic_consultant.evalset.json")
        assert evalset_path.exists(), "evalset.json file not found"

    def test_test_config_exists(self):
        """Test that test_config.json file exists."""
        config_path = Path("evaluation/test_config.json")
        assert config_path.exists(), "test_config.json file not found"

    def test_evalset_is_valid_json(self):
        """Test that evalset.json is valid JSON."""
        evalset_path = Path("evaluation/strategic_consultant.evalset.json")
        with open(evalset_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert isinstance(data, dict)

    def test_test_config_is_valid_json(self):
        """Test that test_config.json is valid JSON."""
        config_path = Path("evaluation/test_config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert isinstance(data, dict)

    def test_evalset_structure(self):
        """Test that evalset has required structure."""
        evalset_path = Path("evaluation/strategic_consultant.evalset.json")
        with open(evalset_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            assert "name" in data
            assert "test_cases" in data
            assert isinstance(data["test_cases"], list)
            assert len(data["test_cases"]) >= 5, "At least 5 test cases required"

    def test_test_case_structure(self):
        """Test that each test case has required fields."""
        evalset_path = Path("evaluation/strategic_consultant.evalset.json")
        with open(evalset_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            required_fields = ["id", "name", "description", "input", "expected_outputs"]

            for test_case in data["test_cases"]:
                for field in required_fields:
                    assert field in test_case, f"Missing field '{field}' in test case"

    def test_test_case_ids_unique(self):
        """Test that all test case IDs are unique."""
        evalset_path = Path("evaluation/strategic_consultant.evalset.json")
        with open(evalset_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            ids = [tc["id"] for tc in data["test_cases"]]
            assert len(ids) == len(set(ids)), "Duplicate test case IDs found"

    def test_framework_selection_test_cases(self):
        """Test that framework selection test cases exist."""
        evalset_path = Path("evaluation/strategic_consultant.evalset.json")
        with open(evalset_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            frameworks_tested = set()
            for tc in data["test_cases"]:
                if "framework_used" in tc.get("expected_outputs", {}):
                    frameworks_tested.add(tc["expected_outputs"]["framework_used"])

            # Should test at least 3 different frameworks
            assert (
                len(frameworks_tested) >= 3
            ), f"Only {len(frameworks_tested)} frameworks tested, need at least 3"

    def test_mece_validation_test_case(self):
        """Test that MECE validation test case exists."""
        evalset_path = Path("evaluation/strategic_consultant.evalset.json")
        with open(evalset_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            has_mece_test = False
            for tc in data["test_cases"]:
                if "mece" in tc["id"].lower() or "validation" in tc["name"].lower():
                    has_mece_test = True
                    break

            assert has_mece_test, "No MECE validation test case found"

    def test_prioritization_test_case(self):
        """Test that prioritization test case exists."""
        evalset_path = Path("evaluation/strategic_consultant.evalset.json")
        with open(evalset_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            has_priority_test = False
            for tc in data["test_cases"]:
                if "priority" in tc["id"].lower() or "matrix" in tc["name"].lower():
                    has_priority_test = True
                    break

            assert has_priority_test, "No prioritization test case found"

    def test_full_workflow_test_case(self):
        """Test that full workflow test case exists."""
        evalset_path = Path("evaluation/strategic_consultant.evalset.json")
        with open(evalset_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            has_workflow_test = False
            for tc in data["test_cases"]:
                if "workflow" in tc["id"].lower() or "full" in tc["name"].lower():
                    has_workflow_test = True
                    break

            assert has_workflow_test, "No full workflow test case found"

    def test_config_has_passing_criteria(self):
        """Test that test_config has passing criteria."""
        config_path = Path("evaluation/test_config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            assert "evaluation_config" in data
            assert "passing_criteria" in data["evaluation_config"]
            assert "minimum_pass_rate" in data["evaluation_config"]["passing_criteria"]

            pass_rate = data["evaluation_config"]["passing_criteria"]["minimum_pass_rate"]
            assert 0.0 <= pass_rate <= 1.0, "Pass rate must be between 0 and 1"

    def test_config_has_agent_config(self):
        """Test that test_config has agent configuration."""
        config_path = Path("evaluation/test_config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            assert "agent_config" in data
            assert "agent_name" in data["agent_config"]
            assert "model" in data["agent_config"]

    def test_config_has_evaluation_metrics(self):
        """Test that test_config has evaluation metrics."""
        config_path = Path("evaluation/test_config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            assert "evaluation_metrics" in data
            assert len(data["evaluation_metrics"]) > 0

            # Check that weights sum to 1.0
            total_weight = sum(
                metric["weight"] for metric in data["evaluation_metrics"].values()
            )
            assert (
                abs(total_weight - 1.0) < 0.01
            ), f"Metric weights sum to {total_weight}, expected 1.0"


class TestEvaluationCoverage:
    """Test that evaluation covers all required ADK concepts."""

    def test_covers_sequential_agent(self):
        """Test that evaluation tests SequentialAgent."""
        evalset_path = Path("evaluation/strategic_consultant.evalset.json")
        with open(evalset_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            # Full workflow test should test SequentialAgent orchestration
            has_sequential = any(
                "workflow" in tc["id"].lower() for tc in data["test_cases"]
            )
            assert has_sequential, "No test for SequentialAgent orchestration"

    def test_covers_parallel_agent(self):
        """Test that evaluation tests ParallelAgent."""
        evalset_path = Path("evaluation/strategic_consultant.evalset.json")
        with open(evalset_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            # Full workflow test should include research phase (ParallelAgent)
            has_parallel = any(
                "research_performed" in tc.get("expected_outputs", {})
                for tc in data["test_cases"]
            )
            assert has_parallel, "No test for ParallelAgent (research phase)"

    def test_covers_loop_agent(self):
        """Test that evaluation tests LoopAgent."""
        evalset_path = Path("evaluation/strategic_consultant.evalset.json")
        with open(evalset_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            # MECE validation test should test LoopAgent iteration
            has_loop = any(
                "validation" in tc["id"].lower() for tc in data["test_cases"]
            )
            assert has_loop, "No test for LoopAgent (MECE validation loop)"

    def test_covers_custom_tools(self):
        """Test that evaluation tests custom FunctionTools."""
        evalset_path = Path("evaluation/strategic_consultant.evalset.json")
        with open(evalset_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            # Should test hypothesis tree, MECE validation, and 2x2 matrix tools
            tool_tests = {
                "hypothesis_tree": False,
                "mece_validation": False,
                "priority_matrix": False,
            }

            for tc in data["test_cases"]:
                outputs = tc.get("expected_outputs", {})
                if "has_hypothesis_tree" in outputs:
                    tool_tests["hypothesis_tree"] = True
                if "validation_performed" in outputs or "mece" in tc["id"].lower():
                    tool_tests["mece_validation"] = True
                if "has_priority_matrix" in outputs:
                    tool_tests["priority_matrix"] = True

            assert all(
                tool_tests.values()
            ), f"Not all tools tested: {tool_tests}"

    def test_minimum_test_cases(self):
        """Test that there are at least 5 test cases."""
        evalset_path = Path("evaluation/strategic_consultant.evalset.json")
        with open(evalset_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            assert (
                len(data["test_cases"]) >= 5
            ), f"Only {len(data['test_cases'])} test cases, need at least 5"


class TestEvaluationQuality:
    """Test quality of evaluation test cases."""

    def test_test_cases_have_descriptions(self):
        """Test that all test cases have meaningful descriptions."""
        evalset_path = Path("evaluation/strategic_consultant.evalset.json")
        with open(evalset_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            for tc in data["test_cases"]:
                assert (
                    len(tc["description"]) > 20
                ), f"Test case {tc['id']} has too short description"

    def test_test_cases_have_evaluation_criteria(self):
        """Test that all test cases have evaluation criteria."""
        evalset_path = Path("evaluation/strategic_consultant.evalset.json")
        with open(evalset_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            for tc in data["test_cases"]:
                assert (
                    "evaluation_criteria" in tc
                ), f"Test case {tc['id']} missing evaluation criteria"
                assert (
                    len(tc["evaluation_criteria"]) > 0
                ), f"Test case {tc['id']} has no evaluation criteria"

    def test_inputs_are_realistic(self):
        """Test that input messages are realistic strategic questions."""
        evalset_path = Path("evaluation/strategic_consultant.evalset.json")
        with open(evalset_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            for tc in data["test_cases"]:
                message = tc["input"]["user_message"]
                assert (
                    len(message) > 10
                ), f"Test case {tc['id']} has too short input message"
                assert (
                    "?" in message
                ), f"Test case {tc['id']} input should be a question"
