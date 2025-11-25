"""Root orchestrator agent: Sequential multi-agent workflow.

This module defines the top-level SequentialAgent that orchestrates
the three-phase strategic analysis workflow.
"""

from google.adk.agents import SequentialAgent, Agent
from google.genai import types

from strategic_consultant_agent.sub_agents.research_agents import create_research_phase
from strategic_consultant_agent.sub_agents.analysis_agents import create_analysis_phase
from strategic_consultant_agent.sub_agents.prioritizer_agent import create_prioritizer
from strategic_consultant_agent.prompts.instructions import INPUT_PROCESSOR_PROMPT


def create_input_processor() -> Agent:
    """
    Create the input processor agent.

    This agent captures the user's strategic question and stores it
    as 'problem' in the session state for downstream agents to use.

    Returns:
        Agent: Input processor that sets the 'problem' state variable
    """
    return Agent(
        name="input_processor",
        model="gemini-2.0-flash",
        instruction=INPUT_PROCESSOR_PROMPT,
        output_key="problem",  # This stores the output as 'problem' in session state
        generate_content_config=types.GenerateContentConfig(
            temperature=0.0,  # Deterministic - just pass through the question
        ),
    )


def create_strategic_analyzer() -> SequentialAgent:
    """
    Create the strategic analyzer root agent.

    This SequentialAgent orchestrates the complete workflow:
    0. Input Processor: Captures user question as 'problem' in session state
    1. Research Phase (ParallelAgent): Market & competitor research
    2. Analysis Phase (LoopAgent): Hypothesis generation & MECE validation
    3. Prioritizer: 2x2 matrix and testing roadmap

    Returns:
        SequentialAgent: Configured strategic analyzer agent
    """
    input_processor = create_input_processor()
    research_phase = create_research_phase()
    analysis_phase = create_analysis_phase()
    prioritizer = create_prioritizer()

    return SequentialAgent(
        name="strategic_analyzer",
        sub_agents=[input_processor, research_phase, analysis_phase, prioritizer],
    )


# Export the root agent as the default (callable for ADK eval)
root_agent = create_strategic_analyzer()
