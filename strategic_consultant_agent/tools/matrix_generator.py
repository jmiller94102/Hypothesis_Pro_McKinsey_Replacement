"""AI-powered matrix generation tool using Google Gemini."""

import json
import os
from typing import Dict, List, Optional

import google.generativeai as genai

from strategic_consultant_agent.config.matrix_types import (
    get_matrix_type_config,
    should_auto_populate,
)
from strategic_consultant_agent.prompts.matrix_generation import (
    RISK_REGISTER_PROMPT,
    TASK_PRIORITIZATION_PROMPT,
    MEASUREMENT_PRIORITIES_PROMPT,
)


# Configure Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


def generate_matrix_from_tree(
    hypothesis_tree: Dict,
    matrix_type: str,
    model_name: str = "gemini-2.0-flash-exp",
) -> Dict:
    """
    Generate a 2x2 matrix using AI based on a hypothesis tree.

    Args:
        hypothesis_tree: The hypothesis tree structure
        matrix_type: One of [hypothesis_prioritization, risk_register,
                     task_prioritization, measurement_priorities]
        model_name: Gemini model to use (default: gemini-2.0-flash-exp)

    Returns:
        dict: Complete matrix data with quadrants, placements, axes, recommendations
    """
    # Get matrix type configuration
    config = get_matrix_type_config(matrix_type)

    # Get the appropriate prompt
    prompt_map = {
        "risk_register": RISK_REGISTER_PROMPT,
        "task_prioritization": TASK_PRIORITIZATION_PROMPT,
        "measurement_priorities": MEASUREMENT_PRIORITIES_PROMPT,
    }

    # For hypothesis_prioritization, use existing logic (auto-populate from L3 leaves)
    if matrix_type == "hypothesis_prioritization":
        return _generate_hypothesis_prioritization_matrix(hypothesis_tree, config)

    # For other types, use AI generation
    if matrix_type not in prompt_map:
        raise ValueError(
            f"Matrix type '{matrix_type}' does not support AI generation yet"
        )

    prompt_template = prompt_map[matrix_type]
    prompt = prompt_template.format(hypothesis_tree=json.dumps(hypothesis_tree, indent=2))

    # Call Gemini
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            temperature=0.7,
            response_mime_type="application/json",
        ),
    )

    # Parse AI response
    try:
        ai_data = json.loads(response.text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse AI response as JSON: {e}")

    # Transform AI response to matrix format
    matrix_data = _transform_ai_response_to_matrix(ai_data, config, matrix_type)

    return matrix_data


def _generate_hypothesis_prioritization_matrix(
    hypothesis_tree: Dict, config: Dict
) -> Dict:
    """
    Generate hypothesis prioritization matrix by extracting L3 leaves from tree.

    This uses the existing logic where we auto-populate from the hypothesis tree
    rather than using AI generation.
    """
    # Extract L3 leaves
    l3_leaves = _extract_l3_leaves(hypothesis_tree)

    # Initialize placements
    placements = {"Q1": [], "Q2": [], "Q3": [], "Q4": []}

    # Simple heuristic: distribute leaves across quadrants based on position
    # In production, this could be more sophisticated or AI-powered
    for i, leaf in enumerate(l3_leaves):
        # Distribute evenly for now
        quadrant_index = i % 4
        quadrant = f"Q{quadrant_index + 1}"
        placements[quadrant].append(leaf["label"])

    return {
        "matrix_type": "hypothesis_prioritization",
        "quadrants": config["quadrants"],
        "placements": placements,
        "x_axis": config["x_axis"],
        "y_axis": config["y_axis"],
        "recommendations": config["default_recommendations"],
    }


def _extract_l3_leaves(hypothesis_tree: Dict) -> List[Dict]:
    """Extract all L3 leaves from hypothesis tree."""
    leaves = []

    # Navigate tree structure: L1 > L2 > L3
    for l1_key, l1_data in hypothesis_tree.items():
        if not isinstance(l1_data, dict) or "L2_branches" not in l1_data:
            continue

        for l2_key, l2_data in l1_data["L2_branches"].items():
            if not isinstance(l2_data, dict) or "L3_leaves" not in l2_data:
                continue

            for l3_key, l3_data in l2_data["L3_leaves"].items():
                if isinstance(l3_data, dict):
                    leaves.append(
                        {
                            "key": l3_key,
                            "label": l3_data.get("label", l3_key),
                            "question": l3_data.get("question", ""),
                            "metric_type": l3_data.get("metric_type", ""),
                            "target": l3_data.get("target", ""),
                        }
                    )

    return leaves


def _transform_ai_response_to_matrix(
    ai_data: Dict, config: Dict, matrix_type: str
) -> Dict:
    """
    Transform AI-generated data into standard matrix format.

    Args:
        ai_data: Raw AI response (e.g., {"risks": [...]} or {"tasks": [...]})
        config: Matrix type configuration
        matrix_type: Type of matrix being generated

    Returns:
        dict: Standard matrix format with quadrants, placements, axes, etc.
    """
    # Determine the data key based on matrix type
    data_key_map = {
        "risk_register": "risks",
        "task_prioritization": "tasks",
        "measurement_priorities": "metrics",
    }

    data_key = data_key_map.get(matrix_type)
    if not data_key or data_key not in ai_data:
        raise ValueError(
            f"AI response missing expected key '{data_key}' for matrix type '{matrix_type}'"
        )

    items = ai_data[data_key]

    # Group items by quadrant
    placements = {"Q1": [], "Q2": [], "Q3": [], "Q4": []}

    for item in items:
        quadrant = item.get("quadrant", "Q1")
        if quadrant not in placements:
            quadrant = "Q1"  # Default to Q1 if invalid

        # Extract the item label (risk/task/metric description)
        if matrix_type == "risk_register":
            label = item.get("risk", "Unknown risk")
        elif matrix_type == "task_prioritization":
            label = item.get("task", "Unknown task")
        elif matrix_type == "measurement_priorities":
            label = item.get("metric", "Unknown metric")
        else:
            label = str(item)

        placements[quadrant].append(label)

    return {
        "matrix_type": matrix_type,
        "quadrants": config["quadrants"],
        "placements": placements,
        "x_axis": config["x_axis"],
        "y_axis": config["y_axis"],
        "recommendations": config["default_recommendations"],
    }


def regenerate_matrix_item(
    hypothesis_tree: Dict,
    matrix_type: str,
    quadrant: str,
    item_text: str,
    model_name: str = "gemini-2.0-flash-exp",
) -> str:
    """
    Regenerate or refine a single matrix item using AI.

    Useful for editing/improving individual items after initial generation.

    Args:
        hypothesis_tree: The hypothesis tree context
        matrix_type: Type of matrix
        quadrant: Which quadrant (Q1-Q4)
        item_text: Current text of the item
        model_name: Gemini model to use

    Returns:
        str: Refined item text
    """
    config = get_matrix_type_config(matrix_type)
    quadrant_info = config["quadrants"].get(quadrant, {})

    prompt = f"""Given this hypothesis tree:
{json.dumps(hypothesis_tree, indent=2)}

Refine this {matrix_type.replace('_', ' ')} item for the {quadrant_info.get('name')} quadrant ({quadrant_info.get('position')}):

Current item: "{item_text}"

Provide an improved, more specific version of this item that:
1. Is directly relevant to the hypothesis tree
2. Fits the quadrant positioning ({quadrant_info.get('position')})
3. Is actionable and concrete
4. Is concise (1-2 sentences max)

Return ONLY the improved item text, no JSON, no explanation.
"""

    model = genai.GenerativeModel(model_name)
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(temperature=0.7),
    )

    return response.text.strip()
