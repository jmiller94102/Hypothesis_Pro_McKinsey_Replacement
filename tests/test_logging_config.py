"""Tests for logging configuration."""

import logging
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from strategic_consultant_agent.logging_config import (
    setup_logging,
    log_tool_call,
    log_agent_transition,
    log_loop_iteration,
    log_session_event,
    log_validation_result,
    get_logger,
)


class TestSetupLogging:
    """Test logging setup."""

    def test_setup_console_only(self):
        """Test setting up console logging only."""
        logger = setup_logging(log_to_file=False, log_to_console=True)

        assert logger.name == "strategic_consultant"
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)

    def test_setup_file_only(self):
        """Test setting up file logging only."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = setup_logging(
                log_to_file=True, log_to_console=False, log_dir=Path(tmpdir)
            )

            assert logger.name == "strategic_consultant"
            assert len(logger.handlers) == 1
            assert isinstance(logger.handlers[0], logging.FileHandler)

    def test_setup_both_handlers(self):
        """Test setting up both console and file logging."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = setup_logging(
                log_to_file=True, log_to_console=True, log_dir=Path(tmpdir)
            )

            assert len(logger.handlers) == 2

    def test_log_level_setting(self):
        """Test that log level is set correctly."""
        logger = setup_logging(log_level="DEBUG", log_to_file=False)

        assert logger.level == logging.DEBUG

    def test_log_file_created(self):
        """Test that log file is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            setup_logging(log_to_file=True, log_to_console=False, log_dir=Path(tmpdir))

            log_files = list(Path(tmpdir).glob("*.log"))
            assert len(log_files) == 1
            assert log_files[0].name.startswith("strategic_consultant_")


class TestLogToolCall:
    """Test tool call logging."""

    def test_log_tool_call_started(self):
        """Test logging tool call start."""
        logger = MagicMock()

        log_tool_call(
            logger,
            tool_name="generate_hypothesis_tree",
            parameters={"framework": "scale"},
        )

        logger.info.assert_called_once()
        call_args = logger.info.call_args
        assert "STARTED" in call_args[0][0]

    def test_log_tool_call_success(self):
        """Test logging successful tool call."""
        logger = MagicMock()

        log_tool_call(
            logger,
            tool_name="generate_hypothesis_tree",
            parameters={"framework": "scale"},
            result={"L1_DESIRABILITY": {}},
        )

        logger.info.assert_called_once()
        call_args = logger.info.call_args
        assert "SUCCESS" in call_args[0][0]

    def test_log_tool_call_error(self):
        """Test logging failed tool call."""
        logger = MagicMock()
        error = ValueError("Invalid framework")

        log_tool_call(
            logger,
            tool_name="generate_hypothesis_tree",
            parameters={"framework": "invalid"},
            error=error,
        )

        logger.error.assert_called_once()
        call_args = logger.error.call_args
        assert "FAILED" in call_args[0][0]


class TestLogAgentTransition:
    """Test agent transition logging."""

    def test_log_agent_transition(self):
        """Test logging agent transitions."""
        logger = MagicMock()

        log_agent_transition(
            logger,
            from_agent="research_phase",
            to_agent="analysis_phase",
            state_keys=["market_research", "competitor_research"],
        )

        logger.info.assert_called_once()
        call_args = logger.info.call_args
        assert "research_phase" in call_args[0][0]
        assert "analysis_phase" in call_args[0][0]
        assert call_args[1]["extra"]["state_keys"] == [
            "market_research",
            "competitor_research",
        ]


class TestLogLoopIteration:
    """Test loop iteration logging."""

    def test_log_loop_iteration_normal(self):
        """Test logging normal loop iteration."""
        logger = MagicMock()

        log_loop_iteration(
            logger, loop_name="analysis_phase", iteration=1, max_iterations=3
        )

        logger.info.assert_called_once()
        call_args = logger.info.call_args
        assert "[1/3]" in call_args[0][0]

    def test_log_loop_iteration_exit(self):
        """Test logging loop exit."""
        logger = MagicMock()

        log_loop_iteration(
            logger,
            loop_name="analysis_phase",
            iteration=2,
            max_iterations=3,
            exit_condition_met=True,
        )

        logger.info.assert_called_once()
        call_args = logger.info.call_args
        assert "EXITED" in call_args[0][0]
        assert call_args[1]["extra"]["exit_condition_met"] is True


class TestLogSessionEvent:
    """Test session event logging."""

    def test_log_session_event_simple(self):
        """Test logging simple session event."""
        logger = MagicMock()

        log_session_event(logger, event_type="START", session_id="session_123")

        logger.info.assert_called_once()
        call_args = logger.info.call_args
        assert "START" in call_args[0][0]
        assert "session_123" in call_args[0][0]

    def test_log_session_event_with_details(self):
        """Test logging session event with details."""
        logger = MagicMock()

        log_session_event(
            logger,
            event_type="SAVE",
            session_id="session_123",
            details={"project_name": "fall_detection"},
        )

        logger.info.assert_called_once()
        call_args = logger.info.call_args
        assert call_args[1]["extra"]["project_name"] == "fall_detection"


class TestLogValidationResult:
    """Test validation result logging."""

    def test_log_validation_passed(self):
        """Test logging successful validation."""
        logger = MagicMock()

        log_validation_result(logger, validator_name="MECE validator", is_valid=True)

        logger.info.assert_called_once()
        call_args = logger.info.call_args
        assert "PASSED" in call_args[0][0]

    def test_log_validation_failed(self):
        """Test logging failed validation."""
        logger = MagicMock()
        issues = {"overlaps": ["Cost and Financial"]}

        log_validation_result(
            logger, validator_name="MECE validator", is_valid=False, issues=issues
        )

        logger.warning.assert_called_once()
        call_args = logger.warning.call_args
        assert "FAILED" in call_args[0][0]
        assert call_args[1]["extra"]["issues"] == issues


class TestGetLogger:
    """Test get_logger function."""

    def test_get_logger_creates_if_missing(self):
        """Test that get_logger creates logger if not exists."""
        # Clean up any existing handlers
        logger = logging.getLogger("test_strategic_consultant")
        logger.handlers = []

        with patch(
            "strategic_consultant_agent.logging_config.setup_logging"
        ) as mock_setup:
            logger = get_logger("test_strategic_consultant")
            # Should call setup_logging since no handlers exist
            mock_setup.assert_called_once()

    def test_get_logger_default_name(self):
        """Test that get_logger uses default name."""
        logger = get_logger()
        assert logger.name == "strategic_consultant"


class TestIntegration:
    """Test integrated logging scenarios."""

    def test_complete_workflow_logging(self):
        """Test logging throughout a complete workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = setup_logging(
                log_level="DEBUG",
                log_to_file=True,
                log_to_console=False,
                log_dir=Path(tmpdir),
            )

            # Log session start
            log_session_event(
                logger,
                event_type="START",
                session_id="test_session",
                details={"question": "Should we scale?"},
            )

            # Log tool call
            log_tool_call(
                logger,
                tool_name="generate_hypothesis_tree",
                parameters={"framework": "scale_decision"},
                result={"L1_DESIRABILITY": {}},
            )

            # Log agent transition
            log_agent_transition(
                logger,
                from_agent="research_phase",
                to_agent="analysis_phase",
                state_keys=["market_research"],
            )

            # Log loop iteration
            log_loop_iteration(
                logger, loop_name="analysis_phase", iteration=1, max_iterations=3
            )

            # Log validation
            log_validation_result(logger, validator_name="MECE", is_valid=True)

            # Verify log file exists and has content
            log_files = list(Path(tmpdir).glob("*.log"))
            assert len(log_files) == 1
            assert log_files[0].stat().st_size > 0

    def test_error_logging(self):
        """Test logging errors."""
        logger = setup_logging(log_to_file=False, log_to_console=True)

        error = ValueError("Test error")
        log_tool_call(
            logger,
            tool_name="test_tool",
            parameters={"param": "value"},
            error=error,
        )

        # Should not raise exception
        assert True
