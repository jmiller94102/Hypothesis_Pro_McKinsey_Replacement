"""Root orchestrator agent: Sequential multi-agent workflow.

This module defines the top-level SequentialAgent that orchestrates
the three-phase strategic analysis workflow.
"""

from google.adk.agents import SequentialAgent

from strategic_consultant_agent.sub_agents.research_agents import create_research_phase
from strategic_consultant_agent.sub_agents.analysis_agents import create_analysis_phase
from strategic_consultant_agent.sub_agents.prioritizer_agent import create_prioritizer


def create_strategic_analyzer() -> SequentialAgent:
    """
    Create the strategic analyzer root agent.

    This SequentialAgent orchestrates the complete workflow:
    1. Research Phase (ParallelAgent): Market & competitor research
    2. Analysis Phase (LoopAgent): Hypothesis generation & MECE validation
    3. Prioritizer: 2x2 matrix and testing roadmap

    Returns:
        SequentialAgent: Configured strategic analyzer agent
    """
    research_phase = create_research_phase()
    analysis_phase = create_analysis_phase()
    prioritizer = create_prioritizer()

    return SequentialAgent(
        name="strategic_analyzer",
        sub_agents=[research_phase, analysis_phase, prioritizer],
    )


# Export the root agent as the default (callable for ADK eval)
root_agent = create_strategic_analyzer()
