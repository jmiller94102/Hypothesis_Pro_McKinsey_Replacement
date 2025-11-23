"""Tests for root orchestrator agent."""

import pytest
from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent

from strategic_consultant_agent.agent import create_strategic_analyzer, root_agent


class TestCreateStrategicAnalyzer:
    """Test create_strategic_analyzer function."""

    def test_creates_sequential_agent_instance(self):
        """Test that function creates a SequentialAgent instance."""
        agent = create_strategic_analyzer()
        assert isinstance(agent, SequentialAgent)

    def test_agent_has_correct_name(self):
        """Test that agent has correct name."""
        agent = create_strategic_analyzer()
        assert agent.name == "strategic_analyzer"

    def test_agent_has_three_sub_agents(self):
        """Test that agent has exactly three sub-agents."""
        agent = create_strategic_analyzer()
        assert len(agent.sub_agents) == 3

    def test_sub_agents_have_correct_names(self):
        """Test that sub-agents have correct names."""
        agent = create_strategic_analyzer()
        names = [sub_agent.name for sub_agent in agent.sub_agents]
        assert "research_phase" in names
        assert "analysis_phase" in names
        assert "prioritizer" in names

    def test_sub_agents_are_in_correct_order(self):
        """Test that sub-agents are in correct sequential order."""
        agent = create_strategic_analyzer()
        assert agent.sub_agents[0].name == "research_phase"
        assert agent.sub_agents[1].name == "analysis_phase"
        assert agent.sub_agents[2].name == "prioritizer"

    def test_multiple_calls_create_independent_instances(self):
        """Test that multiple calls create independent instances."""
        agent1 = create_strategic_analyzer()
        agent2 = create_strategic_analyzer()
        assert agent1 is not agent2
        assert agent1.sub_agents[0] is not agent2.sub_agents[0]


class TestSubAgentTypes:
    """Test that sub-agents have correct types."""

    def test_research_phase_is_parallel_agent(self):
        """Test that research_phase is a ParallelAgent."""
        agent = create_strategic_analyzer()
        research_phase = agent.sub_agents[0]
        assert isinstance(research_phase, ParallelAgent)

    def test_analysis_phase_is_loop_agent(self):
        """Test that analysis_phase is a LoopAgent."""
        agent = create_strategic_analyzer()
        analysis_phase = agent.sub_agents[1]
        assert isinstance(analysis_phase, LoopAgent)

    def test_prioritizer_is_agent(self):
        """Test that prioritizer is a standard Agent."""
        agent = create_strategic_analyzer()
        prioritizer = agent.sub_agents[2]
        assert isinstance(prioritizer, Agent)


class TestAgentHierarchy:
    """Test the complete agent hierarchy."""

    def test_research_phase_has_two_researchers(self):
        """Test that research phase has market and competitor researchers."""
        agent = create_strategic_analyzer()
        research_phase = agent.sub_agents[0]
        assert len(research_phase.sub_agents) == 2

        names = [sub.name for sub in research_phase.sub_agents]
        assert "market_researcher" in names
        assert "competitor_researcher" in names

    def test_analysis_phase_has_generator_and_validator(self):
        """Test that analysis phase has generator and validator."""
        agent = create_strategic_analyzer()
        analysis_phase = agent.sub_agents[1]
        assert len(analysis_phase.sub_agents) == 2

        names = [sub.name for sub in analysis_phase.sub_agents]
        assert "hypothesis_generator" in names
        assert "mece_validator_agent" in names

    def test_all_leaf_agents_are_agent_instances(self):
        """Test that all leaf nodes are Agent instances."""
        agent = create_strategic_analyzer()

        # Research phase sub-agents
        for sub_agent in agent.sub_agents[0].sub_agents:
            assert isinstance(sub_agent, Agent)

        # Analysis phase sub-agents
        for sub_agent in agent.sub_agents[1].sub_agents:
            assert isinstance(sub_agent, Agent)

        # Prioritizer is already an Agent
        assert isinstance(agent.sub_agents[2], Agent)


class TestOutputKeys:
    """Test output key configuration."""

    def test_research_agents_have_output_keys(self):
        """Test that research agents have output keys."""
        agent = create_strategic_analyzer()
        research_phase = agent.sub_agents[0]

        output_keys = [sub.output_key for sub in research_phase.sub_agents]
        assert "market_research" in output_keys
        assert "competitor_research" in output_keys

    def test_analysis_agents_have_output_keys(self):
        """Test that analysis agents have output keys."""
        agent = create_strategic_analyzer()
        analysis_phase = agent.sub_agents[1]

        output_keys = [sub.output_key for sub in analysis_phase.sub_agents]
        assert "hypothesis_tree" in output_keys
        assert "validation_result" in output_keys

    def test_prioritizer_has_output_key(self):
        """Test that prioritizer has output key."""
        agent = create_strategic_analyzer()
        prioritizer = agent.sub_agents[2]
        assert prioritizer.output_key == "priority_matrix"

    def test_all_output_keys_are_unique(self):
        """Test that all output keys across the system are unique."""
        agent = create_strategic_analyzer()

        all_output_keys = []

        # Collect from research phase
        for sub in agent.sub_agents[0].sub_agents:
            all_output_keys.append(sub.output_key)

        # Collect from analysis phase
        for sub in agent.sub_agents[1].sub_agents:
            all_output_keys.append(sub.output_key)

        # Collect from prioritizer
        all_output_keys.append(agent.sub_agents[2].output_key)

        # Check uniqueness
        assert len(all_output_keys) == len(set(all_output_keys))


