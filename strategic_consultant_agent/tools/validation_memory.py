"""Memory system for tracking MECE validation failures and providing feedback."""

from typing import Dict, List, Optional
from datetime import datetime


class ValidationMemory:
    """Tracks validation failures to provide feedback for LLM regeneration."""

    def __init__(self):
        """Initialize empty failure history."""
        self.failures: List[Dict] = []

    def record_failure(
        self,
        level: str,  # "L2" or "L3"
        component: str,  # "L1_DESIRABILITY" or "all"
        validation_result: Dict,
        iteration: int
    ) -> None:
        """
        Record a validation failure.

        Args:
            level: Which level failed validation ("L2" or "L3")
            component: Which component failed ("all", "L1_DESIRABILITY", etc.)
            validation_result: Full validation result dict
            iteration: Which attempt number (1, 2, 3)
        """
        self.failures.append({
            "timestamp": datetime.now().isoformat(),
            "iteration": iteration,
            "level": level,
            "component": component,
            "overlaps": validation_result.get("issues", {}).get("overlaps", []),
            "inconsistencies": validation_result.get("issues", {}).get("level_inconsistencies", [])
        })

    def get_feedback_prompt(self, level: str, component: Optional[str] = None) -> str:
        """
        Format failures into actionable LLM feedback.

        Args:
            level: Filter by level ("L2" or "L3")
            component: Filter by component (optional, e.g. "L1_DESIRABILITY")

        Returns:
            Formatted prompt explaining what failed and how to fix it
        """
        # Filter relevant failures
        relevant_failures = [
            f for f in self.failures
            if f["level"] == level and (component is None or f["component"] == component)
        ]

        if not relevant_failures:
            return ""

        feedback_parts = [
            "",
            "=" * 80,
            "⚠️  PREVIOUS GENERATION ATTEMPTS FAILED - Learn from these mistakes:",
            "=" * 80,
            ""
        ]

        for failure in relevant_failures:
            feedback_parts.append(f"📍 Attempt {failure['iteration']}:")
            feedback_parts.append("")

            if failure["overlaps"]:
                feedback_parts.append("  ❌ OVERLAPS DETECTED:")
                for overlap in failure["overlaps"]:
                    feedback_parts.append(f"     • {overlap}")
                feedback_parts.append("")
                feedback_parts.append("  → FIX: Ensure each branch/leaf is MUTUALLY EXCLUSIVE")
                feedback_parts.append("     - Use different terminology that doesn't overlap semantically")
                feedback_parts.append("     - Avoid synonyms (e.g., 'Cost' and 'Financial' overlap)")
                feedback_parts.append("")

            if failure["inconsistencies"]:
                feedback_parts.append("  ❌ LEVEL INCONSISTENCIES:")
                for inconsistency in failure["inconsistencies"]:
                    feedback_parts.append(f"     • {inconsistency}")
                feedback_parts.append("")
                feedback_parts.append("  → FIX: Maintain CONSISTENT ABSTRACTION LEVEL")
                feedback_parts.append("     - All branches/leaves should be at similar specificity")
                feedback_parts.append("     - Don't mix strategic and tactical items")
                feedback_parts.append("")

            feedback_parts.append("-" * 80)
            feedback_parts.append("")

        feedback_parts.extend([
            "🎯 KEY INSTRUCTION:",
            "   DO NOT repeat the exact same mistakes from previous attempts.",
            "   Generate DIFFERENT branches/leaves that avoid these specific issues.",
            "=" * 80,
            ""
        ])

        return "\n".join(feedback_parts)

    def get_failure_count(self, level: str, component: Optional[str] = None) -> int:
        """
        Count number of failures for a given level/component.

        Args:
            level: Filter by level
            component: Filter by component (optional)

        Returns:
            Number of failures matching criteria
        """
        return len([
            f for f in self.failures
            if f["level"] == level and (component is None or f["component"] == component)
        ])

    def clear(self) -> None:
        """Clear all failure history."""
        self.failures.clear()
