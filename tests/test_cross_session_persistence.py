"""Tests for cross-session persistence integration."""

import json
import os
import tempfile
from datetime import datetime
from unittest.mock import patch

import pytest

from strategic_consultant_agent.persistence_integration import (
    save_completed_analysis,
    load_previous_analysis,
    extract_hypothesis_tree,
    extract_priority_matrix,
    extract_research_findings,
    get_analysis_metadata,
    format_analysis_summary,
    list_saved_analyses,
)


@pytest.fixture
def sample_hypothesis_tree():
    """Sample hypothesis tree for testing."""
    return {
        "strategic_question": "Should we scale deployment of fall detection?",
        "framework_used": "scale_decision",
        "L1_DESIRABILITY": {
            "label": "Desirability",
            "question": "Is there user need?",
        },
        "L1_FEASIBILITY": {
            "label": "Feasibility",
            "question": "Can we build it?",
        },
    }


@pytest.fixture
def sample_priority_matrix():
    """Sample priority matrix for testing."""
    return {
        "matrix_type": "prioritization",
        "x_axis": {"label": "Effort", "low": "Low", "high": "High"},
        "y_axis": {"label": "Impact", "low": "Low", "high": "High"},
    }


@pytest.fixture
def temp_storage_dir():
    """Create temporary storage directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestSaveCompletedAnalysis:
    """Test saving completed analyses."""

    @patch("strategic_consultant_agent.persistence_integration.save_analysis")
    def test_save_minimal_analysis(self, mock_save, sample_hypothesis_tree):
        """Test saving analysis with minimal components."""
        mock_save.return_value = {
            "filepath": "storage/projects/test_project_v1.json",
            "version": 1,
        }

        result = save_completed_analysis(
            project_name="test_project", hypothesis_tree=sample_hypothesis_tree
        )

        assert result["version"] == 1
        mock_save.assert_called_once()
        call_args = mock_save.call_args
        assert call_args.kwargs["project_name"] == "test_project"
        assert call_args.kwargs["analysis_type"] == "hypothesis_tree"
        assert "hypothesis_tree" in call_args.kwargs["content"]

    @patch("strategic_consultant_agent.persistence_integration.save_analysis")
    def test_save_complete_analysis(
        self, mock_save, sample_hypothesis_tree, sample_priority_matrix
    ):
        """Test saving analysis with all components."""
        mock_save.return_value = {
            "filepath": "storage/projects/complete_project_v1.json",
            "version": 1,
        }

        result = save_completed_analysis(
            project_name="complete_project",
            hypothesis_tree=sample_hypothesis_tree,
            priority_matrix=sample_priority_matrix,
            market_research="Market research findings...",
            competitor_research="Competitor analysis...",
        )

        call_args = mock_save.call_args
        content = call_args.kwargs["content"]
        assert "hypothesis_tree" in content
        assert "priority_matrix" in content
        assert "market_research" in content
        assert "competitor_research" in content

    @patch("strategic_consultant_agent.persistence_integration.save_analysis")
    def test_metadata_generation(self, mock_save, sample_hypothesis_tree):
        """Test that metadata is correctly generated."""
        save_completed_analysis(
            project_name="test_project", hypothesis_tree=sample_hypothesis_tree
        )

        call_args = mock_save.call_args
        content = call_args.kwargs["content"]
        metadata = content["metadata"]

        assert "timestamp" in metadata
        assert metadata["framework_used"] == "scale_decision"
        assert (
            metadata["strategic_question"]
            == sample_hypothesis_tree["strategic_question"]
        )
        assert "components_included" in metadata

    @patch("strategic_consultant_agent.persistence_integration.save_analysis")
    def test_additional_metadata(self, mock_save, sample_hypothesis_tree):
        """Test adding custom metadata."""
        additional = {"user": "test_user", "tags": ["urgent", "healthcare"]}

        save_completed_analysis(
            project_name="test_project",
            hypothesis_tree=sample_hypothesis_tree,
            additional_metadata=additional,
        )

        call_args = mock_save.call_args
        content = call_args.kwargs["content"]
        metadata = content["metadata"]

        assert metadata["user"] == "test_user"
        assert metadata["tags"] == ["urgent", "healthcare"]


class TestLoadPreviousAnalysis:
    """Test loading previous analyses."""

    @patch("strategic_consultant_agent.persistence_integration.load_analysis")
    def test_load_latest_version(self, mock_load):
        """Test loading latest version when no version specified."""
        mock_load.return_value = {"hypothesis_tree": {}}

        result = load_previous_analysis("test_project")

        mock_load.assert_called_once_with(
            project_name="test_project", analysis_type="hypothesis_tree", version=None
        )

    @patch("strategic_consultant_agent.persistence_integration.load_analysis")
    def test_load_specific_version(self, mock_load):
        """Test loading a specific version."""
        mock_load.return_value = {"hypothesis_tree": {}}

        result = load_previous_analysis("test_project", version=2)

        mock_load.assert_called_once_with(
            project_name="test_project", analysis_type="hypothesis_tree", version=2
        )

    @patch("strategic_consultant_agent.persistence_integration.load_analysis")
    def test_load_nonexistent_project(self, mock_load):
        """Test loading non-existent project raises error."""
        mock_load.side_effect = FileNotFoundError("No saved analyses found")

        with pytest.raises(FileNotFoundError, match="No saved analyses found"):
            load_previous_analysis("nonexistent_project")


class TestExtractComponents:
    """Test extracting components from loaded analyses."""

    def test_extract_hypothesis_tree(self, sample_hypothesis_tree):
        """Test extracting hypothesis tree."""
        analysis = {"hypothesis_tree": sample_hypothesis_tree}
        tree = extract_hypothesis_tree(analysis)

        assert tree == sample_hypothesis_tree

    def test_extract_hypothesis_tree_missing(self):
        """Test extracting hypothesis tree when missing."""
        analysis = {}
        tree = extract_hypothesis_tree(analysis)

        assert tree == {}

    def test_extract_priority_matrix(self, sample_priority_matrix):
        """Test extracting priority matrix."""
        analysis = {"priority_matrix": sample_priority_matrix}
        matrix = extract_priority_matrix(analysis)

        assert matrix == sample_priority_matrix

    def test_extract_priority_matrix_missing(self):
        """Test extracting priority matrix when missing."""
        analysis = {}
        matrix = extract_priority_matrix(analysis)

        assert matrix is None

    def test_extract_research_findings(self):
        """Test extracting research findings."""
        analysis = {
            "market_research": "Market findings...",
            "competitor_research": "Competitor findings...",
        }

        market, competitor = extract_research_findings(analysis)

        assert market == "Market findings..."
        assert competitor == "Competitor findings..."

    def test_extract_research_findings_partial(self):
        """Test extracting research findings when partially present."""
        analysis = {"market_research": "Market findings..."}

        market, competitor = extract_research_findings(analysis)

        assert market == "Market findings..."
        assert competitor is None

    def test_get_analysis_metadata(self):
        """Test extracting metadata."""
        metadata = {
            "timestamp": "2025-11-23T10:00:00",
            "framework_used": "scale_decision",
        }
        analysis = {"metadata": metadata}

        result = get_analysis_metadata(analysis)

        assert result == metadata

    def test_get_analysis_metadata_missing(self):
        """Test extracting metadata when missing."""
        analysis = {}
        result = get_analysis_metadata(analysis)

        assert result == {}


class TestFormatAnalysisSummary:
    """Test formatting analysis summaries."""

    def test_format_complete_summary(
        self, sample_hypothesis_tree, sample_priority_matrix
    ):
        """Test formatting a complete analysis summary."""
        analysis = {
            "hypothesis_tree": sample_hypothesis_tree,
            "priority_matrix": sample_priority_matrix,
            "metadata": {
                "timestamp": "2025-11-23T10:00:00",
                "framework_used": "scale_decision",
                "components_included": [
                    "hypothesis_tree",
                    "priority_matrix",
                    "market_research",
                ],
            },
        }

        summary = format_analysis_summary(analysis)

        assert "Strategic Analysis Summary" in summary
        assert sample_hypothesis_tree["strategic_question"] in summary
        assert "scale_decision" in summary
        assert "2025-11-23" in summary
        assert "prioritization" in summary  # matrix type
        assert "Desirability" in summary
        assert "Feasibility" in summary

    def test_format_minimal_summary(self):
        """Test formatting a minimal analysis summary."""
        analysis = {"hypothesis_tree": {}, "metadata": {}}

        summary = format_analysis_summary(analysis)

        assert "Strategic Analysis Summary" in summary
        assert "N/A" in summary  # For missing fields


class TestListSavedAnalyses:
    """Test listing saved analyses."""

    @patch("strategic_consultant_agent.persistence_integration.load_analysis")
    def test_list_no_analyses(self, mock_load):
        """Test listing when no analyses exist."""
        mock_load.side_effect = FileNotFoundError("No saved analyses found")

        result = list_saved_analyses("nonexistent_project")

        assert result == []

    @patch("strategic_consultant_agent.persistence_integration.load_analysis")
    def test_list_multiple_analyses(self, mock_load, sample_hypothesis_tree):
        """Test listing multiple saved versions."""

        def mock_load_side_effect(project_name, analysis_type, version=None):
            if version is None:
                return {
                    "hypothesis_tree": sample_hypothesis_tree,
                    "metadata": {"version": 3},
                }
            return {
                "hypothesis_tree": {
                    **sample_hypothesis_tree,
                    "strategic_question": f"Question {version}",
                },
                "metadata": {
                    "timestamp": f"2025-11-23T{version}0:00:00",
                    "framework_used": "scale_decision",
                    "version": version,
                },
            }

        mock_load.side_effect = mock_load_side_effect

        result = list_saved_analyses("test_project")

        assert len(result) == 3
        assert result[0]["version"] == 1
        assert result[1]["version"] == 2
        assert result[2]["version"] == 3
        assert "Question 1" in result[0]["question"]

    @patch("strategic_consultant_agent.persistence_integration.load_analysis")
    def test_list_with_missing_versions(self, mock_load):
        """Test listing when some versions are missing."""

        def mock_load_side_effect(project_name, analysis_type, version=None):
            if version is None:
                return {"hypothesis_tree": {}, "metadata": {"version": 3}}
            if version == 2:
                raise FileNotFoundError("Missing version")
            return {
                "hypothesis_tree": {},
                "metadata": {"timestamp": "2025-11-23T10:00:00", "version": version},
            }

        mock_load.side_effect = mock_load_side_effect

        result = list_saved_analyses("test_project")

        # Should skip v2 and only return v1 and v3
        assert len(result) == 2


class TestIntegrationWorkflow:
    """Test complete save/load workflow."""

    @patch("strategic_consultant_agent.persistence_integration.save_analysis")
    @patch("strategic_consultant_agent.persistence_integration.load_analysis")
    def test_complete_workflow(
        self,
        mock_load,
        mock_save,
        sample_hypothesis_tree,
        sample_priority_matrix,
    ):
        """Test complete save and load workflow."""
        # Save analysis
        mock_save.return_value = {
            "filepath": "storage/projects/test_v1.json",
            "version": 1,
        }

        save_result = save_completed_analysis(
            project_name="test",
            hypothesis_tree=sample_hypothesis_tree,
            priority_matrix=sample_priority_matrix,
            market_research="Market data",
        )

        assert save_result["version"] == 1

        # Load analysis
        saved_data = {
            "hypothesis_tree": sample_hypothesis_tree,
            "priority_matrix": sample_priority_matrix,
            "market_research": "Market data",
            "metadata": {
                "timestamp": "2025-11-23T10:00:00",
                "framework_used": "scale_decision",
            },
        }

        mock_load.return_value = saved_data

        loaded = load_previous_analysis("test")

        tree = extract_hypothesis_tree(loaded)
        matrix = extract_priority_matrix(loaded)
        market, _ = extract_research_findings(loaded)

        assert tree == sample_hypothesis_tree
        assert matrix == sample_priority_matrix
        assert market == "Market data"
