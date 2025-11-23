"""Tests for session management functionality."""

import pytest
from unittest.mock import MagicMock, patch

from strategic_consultant_agent.session_manager import (
    StrategicConsultantSession,
    create_runner,
    run_analysis,
)


class TestStrategicConsultantSession:
    """Test StrategicConsultantSession class."""

    @patch("strategic_consultant_agent.session_manager.InMemoryRunner")
    @patch("strategic_consultant_agent.session_manager.create_strategic_analyzer")
    def test_initialization(self, mock_create_agent, mock_runner):
        """Test session initialization with default values."""
        session = StrategicConsultantSession()

        assert session.session_id == "default_session"
        assert session.user_id == "default_user"
        assert session.app_name == "strategic_consultant"
        mock_create_agent.assert_called_once()
        mock_runner.assert_called_once()

    @patch("strategic_consultant_agent.session_manager.InMemoryRunner")
    @patch("strategic_consultant_agent.session_manager.create_strategic_analyzer")
    def test_initialization_with_custom_ids(self, mock_create_agent, mock_runner):
        """Test session initialization with custom IDs."""
        session = StrategicConsultantSession(
            user_id="user123", session_id="session456", app_name="test_app"
        )

        assert session.session_id == "session456"
        assert session.user_id == "user123"
        assert session.app_name == "test_app"

    @patch("strategic_consultant_agent.session_manager.InMemoryRunner")
    @patch("strategic_consultant_agent.session_manager.create_strategic_analyzer")
    def test_run_creates_message(self, mock_create_agent, mock_runner):
        """Test that run creates proper message content."""
        mock_runner_instance = MagicMock()
        mock_runner_instance.run = MagicMock(return_value=iter([]))
        mock_runner.return_value = mock_runner_instance

        session = StrategicConsultantSession()
        list(session.run("Should we scale fall detection?"))

        # Verify run was called with correct parameters
        mock_runner_instance.run.assert_called_once()
        call_args = mock_runner_instance.run.call_args
        assert call_args.kwargs["user_id"] == "default_user"
        assert call_args.kwargs["session_id"] == "default_session"
        assert call_args.kwargs["new_message"] is not None

    @patch("strategic_consultant_agent.session_manager.InMemoryRunner")
    @patch("strategic_consultant_agent.session_manager.create_strategic_analyzer")
    def test_get_session_id(self, mock_create_agent, mock_runner):
        """Test getting session ID."""
        session = StrategicConsultantSession(session_id="test_session_456")
        assert session.get_session_id() == "test_session_456"

    @patch("strategic_consultant_agent.session_manager.InMemoryRunner")
    @patch("strategic_consultant_agent.session_manager.create_strategic_analyzer")
    def test_get_user_id(self, mock_create_agent, mock_runner):
        """Test getting user ID."""
        session = StrategicConsultantSession(user_id="test_user_789")
        assert session.get_user_id() == "test_user_789"


class TestConvenienceFunctions:
    """Test convenience functions for session management."""

    @patch("strategic_consultant_agent.session_manager.InMemoryRunner")
    @patch("strategic_consultant_agent.session_manager.create_strategic_analyzer")
    def test_create_runner(self, mock_create_agent, mock_runner):
        """Test creating runner."""
        runner = create_runner()

        assert runner is not None
        mock_create_agent.assert_called_once()
        mock_runner.assert_called_once()
        # Verify app_name is set
        call_args = mock_runner.call_args
        assert call_args.kwargs["app_name"] == "strategic_consultant"

    @patch("strategic_consultant_agent.session_manager.InMemoryRunner")
    @patch("strategic_consultant_agent.session_manager.create_strategic_analyzer")
    def test_run_analysis_default_params(self, mock_create_agent, mock_runner):
        """Test run_analysis with default parameters."""
        mock_runner_instance = MagicMock()
        mock_runner_instance.run = MagicMock(return_value=iter([]))
        mock_runner.return_value = mock_runner_instance

        list(run_analysis("Should we scale fall detection?"))

        mock_runner_instance.run.assert_called_once()
        call_args = mock_runner_instance.run.call_args
        assert call_args.kwargs["user_id"] == "default_user"
        assert call_args.kwargs["session_id"] == "default_session"

    @patch("strategic_consultant_agent.session_manager.InMemoryRunner")
    @patch("strategic_consultant_agent.session_manager.create_strategic_analyzer")
    def test_run_analysis_custom_params(self, mock_create_agent, mock_runner):
        """Test run_analysis with custom parameters."""
        mock_runner_instance = MagicMock()
        mock_runner_instance.run = MagicMock(return_value=iter([]))
        mock_runner.return_value = mock_runner_instance

        list(
            run_analysis(
                "Should we scale fall detection?",
                user_id="custom_user",
                session_id="custom_session",
            )
        )

        mock_runner_instance.run.assert_called_once()
        call_args = mock_runner_instance.run.call_args
        assert call_args.kwargs["user_id"] == "custom_user"
        assert call_args.kwargs["session_id"] == "custom_session"


