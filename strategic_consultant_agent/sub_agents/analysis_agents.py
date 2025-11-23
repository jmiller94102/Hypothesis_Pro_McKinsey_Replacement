"""Analysis agents: Hypothesis generator and MECE validator in a loop.

This module defines the analysis phase LoopAgent and its two sub-agents.
The loop continues until MECE validation passes or max_iterations is reached.
"""

from google.adk.agents import Agent, LoopAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import FunctionTool

from strategic_consultant_agent.prompts.instructions import (
    HYPOTHESIS_GENERATOR_PROMPT,
    MECE_VALIDATOR_PROMPT,
)
from strategic_consultant_agent.tools.hypothesis_tree import generate_hypothesis_tree
from strategic_consultant_agent.tools.mece_validator import validate_mece_structure


def exit_loop() -> dict:
    """
    Exit the loop when MECE validation passes.

    This function is called by the MECE validator agent when validation succeeds.

    Returns:
        dict: Status message indicating validation passed
    """
    return {"status": "MECE validation passed. Proceeding to prioritization."}


def create_hypothesis_generator() -> Agent:
    """
    Create the hypothesis generator agent.

    This agent generates MECE hypothesis trees using the selected framework
    and incorporates insights from research.

    Returns:
        Agent: Configured hypothesis generator agent
    """
    return Agent(
        name="hypothesis_generator",
        model=Gemini(model="gemini-2.0-flash"),
        instruction=HYPOTHESIS_GENERATOR_PROMPT,
        tools=[FunctionTool(generate_hypothesis_tree)],
        output_key="hypothesis_tree",
    )


def create_mece_validator() -> Agent:
    """
    Create the MECE validator agent.

    This agent validates hypothesis trees for MECE compliance and
    calls exit_loop when validation passes.

    Returns:
        Agent: Configured MECE validator agent
    """
    return Agent(
        name="mece_validator_agent",
        model=Gemini(model="gemini-2.0-flash"),
        instruction=MECE_VALIDATOR_PROMPT,
        tools=[FunctionTool(validate_mece_structure), FunctionTool(exit_loop)],
        output_key="validation_result",
    )


def create_analysis_phase(max_iterations: int = 3) -> LoopAgent:
    """
    Create the analysis phase agent.

    This LoopAgent runs hypothesis generation and MECE validation iteratively
    until the tree passes validation or max_iterations is reached.

    Args:
        max_iterations: Maximum number of loop iterations (default: 3)

    Returns:
        LoopAgent: Configured analysis phase agent
    """
    hypothesis_generator = create_hypothesis_generator()
    mece_validator = create_mece_validator()

    return LoopAgent(
        name="analysis_phase",
        sub_agents=[hypothesis_generator, mece_validator],
        max_iterations=max_iterations,
    )
