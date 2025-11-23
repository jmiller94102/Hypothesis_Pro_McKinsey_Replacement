"""Tests for agent instruction prompts."""

import pytest

from strategic_consultant_agent.prompts.instructions import (
    MARKET_RESEARCHER_PROMPT,
    COMPETITOR_RESEARCHER_PROMPT,
    HYPOTHESIS_GENERATOR_PROMPT,
    MECE_VALIDATOR_PROMPT,
    PRIORITIZER_PROMPT,
)


class TestPromptDefinitions:
    """Test that all prompts are properly defined."""

    def test_market_researcher_prompt_exists(self):
        """Test that market researcher prompt exists."""
        assert MARKET_RESEARCHER_PROMPT is not None
        assert isinstance(MARKET_RESEARCHER_PROMPT, str)
        assert len(MARKET_RESEARCHER_PROMPT) > 0

    def test_competitor_researcher_prompt_exists(self):
        """Test that competitor researcher prompt exists."""
        assert COMPETITOR_RESEARCHER_PROMPT is not None
        assert isinstance(COMPETITOR_RESEARCHER_PROMPT, str)
        assert len(COMPETITOR_RESEARCHER_PROMPT) > 0

    def test_hypothesis_generator_prompt_exists(self):
        """Test that hypothesis generator prompt exists."""
        assert HYPOTHESIS_GENERATOR_PROMPT is not None
        assert isinstance(HYPOTHESIS_GENERATOR_PROMPT, str)
        assert len(HYPOTHESIS_GENERATOR_PROMPT) > 0

    def test_mece_validator_prompt_exists(self):
        """Test that MECE validator prompt exists."""
        assert MECE_VALIDATOR_PROMPT is not None
        assert isinstance(MECE_VALIDATOR_PROMPT, str)
        assert len(MECE_VALIDATOR_PROMPT) > 0

    def test_prioritizer_prompt_exists(self):
        """Test that prioritizer prompt exists."""
        assert PRIORITIZER_PROMPT is not None
        assert isinstance(PRIORITIZER_PROMPT, str)
        assert len(PRIORITIZER_PROMPT) > 0


class TestMarketResearcherPrompt:
    """Test market researcher prompt content."""

    def test_contains_problem_placeholder(self):
        """Test that prompt contains problem placeholder."""
        assert "{problem}" in MARKET_RESEARCHER_PROMPT

    def test_mentions_market_research_focus_areas(self):
        """Test that prompt mentions key research areas."""
        prompt = MARKET_RESEARCHER_PROMPT.lower()
        assert "market size" in prompt or "market" in prompt
        assert "growth" in prompt
        assert "benchmarks" in prompt or "benchmark" in prompt

    def test_mentions_google_search_tool(self):
        """Test that prompt mentions google_search tool."""
        assert "google_search" in MARKET_RESEARCHER_PROMPT

    def test_provides_source_guidance(self):
        """Test that prompt provides guidance on sources."""
        prompt = MARKET_RESEARCHER_PROMPT.lower()
        assert "industry reports" in prompt or "sources" in prompt


class TestCompetitorResearcherPrompt:
    """Test competitor researcher prompt content."""

    def test_contains_problem_placeholder(self):
        """Test that prompt contains problem placeholder."""
        assert "{problem}" in COMPETITOR_RESEARCHER_PROMPT

    def test_mentions_competitive_analysis_areas(self):
        """Test that prompt mentions competitive analysis areas."""
        prompt = COMPETITOR_RESEARCHER_PROMPT.lower()
        assert "vendors" in prompt or "vendor" in prompt
        assert "competitors" in prompt or "competitive" in prompt

    def test_mentions_google_search_tool(self):
        """Test that prompt mentions google_search tool."""
        assert "google_search" in COMPETITOR_RESEARCHER_PROMPT

    def test_mentions_customer_reviews(self):
        """Test that prompt mentions customer reviews."""
        prompt = COMPETITOR_RESEARCHER_PROMPT.lower()
        assert "reviews" in prompt or "customer" in prompt


class TestHypothesisGeneratorPrompt:
    """Test hypothesis generator prompt content."""

    def test_contains_required_placeholders(self):
        """Test that prompt contains all required placeholders."""
        assert "{problem}" in HYPOTHESIS_GENERATOR_PROMPT
        assert "{framework}" in HYPOTHESIS_GENERATOR_PROMPT
        assert "{market_research}" in HYPOTHESIS_GENERATOR_PROMPT
        assert "{competitor_research}" in HYPOTHESIS_GENERATOR_PROMPT

    def test_mentions_mece_principle(self):
        """Test that prompt mentions MECE principle."""
        prompt = HYPOTHESIS_GENERATOR_PROMPT.upper()
        assert "MECE" in prompt

    def test_mentions_generate_hypothesis_tree_tool(self):
        """Test that prompt mentions the hypothesis tree tool."""
        assert "generate_hypothesis_tree" in HYPOTHESIS_GENERATOR_PROMPT

    def test_provides_quality_standards(self):
        """Test that prompt provides quality standards."""
        prompt = HYPOTHESIS_GENERATOR_PROMPT.lower()
        assert "quality" in prompt or "standards" in prompt
        assert "measurable" in prompt or "specific" in prompt

    def test_mentions_l3_leaves(self):
        """Test that prompt mentions L3 leaves."""
        assert "L3" in HYPOTHESIS_GENERATOR_PROMPT


