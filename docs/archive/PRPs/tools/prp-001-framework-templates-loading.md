# PRP-001: Framework Templates Loading System

**Domain**: Tools
**Phase**: Phase 1 - Core Tools
**Dependencies**: None
**Status**: NOT STARTED
**Estimated Complexity**: Low

---

## OBJECTIVE

Create the foundational system to load, validate, and query framework templates from `framework_templates.json`. This is the data layer that all strategic framework generation depends on.

### Success Criteria
- [ ] Load framework templates from JSON file
- [ ] Validate template structure on load
- [ ] Provide helper functions to query frameworks by trigger phrases
- [ ] Return framework data in expected structure
- [ ] Handle missing or malformed templates gracefully
- [ ] All 5 quality gates passed
- [ ] TASKS.md updated with completion status

---

## CRITICAL REQUIREMENTS

### Data Accuracy
- Framework templates must load exactly as defined in `framework_templates.json`
- No data transformation that changes semantic meaning
- All required fields preserved (L1_categories, L2_branches, suggested_L3)

### Security
- File path validated to prevent directory traversal
- JSON parsing wrapped in try/except for malformed data
- No arbitrary code execution from JSON content

### Performance
- Templates loaded once at module import (cached)
- Query operations <10ms
- No repeated file I/O for each query

---

## IMPLEMENTATION STEPS

### Step 1: Copy Framework Templates JSON File

**Goal**: Make framework_templates.json accessible to the tool

**Files to Create/Modify**:
- `strategic_consultant_agent/data/__init__.py` - Package marker
- `strategic_consultant_agent/data/framework_templates.json` - Copy from docs/project-requirements/

**Instructions**:
1. Create the data directory structure:
   ```bash
   mkdir -p strategic_consultant_agent/data
   touch strategic_consultant_agent/data/__init__.py
   ```

2. Copy the framework templates file:
   ```bash
   cp docs/project-requirements/framework_templates.json strategic_consultant_agent/data/
   ```

3. Verify the file was copied correctly:
   ```bash
   ls -lh strategic_consultant_agent/data/framework_templates.json
   ```

**Expected Outcome**: JSON file exists at `strategic_consultant_agent/data/framework_templates.json`

**Validation**: File exists and is readable

---

### Step 2: Create Framework Loader Module

**Goal**: Implement the core loading and validation logic

**Files to Create**:
- `strategic_consultant_agent/tools/__init__.py` - Package marker
- `strategic_consultant_agent/tools/framework_loader.py` - Main implementation

**Instructions**:

1. Create the tools package:
   ```bash
   mkdir -p strategic_consultant_agent/tools
   touch strategic_consultant_agent/tools/__init__.py
   ```

2. Create `framework_loader.py` with the following structure:

