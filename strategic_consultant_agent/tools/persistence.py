"""Persistence tools for saving and loading analysis artifacts."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


# Default storage directory
DEFAULT_STORAGE_DIR = Path(__file__).parent.parent.parent / "storage" / "projects"


def save_analysis(
    project_name: str,
    analysis_type: str,
    content: Dict,
    storage_dir: Optional[str] = None,
) -> Dict:
    """
    Persist analysis to JSON file for cross-session access.

    Args:
        project_name: Unique identifier for the project
        analysis_type: One of [hypothesis_tree, matrix_hypothesis_prioritization,
                        matrix_risk_register, matrix_task_prioritization,
                        matrix_measurement_priorities, research]
        content: The analysis content to save
        storage_dir: Optional custom storage directory

    Returns:
        dict: {"filepath": str, "version": int, "timestamp": str}
    """
    # Validate analysis type
    valid_types = [
        "hypothesis_tree",
        "matrix_hypothesis_prioritization",
        "matrix_risk_register",
        "matrix_task_prioritization",
        "matrix_measurement_priorities",
        "research",
    ]
    if analysis_type not in valid_types:
        raise ValueError(
            f"Invalid analysis_type '{analysis_type}'. "
            f"Must be one of: {valid_types}"
        )

    # Sanitize project name for filesystem
    safe_project_name = _sanitize_filename(project_name)

    # Determine storage directory
    base_dir = Path(storage_dir) if storage_dir else DEFAULT_STORAGE_DIR
    project_dir = base_dir / safe_project_name
    project_dir.mkdir(parents=True, exist_ok=True)

    # Determine version number
    existing_files = list(project_dir.glob(f"{analysis_type}_v*.json"))
    version = len(existing_files) + 1

    # Create filename
    filename = f"{analysis_type}_v{version}.json"
    filepath = project_dir / filename

    # Create metadata
    timestamp = datetime.now().isoformat()
    metadata = {
        "project_name": project_name,
        "analysis_type": analysis_type,
        "version": version,
        "timestamp": timestamp,
    }

    # Combine metadata and content
    save_data = {"metadata": metadata, "content": content}

    # Write to file
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(save_data, f, indent=2, ensure_ascii=False)

    return {
        "filepath": str(filepath),
        "version": version,
        "timestamp": timestamp,
    }


def load_analysis(
    project_name: str,
    analysis_type: Optional[str] = None,
    version: Optional[int] = None,
    storage_dir: Optional[str] = None,
) -> Dict:
    """
    Retrieve previous analysis from storage.

    Args:
        project_name: Project to load
        analysis_type: Specific analysis type (optional)
        version: Specific version number (optional, default: latest)
        storage_dir: Optional custom storage directory

    Returns:
        dict: Saved analysis content with metadata
    """
    # Sanitize project name
    safe_project_name = _sanitize_filename(project_name)

    # Determine storage directory
    base_dir = Path(storage_dir) if storage_dir else DEFAULT_STORAGE_DIR
    project_dir = base_dir / safe_project_name

    # Check if project directory exists
    if not project_dir.exists():
        raise FileNotFoundError(f"No saved analyses found for project '{project_name}'")

    # If no analysis_type specified, list all available
    if analysis_type is None:
        return _list_project_analyses(project_dir, project_name)

    # Find matching files
    if version is not None:
        # Load specific version
        filename = f"{analysis_type}_v{version}.json"
        filepath = project_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(
                f"Analysis '{analysis_type}' version {version} "
                f"not found for project '{project_name}'"
            )
    else:
        # Load latest version
        matching_files = sorted(
            project_dir.glob(f"{analysis_type}_v*.json"), reverse=True
        )

        if not matching_files:
            raise FileNotFoundError(
                f"No '{analysis_type}' analyses found for project '{project_name}'"
            )

        filepath = matching_files[0]

    # Load and return
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


def _sanitize_filename(name: str) -> str:
    """
    Sanitize a string for use as a filename.

    Args:
        name: String to sanitize

    Returns:
        str: Sanitized filename
    """
    # Replace spaces and special characters with underscores
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)

    # Remove consecutive underscores
    while "__" in safe_name:
        safe_name = safe_name.replace("__", "_")

    # Remove leading/trailing underscores
    safe_name = safe_name.strip("_")

    # Convert to lowercase
    safe_name = safe_name.lower()

    # Limit length
    if len(safe_name) > 100:
        safe_name = safe_name[:100]

    return safe_name


def _list_project_analyses(project_dir: Path, project_name: str) -> Dict:
    """
    List all analyses for a project.

    Args:
        project_dir: Path to project directory
        project_name: Project name

    Returns:
        dict: Summary of available analyses
    """
    analyses = {}

    # Find all JSON files
    all_files = list(project_dir.glob("*.json"))

    for filepath in all_files:
        # Parse filename
        stem = filepath.stem  # e.g., "hypothesis_tree_v1"

        # Extract analysis type and version
        if "_v" in stem:
            parts = stem.rsplit("_v", 1)
            if len(parts) == 2:
                analysis_type = parts[0]
                try:
                    version = int(parts[1])

                    # Initialize type list if needed
                    if analysis_type not in analyses:
                        analyses[analysis_type] = []

                    # Load metadata
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    metadata = data.get("metadata", {})

                    analyses[analysis_type].append(
                        {
                            "version": version,
                            "timestamp": metadata.get("timestamp"),
                            "filepath": str(filepath),
                        }
                    )
                except (ValueError, json.JSONDecodeError):
                    # Skip malformed files
                    continue

    # Sort by version (descending)
    for analysis_type in analyses:
        analyses[analysis_type].sort(key=lambda x: x["version"], reverse=True)

    return {
        "project_name": project_name,
        "analyses": analyses,
        "total_count": sum(len(versions) for versions in analyses.values()),
    }


def delete_analysis(
    project_name: str,
    analysis_type: str,
    version: int,
    storage_dir: Optional[str] = None,
) -> Dict:
    """
    Delete a specific analysis version.

    Args:
        project_name: Project name
        analysis_type: Analysis type to delete
        version: Version number to delete
        storage_dir: Optional custom storage directory

    Returns:
        dict: {"deleted": bool, "filepath": str}
    """
    # Sanitize project name
    safe_project_name = _sanitize_filename(project_name)

    # Determine storage directory
    base_dir = Path(storage_dir) if storage_dir else DEFAULT_STORAGE_DIR
    project_dir = base_dir / safe_project_name

    # Build filepath
    filename = f"{analysis_type}_v{version}.json"
    filepath = project_dir / filename

    if not filepath.exists():
        raise FileNotFoundError(
            f"Analysis '{analysis_type}' version {version} "
            f"not found for project '{project_name}'"
        )

    # Delete file
    os.remove(filepath)

    return {"deleted": True, "filepath": str(filepath)}


def delete_project(
    project_name: str,
    storage_dir: Optional[str] = None,
) -> Dict:
    """
    Delete an entire project directory and all its contents.

    Args:
        project_name: Project name to delete
        storage_dir: Optional custom storage directory

    Returns:
        dict: {"deleted": bool, "project_dir": str, "files_deleted": int}
    """
    import shutil

    # Sanitize project name
    safe_project_name = _sanitize_filename(project_name)

    # Determine storage directory
    base_dir = Path(storage_dir) if storage_dir else DEFAULT_STORAGE_DIR
    project_dir = base_dir / safe_project_name

    if not project_dir.exists():
        raise FileNotFoundError(
            f"Project '{project_name}' not found"
        )

    # Count files before deletion
    files_deleted = sum(1 for _ in project_dir.rglob("*") if _.is_file())

    # Delete entire project directory
    shutil.rmtree(project_dir)

    return {
        "deleted": True,
        "project_dir": str(project_dir),
        "files_deleted": files_deleted
    }


def get_latest_version(
    project_name: str, analysis_type: str, storage_dir: Optional[str] = None
) -> int:
    """
    Get the latest version number for an analysis type.

    Args:
        project_name: Project name
        analysis_type: Analysis type
        storage_dir: Optional custom storage directory

    Returns:
        int: Latest version number (0 if none exist)
    """
    # Sanitize project name
    safe_project_name = _sanitize_filename(project_name)

    # Determine storage directory
    base_dir = Path(storage_dir) if storage_dir else DEFAULT_STORAGE_DIR
    project_dir = base_dir / safe_project_name

    if not project_dir.exists():
        return 0

    # Find matching files
    matching_files = list(project_dir.glob(f"{analysis_type}_v*.json"))

    if not matching_files:
        return 0

    # Extract version numbers
    versions = []
    for filepath in matching_files:
        stem = filepath.stem
        if "_v" in stem:
            version_str = stem.rsplit("_v", 1)[1]
            try:
                versions.append(int(version_str))
            except ValueError:
                continue

    return max(versions) if versions else 0


# Matrix-specific convenience functions


def save_matrix(
    project_name: str,
    matrix_type: str,
    matrix_data: Dict,
    storage_dir: Optional[str] = None,
) -> Dict:
    """
    Save a 2x2 matrix for a project.

    Args:
        project_name: Project name
        matrix_type: One of [hypothesis_prioritization, risk_register,
                     task_prioritization, measurement_priorities]
        matrix_data: Matrix content including quadrants, placements, axes, etc.
        storage_dir: Optional custom storage directory

    Returns:
        dict: Save result with filepath, version, timestamp
    """
    # Convert matrix_type to analysis_type format
    analysis_type = f"matrix_{matrix_type}"

    return save_analysis(
        project_name=project_name,
        analysis_type=analysis_type,
        content=matrix_data,
        storage_dir=storage_dir,
    )


def load_matrix(
    project_name: str,
    matrix_type: str,
    version: Optional[int] = None,
    storage_dir: Optional[str] = None,
) -> Dict:
    """
    Load a 2x2 matrix for a project.

    Args:
        project_name: Project name
        matrix_type: One of [hypothesis_prioritization, risk_register,
                     task_prioritization, measurement_priorities]
        version: Specific version (optional, default: latest)
        storage_dir: Optional custom storage directory

    Returns:
        dict: Matrix data with metadata
    """
    # Convert matrix_type to analysis_type format
    analysis_type = f"matrix_{matrix_type}"

    return load_analysis(
        project_name=project_name,
        analysis_type=analysis_type,
        version=version,
        storage_dir=storage_dir,
    )


def list_project_matrices(
    project_name: str, storage_dir: Optional[str] = None
) -> Dict:
    """
    List all matrices for a project.

    Args:
        project_name: Project name
        storage_dir: Optional custom storage directory

    Returns:
        dict: Dictionary with matrix types as keys and lists of versions
    """
    # Load all analyses for project
    try:
        all_analyses = load_analysis(
            project_name=project_name, analysis_type=None, storage_dir=storage_dir
        )
    except FileNotFoundError:
        return {"project_name": project_name, "matrices": {}, "total_count": 0}

    # Filter for matrix types only
    matrices = {}
    for analysis_type, versions in all_analyses.get("analyses", {}).items():
        if analysis_type.startswith("matrix_"):
            # Extract matrix type (e.g., "matrix_risk_register" -> "risk_register")
            matrix_type = analysis_type.replace("matrix_", "")
            matrices[matrix_type] = versions

    return {
        "project_name": project_name,
        "matrices": matrices,
        "total_count": sum(len(versions) for versions in matrices.values()),
    }


def get_all_project_data(
    project_name: str, storage_dir: Optional[str] = None
) -> Dict:
    """
    Load complete project data including hypothesis tree and all matrices.

    Args:
        project_name: Project name
        storage_dir: Optional custom storage directory

    Returns:
        dict: {
            "hypothesis_tree": {...},
            "matrices": {
                "hypothesis_prioritization": {...},
                "risk_register": {...},
                "task_prioritization": {...},
                "measurement_priorities": {...}
            }
        }
    """
    result = {"hypothesis_tree": None, "matrices": {}}

    # Load hypothesis tree (latest version)
    try:
        tree_data = load_analysis(
            project_name=project_name,
            analysis_type="hypothesis_tree",
            storage_dir=storage_dir,
        )
        result["hypothesis_tree"] = tree_data.get("content")
    except FileNotFoundError:
        pass

    # Load all matrices (latest versions)
    matrix_types = [
        "hypothesis_prioritization",
        "risk_register",
        "task_prioritization",
        "measurement_priorities",
    ]

    for matrix_type in matrix_types:
        try:
            matrix_data = load_matrix(
                project_name=project_name,
                matrix_type=matrix_type,
                storage_dir=storage_dir,
            )
            result["matrices"][matrix_type] = matrix_data.get("content")
        except FileNotFoundError:
            # Matrix doesn't exist yet, that's okay
            result["matrices"][matrix_type] = None

    return result