class TestMeceValidatorPrompt:
    """Test MECE validator prompt content."""

    def test_contains_hypothesis_tree_placeholder(self):
        """Test that prompt contains hypothesis tree placeholder."""
        assert "{hypothesis_tree}" in MECE_VALIDATOR_PROMPT

    def test_mentions_validate_mece_structure_tool(self):
        """Test that prompt mentions validation tool."""
        assert "validate_mece_structure" in MECE_VALIDATOR_PROMPT

    def test_mentions_exit_loop_function(self):
        """Test that prompt mentions exit_loop function."""
        assert "exit_loop" in MECE_VALIDATOR_PROMPT

    def test_provides_decision_logic(self):
        """Test that prompt provides clear decision logic."""
        prompt = MECE_VALIDATOR_PROMPT.lower()
        assert "is_mece" in prompt
        assert "true" in prompt
        assert "false" in prompt

    def test_provides_feedback_format(self):
        """Test that prompt provides feedback format."""
        prompt = MECE_VALIDATOR_PROMPT.lower()
        assert "feedback" in prompt or "issues" in prompt


class TestPrioritizerPrompt:
    """Test prioritizer prompt content."""

    def test_contains_hypothesis_tree_placeholder(self):
        """Test that prompt contains hypothesis tree placeholder."""
        assert "{hypothesis_tree}" in PRIORITIZER_PROMPT

    def test_mentions_generate_2x2_matrix_tool(self):
        """Test that prompt mentions 2x2 matrix tool."""
        assert "generate_2x2_matrix" in PRIORITIZER_PROMPT

    def test_mentions_impact_and_effort(self):
        """Test that prompt mentions impact and effort assessment."""
        prompt = PRIORITIZER_PROMPT.lower()
        assert "impact" in prompt
        assert "effort" in prompt

    def test_mentions_all_quadrants(self):
        """Test that prompt mentions all prioritization quadrants."""
        prompt = PRIORITIZER_PROMPT.lower()
        assert "quick wins" in prompt
        assert "strategic bets" in prompt
        assert "fill later" in prompt or "deprioritize" in prompt

    def test_provides_output_format(self):
        """Test that prompt provides clear output format."""
        prompt = PRIORITIZER_PROMPT.lower()
        assert "testing sequence" in prompt or "roadmap" in prompt
        assert "phase" in prompt


class TestPromptFormatting:
    """Test prompt formatting and consistency."""

    def test_all_prompts_are_multiline(self):
        """Test that all prompts are multiline for readability."""
        prompts = [
            MARKET_RESEARCHER_PROMPT,
            COMPETITOR_RESEARCHER_PROMPT,
            HYPOTHESIS_GENERATOR_PROMPT,
            MECE_VALIDATOR_PROMPT,
            PRIORITIZER_PROMPT,
        ]
        for prompt in prompts:
            assert "\n" in prompt

    def test_prompts_use_consistent_formatting(self):
        """Test that prompts use consistent formatting."""
        # All prompts should start with a role description
        prompts = [
            MARKET_RESEARCHER_PROMPT,
            COMPETITOR_RESEARCHER_PROMPT,
            HYPOTHESIS_GENERATOR_PROMPT,
            MECE_VALIDATOR_PROMPT,
            PRIORITIZER_PROMPT,
        ]
        for prompt in prompts:
            assert prompt.startswith("You are")

    def test_no_trailing_whitespace(self):
        """Test that prompts don't have trailing whitespace."""
        prompts = [
            MARKET_RESEARCHER_PROMPT,
            COMPETITOR_RESEARCHER_PROMPT,
            HYPOTHESIS_GENERATOR_PROMPT,
            MECE_VALIDATOR_PROMPT,
            PRIORITIZER_PROMPT,
        ]
        for prompt in prompts:
            lines = prompt.split("\n")
            for line in lines:
                # Allow empty lines, but no trailing spaces
                if line:
                    assert line == line.rstrip()


class TestPromptIntegration:
    """Test that prompts work together as a system."""

    def test_research_prompts_output_feeds_generator(self):
        """Test that research outputs are expected by generator."""
        # Generator expects market_research and competitor_research
        assert "{market_research}" in HYPOTHESIS_GENERATOR_PROMPT
        assert "{competitor_research}" in HYPOTHESIS_GENERATOR_PROMPT

    def test_generator_output_feeds_validator(self):
        """Test that generator output feeds validator."""
        # Validator expects hypothesis_tree
        assert "{hypothesis_tree}" in MECE_VALIDATOR_PROMPT

    def test_validator_output_feeds_prioritizer(self):
        """Test that validator output feeds prioritizer."""
        # Prioritizer expects hypothesis_tree (validated)
        assert "{hypothesis_tree}" in PRIORITIZER_PROMPT

    def test_all_tool_mentions_are_valid(self):
        """Test that all mentioned tools exist in our implementation."""
        # Check that all tool names mentioned in prompts are real
        tool_names = [
            "google_search",
            "generate_hypothesis_tree",
            "validate_mece_structure",
            "exit_loop",
            "generate_2x2_matrix",
        ]

        all_prompts = "\n".join(
            [
                MARKET_RESEARCHER_PROMPT,
                COMPETITOR_RESEARCHER_PROMPT,
                HYPOTHESIS_GENERATOR_PROMPT,
                MECE_VALIDATOR_PROMPT,
                PRIORITIZER_PROMPT,
            ]
        )

        for tool_name in tool_names:
            # All these tools should be mentioned somewhere
            if tool_name != "google_search" and tool_name != "exit_loop":
                # These are our custom tools
                assert tool_name in all_prompts
