"""Matrix generation prompts for AI-powered auto-population.

This module contains prompts for generating different types of 2x2 matrices
from hypothesis trees. Each prompt is designed to be easily maintainable
and refineable by developers.
"""

from strategic_consultant_agent.prompts.matrix_generation.risk_register import (
    RISK_REGISTER_PROMPT,
)
from strategic_consultant_agent.prompts.matrix_generation.task_prioritization import (
    TASK_PRIORITIZATION_PROMPT,
)
from strategic_consultant_agent.prompts.matrix_generation.measurement_priorities import (
    MEASUREMENT_PRIORITIES_PROMPT,
)

__all__ = [
    "RISK_REGISTER_PROMPT",
    "TASK_PRIORITIZATION_PROMPT",
    "MEASUREMENT_PRIORITIES_PROMPT",
]
