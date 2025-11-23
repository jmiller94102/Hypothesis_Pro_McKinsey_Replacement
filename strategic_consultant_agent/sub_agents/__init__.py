"""Sub-agents for the strategic consultant multi-agent system."""

from strategic_consultant_agent.sub_agents.research_agents import (
    create_research_phase,
    create_market_researcher,
    create_competitor_researcher,
)

__all__ = [
    "create_research_phase",
    "create_market_researcher",
    "create_competitor_researcher",
]
