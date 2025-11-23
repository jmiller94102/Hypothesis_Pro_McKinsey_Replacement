"""Logging configuration for strategic consultant agent.

This module provides logging configuration and observability tools
for debugging and monitoring agent execution.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


# Default log directory
DEFAULT_LOG_DIR = Path(__file__).parent.parent / "logs"


def setup_logging(
    log_level: str = "INFO",
    log_to_file: bool = True,
    log_to_console: bool = True,
    log_dir: Path | None = None,
) -> logging.Logger:
    """
    Configure logging for the strategic consultant agent.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to file (default: True)
        log_to_console: Whether to log to console (default: True)
        log_dir: Custom log directory (default: ./logs)

    Returns:
        logging.Logger: Configured logger instance

    Example:
        >>> logger = setup_logging(log_level="DEBUG")
        >>> logger.info("Agent started")
    """
    # Create logger
    logger = logging.getLogger("strategic_consultant")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    logger.handlers = []

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_to_file:
        log_directory = log_dir or DEFAULT_LOG_DIR
        log_directory.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_directory / f"strategic_consultant_{timestamp}.log"

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        logger.info(f"Logging to file: {log_file}")

    return logger


def log_tool_call(
    logger: logging.Logger,
    tool_name: str,
    parameters: dict[str, Any],
    result: Any = None,
    error: Exception | None = None,
):
    """
    Log a tool function call.

    Args:
        logger: Logger instance
        tool_name: Name of the tool
        parameters: Tool parameters
        result: Tool result (optional)
        error: Exception if tool call failed (optional)

    Example:
        >>> logger = setup_logging()
        >>> log_tool_call(
        ...     logger,
        ...     "generate_hypothesis_tree",
        ...     {"framework": "scale_decision"},
        ...     result={"L1_DESIRABILITY": {...}}
        ... )
    """
    if error:
        logger.error(
            f"Tool call FAILED: {tool_name}",
            extra={
                "tool_name": tool_name,
                "parameters": parameters,
                "error": str(error),
                "error_type": type(error).__name__,
            },
        )
    elif result:
        logger.info(
            f"Tool call SUCCESS: {tool_name}",
            extra={
                "tool_name": tool_name,
                "parameters": parameters,
                "has_result": True,
            },
        )
    else:
        logger.info(
            f"Tool call STARTED: {tool_name}",
            extra={"tool_name": tool_name, "parameters": parameters},
        )


def log_agent_transition(
    logger: logging.Logger, from_agent: str, to_agent: str, state_keys: list[str]
):
    """
    Log a transition between agents.

    Args:
        logger: Logger instance
        from_agent: Source agent name
        to_agent: Destination agent name
        state_keys: Keys available in session state

    Example:
        >>> logger = setup_logging()
        >>> log_agent_transition(
        ...     logger,
        ...     from_agent="research_phase",
        ...     to_agent="analysis_phase",
        ...     state_keys=["market_research", "competitor_research"]
        ... )
    """
    logger.info(
        f"Agent transition: {from_agent} → {to_agent}",
        extra={
            "from_agent": from_agent,
            "to_agent": to_agent,
            "state_keys": state_keys,
        },
    )


def log_loop_iteration(
    logger: logging.Logger,
    loop_name: str,
    iteration: int,
    max_iterations: int,
    exit_condition_met: bool = False,
):
    """
    Log a loop iteration.

    Args:
        logger: Logger instance
        loop_name: Name of the loop (e.g., "analysis_phase")
        iteration: Current iteration number
        max_iterations: Maximum iterations allowed
        exit_condition_met: Whether exit condition was met

    Example:
        >>> logger = setup_logging()
        >>> log_loop_iteration(
        ...     logger,
        ...     loop_name="analysis_phase",
        ...     iteration=1,
        ...     max_iterations=3
        ... )
    """
    if exit_condition_met:
        logger.info(
            f"Loop EXITED: {loop_name} (exit condition met at iteration {iteration})",
            extra={
                "loop_name": loop_name,
                "iteration": iteration,
                "max_iterations": max_iterations,
                "exit_condition_met": True,
            },
        )
    else:
        logger.info(
            f"Loop iteration: {loop_name} [{iteration}/{max_iterations}]",
            extra={
                "loop_name": loop_name,
                "iteration": iteration,
                "max_iterations": max_iterations,
                "exit_condition_met": False,
            },
        )


def log_session_event(
    logger: logging.Logger,
    event_type: str,
    session_id: str,
    details: dict[str, Any] | None = None,
):
    """
    Log a session event.

    Args:
        logger: Logger instance
        event_type: Type of event (START, END, SAVE, LOAD, etc.)
        session_id: Session ID
        details: Additional event details

    Example:
        >>> logger = setup_logging()
        >>> log_session_event(
        ...     logger,
        ...     event_type="START",
        ...     session_id="session_123",
        ...     details={"user_question": "Should we scale?"}
        ... )
    """
    extra = {"event_type": event_type, "session_id": session_id}
    if details:
        extra.update(details)

    logger.info(f"Session event: {event_type} (session: {session_id})", extra=extra)


def log_validation_result(
    logger: logging.Logger,
    validator_name: str,
    is_valid: bool,
    issues: dict[str, Any] | None = None,
):
    """
    Log a validation result.

    Args:
        logger: Logger instance
        validator_name: Name of the validator
        is_valid: Whether validation passed
        issues: Validation issues if any

    Example:
        >>> logger = setup_logging()
        >>> log_validation_result(
        ...     logger,
        ...     validator_name="MECE validator",
        ...     is_valid=False,
        ...     issues={"overlaps": ["Cost and Financial overlap"]}
        ... )
    """
    if is_valid:
        logger.info(
            f"Validation PASSED: {validator_name}",
            extra={"validator_name": validator_name, "is_valid": True},
        )
    else:
        logger.warning(
            f"Validation FAILED: {validator_name}",
            extra={
                "validator_name": validator_name,
                "is_valid": False,
                "issues": issues,
            },
        )


def get_logger(name: str = "strategic_consultant") -> logging.Logger:
    """
    Get or create a logger instance.

    Args:
        name: Logger name (default: "strategic_consultant")

    Returns:
        logging.Logger: Logger instance

    Example:
        >>> logger = get_logger()
        >>> logger.info("Message")
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        # Setup default logging if not already configured
        setup_logging()
    return logger
