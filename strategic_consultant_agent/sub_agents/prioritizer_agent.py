"""Prioritizer agent: Creates 2x2 matrix and recommends testing sequence.

This module defines the standalone prioritizer agent that runs after
the analysis phase completes.
"""

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import FunctionTool

from strategic_consultant_agent.prompts.instructions import PRIORITIZER_PROMPT
from strategic_consultant_agent.tools.matrix_2x2 import generate_2x2_matrix


def create_prioritizer() -> Agent:
    """
    Create the prioritizer agent.

    This agent extracts hypotheses from the validated tree, assesses
    impact and effort, and generates a 2x2 prioritization matrix with
    a recommended testing sequence.

    Returns:
        Agent: Configured prioritizer agent
    """
    return Agent(
        name="prioritizer",
        model=Gemini(model="gemini-2.0-flash"),
        instruction=PRIORITIZER_PROMPT,
        tools=[FunctionTool(generate_2x2_matrix)],
        output_key="priority_matrix",
    )
