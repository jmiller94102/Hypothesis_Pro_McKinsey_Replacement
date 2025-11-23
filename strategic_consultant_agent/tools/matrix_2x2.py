"""Generate 2x2 prioritization and positioning matrices."""

from typing import Dict, List, Optional


def generate_2x2_matrix(
    items: List[str],
    x_axis: str = "Effort",
    y_axis: str = "Impact",
    matrix_type: str = "prioritization",
    assessments: Optional[Dict] = None,
) -> Dict:
    """
    Create a 2x2 prioritization or positioning matrix.

    Args:
        items: List of items to plot (hypotheses, features, etc.)
        x_axis: Label for x-axis (default: "Effort")
        y_axis: Label for y-axis (default: "Impact")
        matrix_type: One of [prioritization, bcg, risk, eisenhower, custom]
        assessments: Optional dict of {item: {"x": score, "y": score}}

    Returns:
        dict: Matrix with quadrant definitions and item placements
    """
    # Get quadrant definitions based on matrix type
    quadrants = _get_quadrant_definitions(matrix_type, x_axis, y_axis)

    # Assess items if not provided
    if assessments is None:
        assessments = _auto_assess_items(items, x_axis, y_axis)

    # Place items in quadrants
    placements = _place_items_in_quadrants(items, assessments, quadrants)

    # Generate recommendations
    recommendations = _generate_recommendations(placements, matrix_type)

    return {
        "matrix_type": matrix_type,
        "x_axis": x_axis,
        "y_axis": y_axis,
        "quadrants": quadrants,
        "items": items,
        "assessments": assessments,
        "placements": placements,
        "recommendations": recommendations,
    }


def _get_quadrant_definitions(matrix_type: str, x_axis: str, y_axis: str) -> Dict:
    """
    Get quadrant definitions based on matrix type.

    Args:
        matrix_type: Type of matrix
        x_axis: X-axis label
        y_axis: Y-axis label

    Returns:
        dict: Quadrant definitions
    """
    if matrix_type == "prioritization":
        return {
            "Q1": {
                "name": "Quick Wins",
                "position": "High Impact, Low Effort",
                "description": "Do these first - high value with minimal investment",
                "action": "Prioritize immediately",
            },
            "Q2": {
                "name": "Strategic Bets",
                "position": "High Impact, High Effort",
                "description": "Invest carefully - high value but requires significant resources",
                "action": "Plan strategically and resource appropriately",
            },
            "Q3": {
                "name": "Fill Later",
                "position": "Low Impact, Low Effort",
                "description": "Do if time/resources permit - low priority",
                "action": "Deprioritize or delegate",
            },
            "Q4": {
                "name": "Hard Slogs",
                "position": "Low Impact, High Effort",
                "description": "Avoid unless required - poor return on investment",
                "action": "Eliminate or rethink approach",
            },
        }
    elif matrix_type == "bcg":
        return {
            "Q1": {
                "name": "Stars",
                "position": "High Growth, High Market Share",
                "description": "Invest for growth - market leaders in growing markets",
                "action": "Invest to maintain leadership",
            },
            "Q2": {
                "name": "Question Marks",
                "position": "High Growth, Low Market Share",
                "description": "Uncertain future - growing market but weak position",
                "action": "Invest selectively or divest",
            },
            "Q3": {
                "name": "Dogs",
                "position": "Low Growth, Low Market Share",
                "description": "Poor prospects - weak position in stagnant market",
                "action": "Divest or harvest",
            },
            "Q4": {
                "name": "Cash Cows",
                "position": "Low Growth, High Market Share",
                "description": "Milk for cash - strong position but limited growth",
                "action": "Harvest cash for investment elsewhere",
            },
        }
    elif matrix_type == "risk":
        return {
            "Q1": {
                "name": "Mitigate",
                "position": "High Impact, High Likelihood",
                "description": "Critical risks - must address proactively",
                "action": "Develop mitigation plans immediately",
            },
            "Q2": {
                "name": "Monitor",
                "position": "High Impact, Low Likelihood",
                "description": "Significant but unlikely - watch closely",
                "action": "Create contingency plans",
            },
            "Q3": {
                "name": "Accept",
                "position": "Low Impact, Low Likelihood",
                "description": "Minor risks - accept and monitor",
                "action": "Document and accept",
            },
            "Q4": {
                "name": "Reduce",
                "position": "Low Impact, High Likelihood",
                "description": "Frequent but minor - reduce if cost-effective",
                "action": "Implement simple controls",
            },
        }
    elif matrix_type == "eisenhower":
        return {
            "Q1": {
                "name": "Do First",
                "position": "Urgent and Important",
                "description": "Critical and time-sensitive",
                "action": "Do immediately",
            },
            "Q2": {
                "name": "Schedule",
                "position": "Not Urgent but Important",
                "description": "Important but can be planned",
                "action": "Schedule and allocate time",
            },
            "Q3": {
                "name": "Delegate",
                "position": "Urgent but Not Important",
                "description": "Time-sensitive but low strategic value",
                "action": "Delegate to others",
            },
            "Q4": {
                "name": "Eliminate",
                "position": "Not Urgent and Not Important",
                "description": "Neither urgent nor important",
                "action": "Eliminate or minimize",
            },
        }
    else:  # custom
        return {
            "Q1": {
                "name": f"High {y_axis}, Low {x_axis}",
                "position": f"High {y_axis}, Low {x_axis}",
                "description": "Top-left quadrant",
                "action": "Prioritize",
            },
            "Q2": {
                "name": f"High {y_axis}, High {x_axis}",
                "position": f"High {y_axis}, High {x_axis}",
                "description": "Top-right quadrant",
                "action": "Invest carefully",
            },
            "Q3": {
                "name": f"Low {y_axis}, Low {x_axis}",
                "position": f"Low {y_axis}, Low {x_axis}",
                "description": "Bottom-left quadrant",
                "action": "Deprioritize",
            },
            "Q4": {
                "name": f"Low {y_axis}, High {x_axis}",
                "position": f"Low {y_axis}, High {x_axis}",
                "description": "Bottom-right quadrant",
                "action": "Avoid or rethink",
            },
        }


