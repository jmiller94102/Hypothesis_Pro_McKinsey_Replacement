"""Framework template loading and validation system."""

import json
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
            with open(self.template_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Validate structure
            self._validate_structure(data)

            return data

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in framework templates: {e}") from e

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
                raise ValueError(f"Framework '{name}' missing 'L1_categories'")

            # Custom framework is allowed to have empty L1_categories
            if name != "custom" and not framework["L1_categories"]:
                raise ValueError(f"Framework '{name}' has empty 'L1_categories'")

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
