"""Tests for analysis agents module."""

import pytest
from google.adk.agents import Agent, LoopAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import FunctionTool

from strategic_consultant_agent.sub_agents.analysis_agents import (
    create_hypothesis_generator,
    create_mece_validator,
    create_analysis_phase,
    exit_loop,
)
from strategic_consultant_agent.prompts.instructions import (
    HYPOTHESIS_GENERATOR_PROMPT,
    MECE_VALIDATOR_PROMPT,
)
from strategic_consultant_agent.tools.hypothesis_tree import generate_hypothesis_tree
from strategic_consultant_agent.tools.mece_validator import validate_mece_structure


class TestExitLoop:
    """Test exit_loop function."""

    def test_exit_loop_is_callable(self):
        """Test that exit_loop is callable."""
        assert callable(exit_loop)

    def test_exit_loop_returns_dict(self):
        """Test that exit_loop returns a dictionary."""
        result = exit_loop()
        assert isinstance(result, dict)

    def test_exit_loop_has_status_key(self):
        """Test that exit_loop result has status key."""
        result = exit_loop()
        assert "status" in result

    def test_exit_loop_status_message(self):
        """Test that exit_loop has appropriate status message."""
        result = exit_loop()
        assert "MECE validation passed" in result["status"]


class TestCreateHypothesisGenerator:
    """Test create_hypothesis_generator function."""

    def test_creates_agent_instance(self):
        """Test that function creates an Agent instance."""
        agent = create_hypothesis_generator()
        assert isinstance(agent, Agent)

    def test_agent_has_correct_name(self):
        """Test that agent has correct name."""
        agent = create_hypothesis_generator()
        assert agent.name == "hypothesis_generator"

    def test_agent_has_gemini_model(self):
        """Test that agent uses Gemini model."""
        agent = create_hypothesis_generator()
        assert isinstance(agent.model, Gemini)

    def test_agent_uses_correct_prompt(self):
        """Test that agent uses hypothesis generator prompt."""
        agent = create_hypothesis_generator()
        assert agent.instruction == HYPOTHESIS_GENERATOR_PROMPT

    def test_agent_has_hypothesis_tree_tool(self):
        """Test that agent has generate_hypothesis_tree tool."""
        agent = create_hypothesis_generator()
        # Check that tools list contains a FunctionTool
        assert len(agent.tools) > 0
        assert any(isinstance(tool, FunctionTool) for tool in agent.tools)

    def test_agent_has_output_key(self):
        """Test that agent has correct output_key."""
        agent = create_hypothesis_generator()
        assert agent.output_key == "hypothesis_tree"

    def test_multiple_calls_create_independent_instances(self):
        """Test that multiple calls create independent instances."""
        agent1 = create_hypothesis_generator()
        agent2 = create_hypothesis_generator()
        assert agent1 is not agent2


class TestCreateMeceValidator:
    """Test create_mece_validator function."""

    def test_creates_agent_instance(self):
        """Test that function creates an Agent instance."""
        agent = create_mece_validator()
        assert isinstance(agent, Agent)

    def test_agent_has_correct_name(self):
        """Test that agent has correct name."""
        agent = create_mece_validator()
        assert agent.name == "mece_validator_agent"

    def test_agent_has_gemini_model(self):
        """Test that agent uses Gemini model."""
        agent = create_mece_validator()
        assert isinstance(agent.model, Gemini)

    def test_agent_uses_correct_prompt(self):
        """Test that agent uses MECE validator prompt."""
        agent = create_mece_validator()
        assert agent.instruction == MECE_VALIDATOR_PROMPT

    def test_agent_has_validation_tools(self):
        """Test that agent has validation and exit_loop tools."""
        agent = create_mece_validator()
        # Should have 2 FunctionTools: validate_mece_structure and exit_loop
        function_tools = [
            tool for tool in agent.tools if isinstance(tool, FunctionTool)
        ]
        assert len(function_tools) == 2

    def test_agent_has_output_key(self):
        """Test that agent has correct output_key."""
        agent = create_mece_validator()
        assert agent.output_key == "validation_result"

    def test_multiple_calls_create_independent_instances(self):
        """Test that multiple calls create independent instances."""
        agent1 = create_mece_validator()
        agent2 = create_mece_validator()
        assert agent1 is not agent2