def _auto_assess_items(items: List[str], x_axis: str, y_axis: str) -> Dict:
    """
    Auto-assess items with placeholder scores.

    Args:
        items: List of items
        x_axis: X-axis label
        y_axis: Y-axis label

    Returns:
        dict: {item: {"x": score, "y": score}}
    """
    # Return placeholder assessments - in real use, these would come from user/agent
    assessments = {}
    for i, item in enumerate(items):
        # Distribute items across quadrants for demonstration
        x_score = "low" if i % 2 == 0 else "high"
        y_score = "high" if i < len(items) // 2 else "low"

        assessments[item] = {"x": x_score, "y": y_score}

    return assessments


def _place_items_in_quadrants(
    items: List[str], assessments: Dict, quadrants: Dict
) -> Dict:
    """
    Place items in appropriate quadrants.

    Args:
        items: List of items
        assessments: Item assessments
        quadrants: Quadrant definitions

    Returns:
        dict: {quadrant_id: [items]}
    """
    placements = {"Q1": [], "Q2": [], "Q3": [], "Q4": []}

    for item in items:
        if item not in assessments:
            # Default to Q3 if no assessment
            placements["Q3"].append(item)
            continue

        assessment = assessments[item]
        x_val = assessment.get("x", "low")
        y_val = assessment.get("y", "low")

        # Convert to boolean if string
        if isinstance(x_val, str):
            x_high = x_val.lower() in ["high", "yes", "true"]
        else:
            x_high = x_val > 0.5

        if isinstance(y_val, str):
            y_high = y_val.lower() in ["high", "yes", "true"]
        else:
            y_high = y_val > 0.5

        # Assign to quadrant
        # Q1: High Y, Low X (top-left)
        # Q2: High Y, High X (top-right)
        # Q3: Low Y, Low X (bottom-left)
        # Q4: Low Y, High X (bottom-right)

        if y_high and not x_high:
            placements["Q1"].append(item)
        elif y_high and x_high:
            placements["Q2"].append(item)
        elif not y_high and not x_high:
            placements["Q3"].append(item)
        else:  # not y_high and x_high
            placements["Q4"].append(item)

    return placements


def _generate_recommendations(placements: Dict, matrix_type: str) -> List[str]:
    """
    Generate action recommendations based on placements.

    Args:
        placements: Item placements by quadrant
        matrix_type: Type of matrix

    Returns:
        list: Recommendations
    """
    recommendations = []

    # Count items in each quadrant
    q1_count = len(placements["Q1"])
    q2_count = len(placements["Q2"])
    q3_count = len(placements["Q3"])
    q4_count = len(placements["Q4"])

    if matrix_type == "prioritization":
        if q1_count > 0:
            recommendations.append(
                f"Start with {q1_count} Quick Win(s) - highest ROI with minimal effort"
            )
        if q2_count > 0:
            recommendations.append(
                f"Plan carefully for {q2_count} Strategic Bet(s) - "
                f"high impact but requires resources"
            )
        if q4_count > 0:
            recommendations.append(
                f"Reconsider {q4_count} Hard Slog(s) - "
                f"high effort with limited return"
            )
        if q3_count > 0:
            recommendations.append(
                f"Defer {q3_count} Fill Later item(s) - low priority"
            )

        # Suggested sequence
        if q1_count > 0:
            recommendations.append(
                "Suggested sequence: Quick Wins → Strategic Bets → "
                "Fill Later (if time permits)"
            )

    elif matrix_type == "risk":
        if q1_count > 0:
            recommendations.append(
                f"URGENT: Mitigate {q1_count} critical risk(s) immediately"
            )
        if q2_count > 0:
            recommendations.append(
                f"Create contingency plans for {q2_count} high-impact risk(s)"
            )

    else:  # Other types or custom
        if q1_count > 0:
            recommendations.append(f"Focus on {q1_count} top-priority item(s) in Q1")
        if q2_count > 0:
            recommendations.append(
                f"Plan investment for {q2_count} strategic item(s) in Q2"
            )

    if not recommendations:
        recommendations.append("Review placements and adjust assessments as needed")

    return recommendations
