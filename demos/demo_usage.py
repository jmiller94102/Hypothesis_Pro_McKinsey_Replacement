"""Demonstration of HypothesisTree Pro usage.

This script demonstrates how to use the strategic consultant agent
for various strategic decision-making scenarios.
"""

from strategic_consultant_agent.session_manager import StrategicConsultantSession
from strategic_consultant_agent.persistence_integration import (
    save_completed_analysis,
    load_previous_analysis,
    format_analysis_summary,
)
from strategic_consultant_agent.logging_config import setup_logging


def demo_session_usage():
    """Demonstrate basic session usage."""
    print("=" * 70)
    print("DEMO 1: Basic Session Usage")
    print("=" * 70)

    # Setup logging
    logger = setup_logging(log_level="INFO", log_to_file=True)
    logger.info("Starting HypothesisTree Pro demo")

    # Create session
    session = StrategicConsultantSession(
        user_id="demo_user", session_id="demo_session_001"
    )

    print("\nSession created:")
    print(f"  User ID: {session.get_user_id()}")
    print(f"  Session ID: {session.get_session_id()}")

    # Example question
    question = "Should we scale deployment of fall detection in senior living?"
    print(f"\nQuestion: {question}")

    # In a real scenario, you would iterate over events:
    # for event in session.run(question):
    #     # Process events from the agent
    #     pass

    print("\n✓ Session ready to process strategic questions")
    print("=" * 70)


def demo_persistence():
    """Demonstrate persistence features."""
    print("\n" + "=" * 70)
    print("DEMO 2: Persistence and Cross-Session Storage")
    print("=" * 70)

    # Example hypothesis tree (would come from actual agent execution)
    sample_tree = {
        "strategic_question": "Should we scale fall detection?",
        "framework_used": "scale_decision",
        "L1_DESIRABILITY": {
            "label": "Desirability",
            "question": "Is there user need?",
        },
        "L1_FEASIBILITY": {"label": "Feasibility", "question": "Can we build it?"},
        "L1_VIABILITY": {"label": "Viability", "question": "Is it profitable?"},
    }

    # Save analysis
    print("\nSaving analysis...")
    result = save_completed_analysis(
        project_name="fall_detection_demo",
        hypothesis_tree=sample_tree,
        market_research="Sample market research data",
        additional_metadata={"demo": True, "user": "demo_user"},
    )

    print(f"✓ Analysis saved: {result['filepath']}")
    print(f"  Version: {result['version']}")

    # Load analysis
    print("\nLoading analysis...")
    loaded = load_previous_analysis("fall_detection_demo")

    print("✓ Analysis loaded successfully")
    print("\nSummary:")
    print(format_analysis_summary(loaded))

    print("=" * 70)


def demo_frameworks():
    """Demonstrate different framework types."""
    print("\n" + "=" * 70)
    print("DEMO 3: Framework Selection")
    print("=" * 70)

    frameworks = {
        "scale_decision": "Should we scale deployment of X?",
        "product_launch": "Should we launch product Y?",
        "market_entry": "Should we enter market Z?",
        "investment_decision": "Should we acquire company A?",
        "operations_improvement": "Should we implement process B?",
    }

    print("\nSupported Frameworks:\n")
    for framework, example in frameworks.items():
        print(f"  • {framework:25} → {example}")

    print("\n✓ Agent automatically selects appropriate framework")
    print("=" * 70)


def demo_multi_turn_conversation():
    """Demonstrate multi-turn conversation."""
    print("\n" + "=" * 70)
    print("DEMO 4: Multi-Turn Conversation")
    print("=" * 70)

    session = StrategicConsultantSession(session_id="multi_turn_demo")

    questions = [
        "Should we scale fall detection in senior living?",
        "What are the top priority hypotheses to test?",
        "Tell me more about the desirability factors",
    ]

    print("\nMulti-turn conversation flow:")
    for i, question in enumerate(questions, 1):
        print(f"\nTurn {i}: {question}")
        # In real usage: for event in session.run(question): ...
        print(f"  → Agent processes question in same session")

    print("\n✓ Session state persists across all turns")
    print("=" * 70)


def main():
    """Run all demos."""
    print("\n")
    print("*" * 70)
    print("HypothesisTree Pro - Strategic Consultant Agent Demonstration".center(70))
    print("*" * 70)

    try:
        demo_session_usage()
        demo_persistence()
        demo_frameworks()
        demo_multi_turn_conversation()

        print("\n" + "*" * 70)
        print("All demos completed successfully!".center(70))
        print("*" * 70)
        print("\nNext steps:")
        print("  1. Set GOOGLE_API_KEY environment variable")
        print("  2. Run actual agent with: adk web")
        print("  3. Or use the Python API as shown above")
        print()

    except Exception as e:
        print(f"\nError during demo: {e}")
        print("Note: Some demos require actual agent execution")


if __name__ == "__main__":
    main()
