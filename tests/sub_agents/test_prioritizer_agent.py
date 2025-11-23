"""Tests for prioritizer agent module."""

import pytest
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import FunctionTool

from strategic_consultant_agent.sub_agents.prioritizer_agent import create_prioritizer
from strategic_consultant_agent.prompts.instructions import PRIORITIZER_PROMPT
from strategic_consultant_agent.tools.matrix_2x2 import generate_2x2_matrix


class TestCreatePrioritizer:
    """Test create_prioritizer function."""

    def test_creates_agent_instance(self):
        """Test that function creates an Agent instance."""
        agent = create_prioritizer()
        assert isinstance(agent, Agent)

    def test_agent_has_correct_name(self):
        """Test that agent has correct name."""
        agent = create_prioritizer()
        assert agent.name == "prioritizer"

    def test_agent_has_gemini_model(self):
        """Test that agent uses Gemini model."""
        agent = create_prioritizer()
        assert isinstance(agent.model, Gemini)

    def test_agent_uses_correct_prompt(self):
        """Test that agent uses prioritizer prompt."""
        agent = create_prioritizer()
        assert agent.instruction == PRIORITIZER_PROMPT

    def test_agent_has_matrix_tool(self):
        """Test that agent has generate_2x2_matrix tool."""
        agent = create_prioritizer()
        # Check that tools list contains a FunctionTool
        assert len(agent.tools) > 0
        assert any(isinstance(tool, FunctionTool) for tool in agent.tools)

    def test_agent_has_output_key(self):
        """Test that agent has correct output_key."""
        agent = create_prioritizer()
        assert agent.output_key == "priority_matrix"

    def test_multiple_calls_create_independent_instances(self):
        """Test that multiple calls create independent instances."""
        agent1 = create_prioritizer()
        agent2 = create_prioritizer()
        assert agent1 is not agent2


class TestAgentConfiguration:
    """Test agent configuration details."""

    def test_prioritizer_uses_flash_model(self):
        """Test that prioritizer uses gemini-2.0-flash."""
        agent = create_prioritizer()
        if hasattr(agent.model, "model"):
            assert "gemini-2.0-flash" in str(agent.model.model)

    def test_agent_uses_prioritizer_prompt(self):
        """Test that agent uses PRIORITIZER_PROMPT."""
        agent = create_prioritizer()
        assert agent.instruction == PRIORITIZER_PROMPT

    def test_agent_has_exactly_one_tool(self):
        """Test that agent has exactly one FunctionTool."""
        agent = create_prioritizer()
        function_tools = [
            tool for tool in agent.tools if isinstance(tool, FunctionTool)
        ]
        assert len(function_tools) == 1


class TestAgentIntegration:
    """Test integration aspects."""

    def test_output_key_matches_expected_state_key(self):
        """Test that output_key matches what downstream consumers expect."""
        agent = create_prioritizer()
        # Output should be "priority_matrix" for final report
        assert agent.output_key == "priority_matrix"

    def test_prompt_references_hypothesis_tree(self):
        """Test that prompt expects hypothesis_tree from previous phase."""
        # Prompt should reference {hypothesis_tree} input
        assert "{hypothesis_tree}" in PRIORITIZER_PROMPT

    def test_prompt_mentions_generate_2x2_matrix_tool(self):
        """Test that prompt mentions the 2x2 matrix tool."""
        assert "generate_2x2_matrix" in PRIORITIZER_PROMPT


class TestFactoryPattern:
    """Test factory pattern implementation."""

    def test_function_is_callable(self):
        """Test that factory function is callable."""
        assert callable(create_prioritizer)

    def test_factory_function_requires_no_parameters(self):
        """Test that factory function can be called without parameters."""
        # Should not raise exceptions
        create_prioritizer()

    def test_factory_function_returns_non_none(self):
        """Test that factory function returns non-None value."""
        assert create_prioritizer() is not None