```python
"""Framework template loading and validation system."""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional


class FrameworkLoader:
    """Loads and manages strategic framework templates."""

    def __init__(self, template_path: Optional[str] = None):
        """
        Initialize the framework loader.

        Args:
            template_path: Path to framework_templates.json
                         (default: uses bundled data file)
        """
        if template_path is None:
            # Use bundled template file
            current_dir = Path(__file__).parent.parent
            template_path = current_dir / "data" / "framework_templates.json"

        self.template_path = Path(template_path)
        self.frameworks = self._load_templates()

    def _load_templates(self) -> Dict:
        """
        Load framework templates from JSON file.

        Returns:
            dict: Parsed framework templates

        Raises:
            FileNotFoundError: If template file doesn't exist
            json.JSONDecodeError: If JSON is malformed
        """
        if not self.template_path.exists():
            raise FileNotFoundError(
                f"Framework templates not found at {self.template_path}"
            )

        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validate structure
            self._validate_structure(data)

            return data

        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON in framework templates: {e}"
            ) from e

    def _validate_structure(self, data: Dict) -> None:
        """
        Validate that loaded data has expected structure.

        Args:
            data: Loaded template data

        Raises:
            ValueError: If structure is invalid
        """
        # Check for required top-level keys
        if "frameworks" not in data:
            raise ValueError("Template data missing 'frameworks' key")

        frameworks = data["frameworks"]
        if not isinstance(frameworks, dict):
            raise ValueError("'frameworks' must be a dictionary")

        # Validate each framework
        for name, framework in frameworks.items():
            if "L1_categories" not in framework:
                raise ValueError(
                    f"Framework '{name}' missing 'L1_categories'"
                )

            # Custom framework is allowed to have empty L1_categories
            if name != "custom" and not framework["L1_categories"]:
                raise ValueError(
                    f"Framework '{name}' has empty 'L1_categories'"
                )

    def get_framework(self, name: str) -> Optional[Dict]:
        """
        Get a specific framework by name.

        Args:
            name: Framework name (e.g., "scale_decision", "product_launch")

        Returns:
            dict: Framework definition or None if not found
        """
        return self.frameworks.get("frameworks", {}).get(name)

    def get_framework_by_trigger(self, phrase: str) -> Optional[Dict]:
        """
        Find framework matching a trigger phrase.

        Args:
            phrase: User input phrase to match

        Returns:
            dict: Best matching framework or None
        """
        phrase_lower = phrase.lower()

        # Check each framework's trigger phrases
        for framework in self.frameworks.get("frameworks", {}).values():
            if "trigger_phrases" in framework:
                for trigger in framework["trigger_phrases"]:
                    if trigger.lower() in phrase_lower:
                        return framework

        return None

    def list_frameworks(self) -> List[str]:
        """
        Get list of all available framework names.

        Returns:
            list: Framework names
        """
        return list(self.frameworks.get("frameworks", {}).keys())

    def get_framework_names_with_descriptions(self) -> Dict[str, str]:
        """
        Get framework names with their descriptions.

        Returns:
            dict: {framework_name: description}
        """
        result = {}
        for name, framework in self.frameworks.get("frameworks", {}).items():
            result[name] = framework.get("description", "No description")
        return result


# Global instance (singleton pattern)
_loader_instance: Optional[FrameworkLoader] = None


def get_framework_loader() -> FrameworkLoader:
    """
    Get the global FrameworkLoader instance (singleton).

    Returns:
        FrameworkLoader: Singleton instance
    """
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = FrameworkLoader()
    return _loader_instance


# Convenience functions

def load_framework(name: str) -> Optional[Dict]:
    """
    Load a framework by name.

    Args:
        name: Framework name

    Returns:
        dict: Framework definition or None
    """
    loader = get_framework_loader()
    return loader.get_framework(name)


def find_framework_by_trigger(phrase: str) -> Optional[Dict]:
    """
    Find framework matching trigger phrase.

    Args:
        phrase: User input phrase

    Returns:
        dict: Framework or None
    """
    loader = get_framework_loader()
    return loader.get_framework_by_trigger(phrase)


def list_available_frameworks() -> List[str]:
    """
    List all framework names.

    Returns:
        list: Framework names
    """
    loader = get_framework_loader()
    return loader.list_frameworks()
```

**Expected Outcome**: Framework loader module created with all required functions

**Validation**: Module can be imported without errors

---

### Step 3: Write Unit Tests

**Goal**: Achieve >80% test coverage for framework loader

**Files to Create**:
- `tests/tools/__init__.py` - Package marker
- `tests/tools/test_framework_loader.py` - Unit tests

**Instructions**:

1. Create test directory structure:
   ```bash
   mkdir -p tests/tools
   touch tests/tools/__init__.py
   ```

2. Create comprehensive test suite in `tests/tools/test_framework_loader.py`:

```python
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
                    "L1_categories": {
                        "CATEGORY1": {"label": "Category 1"}
                    }
                }
            }
        }

        template_file = tmp_path / "test_templates.json"
        with open(template_file, 'w') as f:
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
        with open(bad_json, 'w') as f:
            f.write("{invalid json")

        with pytest.raises(ValueError, match="Invalid JSON"):
            FrameworkLoader(str(bad_json))

    def test_raises_on_invalid_structure(self, tmp_path):
        """Test error on missing required keys."""
        invalid_data = tmp_path / "invalid.json"
        with open(invalid_data, 'w') as f:
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
```

**Expected Outcome**: All tests pass, coverage >80%

