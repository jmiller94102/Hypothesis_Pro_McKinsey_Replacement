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


def validate_l2_branches(tree: Dict, l1_key: str) -> Dict:
    """
    Validate L2 branches within a specific L1 category for MECE compliance.

    Args:
        tree: Full tree structure
        l1_key: The L1 category key to validate (e.g., "L1_DESIRABILITY")

    Returns:
        dict: {
            "is_mece": bool,
            "level": "L2",
            "component": str (L1 key),
            "issues": {
                "overlaps": [...],
                "level_inconsistencies": [...]
            }
        }
    """
    issues = {"overlaps": [], "level_inconsistencies": []}

    if l1_key not in tree:
        return {
            "is_mece": False,
            "level": "L2",
            "component": l1_key,
            "issues": {"overlaps": [f"L1 category {l1_key} not found"], "level_inconsistencies": []}
        }

    l1_data = tree[l1_key]
    l2_branches = l1_data.get("L2", {})

    if not l2_branches:
        return {
            "is_mece": False,
            "level": "L2",
            "component": l1_key,
            "issues": {"overlaps": [], "level_inconsistencies": ["No L2 branches found"]}
        }

    # Check for overlaps between L2 branches
    l2_keys = list(l2_branches.keys())
    for i, l2_key_a in enumerate(l2_keys):
        label_a = l2_branches[l2_key_a].get("label", l2_key_a).lower()

        for l2_key_b in l2_keys[i + 1:]:
            label_b = l2_branches[l2_key_b].get("label", l2_key_b).lower()

            # Check for keyword overlap
            words_a = set(label_a.split()) - {"the", "and", "or", "of", "to", "in", "for"}
            words_b = set(label_b.split()) - {"the", "and", "or", "of", "to", "in", "for"}

            common_words = words_a & words_b
            if len(common_words) > 1:
                issues["overlaps"].append(
                    f"L2 branches '{l2_branches[l2_key_a]['label']}' and "
                    f"'{l2_branches[l2_key_b]['label']}' may overlap (shared keywords: {common_words})"
                )

    # Check abstraction level consistency
    l2_labels = [branch.get("label", "").lower() for branch in l2_branches.values()]

    # Check for mixing strategic and tactical levels
    strategic_indicators = ["strategy", "approach", "model", "framework", "structure"]
    tactical_indicators = ["task", "action", "step", "activity", "process"]

    has_strategic = any(any(ind in label for ind in strategic_indicators) for label in l2_labels)
    has_tactical = any(any(ind in label for ind in tactical_indicators) for label in l2_labels)

    if has_strategic and has_tactical:
        issues["level_inconsistencies"].append(
            f"L2 branches in {l1_key} mix strategic and tactical levels"
        )

    # Check for too many branches (overwhelming for users)
    if len(l2_branches) > 7:
        issues["level_inconsistencies"].append(
            f"L2 in {l1_key} has {len(l2_branches)} branches - recommend 3-7 for clarity"
        )

    has_critical_issues = bool(issues["overlaps"] or issues["level_inconsistencies"])

    return {
        "is_mece": not has_critical_issues,
        "level": "L2",
        "component": l1_key,
        "issues": issues
    }


def validate_l3_leaves(tree: Dict, l1_key: str, l2_key: str) -> Dict:
    """
    Validate L3 leaves within a specific L2 branch for MECE compliance.

    Args:
        tree: Full tree structure
        l1_key: The L1 category key (e.g., "L1_DESIRABILITY")
        l2_key: The L2 branch key (e.g., "L2_USER_SATISFACTION")

    Returns:
        dict: {
            "is_mece": bool,
            "level": "L3",
            "component": str (L1_key.L2_key),
            "issues": {
                "overlaps": [...],
                "level_inconsistencies": [...],
                "missing_fields": [...]
            }
        }
    """
    issues = {"overlaps": [], "level_inconsistencies": [], "missing_fields": []}

    if l1_key not in tree:
        return {
            "is_mece": False,
            "level": "L3",
            "component": f"{l1_key}.{l2_key}",
            "issues": {"overlaps": [f"L1 category {l1_key} not found"],
                      "level_inconsistencies": [],
                      "missing_fields": []}
        }

    l2_branches = tree[l1_key].get("L2", {})

    if l2_key not in l2_branches:
        return {
            "is_mece": False,
            "level": "L3",
            "component": f"{l1_key}.{l2_key}",
            "issues": {"overlaps": [f"L2 branch {l2_key} not found in {l1_key}"],
                      "level_inconsistencies": [],
                      "missing_fields": []}
        }

    l3_leaves = l2_branches[l2_key].get("L3", {})

    if not l3_leaves:
        return {
            "is_mece": False,
            "level": "L3",
            "component": f"{l1_key}.{l2_key}",
            "issues": {"overlaps": [],
                      "level_inconsistencies": ["No L3 leaves found"],
                      "missing_fields": []}
        }

    # Check for overlaps between L3 leaves
    l3_keys = list(l3_leaves.keys())
    for i, l3_key_a in enumerate(l3_keys):
        label_a = l3_leaves[l3_key_a].get("label", l3_key_a).lower()

        for l3_key_b in l3_keys[i + 1:]:
            label_b = l3_leaves[l3_key_b].get("label", l3_key_b).lower()

            # Check for keyword overlap
            words_a = set(label_a.split()) - {"the", "and", "or", "of", "to", "in", "for", "by"}
            words_b = set(label_b.split()) - {"the", "and", "or", "of", "to", "in", "for", "by"}

            common_words = words_a & words_b
            if len(common_words) > 1:
                issues["overlaps"].append(
                    f"L3 leaves '{l3_leaves[l3_key_a]['label']}' and "
                    f"'{l3_leaves[l3_key_b]['label']}' may overlap (shared keywords: {common_words})"
                )

    # Validate required fields for each L3 leaf
    required_fields = ["label", "question", "metric_type", "target", "data_source"]

    for l3_key, l3_data in l3_leaves.items():
        missing = [field for field in required_fields if field not in l3_data or not l3_data[field]]
        if missing:
            issues["missing_fields"].append(
                f"L3 leaf '{l3_data.get('label', l3_key)}' missing required fields: {missing}"
            )

    # Check abstraction level consistency - L3 should be specific/measurable
    l3_labels = [leaf.get("label", "").lower() for leaf in l3_leaves.values()]

    # L3 should be concrete, not abstract
    abstract_indicators = ["overall", "general", "broad", "strategic", "high-level"]
    has_abstract = any(any(ind in label for ind in abstract_indicators) for label in l3_labels)

    if has_abstract:
        issues["level_inconsistencies"].append(
            f"L3 leaves in {l1_key}.{l2_key} should be specific/measurable, not abstract"
        )

    # Check for too many leaves
    if len(l3_leaves) > 7:
        issues["level_inconsistencies"].append(
            f"L3 in {l1_key}.{l2_key} has {len(l3_leaves)} leaves - recommend 3-7 for clarity"
        )

    has_critical_issues = bool(
        issues["overlaps"] or
        issues["level_inconsistencies"] or
        issues["missing_fields"]
    )

    return {
        "is_mece": not has_critical_issues,
        "level": "L3",
        "component": f"{l1_key}.{l2_key}",
        "issues": issues
    }
