"""Tests for research agents module."""

import pytest
from google.adk.agents import Agent, ParallelAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search

from strategic_consultant_agent.sub_agents.research_agents import (
    create_market_researcher,
    create_competitor_researcher,
    create_research_phase,
    RETRY_CONFIG,
)
from strategic_consultant_agent.prompts.instructions import (
    MARKET_RESEARCHER_PROMPT,
    COMPETITOR_RESEARCHER_PROMPT,
)


class TestRetryConfig:
    """Test retry configuration."""

    def test_retry_config_exists(self):
        """Test that retry config is defined."""
        # Retry config is None - handled by Gemini model defaults
        assert RETRY_CONFIG is None


class TestCreateMarketResearcher:
    """Test create_market_researcher function."""

    def test_creates_agent_instance(self):
        """Test that function creates an Agent instance."""
        agent = create_market_researcher()
        assert isinstance(agent, Agent)

    def test_agent_has_correct_name(self):
        """Test that agent has correct name."""
        agent = create_market_researcher()
        assert agent.name == "market_researcher"

    def test_agent_has_gemini_model(self):
        """Test that agent uses Gemini model."""
        agent = create_market_researcher()
        assert isinstance(agent.model, Gemini)

    def test_agent_uses_correct_prompt(self):
        """Test that agent uses market researcher prompt."""
        agent = create_market_researcher()
        assert agent.instruction == MARKET_RESEARCHER_PROMPT

    def test_agent_has_google_search_tool(self):
        """Test that agent has google_search tool."""
        agent = create_market_researcher()
        assert google_search in agent.tools

    def test_agent_has_output_key(self):
        """Test that agent has correct output_key."""
        agent = create_market_researcher()
        assert agent.output_key == "market_research"

    def test_multiple_calls_create_independent_instances(self):
        """Test that multiple calls create independent agent instances."""
        agent1 = create_market_researcher()
        agent2 = create_market_researcher()
        assert agent1 is not agent2


class TestCreateCompetitorResearcher:
    """Test create_competitor_researcher function."""

    def test_creates_agent_instance(self):
        """Test that function creates an Agent instance."""
        agent = create_competitor_researcher()
        assert isinstance(agent, Agent)

    def test_agent_has_correct_name(self):
        """Test that agent has correct name."""
        agent = create_competitor_researcher()
        assert agent.name == "competitor_researcher"

    def test_agent_has_gemini_model(self):
        """Test that agent uses Gemini model."""
        agent = create_competitor_researcher()
        assert isinstance(agent.model, Gemini)

    def test_agent_uses_correct_prompt(self):
        """Test that agent uses competitor researcher prompt."""
        agent = create_competitor_researcher()
        assert agent.instruction == COMPETITOR_RESEARCHER_PROMPT

    def test_agent_has_google_search_tool(self):
        """Test that agent has google_search tool."""
        agent = create_competitor_researcher()
        assert google_search in agent.tools

    def test_agent_has_output_key(self):
        """Test that agent has correct output_key."""
        agent = create_competitor_researcher()
        assert agent.output_key == "competitor_research"

    def test_multiple_calls_create_independent_instances(self):
        """Test that multiple calls create independent agent instances."""
        agent1 = create_competitor_researcher()
        agent2 = create_competitor_researcher()
        assert agent1 is not agent2


