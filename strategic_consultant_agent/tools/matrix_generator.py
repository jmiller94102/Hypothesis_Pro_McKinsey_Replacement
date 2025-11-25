"""AI-powered matrix generation tool using Google Gemini."""

import json
import os
import time
from typing import Dict, List, Optional

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from strategic_consultant_agent.config.matrix_types import (
    get_matrix_type_config,
    should_auto_populate,
)
from strategic_consultant_agent.prompts.matrix_generation import (
    RISK_REGISTER_PROMPT,
    TASK_PRIORITIZATION_PROMPT,
    MEASUREMENT_PRIORITIES_PROMPT,
    HYPOTHESIS_PRIORITIZATION_PROMPT,
)


# Configure Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# Model fallback order (from preferred to fallback)
# Using actual available models from the API
MODEL_FALLBACK_ORDER = [
    "gemini-2.5-flash",           # Latest flash model with good limits
    "gemini-flash-latest",        # Alias for latest flash
    "gemini-2.0-flash",           # Stable flash model
    "gemini-2.0-flash-lite",      # Lighter version with higher limits
    "gemini-pro-latest",          # Latest pro model (more capable but slower)
    "gemini-2.5-pro",             # Specific pro version
]


def _call_gemini_with_fallback(
    prompt: str,
    generation_config: genai.GenerationConfig,
    max_retries: int = 3,
) -> str:
    """
    Call Gemini API with automatic model fallback and retry logic.

    Tries models in order from MODEL_FALLBACK_ORDER until one succeeds.
    Handles rate limits with exponential backoff.

    Args:
        prompt: The prompt to send to the model
        generation_config: Generation configuration
        max_retries: Maximum retry attempts per model

    Returns:
        str: The model's response text

    Raises:
        ValueError: If all models fail
    """
    last_error = None

    for model_name in MODEL_FALLBACK_ORDER:
        print(f"Trying model: {model_name}")

        for attempt in range(max_retries):
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt, generation_config=generation_config)
                print(f"Success with model: {model_name}")
                return response.text

            except google_exceptions.ResourceExhausted as e:
                # Rate limit hit - wait and retry
                wait_time = (2 ** attempt) * 1  # Exponential backoff: 1s, 2s, 4s
                print(f"Rate limit hit for {model_name}, waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                last_error = e
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                # If last retry, move to next model

            except google_exceptions.NotFound as e:
                # Model not found - try next model immediately
                print(f"Model {model_name} not found, trying next model")
                last_error = e
                break

            except google_exceptions.InvalidArgument as e:
                # Invalid request - try next model
                print(f"Invalid argument for {model_name}, trying next model")
                last_error = e
                break

            except Exception as e:
                # Other errors - try next model
                print(f"Error with {model_name}: {e}, trying next model")
                last_error = e
                break

    # All models failed
    raise ValueError(
        f"All Gemini models failed. Last error: {last_error}. "
        f"Please check your API key and quota limits at https://ai.google.dev/usage"
    )


def generate_matrix_from_tree(
    hypothesis_tree: Dict,
    matrix_type: str,
    model_name: str = "gemini-1.5-flash",
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
        "hypothesis_prioritization": HYPOTHESIS_PRIORITIZATION_PROMPT,
        "risk_register": RISK_REGISTER_PROMPT,
        "task_prioritization": TASK_PRIORITIZATION_PROMPT,
        "measurement_priorities": MEASUREMENT_PRIORITIES_PROMPT,
    }

    # Use AI generation for all matrix types
    if matrix_type not in prompt_map:
        raise ValueError(
            f"Matrix type '{matrix_type}' does not support AI generation yet"
        )

    prompt_template = prompt_map[matrix_type]
    prompt = prompt_template.format(hypothesis_tree=json.dumps(hypothesis_tree, indent=2))

    # Call Gemini with automatic fallback
    generation_config = genai.GenerationConfig(
        temperature=0.7,
        response_mime_type="application/json",
    )

    response_text = _call_gemini_with_fallback(prompt, generation_config)

    # Parse AI response
    try:
        ai_data = json.loads(response_text)
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
        "hypothesis_prioritization": "hypotheses",
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

        # Extract the item label (risk/task/metric/hypothesis description)
        if matrix_type == "risk_register":
            label = item.get("risk", "Unknown risk")
        elif matrix_type == "task_prioritization":
            label = item.get("task", "Unknown task")
        elif matrix_type == "measurement_priorities":
            label = item.get("metric", "Unknown metric")
        elif matrix_type == "hypothesis_prioritization":
            label = item.get("hypothesis", "Unknown hypothesis")
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
    model_name: str = "gemini-1.5-flash",
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

    generation_config = genai.GenerationConfig(temperature=0.7)
    response_text = _call_gemini_with_fallback(prompt, generation_config)

    return response_text.strip()
