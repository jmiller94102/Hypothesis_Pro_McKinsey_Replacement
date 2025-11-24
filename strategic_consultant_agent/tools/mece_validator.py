"""MECE (Mutually Exclusive, Collectively Exhaustive) structure validation."""

from typing import Dict, List, Set


def validate_mece_structure(structure: Dict) -> Dict:
    """
    Validate a hierarchical structure for MECE compliance.

    Args:
        structure: Hypothesis tree structure to validate

    Returns:
        dict: {
            "is_mece": bool,
            "issues": {
                "overlaps": [...],
                "gaps": [...],
                "level_inconsistencies": [...]
            },
            "suggestions": [...]
        }
    """
    issues = {"overlaps": [], "gaps": [], "level_inconsistencies": []}
    suggestions = []

    # Extract tree structure
    tree = structure.get("tree", {})
    problem = structure.get("problem", "")

    # Check for overlaps at L1 level
    l1_overlaps = _check_l1_overlaps(tree)
    issues["overlaps"].extend(l1_overlaps)

    # Check for gaps at L1 level
    l1_gaps = _check_l1_gaps(tree, problem)
    issues["gaps"].extend(l1_gaps)

    # Check for level inconsistencies
    level_issues = _check_level_consistency(tree)
    issues["level_inconsistencies"].extend(level_issues)

    # Generate suggestions
    if issues["overlaps"]:
        suggestions.append(
            "Clarify boundaries between overlapping categories to ensure mutual exclusivity"
        )

    if issues["gaps"]:
        suggestions.append(
            "Consider adding missing dimensions to ensure comprehensive coverage"
        )

    if issues["level_inconsistencies"]:
        suggestions.append(
            "Ensure all categories at the same level are at similar levels of abstraction"
        )

    # Determine if MECE
    # CRITICAL: Only overlaps and level_inconsistencies are HARD failures
    # Gaps are SOFT warnings - they suggest potential improvements but don't fail MECE
    has_critical_issues = bool(
        issues["overlaps"] or issues["level_inconsistencies"]
    )
    is_mece = not has_critical_issues

    # Separate warnings from issues
    warnings = issues["gaps"]  # Gaps are soft warnings

    return {
        "is_mece": is_mece,
        "issues": {
            "overlaps": issues["overlaps"],
            "level_inconsistencies": issues["level_inconsistencies"]
        },
        "warnings": warnings,  # Gaps are now warnings, not failures
        "suggestions": (
            suggestions if not is_mece else ["Structure passes MECE validation"]
        ),
    }


def _check_l1_overlaps(tree: Dict) -> List[str]:
    """
    Check for overlaps between L1 categories.

    Args:
        tree: Tree structure

    Returns:
        list: List of overlap descriptions
    """
    overlaps = []

    # Known overlap patterns
    overlap_keywords = {
        "cost": ["financial", "budget", "savings", "roi"],
        "financial": ["cost", "revenue", "budget"],
        "risk": ["regulatory", "compliance", "legal"],
        "technical": ["system", "infrastructure", "capability"],
        "operational": ["process", "workflow", "capability"],
    }

    # Exception patterns (these are valid L1 structures that may appear to overlap)
    valid_patterns = {
        # Standard frameworks
        ("desirability", "feasibility", "viability"),
        ("strategic", "operational", "external"),
        # Hypothesis trees
        ("hypothesis", "hypothesis", "hypothesis"),  # Multiple hypotheses are valid
        ("primary", "alternative", "tertiary"),
    }

    l1_keys = list(tree.keys())
    l1_labels = [tree[key].get("label", key).lower() for key in l1_keys]

    # Check if this matches a valid pattern
    for pattern in valid_patterns:
        if all(any(p in label for p in pattern) for label in l1_labels):
            return []  # No overlaps for recognized valid patterns

    for i, l1_key_a in enumerate(l1_keys):
        label_a = tree[l1_key_a].get("label", l1_key_a).lower()

        for l1_key_b in l1_keys[i + 1 :]:
            label_b = tree[l1_key_b].get("label", l1_key_b).lower()

            # Check if labels share keywords (but ignore common words)
            words_a = set(label_a.split()) - {"risk", "risks", "hypothesis", "the", "and", "or"}
            words_b = set(label_b.split()) - {"risk", "risks", "hypothesis", "the", "and", "or"}

            # Direct keyword match (only if substantive overlap)
            common_words = words_a & words_b
            if len(common_words) > 1:  # More than one word overlap
                overlaps.append(
                    f"L1 categories '{tree[l1_key_a]['label']}' and "
                    f"'{tree[l1_key_b]['label']}' may overlap (shared keywords: {common_words})"
                )

            # Semantic overlap check
            for base_word, related_words in overlap_keywords.items():
                if base_word in label_a:
                    if any(word in label_b for word in related_words):
                        overlaps.append(
                            f"L1 categories '{tree[l1_key_a]['label']}' and "
                            f"'{tree[l1_key_b]['label']}' may have semantic overlap"
                        )

    return overlaps


def _check_l1_gaps(tree: Dict, problem: str) -> List[str]:
    """
    Check for potential gaps in L1 coverage.

    Args:
        tree: Tree structure
        problem: Strategic question

    Returns:
        list: List of gap descriptions
    """
    gaps = []

    # Extract all L1 labels
    l1_labels = [data.get("label", "").lower() for data in tree.values()]
    combined_labels = " ".join(l1_labels)

    # Common critical dimensions by industry/problem type
    critical_dimensions = {
        "regulatory": ["healthcare", "medical", "pharma", "compliance"],
        "competitive": ["market", "launch", "entry", "competitive"],
        "customer": ["product", "service", "user", "customer"],
        "technology": ["technical", "system", "digital", "infrastructure"],
        "financial": ["investment", "budget", "financial", "cost"],
    }

    problem_lower = problem.lower()

    # Check if problem indicates need for certain dimensions
    for dimension, trigger_words in critical_dimensions.items():
        # If problem mentions trigger words but dimension not in tree
        problem_needs_dimension = any(word in problem_lower for word in trigger_words)
        dimension_missing = dimension not in combined_labels

        if problem_needs_dimension and dimension_missing:
            gaps.append(
                f"Consider adding '{dimension.capitalize()}' dimension - "
                f"problem context suggests it may be relevant"
            )

    return gaps


def _check_level_consistency(tree: Dict) -> List[str]:
    """
    Check that all items at same level have similar abstraction level.

    Args:
        tree: Tree structure

    Returns:
        list: List of level inconsistency descriptions
    """
    inconsistencies = []

    # Check L1 level - all should be high-level strategic categories
    strategic_keywords = {
        "desirability",
        "feasibility",
        "viability",
        "strategic",
        "market",
        "competitive",
        "execution",
    }
    tactical_keywords = {
        "testing",
        "deployment",
        "implementation",
        "specific",
        "detailed",
    }

    l1_labels = [data.get("label", "").lower() for data in tree.values()]

    has_strategic = any(
        any(keyword in label for keyword in strategic_keywords) for label in l1_labels
    )
    has_tactical = any(
        any(keyword in label for keyword in tactical_keywords) for label in l1_labels
    )

    if has_strategic and has_tactical:
        inconsistencies.append(
            "L1 categories mix strategic and tactical levels - "
            "consider keeping all at strategic level"
        )

    # Check that L1 categories are not too granular
    if len(tree) > 6:
        inconsistencies.append(
            f"L1 has {len(tree)} categories - "
            f"consider consolidating for better comprehension (recommend 3-5)"
        )

    return inconsistencies
