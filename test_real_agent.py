"""Test the strategic consultant agent with real API calls.

This script tests the complete agent workflow with actual Google API calls.
"""

import os
import sys
from strategic_consultant_agent.session_manager import StrategicConsultantSession
from strategic_consultant_agent.logging_config import setup_logging


def test_simple_question():
    """Test a simple strategic question."""
    print("\n" + "=" * 70)
    print("TEST 1: Simple Strategic Question")
    print("=" * 70)

    # Setup logging
    logger = setup_logging(log_level="INFO", log_to_file=True, log_to_console=True)
    logger.info("Starting real API test")

    # Create session
    session = StrategicConsultantSession(
        user_id="test_user",
        session_id="real_test_001"
    )

    # Ask a simple question
    question = "Should we scale deployment of fall detection in senior living?"
    print(f"\nQuestion: {question}")
    print("\nAgent is thinking...\n")

    try:
        # Run the agent
        events_received = 0
        for event in session.run(question):
            events_received += 1
            # Print event type and basic info
            if hasattr(event, 'type'):
                print(f"Event {events_received}: {event.type}")
            else:
                print(f"Event {events_received}: {type(event).__name__}")

            # Limit output for readability
            if events_received > 20:
                print(f"... (showing first 20 events, total received: {events_received})")
                break

        print(f"\n✓ Agent executed successfully")
        print(f"  Total events: {events_received}")
        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tool_execution():
    """Test that tools are being called."""
    print("\n" + "=" * 70)
    print("TEST 2: Verify Tool Execution")
    print("=" * 70)

    # Test the tools directly first
    from strategic_consultant_agent.tools.hypothesis_tree import generate_hypothesis_tree
    from strategic_consultant_agent.tools.mece_validator import validate_mece_structure
    from strategic_consultant_agent.tools.matrix_2x2 import generate_2x2_matrix

    print("\nTesting tools directly...")

    # Test hypothesis tree generation
    try:
        tree = generate_hypothesis_tree(
            strategic_question="Should we scale fall detection?",
            framework="scale_decision"
        )
        print(f"✓ generate_hypothesis_tree works: {len(tree)} keys")
    except Exception as e:
        print(f"✗ generate_hypothesis_tree failed: {e}")
        return False

    # Test MECE validation
    try:
        result = validate_mece_structure(tree)
        print(f"✓ validate_mece_structure works: is_mece={result['is_mece']}")
    except Exception as e:
        print(f"✗ validate_mece_structure failed: {e}")
        return False

    # Test 2x2 matrix
    try:
        items = [
            {"name": "Test 1", "impact": 8, "effort": 3},
            {"name": "Test 2", "impact": 5, "effort": 7}
        ]
        matrix = generate_2x2_matrix(items, matrix_type="prioritization")
        print(f"✓ generate_2x2_matrix works: {len(matrix['quadrants'])} quadrants")
    except Exception as e:
        print(f"✗ generate_2x2_matrix failed: {e}")
        return False

    print("\n✓ All tools working correctly")
    return True


def main():
    """Run all tests."""
    print("\n" + "*" * 70)
    print("REAL API TEST - Strategic Consultant Agent".center(70))
    print("*" * 70)

    # Check API key
    if not os.environ.get("GOOGLE_API_KEY"):
        print("\n✗ ERROR: GOOGLE_API_KEY not set")
        print("Please set your API key: export GOOGLE_API_KEY='your-key-here'")
        sys.exit(1)

    print(f"\n✓ API Key found (length: {len(os.environ.get('GOOGLE_API_KEY', ''))} chars)")

    # Run tests
    results = []

    # Test 1: Tool execution (faster, doesn't use API)
    results.append(("Tool Execution", test_tool_execution()))

    # Test 2: Real agent execution (uses API)
    print("\n⚠️  NOTE: The next test will make real API calls to Google Gemini")
    print("This may take 30-60 seconds depending on the agent complexity...")

    try:
        results.append(("Simple Question", test_simple_question()))
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        results.append(("Simple Question", False))

    # Summary
    print("\n" + "*" * 70)
    print("TEST SUMMARY".center(70))
    print("*" * 70)

    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {test_name:30} {status}")

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    print(f"\nTotal: {total_passed}/{total_tests} tests passed")

    if total_passed == total_tests:
        print("\n🎉 All tests passed! Agent is working correctly.")
    else:
        print(f"\n⚠️  {total_tests - total_passed} test(s) failed")

    print("*" * 70)
    print()


if __name__ == "__main__":
    main()