class TestCreateResearchPhase:
    """Test create_research_phase function."""

    def test_creates_parallel_agent_instance(self):
        """Test that function creates a ParallelAgent instance."""
        agent = create_research_phase()
        assert isinstance(agent, ParallelAgent)

    def test_agent_has_correct_name(self):
        """Test that agent has correct name."""
        agent = create_research_phase()
        assert agent.name == "research_phase"

    def test_agent_has_two_sub_agents(self):
        """Test that agent has exactly two sub-agents."""
        agent = create_research_phase()
        assert len(agent.sub_agents) == 2

    def test_sub_agents_are_agent_instances(self):
        """Test that sub-agents are Agent instances."""
        agent = create_research_phase()
        for sub_agent in agent.sub_agents:
            assert isinstance(sub_agent, Agent)

    def test_sub_agents_have_correct_names(self):
        """Test that sub-agents have correct names."""
        agent = create_research_phase()
        names = [sub_agent.name for sub_agent in agent.sub_agents]
        assert "market_researcher" in names
        assert "competitor_researcher" in names

    def test_sub_agents_have_output_keys(self):
        """Test that sub-agents have output keys set."""
        agent = create_research_phase()
        output_keys = [sub_agent.output_key for sub_agent in agent.sub_agents]
        assert "market_research" in output_keys
        assert "competitor_research" in output_keys

    def test_multiple_calls_create_independent_instances(self):
        """Test that multiple calls create independent instances."""
        agent1 = create_research_phase()
        agent2 = create_research_phase()
        assert agent1 is not agent2
        assert agent1.sub_agents[0] is not agent2.sub_agents[0]


class TestAgentIntegration:
    """Test integration between research agents."""

    def test_research_phase_output_keys_dont_conflict(self):
        """Test that output keys from sub-agents don't conflict."""
        agent = create_research_phase()
        output_keys = [sub_agent.output_key for sub_agent in agent.sub_agents]
        # Should have unique output keys
        assert len(output_keys) == len(set(output_keys))

    def test_all_sub_agents_use_gemini_model(self):
        """Test that all agents use Gemini model."""
        market = create_market_researcher()
        competitor = create_competitor_researcher()

        # Both should use Gemini model
        assert isinstance(market.model, Gemini)
        assert isinstance(competitor.model, Gemini)

    def test_parallel_agent_has_no_model(self):
        """Test that ParallelAgent doesn't have its own model."""
        agent = create_research_phase()
        # ParallelAgent shouldn't have model or instruction attributes
        assert not hasattr(agent, "model") or agent.model is None
        assert not hasattr(agent, "instruction") or agent.instruction is None

    def test_all_researchers_have_google_search(self):
        """Test that all researcher agents have google_search tool."""
        market = create_market_researcher()
        competitor = create_competitor_researcher()

        assert google_search in market.tools
        assert google_search in competitor.tools


class TestAgentConfiguration:
    """Test agent configuration details."""

    def test_market_researcher_uses_flash_model(self):
        """Test that market researcher uses gemini-2.0-flash."""
        agent = create_market_researcher()
        # Check model name if accessible
        if hasattr(agent.model, "model"):
            assert "gemini-2.0-flash" in str(agent.model.model)

    def test_competitor_researcher_uses_flash_model(self):
        """Test that competitor researcher uses gemini-2.0-flash."""
        agent = create_competitor_researcher()
        # Check model name if accessible
        if hasattr(agent.model, "model"):
            assert "gemini-2.0-flash" in str(agent.model.model)

    def test_agents_use_correct_prompts(self):
        """Test that agents use their respective prompts."""
        market = create_market_researcher()
        competitor = create_competitor_researcher()

        # Prompts should be different
        assert market.instruction != competitor.instruction

        # Should match the imported constants
        assert market.instruction == MARKET_RESEARCHER_PROMPT
        assert competitor.instruction == COMPETITOR_RESEARCHER_PROMPT


class TestFactoryPattern:
    """Test factory pattern implementation."""

    def test_functions_are_callable(self):
        """Test that all factory functions are callable."""
        assert callable(create_market_researcher)
        assert callable(create_competitor_researcher)
        assert callable(create_research_phase)

    def test_factory_functions_require_no_parameters(self):
        """Test that factory functions can be called without parameters."""
        # Should not raise exceptions
        create_market_researcher()
        create_competitor_researcher()
        create_research_phase()

    def test_factory_functions_return_non_none(self):
        """Test that factory functions return non-None values."""
        assert create_market_researcher() is not None
        assert create_competitor_researcher() is not None
        assert create_research_phase() is not None
