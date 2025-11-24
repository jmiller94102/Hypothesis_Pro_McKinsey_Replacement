"""Configuration module for strategic consultant agent."""

from strategic_consultant_agent.config.matrix_types import (
    MATRIX_TYPES,
    MatrixType,
    get_matrix_type_config,
    get_all_matrix_types,
    should_auto_populate,
)

__all__ = [
    "MATRIX_TYPES",
    "MatrixType",
    "get_matrix_type_config",
    "get_all_matrix_types",
    "should_auto_populate",
]
