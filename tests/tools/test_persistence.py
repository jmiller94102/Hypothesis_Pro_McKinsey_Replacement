"""Tests for persistence module."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from strategic_consultant_agent.tools.persistence import (
    save_analysis,
    load_analysis,
    delete_analysis,
    get_latest_version,
    _sanitize_filename,
    _list_project_analyses,
)


@pytest.fixture
def temp_storage():
    """Create a temporary storage directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


class TestSaveAnalysis:
    """Test save_analysis function."""

    def test_saves_hypothesis_tree(self, temp_storage):
        """Test saving a hypothesis tree."""
        content = {
            "problem": "Should we scale?",
            "tree": {
                "DESIRABILITY": {"label": "Desirability"},
            },
        }

        result = save_analysis(
            project_name="test_project",
            analysis_type="hypothesis_tree",
            content=content,
            storage_dir=temp_storage,
        )

        assert "filepath" in result
        assert "version" in result
        assert result["version"] == 1
        assert "timestamp" in result
        assert Path(result["filepath"]).exists()

    def test_saves_matrix(self, temp_storage):
        """Test saving a matrix."""
        content = {
            "matrix_type": "prioritization",
            "items": ["Item 1", "Item 2"],
        }

        result = save_analysis(
            project_name="test_project",
            analysis_type="matrix",
            content=content,
            storage_dir=temp_storage,
        )

        assert result["version"] == 1
        assert Path(result["filepath"]).exists()

    def test_saves_research(self, temp_storage):
        """Test saving research."""
        content = {
            "market_research": "Market is growing at 15% CAGR",
            "sources": ["Industry report 2024"],
        }

        result = save_analysis(
            project_name="test_project",
            analysis_type="research",
            content=content,
            storage_dir=temp_storage,
        )

        assert result["version"] == 1
        assert Path(result["filepath"]).exists()

    def test_increments_version_number(self, temp_storage):
        """Test that version numbers increment."""
        content = {"data": "test"}

        # Save first version
        result1 = save_analysis(
            "test_project", "hypothesis_tree", content, temp_storage
        )
        assert result1["version"] == 1

        # Save second version
        result2 = save_analysis(
            "test_project", "hypothesis_tree", content, temp_storage
        )
        assert result2["version"] == 2

        # Save third version
        result3 = save_analysis(
            "test_project", "hypothesis_tree", content, temp_storage
        )
        assert result3["version"] == 3

    def test_creates_project_directory(self, temp_storage):
        """Test that project directory is created."""
        content = {"data": "test"}

        save_analysis(
            "new_project", "hypothesis_tree", content, storage_dir=temp_storage
        )

        project_dir = Path(temp_storage) / "new_project"
        assert project_dir.exists()
        assert project_dir.is_dir()

    def test_sanitizes_project_name(self, temp_storage):
        """Test that project name is sanitized for filesystem."""
        content = {"data": "test"}

        result = save_analysis(
            "Project with Spaces & Special!@#",
            "hypothesis_tree",
            content,
            storage_dir=temp_storage,
        )

        # Should have sanitized directory name
        assert "project_with_spaces_special" in result["filepath"].lower()

    def test_includes_metadata(self, temp_storage):
        """Test that saved file includes metadata."""
        content = {"data": "test"}

        result = save_analysis(
            "test_project", "hypothesis_tree", content, storage_dir=temp_storage
        )

        # Load file and check metadata
        with open(result["filepath"], "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "metadata" in data
        assert "content" in data
        assert data["metadata"]["project_name"] == "test_project"
        assert data["metadata"]["analysis_type"] == "hypothesis_tree"
        assert data["metadata"]["version"] == 1
        assert "timestamp" in data["metadata"]
        assert data["content"] == content

    def test_raises_error_for_invalid_type(self, temp_storage):
        """Test that invalid analysis type raises error."""
        with pytest.raises(ValueError, match="Invalid analysis_type"):
            save_analysis(
                "test_project",
                "invalid_type",
                {"data": "test"},
                storage_dir=temp_storage,
            )

    def test_handles_unicode_content(self, temp_storage):
        """Test saving content with Unicode characters."""
        content = {"description": "Análisis de mercado 市場分析"}

        result = save_analysis(
            "test_project", "research", content, storage_dir=temp_storage
        )

        # Load and verify
        with open(result["filepath"], "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["content"]["description"] == "Análisis de mercado 市場分析"


class TestLoadAnalysis:
    """Test load_analysis function."""

    def test_loads_latest_version(self, temp_storage):
        """Test loading latest version."""
        content1 = {"version": "1"}
        content2 = {"version": "2"}

        save_analysis("test_project", "hypothesis_tree", content1, temp_storage)
        save_analysis("test_project", "hypothesis_tree", content2, temp_storage)

        result = load_analysis(
            "test_project", "hypothesis_tree", storage_dir=temp_storage
        )

        assert result["content"]["version"] == "2"
        assert result["metadata"]["version"] == 2

    def test_loads_specific_version(self, temp_storage):
        """Test loading specific version."""
        content1 = {"version": "1"}
        content2 = {"version": "2"}

        save_analysis("test_project", "hypothesis_tree", content1, temp_storage)
        save_analysis("test_project", "hypothesis_tree", content2, temp_storage)

        result = load_analysis(
            "test_project", "hypothesis_tree", version=1, storage_dir=temp_storage
        )

        assert result["content"]["version"] == "1"
        assert result["metadata"]["version"] == 1

    def test_lists_all_analyses_when_type_not_specified(self, temp_storage):
        """Test listing all analyses when no type specified."""
        save_analysis("test_project", "hypothesis_tree", {"a": 1}, temp_storage)
        save_analysis("test_project", "matrix", {"b": 2}, temp_storage)

        result = load_analysis("test_project", storage_dir=temp_storage)

        assert "analyses" in result
        assert "hypothesis_tree" in result["analyses"]
        assert "matrix" in result["analyses"]
        assert result["total_count"] == 2

    def test_raises_error_for_nonexistent_project(self, temp_storage):
        """Test error for nonexistent project."""
        with pytest.raises(FileNotFoundError, match="No saved analyses found"):
            load_analysis("nonexistent_project", storage_dir=temp_storage)

    def test_raises_error_for_nonexistent_version(self, temp_storage):
        """Test error for nonexistent version."""
        save_analysis("test_project", "hypothesis_tree", {"a": 1}, temp_storage)

        with pytest.raises(FileNotFoundError, match="version 99 not found"):
            load_analysis(
                "test_project",
                "hypothesis_tree",
                version=99,
                storage_dir=temp_storage,
            )

    def test_raises_error_for_nonexistent_type(self, temp_storage):
        """Test error for nonexistent analysis type."""
        save_analysis("test_project", "hypothesis_tree", {"a": 1}, temp_storage)

        with pytest.raises(FileNotFoundError, match="No 'matrix' analyses found"):
            load_analysis("test_project", "matrix", storage_dir=temp_storage)

    def test_loads_unicode_content(self, temp_storage):
        """Test loading content with Unicode characters."""
        content = {"description": "Análisis de mercado 市場分析"}

        save_analysis("test_project", "research", content, temp_storage)
        result = load_analysis("test_project", "research", storage_dir=temp_storage)

        assert result["content"]["description"] == "Análisis de mercado 市場分析"


class TestSanitizeFilename:
    """Test _sanitize_filename function."""

    def test_removes_special_characters(self):
        """Test removing special characters."""
        result = _sanitize_filename("Project!@# with $%^ special &*() chars")
        assert result == "project_with_special_chars"

    def test_replaces_spaces_with_underscores(self):
        """Test replacing spaces with underscores."""
        result = _sanitize_filename("My Test Project")
        assert result == "my_test_project"

    def test_removes_consecutive_underscores(self):
        """Test removing consecutive underscores."""
        result = _sanitize_filename("test___project__name")
        assert result == "test_project_name"

    def test_converts_to_lowercase(self):
        """Test converting to lowercase."""
        result = _sanitize_filename("TestProject")
        assert result == "testproject"

    def test_preserves_hyphens(self):
        """Test preserving hyphens."""
        result = _sanitize_filename("test-project-name")
        assert result == "test-project-name"

    def test_limits_length(self):
        """Test limiting length to 100 characters."""
        long_name = "a" * 150
        result = _sanitize_filename(long_name)
        assert len(result) == 100

    def test_strips_leading_trailing_underscores(self):
        """Test stripping leading/trailing underscores."""
        result = _sanitize_filename("__test_project__")
        assert result == "test_project"


class TestDeleteAnalysis:
    """Test delete_analysis function."""

    def test_deletes_specific_version(self, temp_storage):
        """Test deleting specific version."""
        content1 = {"version": "1"}
        content2 = {"version": "2"}

        save_analysis("test_project", "hypothesis_tree", content1, temp_storage)
        save_analysis("test_project", "hypothesis_tree", content2, temp_storage)

        result = delete_analysis(
            "test_project", "hypothesis_tree", version=1, storage_dir=temp_storage
        )

        assert result["deleted"] is True

        # Version 1 should be gone
        with pytest.raises(FileNotFoundError):
            load_analysis(
                "test_project",
                "hypothesis_tree",
                version=1,
                storage_dir=temp_storage,
            )

        # Version 2 should still exist
        loaded = load_analysis(
            "test_project", "hypothesis_tree", storage_dir=temp_storage
        )
        assert loaded["metadata"]["version"] == 2

    def test_raises_error_for_nonexistent_version(self, temp_storage):
        """Test error when deleting nonexistent version."""
        save_analysis("test_project", "hypothesis_tree", {"a": 1}, temp_storage)

        with pytest.raises(FileNotFoundError):
            delete_analysis(
                "test_project", "hypothesis_tree", version=99, storage_dir=temp_storage
            )


class TestGetLatestVersion:
    """Test get_latest_version function."""

    def test_returns_latest_version(self, temp_storage):
        """Test getting latest version number."""
        save_analysis("test_project", "hypothesis_tree", {"v": 1}, temp_storage)
        save_analysis("test_project", "hypothesis_tree", {"v": 2}, temp_storage)
        save_analysis("test_project", "hypothesis_tree", {"v": 3}, temp_storage)

        version = get_latest_version(
            "test_project", "hypothesis_tree", storage_dir=temp_storage
        )

        assert version == 3

    def test_returns_zero_for_nonexistent_project(self, temp_storage):
        """Test returning 0 for nonexistent project."""
        version = get_latest_version(
            "nonexistent_project", "hypothesis_tree", storage_dir=temp_storage
        )

        assert version == 0

    def test_returns_zero_for_nonexistent_type(self, temp_storage):
        """Test returning 0 for nonexistent analysis type."""
        save_analysis("test_project", "hypothesis_tree", {"a": 1}, temp_storage)

        version = get_latest_version("test_project", "matrix", storage_dir=temp_storage)

        assert version == 0


class TestListProjectAnalyses:
    """Test _list_project_analyses function."""

    def test_lists_all_analyses(self, temp_storage):
        """Test listing all analyses for a project."""
        save_analysis("test_project", "hypothesis_tree", {"a": 1}, temp_storage)
        save_analysis("test_project", "hypothesis_tree", {"a": 2}, temp_storage)
        save_analysis("test_project", "matrix", {"b": 1}, temp_storage)

        project_dir = Path(temp_storage) / "test_project"
        result = _list_project_analyses(project_dir, "test_project")

        assert result["project_name"] == "test_project"
        assert result["total_count"] == 3
        assert len(result["analyses"]["hypothesis_tree"]) == 2
        assert len(result["analyses"]["matrix"]) == 1

    def test_sorts_by_version_descending(self, temp_storage):
        """Test that analyses are sorted by version (descending)."""
        save_analysis("test_project", "hypothesis_tree", {"v": 1}, temp_storage)
        save_analysis("test_project", "hypothesis_tree", {"v": 2}, temp_storage)
        save_analysis("test_project", "hypothesis_tree", {"v": 3}, temp_storage)

        project_dir = Path(temp_storage) / "test_project"
        result = _list_project_analyses(project_dir, "test_project")

        versions = [item["version"] for item in result["analyses"]["hypothesis_tree"]]
        assert versions == [3, 2, 1]

    def test_handles_empty_project(self, temp_storage):
        """Test handling project with no analyses."""
        project_dir = Path(temp_storage) / "empty_project"
        project_dir.mkdir(parents=True)

        result = _list_project_analyses(project_dir, "empty_project")

        assert result["total_count"] == 0
        assert result["analyses"] == {}


class TestIntegration:
    """Integration tests."""

    def test_full_save_load_workflow(self, temp_storage):
        """Test full save and load workflow."""
        # Create hypothesis tree
        tree_content = {
            "problem": "Should we scale fall detection?",
            "tree": {
                "DESIRABILITY": {
                    "label": "Desirability",
                    "L2_branches": {"CLINICAL_IMPACT": {"label": "Clinical Impact"}},
                }
            },
        }

        # Save it
        save_result = save_analysis(
            "fall_detection_eval", "hypothesis_tree", tree_content, temp_storage
        )

        assert save_result["version"] == 1

        # Load it back
        load_result = load_analysis(
            "fall_detection_eval", "hypothesis_tree", storage_dir=temp_storage
        )

        assert load_result["content"] == tree_content
        assert load_result["metadata"]["project_name"] == "fall_detection_eval"

    def test_multiple_projects_and_types(self, temp_storage):
        """Test working with multiple projects and analysis types."""
        # Project 1
        save_analysis("project1", "hypothesis_tree", {"p1": "tree"}, temp_storage)
        save_analysis("project1", "matrix", {"p1": "matrix"}, temp_storage)

        # Project 2
        save_analysis("project2", "hypothesis_tree", {"p2": "tree"}, temp_storage)
        save_analysis("project2", "research", {"p2": "research"}, temp_storage)

        # Load Project 1 summary
        p1_summary = load_analysis("project1", storage_dir=temp_storage)
        assert len(p1_summary["analyses"]) == 2

        # Load Project 2 summary
        p2_summary = load_analysis("project2", storage_dir=temp_storage)
        assert len(p2_summary["analyses"]) == 2

    def test_version_management(self, temp_storage):
        """Test version management across saves and deletes."""
        # Save 3 versions
        save_analysis("test", "hypothesis_tree", {"v": 1}, temp_storage)
        save_analysis("test", "hypothesis_tree", {"v": 2}, temp_storage)
        save_analysis("test", "hypothesis_tree", {"v": 3}, temp_storage)

        # Check latest version
        assert get_latest_version("test", "hypothesis_tree", temp_storage) == 3

        # Delete v2
        delete_analysis("test", "hypothesis_tree", 2, temp_storage)

        # Latest should still be 3
        assert get_latest_version("test", "hypothesis_tree", temp_storage) == 3

        # v1 and v3 should still load
        v1 = load_analysis(
            "test", "hypothesis_tree", version=1, storage_dir=temp_storage
        )
        v3 = load_analysis(
            "test", "hypothesis_tree", version=3, storage_dir=temp_storage
        )

        assert v1["content"]["v"] == 1
        assert v3["content"]["v"] == 3
