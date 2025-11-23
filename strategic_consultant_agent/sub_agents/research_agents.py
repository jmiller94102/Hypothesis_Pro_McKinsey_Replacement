"""Research agents: Market and competitor researchers running in parallel.

This module defines the research phase ParallelAgent and its two sub-agents.
"""

from google.adk.agents import Agent, ParallelAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search

from strategic_consultant_agent.prompts.instructions import (
    MARKET_RESEARCHER_PROMPT,
    COMPETITOR_RESEARCHER_PROMPT,
)


# Retry configuration will be handled by Gemini model defaults
# The model has built-in retry logic for common error codes
RETRY_CONFIG = None


def create_market_researcher() -> Agent:
    """
    Create the market researcher agent.

    This agent researches market size, growth, trends, and benchmarks.

    Returns:
        Agent: Configured market researcher agent
    """
    return Agent(
        name="market_researcher",
        model=Gemini(model="gemini-2.0-flash"),
        instruction=MARKET_RESEARCHER_PROMPT,
        tools=[google_search],
        output_key="market_research",
    )


def create_competitor_researcher() -> Agent:
    """
    Create the competitor researcher agent.

    This agent researches competitive landscape, vendors, and alternatives.

    Returns:
        Agent: Configured competitor researcher agent
    """
    return Agent(
        name="competitor_researcher",
        model=Gemini(model="gemini-2.0-flash"),
        instruction=COMPETITOR_RESEARCHER_PROMPT,
        tools=[google_search],
        output_key="competitor_research",
    )


def create_research_phase() -> ParallelAgent:
    """
    Create the research phase agent.

    This ParallelAgent runs market and competitor research simultaneously
    for better performance.

    Returns:
        ParallelAgent: Configured research phase agent
    """
    market_researcher = create_market_researcher()
    competitor_researcher = create_competitor_researcher()

    return ParallelAgent(
        name="research_phase",
        sub_agents=[market_researcher, competitor_researcher],
    )
