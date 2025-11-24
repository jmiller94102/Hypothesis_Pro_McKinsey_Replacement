"""Matrix type definitions for all supported 2x2 matrices.

This module defines the configuration for each matrix type, including:
- Axis labels
- Quadrant names and descriptions
- Whether to auto-populate from hypothesis tree
- Default recommendations

These definitions are used by the matrix generation and display logic.
"""

from typing import Dict, Any, Literal

MatrixType = Literal[
    "hypothesis_prioritization",
    "risk_register",
    "task_prioritization",
    "measurement_priorities"
]

MATRIX_TYPES: Dict[str, Dict[str, Any]] = {
    "hypothesis_prioritization": {
        "name": "Hypothesis Prioritization",
        "description": "Prioritize which hypotheses to test first based on strategic impact and validation effort.",
        "x_axis": "Effort to Validate",
        "y_axis": "Strategic Impact",
        "auto_populate": True,  # Populated from hypothesis tree L3 leaves
        "source": "hypothesis_tree_l3",
        "quadrants": {
            "Q1": {
                "name": "Quick Wins",
                "position": "High Impact, Low Effort",
                "description": "High-value hypotheses that are easy to test. Validate these first to quickly de-risk the decision.",
                "color": "green",
                "priority": 1
            },
            "Q2": {
                "name": "Strategic Bets",
                "position": "High Impact, High Effort",
                "description": "Critical hypotheses that require significant resources. Plan these carefully with adequate time and budget.",
                "color": "yellow",
                "priority": 2
            },
            "Q3": {
                "name": "Fill Later",
                "position": "Low Impact, Low Effort",
                "description": "Nice-to-know hypotheses with limited strategic value. Test only if time and resources permit.",
                "color": "gray",
                "priority": 4
            },
            "Q4": {
                "name": "Deprioritize",
                "position": "Low Impact, High Effort",
                "description": "Low-value hypotheses that consume significant resources. Skip unless explicitly required for compliance or stakeholder management.",
                "color": "red",
                "priority": 3
            }
        },
        "default_recommendations": [
            "Start with Quick Wins (Q1) to build momentum and quickly gather insights",
            "Plan Strategic Bets (Q2) carefully with adequate timeline and resources",
            "Consider skipping Deprioritize items (Q4) unless required by stakeholders",
            "Revisit Fill Later items (Q3) only after completing Q1 and Q2"
        ]
    },

    "risk_register": {
        "name": "Risk Register",
        "description": "Identify and assess risks that could derail the project based on likelihood and potential impact.",
        "x_axis": "Likelihood",
        "y_axis": "Impact",
        "auto_populate": False,  # User adds specific risks
        "source": "manual",
        "quadrants": {
            "Q1": {
                "name": "Monitor",
                "position": "High Impact, Low Likelihood",
                "description": "Low-probability risks with high consequences. Monitor regularly but don't over-invest in mitigation.",
                "color": "yellow",
                "priority": 3
            },
            "Q2": {
                "name": "Mitigate Now",
                "position": "High Impact, High Likelihood",
                "description": "Critical risks that are likely to occur. Develop and implement mitigation plans immediately.",
                "color": "red",
                "priority": 1
            },
            "Q3": {
                "name": "Accept",
                "position": "Low Impact, Low Likelihood",
                "description": "Minor risks with low probability. Accept these risks and document for awareness.",
                "color": "green",
                "priority": 4
            },
            "Q4": {
                "name": "Contingency Plan",
                "position": "Low Impact, High Likelihood",
                "description": "Likely to occur but limited impact. Develop simple contingency plans to address if they materialize.",
                "color": "yellow",
                "priority": 2
            }
        },
        "default_recommendations": [
            "Focus mitigation efforts on 'Mitigate Now' (Q2) risks immediately",
            "Create monitoring dashboards for 'Monitor' (Q1) risks to track early warning signals",
            "Develop lightweight contingency plans for 'Contingency Plan' (Q4) risks",
            "Document 'Accept' (Q3) risks for stakeholder awareness but take no action"
        ]
    },

    "task_prioritization": {
        "name": "Task Prioritization (Eisenhower Matrix)",
        "description": "Prioritize implementation tasks based on urgency and importance to optimize execution.",
        "x_axis": "Urgency",
        "y_axis": "Importance",
        "auto_populate": False,  # User adds implementation tasks
        "source": "manual",
        "quadrants": {
            "Q1": {
                "name": "Do First",
                "position": "Important, Not Urgent",
                "description": "Strategic work that drives long-term value. Schedule dedicated time for these high-leverage activities.",
                "color": "green",
                "priority": 2
            },
            "Q2": {
                "name": "Schedule",
                "position": "Important, Urgent",
                "description": "Critical tasks requiring immediate attention. Focus here but try to prevent tasks from becoming urgent through better planning.",
                "color": "red",
                "priority": 1
            },
            "Q3": {
                "name": "Eliminate",
                "position": "Not Important, Not Urgent",
                "description": "Time-wasters and distractions. Eliminate these tasks or defer indefinitely.",
                "color": "gray",
                "priority": 4
            },
            "Q4": {
                "name": "Delegate",
                "position": "Not Important, Urgent",
                "description": "Tasks that feel urgent but don't contribute to strategic goals. Delegate to others or automate if possible.",
                "color": "yellow",
                "priority": 3
            }
        },
        "default_recommendations": [
            "Block calendar time for 'Do First' (Q1) strategic work before it becomes urgent",
            "Address 'Schedule' (Q2) tasks immediately but investigate root causes of urgency",
            "Delegate 'Delegate' (Q4) tasks to appropriate team members or automate",
            "Eliminate 'Eliminate' (Q3) tasks ruthlessly to free up capacity for Q1 and Q2"
        ]
    },

    "measurement_priorities": {
        "name": "Measurement Priorities",
        "description": "Prioritize which metrics to track based on strategic value and measurement feasibility.",
        "x_axis": "Feasibility of Measurement",
        "y_axis": "Strategic Value",
        "auto_populate": True,  # Can populate from L3 leaves with metrics
        "source": "hypothesis_tree_l3_metrics",
        "quadrants": {
            "Q1": {
                "name": "Core KPIs",
                "position": "High Value, Easy to Measure",
                "description": "High-impact metrics that are easy to track. These should be your primary KPIs tracked in real-time dashboards.",
                "color": "green",
                "priority": 1
            },
            "Q2": {
                "name": "Strategic Metrics",
                "position": "High Value, Hard to Measure",
                "description": "Critical metrics that require investment in measurement infrastructure. Worth the effort for strategic decisions.",
                "color": "yellow",
                "priority": 2
            },
            "Q3": {
                "name": "Nice to Have",
                "position": "Low Value, Easy to Measure",
                "description": "Low-impact metrics that are easy to track. Include if spare capacity exists but not a priority.",
                "color": "gray",
                "priority": 4
            },
            "Q4": {
                "name": "Deprioritize",
                "position": "Low Value, Hard to Measure",
                "description": "Low-impact metrics that are expensive to track. Skip these measurements entirely.",
                "color": "red",
                "priority": 3
            }
        },
        "default_recommendations": [
            "Build real-time dashboards for Core KPIs (Q1) with automated data collection",
            "Invest in measurement infrastructure for Strategic Metrics (Q2) over time",
            "Track Nice to Have (Q3) metrics only if they require zero incremental effort",
            "Do not waste resources measuring Deprioritize (Q4) metrics"
        ]
    }
}


def get_matrix_type_config(matrix_type: str) -> Dict[str, Any]:
    """Get configuration for a specific matrix type.

    Args:
        matrix_type: Type of matrix to get config for

    Returns:
        Configuration dictionary for the matrix type

    Raises:
        ValueError: If matrix_type is not recognized
    """
    if matrix_type not in MATRIX_TYPES:
        raise ValueError(
            f"Unknown matrix type: {matrix_type}. "
            f"Valid types are: {', '.join(MATRIX_TYPES.keys())}"
        )
    return MATRIX_TYPES[matrix_type]


def get_all_matrix_types() -> list[str]:
    """Get list of all supported matrix types.

    Returns:
        List of matrix type identifiers
    """
    return list(MATRIX_TYPES.keys())


def should_auto_populate(matrix_type: str) -> bool:
    """Check if a matrix type should auto-populate from hypothesis tree.

    Args:
        matrix_type: Type of matrix to check

    Returns:
        True if matrix should auto-populate, False otherwise
    """
    config = get_matrix_type_config(matrix_type)
    return config.get("auto_populate", False)