**Validation**:
```bash
pytest tests/tools/test_framework_loader.py -v
pytest --cov=strategic_consultant_agent.tools.framework_loader tests/tools/test_framework_loader.py
```

---

## SUB-AGENT VALIDATION CHECKPOINTS

### Checkpoint 1: After Module Implementation

**When**: After completing Step 2 (framework_loader.py created)

**Use Task Tool**: Create validation sub-agent

**What to Validate**:
- [ ] Code follows Python best practices (PEP 8)
- [ ] Type hints used consistently
- [ ] Docstrings complete and accurate
- [ ] Error handling comprehensive (FileNotFoundError, ValueError, json.JSONDecodeError)
- [ ] Singleton pattern implemented correctly
- [ ] No security vulnerabilities (path traversal, code injection)

**Validation Prompt for Sub-Agent**:
```
Review the following file for code quality:
- strategic_consultant_agent/tools/framework_loader.py

Check for:
1. PEP 8 compliance and code style
2. Type hints on all functions
3. Comprehensive docstrings
4. Proper error handling for file I/O and JSON parsing
5. Security: no path traversal, no eval/exec
6. Performance: templates loaded once and cached

Verify against project rules in CLAUDE.md.
```

**Expected Outcome**: Sub-agent confirms code meets quality standards

**Do NOT Proceed Until**: All validation issues resolved

---

### Checkpoint 2: Before Commit (MANDATORY)

**When**: After all tests pass and before git commit

**Use Task Tool**: Create final validation sub-agent

**What to Validate**:
- [ ] All tests passing (100% pass rate)
- [ ] Coverage >80%
- [ ] Code quality (black, pylint)
- [ ] No TODO comments without tracking
- [ ] Documentation complete

**Validation Prompt for Sub-Agent**:
```
Final review before commit:
- All files in strategic_consultant_agent/tools/framework_loader.py and tests/
- Verify:
  1. All tests passing
  2. Coverage >80%
  3. Black formatting applied
  4. Pylint passing
  5. All acceptance criteria met from PRP-001
```

**Expected Outcome**: Ready to commit

---

## QUALITY GATES (ALL MUST PASS)

### Gate 1: Code Quality ✓

**Run**:
```bash
# Format code
black strategic_consultant_agent/tools/framework_loader.py tests/tools/test_framework_loader.py

# Lint
pylint strategic_consultant_agent/tools/framework_loader.py
```

**Pass Criteria**:
- Zero linting errors
- Black formatting applied
- Code follows project patterns (CLAUDE.md)

**If Fails**: Fix errors before proceeding

---

### Gate 2: Testing ✓

**Run**:
```bash
pytest tests/tools/test_framework_loader.py --cov=strategic_consultant_agent.tools.framework_loader --cov-report=term-missing -v
```

**Pass Criteria**:
- All tests passing (100% pass rate)
- Coverage >80%
- All edge cases tested (missing file, malformed JSON, invalid structure)

**If Fails**: Write missing tests or fix failing tests

---

### Gate 3: ADK Pattern Compliance ✓

**Not applicable for this PRP** - No ADK agents or tools yet

---

### Gate 4: Framework Quality ✓

**Checks**:
- [ ] All 6 frameworks load correctly (scale_decision, product_launch, market_entry, investment_decision, operations_improvement, custom)
- [ ] Trigger phrases work for framework matching
- [ ] L1_categories structure preserved
- [ ] L2_branches structure preserved
- [ ] Custom framework (empty L1) handled

**Manual Test**:
```python
from strategic_consultant_agent.tools.framework_loader import load_framework, find_framework_by_trigger

# Test direct loading
framework = load_framework("scale_decision")
assert "L1_DESIRABILITY" in framework["L1_categories"]
assert "L1_FEASIBILITY" in framework["L1_categories"]
assert "L1_VIABILITY" in framework["L1_categories"]

# Test trigger matching
framework = find_framework_by_trigger("Should we scale deployment")
assert framework["name"] == "Scale Decision Framework"

print("✓ Framework Quality Gate Passed")
```

**Pass Criteria**: All frameworks load with complete structure

---