class TestAgentConfiguration:
    """Test agent configuration details."""

    def test_sequential_agent_has_no_model(self):
        """Test that SequentialAgent doesn't have its own model."""
        agent = create_strategic_analyzer()
        assert not hasattr(agent, "model") or agent.model is None
        assert not hasattr(agent, "instruction") or agent.instruction is None

    def test_parallel_agent_has_no_model(self):
        """Test that ParallelAgent doesn't have its own model."""
        agent = create_strategic_analyzer()
        research_phase = agent.sub_agents[0]
        assert not hasattr(research_phase, "model") or research_phase.model is None

    def test_loop_agent_has_no_model(self):
        """Test that LoopAgent doesn't have its own model."""
        agent = create_strategic_analyzer()
        analysis_phase = agent.sub_agents[1]
        assert not hasattr(analysis_phase, "model") or analysis_phase.model is None

    def test_loop_agent_has_max_iterations(self):
        """Test that LoopAgent has max_iterations configured."""
        agent = create_strategic_analyzer()
        analysis_phase = agent.sub_agents[1]
        assert hasattr(analysis_phase, "max_iterations")
        assert analysis_phase.max_iterations == 3


class TestRootAgentExport:
    """Test root_agent export."""

    def test_root_agent_is_callable(self):
        """Test that root_agent is callable."""
        assert callable(root_agent)

    def test_root_agent_creates_strategic_analyzer(self):
        """Test that root_agent creates the same agent as factory."""
        agent1 = root_agent()
        agent2 = create_strategic_analyzer()

        assert agent1.name == agent2.name
        assert len(agent1.sub_agents) == len(agent2.sub_agents)

    def test_root_agent_returns_sequential_agent(self):
        """Test that root_agent returns a SequentialAgent."""
        agent = root_agent()
        assert isinstance(agent, SequentialAgent)


class TestFactoryPattern:
    """Test factory pattern implementation."""

    def test_function_is_callable(self):
        """Test that factory function is callable."""
        assert callable(create_strategic_analyzer)

    def test_factory_function_requires_no_parameters(self):
        """Test that factory function can be called without parameters."""
        # Should not raise exceptions
        create_strategic_analyzer()

    def test_factory_function_returns_non_none(self):
        """Test that factory function returns non-None value."""
        assert create_strategic_analyzer() is not None


class TestWorkflowIntegration:
    """Test workflow integration aspects."""

    def test_research_outputs_feed_analysis(self):
        """Test that research outputs are available to analysis phase."""
        agent = create_strategic_analyzer()

        # Research phase outputs market_research and competitor_research
        research_phase = agent.sub_agents[0]
        research_outputs = [sub.output_key for sub in research_phase.sub_agents]

        # Analysis phase (hypothesis generator) expects these in its prompt
        analysis_phase = agent.sub_agents[1]
        hypothesis_generator = analysis_phase.sub_agents[0]

        # Generator instruction should reference research outputs
        assert "{market_research}" in hypothesis_generator.instruction
        assert "{competitor_research}" in hypothesis_generator.instruction

    def test_analysis_output_feeds_prioritizer(self):
        """Test that analysis output is available to prioritizer."""
        agent = create_strategic_analyzer()

        # Analysis phase outputs hypothesis_tree
        analysis_phase = agent.sub_agents[1]
        hypothesis_generator = analysis_phase.sub_agents[0]
        assert hypothesis_generator.output_key == "hypothesis_tree"

        # Prioritizer expects hypothesis_tree
        prioritizer = agent.sub_agents[2]
        assert "{hypothesis_tree}" in prioritizer.instruction

    def test_complete_data_flow_chain(self):
        """Test complete data flow from research to prioritization."""
        agent = create_strategic_analyzer()

        # Phase 1: Research produces market_research and competitor_research
        research_outputs = {sub.output_key for sub in agent.sub_agents[0].sub_agents}
        assert "market_research" in research_outputs
        assert "competitor_research" in research_outputs

        # Phase 2: Analysis consumes research, produces hypothesis_tree
        hypothesis_gen = agent.sub_agents[1].sub_agents[0]
        assert hypothesis_gen.output_key == "hypothesis_tree"

        # Phase 3: Prioritizer consumes hypothesis_tree, produces priority_matrix
        prioritizer = agent.sub_agents[2]
        assert prioritizer.output_key == "priority_matrix"