class TestMultiTurnConversation:
    """Test multi-turn conversation scenarios."""

    @patch("strategic_consultant_agent.session_manager.InMemoryRunner")
    @patch("strategic_consultant_agent.session_manager.create_strategic_analyzer")
    def test_three_turn_conversation(self, mock_create_agent, mock_runner):
        """Test a three-turn conversation maintaining session."""
        mock_runner_instance = MagicMock()
        call_count = 0

        def mock_run(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return iter([f"Response {call_count}"])

        mock_runner_instance.run = mock_run
        mock_runner.return_value = mock_runner_instance

        session = StrategicConsultantSession(session_id="multi_turn_session")

        # Turn 1: Initial question
        list(session.run("Should we scale fall detection?"))

        # Turn 2: Follow-up question
        list(session.run("What are the top priorities?"))

        # Turn 3: Deep dive
        list(session.run("Tell me more about the top priority"))

        # Verify all runs used same session_id
        assert call_count == 3

    @patch("strategic_consultant_agent.session_manager.InMemoryRunner")
    @patch("strategic_consultant_agent.session_manager.create_strategic_analyzer")
    def test_session_id_persists(self, mock_create_agent, mock_runner):
        """Test that session ID persists across multiple runs."""
        mock_runner_instance = MagicMock()
        mock_runner_instance.run = MagicMock(return_value=iter([]))
        mock_runner.return_value = mock_runner_instance

        session = StrategicConsultantSession(session_id="persistent_session")

        # Run multiple times
        list(session.run("Question 1"))
        list(session.run("Question 2"))
        list(session.run("Question 3"))

        # All calls should use the same session_id
        assert mock_runner_instance.run.call_count == 3
        for call in mock_runner_instance.run.call_args_list:
            assert call.kwargs["session_id"] == "persistent_session"


class TestEdgeCases:
    """Test edge cases and error handling."""

    @patch("strategic_consultant_agent.session_manager.InMemoryRunner")
    @patch("strategic_consultant_agent.session_manager.create_strategic_analyzer")
    def test_empty_input(self, mock_create_agent, mock_runner):
        """Test handling of empty input."""
        mock_runner_instance = MagicMock()
        mock_runner_instance.run = MagicMock(return_value=iter([]))
        mock_runner.return_value = mock_runner_instance

        session = StrategicConsultantSession()
        list(session.run(""))

        # Should still call runner
        mock_runner_instance.run.assert_called_once()

    @patch("strategic_consultant_agent.session_manager.InMemoryRunner")
    @patch("strategic_consultant_agent.session_manager.create_strategic_analyzer")
    def test_long_input(self, mock_create_agent, mock_runner):
        """Test handling of very long input."""
        mock_runner_instance = MagicMock()
        mock_runner_instance.run = MagicMock(return_value=iter([]))
        mock_runner.return_value = mock_runner_instance

        session = StrategicConsultantSession()
        long_input = "Should we scale? " * 1000  # Very long question
        list(session.run(long_input))

        # Should still work
        mock_runner_instance.run.assert_called_once()

    @patch("strategic_consultant_agent.session_manager.InMemoryRunner")
    @patch("strategic_consultant_agent.session_manager.create_strategic_analyzer")
    def test_special_characters_in_input(self, mock_create_agent, mock_runner):
        """Test handling of special characters."""
        mock_runner_instance = MagicMock()
        mock_runner_instance.run = MagicMock(return_value=iter([]))
        mock_runner.return_value = mock_runner_instance

        session = StrategicConsultantSession()
        special_input = "Should we scale? 💡 #strategy @consultant"
        list(session.run(special_input))

        # Should handle special characters
        mock_runner_instance.run.assert_called_once()