### Gate 5: Performance ✓

**Checks**:
- [ ] Templates loaded once at import (<100ms)
- [ ] Query operations <10ms
- [ ] No repeated file I/O

**Manual Test**:
```python
import time
from strategic_consultant_agent.tools.framework_loader import get_framework_loader

# Test load time
start = time.time()
loader1 = get_framework_loader()
load_time = (time.time() - start) * 1000
assert load_time < 100, f"Load too slow: {load_time}ms"

# Test singleton (should be instant)
start = time.time()
loader2 = get_framework_loader()
singleton_time = (time.time() - start) * 1000
assert singleton_time < 1, f"Singleton not working: {singleton_time}ms"
assert loader1 is loader2

# Test query time
start = time.time()
loader1.get_framework("scale_decision")
query_time = (time.time() - start) * 1000
assert query_time < 10, f"Query too slow: {query_time}ms"

print(f"✓ Performance Gate Passed (load: {load_time:.2f}ms, query: {query_time:.2f}ms)")
```

**Pass Criteria**: All performance targets met

---

## DOCUMENTATION UPDATES

### Code Comments
- [ ] Module docstring explains purpose
- [ ] Class docstring explains FrameworkLoader
- [ ] Function docstrings explain parameters and returns
- [ ] Complex logic has inline comments

### No README updates needed
This is an internal module, user-facing docs come later

---

## TESTING STRATEGY

### Unit Tests

**Location**: `tests/tools/test_framework_loader.py`

**Coverage Target**: >80%

**Test Cases**:
1. **Happy path**: Load bundled templates successfully
2. **Custom path**: Load from specified file path
3. **Error cases**:
   - Missing file → FileNotFoundError
   - Malformed JSON → ValueError
   - Invalid structure → ValueError (missing frameworks key)
   - Empty L1_categories for non-custom framework → ValueError
4. **Retrieval**:
   - Get framework by name (valid and invalid)
   - Get framework by trigger phrase (case-insensitive)
   - List all frameworks
   - Get frameworks with descriptions
5. **Singleton**: Verify singleton pattern works

---

## COMPLETION CHECKLIST

Before marking this PRP as complete:

### Implementation
- [ ] `strategic_consultant_agent/data/framework_templates.json` copied
- [ ] `strategic_consultant_agent/tools/framework_loader.py` created
- [ ] All functions implemented (FrameworkLoader class + convenience functions)
- [ ] Singleton pattern working correctly

### Testing
- [ ] `tests/tools/test_framework_loader.py` created
- [ ] All tests passing (100% pass rate)
- [ ] Coverage >80%
- [ ] Edge cases tested (missing file, malformed JSON, invalid structure)

### Validation
- [ ] Sub-agent validation checkpoint 1 passed (code quality)
- [ ] Sub-agent validation checkpoint 2 passed (final review)

### Quality Gates
- [ ] Gate 1: Code Quality ✓ (black, pylint)
- [ ] Gate 2: Testing ✓ (tests pass, >80% coverage)
- [ ] Gate 3: ADK Pattern Compliance ✓ (N/A for this PRP)
- [ ] Gate 4: Framework Quality ✓ (all 6 frameworks load)
- [ ] Gate 5: Performance ✓ (load <100ms, query <10ms)

### Documentation
- [ ] Code docstrings complete
- [ ] Inline comments for complex logic

### Progress Tracking
- [ ] TASKS.md updated with completion status
- [ ] All TodoWrite items marked complete
- [ ] Code committed with PRP reference

---

## NOTES

**Common Issues**:
- **Path issues**: Use `Path(__file__).parent.parent / "data"` for relative path
- **JSON encoding**: Ensure UTF-8 encoding when reading file
- **Singleton not working**: Check that `_loader_instance` is global variable

**Related Resources**:
- `docs/project-requirements/framework_templates.json` - Source data
- Python pathlib docs: https://docs.python.org/3/library/pathlib.html
- JSON module docs: https://docs.python.org/3/library/json.html

**Estimated Time**: 1 hour

---

**Generated**: 2025-11-20
**Last Updated**: 2025-11-20
**Status**: NOT STARTED