class TestCreateAnalysisPhase:
    """Test create_analysis_phase function."""

    def test_creates_loop_agent_instance(self):
        """Test that function creates a LoopAgent instance."""
        agent = create_analysis_phase()
        assert isinstance(agent, LoopAgent)

    def test_agent_has_correct_name(self):
        """Test that agent has correct name."""
        agent = create_analysis_phase()
        assert agent.name == "analysis_phase"

    def test_agent_has_two_sub_agents(self):
        """Test that agent has exactly two sub-agents."""
        agent = create_analysis_phase()
        assert len(agent.sub_agents) == 2

    def test_sub_agents_are_agent_instances(self):
        """Test that sub-agents are Agent instances."""
        agent = create_analysis_phase()
        for sub_agent in agent.sub_agents:
            assert isinstance(sub_agent, Agent)

    def test_sub_agents_have_correct_names(self):
        """Test that sub-agents have correct names."""
        agent = create_analysis_phase()
        names = [sub_agent.name for sub_agent in agent.sub_agents]
        assert "hypothesis_generator" in names
        assert "mece_validator_agent" in names

    def test_sub_agents_have_output_keys(self):
        """Test that sub-agents have output keys set."""
        agent = create_analysis_phase()
        output_keys = [sub_agent.output_key for sub_agent in agent.sub_agents]
        assert "hypothesis_tree" in output_keys
        assert "validation_result" in output_keys

    def test_default_max_iterations(self):
        """Test that default max_iterations is 3."""
        agent = create_analysis_phase()
        assert agent.max_iterations == 3

    def test_custom_max_iterations(self):
        """Test that custom max_iterations can be set."""
        agent = create_analysis_phase(max_iterations=5)
        assert agent.max_iterations == 5

    def test_multiple_calls_create_independent_instances(self):
        """Test that multiple calls create independent instances."""
        agent1 = create_analysis_phase()
        agent2 = create_analysis_phase()
        assert agent1 is not agent2
        assert agent1.sub_agents[0] is not agent2.sub_agents[0]


class TestAgentIntegration:
    """Test integration between analysis agents."""

    def test_analysis_phase_output_keys_dont_conflict(self):
        """Test that output keys from sub-agents don't conflict."""
        agent = create_analysis_phase()
        output_keys = [sub_agent.output_key for sub_agent in agent.sub_agents]
        # Should have unique output keys
        assert len(output_keys) == len(set(output_keys))

    def test_hypothesis_generator_output_feeds_validator(self):
        """Test that generator output key matches validator input."""
        # Validator prompt should reference {hypothesis_tree}
        assert "{hypothesis_tree}" in MECE_VALIDATOR_PROMPT

        # Generator should output to "hypothesis_tree"
        generator = create_hypothesis_generator()
        assert generator.output_key == "hypothesis_tree"

    def test_all_sub_agents_use_gemini_model(self):
        """Test that all agents use Gemini model."""
        generator = create_hypothesis_generator()
        validator = create_mece_validator()

        assert isinstance(generator.model, Gemini)
        assert isinstance(validator.model, Gemini)

    def test_loop_agent_has_no_model(self):
        """Test that LoopAgent doesn't have its own model."""
        agent = create_analysis_phase()
        # LoopAgent shouldn't have model or instruction attributes
        assert not hasattr(agent, "model") or agent.model is None
        assert not hasattr(agent, "instruction") or agent.instruction is None

    def test_validator_has_exit_loop_tool(self):
        """Test that validator has exit_loop tool for loop termination."""
        validator = create_mece_validator()
        # Should have FunctionTools including exit_loop
        assert len(validator.tools) >= 2


class TestAgentConfiguration:
    """Test agent configuration details."""

    def test_hypothesis_generator_uses_flash_model(self):
        """Test that hypothesis generator uses gemini-2.0-flash."""
        agent = create_hypothesis_generator()
        if hasattr(agent.model, "model"):
            assert "gemini-2.0-flash" in str(agent.model.model)

    def test_mece_validator_uses_flash_model(self):
        """Test that MECE validator uses gemini-2.0-flash."""
        agent = create_mece_validator()
        if hasattr(agent.model, "model"):
            assert "gemini-2.0-flash" in str(agent.model.model)

    def test_agents_use_correct_prompts(self):
        """Test that agents use their respective prompts."""
        generator = create_hypothesis_generator()
        validator = create_mece_validator()

        # Prompts should be different
        assert generator.instruction != validator.instruction

        # Should match the imported constants
        assert generator.instruction == HYPOTHESIS_GENERATOR_PROMPT
        assert validator.instruction == MECE_VALIDATOR_PROMPT

    def test_generator_has_hypothesis_tree_tool_function(self):
        """Test that generator's tool wraps the correct function."""
        agent = create_hypothesis_generator()
        # Should have at least one FunctionTool
        function_tools = [
            tool for tool in agent.tools if isinstance(tool, FunctionTool)
        ]
        assert len(function_tools) > 0

    def test_validator_has_both_required_tools(self):
        """Test that validator has validate_mece_structure and exit_loop."""
        agent = create_mece_validator()
        # Should have exactly 2 FunctionTools
        function_tools = [
            tool for tool in agent.tools if isinstance(tool, FunctionTool)
        ]
        assert len(function_tools) == 2


class TestFactoryPattern:
    """Test factory pattern implementation."""

    def test_functions_are_callable(self):
        """Test that all factory functions are callable."""
        assert callable(create_hypothesis_generator)
        assert callable(create_mece_validator)
        assert callable(create_analysis_phase)
        assert callable(exit_loop)

    def test_factory_functions_return_non_none(self):
        """Test that factory functions return non-None values."""
        assert create_hypothesis_generator() is not None
        assert create_mece_validator() is not None
        assert create_analysis_phase() is not None
        assert exit_loop() is not None

    def test_analysis_phase_accepts_optional_parameter(self):
        """Test that analysis_phase accepts optional max_iterations."""
        # Should work with no parameters
        agent1 = create_analysis_phase()
        assert agent1 is not None

        # Should work with custom max_iterations
        agent2 = create_analysis_phase(max_iterations=5)
        assert agent2 is not None
        assert agent2.max_iterations == 5
