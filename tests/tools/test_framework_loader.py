"""Tests for framework_loader module."""

import pytest
import json
import tempfile
from pathlib import Path

from strategic_consultant_agent.tools.framework_loader import (
    FrameworkLoader,
    load_framework,
    find_framework_by_trigger,
    list_available_frameworks,
)


class TestFrameworkLoader:
    """Test FrameworkLoader class."""

    def test_loads_bundled_templates(self):
        """Test that loader can load bundled templates."""
        loader = FrameworkLoader()
        assert loader.frameworks is not None
        assert "frameworks" in loader.frameworks

    def test_loads_custom_template_path(self, tmp_path):
        """Test loading from custom path."""
        # Create a minimal valid template
        template_data = {
            "frameworks": {
                "test_framework": {
                    "name": "Test Framework",
                    "L1_categories": {"CATEGORY1": {"label": "Category 1"}},
                }
            }
        }

        template_file = tmp_path / "test_templates.json"
        with open(template_file, "w") as f:
            json.dump(template_data, f)

        loader = FrameworkLoader(str(template_file))
        assert loader.get_framework("test_framework") is not None

    def test_raises_on_missing_file(self):
        """Test error when template file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            FrameworkLoader("/nonexistent/path.json")

    def test_raises_on_malformed_json(self, tmp_path):
        """Test error on invalid JSON."""
        bad_json = tmp_path / "bad.json"
        with open(bad_json, "w") as f:
            f.write("{invalid json")

        with pytest.raises(ValueError, match="Invalid JSON"):
            FrameworkLoader(str(bad_json))

    def test_raises_on_invalid_structure(self, tmp_path):
        """Test error on missing required keys."""
        invalid_data = tmp_path / "invalid.json"
        with open(invalid_data, "w") as f:
            json.dump({"wrong_key": {}}, f)

        with pytest.raises(ValueError, match="missing 'frameworks'"):
            FrameworkLoader(str(invalid_data))

    def test_get_framework_by_name(self):
        """Test retrieving framework by name."""
        loader = FrameworkLoader()
        framework = loader.get_framework("scale_decision")

        assert framework is not None
        assert "name" in framework
        assert framework["name"] == "Scale Decision Framework"

    def test_get_framework_returns_none_for_invalid_name(self):
        """Test that invalid name returns None."""
        loader = FrameworkLoader()
        assert loader.get_framework("nonexistent") is None

    def test_get_framework_by_trigger_phrase(self):
        """Test finding framework by trigger phrase."""
        loader = FrameworkLoader()

        # Should match "scale_decision" framework
        framework = loader.get_framework_by_trigger("Should we scale deployment")
        assert framework is not None
        assert framework["name"] == "Scale Decision Framework"

        # Should match "product_launch" framework
        framework = loader.get_framework_by_trigger("Should we launch a new product")
        assert framework is not None
        assert framework["name"] == "Product Launch Framework"

    def test_trigger_phrase_case_insensitive(self):
        """Test that trigger matching is case-insensitive."""
        loader = FrameworkLoader()

        framework1 = loader.get_framework_by_trigger("SHOULD WE SCALE")
        framework2 = loader.get_framework_by_trigger("should we scale")

        assert framework1 == framework2

    def test_list_frameworks(self):
        """Test listing all framework names."""
        loader = FrameworkLoader()
        names = loader.list_frameworks()

        assert "scale_decision" in names
        assert "product_launch" in names
        assert "market_entry" in names
        assert "investment_decision" in names
        assert "operations_improvement" in names
        assert "custom" in names

    def test_get_framework_names_with_descriptions(self):
        """Test getting framework names with descriptions."""
        loader = FrameworkLoader()
        descriptions = loader.get_framework_names_with_descriptions()

        assert "scale_decision" in descriptions
        assert isinstance(descriptions["scale_decision"], str)
        assert len(descriptions["scale_decision"]) > 0


class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_load_framework(self):
        """Test load_framework convenience function."""
        framework = load_framework("scale_decision")
        assert framework is not None
        assert framework["name"] == "Scale Decision Framework"

    def test_find_framework_by_trigger(self):
        """Test find_framework_by_trigger convenience function."""
        framework = find_framework_by_trigger("should we enter the market")
        assert framework is not None
        # Should match market_entry

    def test_list_available_frameworks(self):
        """Test list_available_frameworks convenience function."""
        names = list_available_frameworks()
        assert isinstance(names, list)
        assert len(names) >= 6  # At least 6 frameworks
