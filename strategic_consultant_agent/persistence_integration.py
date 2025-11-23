"""Integration of persistence tools into agent workflow.

This module provides helper functions to automatically save completed analyses
and load previous projects, integrating the persistence tools with the
multi-agent workflow.
"""

from datetime import datetime
from typing import Any

from strategic_consultant_agent.tools.persistence import (
    save_analysis,
    load_analysis,
    get_latest_version,
)


def save_completed_analysis(
    project_name: str,
    hypothesis_tree: dict[str, Any],
    priority_matrix: dict[str, Any] | None = None,
    market_research: str | None = None,
    competitor_research: str | None = None,
    additional_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Save a completed strategic analysis with all components.

    This function packages the results from all three phases of the workflow
    (research, analysis, prioritization) into a single saved analysis file.

    Args:
        project_name: Name of the project/analysis
        hypothesis_tree: The generated hypothesis tree (from analysis phase)
        priority_matrix: The prioritization matrix (from prioritizer), optional
        market_research: Market research findings (from research phase), optional
        competitor_research: Competitor research findings (from research phase), optional
        additional_metadata: Additional metadata to include, optional

    Returns:
        dict: Result containing file_path and version info

    Example:
        >>> result = save_completed_analysis(
        ...     project_name="fall_detection_scaling",
        ...     hypothesis_tree={...},
        ...     priority_matrix={...},
        ...     market_research="Market analysis...",
        ...     competitor_research="Competitor analysis..."
        ... )
        >>> print(result["file_path"])
        'storage/projects/fall_detection_scaling_v1.json'
    """
    # Package all analysis components
    analysis_data = {
        "hypothesis_tree": hypothesis_tree,
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "framework_used": hypothesis_tree.get("framework_used", "unknown"),
            "strategic_question": hypothesis_tree.get("strategic_question", ""),
            "components_included": ["hypothesis_tree"],
        },
    }

    if priority_matrix:
        analysis_data["priority_matrix"] = priority_matrix
        analysis_data["metadata"]["components_included"].append("priority_matrix")

    if market_research:
        analysis_data["market_research"] = market_research
        analysis_data["metadata"]["components_included"].append("market_research")

    if competitor_research:
        analysis_data["competitor_research"] = competitor_research
        analysis_data["metadata"]["components_included"].append("competitor_research")

    if additional_metadata:
        analysis_data["metadata"].update(additional_metadata)

    # Save the analysis using the persistence tool
    # Note: We save as "hypothesis_tree" type since that's the primary artifact
    return save_analysis(
        project_name=project_name, analysis_type="hypothesis_tree", content=analysis_data
    )


def load_previous_analysis(
    project_name: str, version: int | None = None
) -> dict[str, Any]:
    """
    Load a previous strategic analysis.

    Args:
        project_name: Name of the project/analysis to load
        version: Specific version number to load (e.g., 1, 2, 3).
                If None, loads the latest version.

    Returns:
        dict: The complete saved analysis including all components and metadata

    Raises:
        FileNotFoundError: If the requested analysis doesn't exist

    Example:
        >>> # Load latest version
        >>> analysis = load_previous_analysis("fall_detection_scaling")
        >>> print(analysis["hypothesis_tree"]["strategic_question"])
        'Should we scale deployment of fall detection?'
        >>>
        >>> # Load specific version
        >>> v1_analysis = load_previous_analysis("fall_detection_scaling", version=1)
    """
    # Load analysis (defaults to hypothesis_tree type and latest version if not specified)
    return load_analysis(
        project_name=project_name, analysis_type="hypothesis_tree", version=version
    )


def extract_hypothesis_tree(analysis: dict[str, Any]) -> dict[str, Any]:
    """
    Extract hypothesis tree from a loaded analysis.

    Args:
        analysis: The loaded analysis dictionary

    Returns:
        dict: The hypothesis tree

    Example:
        >>> analysis = load_previous_analysis("fall_detection_scaling")
        >>> tree = extract_hypothesis_tree(analysis)
        >>> print(tree["L1_DESIRABILITY"]["label"])
        'Desirability'
    """
    return analysis.get("hypothesis_tree", {})


def extract_priority_matrix(analysis: dict[str, Any]) -> dict[str, Any] | None:
    """
    Extract priority matrix from a loaded analysis.

    Args:
        analysis: The loaded analysis dictionary

    Returns:
        dict | None: The priority matrix, or None if not included

    Example:
        >>> analysis = load_previous_analysis("fall_detection_scaling")
        >>> matrix = extract_priority_matrix(analysis)
        >>> if matrix:
        ...     print(matrix["matrix_type"])
    """
    return analysis.get("priority_matrix")


def extract_research_findings(
    analysis: dict[str, Any],
) -> tuple[str | None, str | None]:
    """
    Extract research findings from a loaded analysis.

    Args:
        analysis: The loaded analysis dictionary

    Returns:
        tuple: (market_research, competitor_research)
               Either or both may be None if not included

    Example:
        >>> analysis = load_previous_analysis("fall_detection_scaling")
        >>> market, competitor = extract_research_findings(analysis)
        >>> if market:
        ...     print("Market research available")
    """
    market_research = analysis.get("market_research")
    competitor_research = analysis.get("competitor_research")
    return market_research, competitor_research


def get_analysis_metadata(analysis: dict[str, Any]) -> dict[str, Any]:
    """
    Extract metadata from a loaded analysis.

    Args:
        analysis: The loaded analysis dictionary

    Returns:
        dict: Metadata including timestamp, framework_used, etc.

    Example:
        >>> analysis = load_previous_analysis("fall_detection_scaling")
        >>> metadata = get_analysis_metadata(analysis)
        >>> print(metadata["timestamp"])
        '2025-11-23T...'
        >>> print(metadata["framework_used"])
        'scale_decision'
    """
    return analysis.get("metadata", {})


def format_analysis_summary(analysis: dict[str, Any]) -> str:
    """
    Create a human-readable summary of a loaded analysis.

    Args:
        analysis: The loaded analysis dictionary

    Returns:
        str: Formatted summary text

    Example:
        >>> analysis = load_previous_analysis("fall_detection_scaling")
        >>> summary = format_analysis_summary(analysis)
        >>> print(summary)
        Strategic Analysis Summary
        ==========================
        Question: Should we scale deployment of fall detection?
        Framework: scale_decision
        Date: 2025-11-23
        ...
    """
    metadata = get_analysis_metadata(analysis)
    tree = extract_hypothesis_tree(analysis)
    matrix = extract_priority_matrix(analysis)

    summary_lines = [
        "Strategic Analysis Summary",
        "=" * 50,
        f"Question: {tree.get('strategic_question', 'N/A')}",
        f"Framework: {metadata.get('framework_used', 'N/A')}",
        f"Date: {metadata.get('timestamp', 'N/A')[:10]}",
        "",
        "Components Included:",
    ]

    components = metadata.get("components_included", [])
    for component in components:
        summary_lines.append(f"  ✓ {component.replace('_', ' ').title()}")

    if matrix:
        summary_lines.extend(
            ["", f"Priority Matrix Type: {matrix.get('matrix_type', 'N/A')}"]
        )

    # Add L1 categories summary
    if tree:
        l1_categories = [
            key for key in tree.keys() if key.startswith("L1_") and key != "L1_"
        ]
        if l1_categories:
            summary_lines.extend(["", "L1 Categories:"])
            for cat in l1_categories:
                label = tree[cat].get("label", cat)
                summary_lines.append(f"  - {label}")

    return "\n".join(summary_lines)


def list_saved_analyses(project_name: str) -> list[dict[str, Any]]:
    """
    List all saved versions of a project.

    Args:
        project_name: Name of the project

    Returns:
        list: List of dicts with version info

    Example:
        >>> analyses = list_saved_analyses("fall_detection_scaling")
        >>> for analysis in analyses:
        ...     print(f"{analysis['version']}: {analysis['timestamp']}")
        1: 2025-11-23T10:00:00
        2: 2025-11-23T14:30:00
    """
    try:
        # Try to load to get version info - this will fail if no analyses exist
        analysis = load_analysis(project_name, analysis_type="hypothesis_tree")
        # Get the version from the loaded analysis
        version = analysis.get("metadata", {}).get("version", 1)

        versions = []
        for v in range(1, version + 1):
            try:
                analysis = load_analysis(
                    project_name, analysis_type="hypothesis_tree", version=v
                )
                metadata = get_analysis_metadata(analysis)
                versions.append(
                    {
                        "version": v,
                        "timestamp": metadata.get("timestamp", "unknown"),
                        "framework": metadata.get("framework_used", "unknown"),
                        "question": extract_hypothesis_tree(analysis).get(
                            "strategic_question", ""
                        ),
                    }
                )
            except FileNotFoundError:
                continue

        return versions
    except FileNotFoundError:
        return []
