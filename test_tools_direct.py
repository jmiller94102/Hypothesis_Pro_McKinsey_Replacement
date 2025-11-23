"""Direct test of tools without the full agent system."""

from strategic_consultant_agent.tools.hypothesis_tree import generate_hypothesis_tree
from strategic_consultant_agent.tools.mece_validator import validate_mece_structure
from strategic_consultant_agent.tools.matrix_2x2 import generate_2x2_matrix
from strategic_consultant_agent.tools.persistence import save_analysis, load_analysis
import json


def test_hypothesis_tree():
    """Test hypothesis tree generation."""
    print("=" * 70)
    print("TEST 1: Hypothesis Tree Generation")
    print("=" * 70)

    problem = "Should we scale deployment of fall detection in senior living?"

    print(f"\nProblem: {problem}")
    print("Framework: scale_decision\n")

    tree = generate_hypothesis_tree(
        problem=problem,
        framework="scale_decision"
    )

    print("✓ Hypothesis tree generated successfully!")
    print(f"  Framework: {tree.get('framework')}")
    print(f"  Framework Name: {tree.get('framework_name')}")
    print(f"  L1 Categories in tree: {len([k for k in tree.get('tree', {}).keys()])}")

    # Print structure
    print("\nTree Structure:")
    for l1_key, l1_data in tree.get('tree', {}).items():
        print(f"  • {l1_key}: {l1_data.get('label', 'N/A')}")
        l2_branches = l1_data.get('L2_branches', {})
        print(f"    - L2 branches: {len(l2_branches)}")
        total_l3 = sum(len(l2.get('L3_leaves', [])) for l2 in l2_branches.values())
        print(f"    - Total L3 leaves: {total_l3}")

    return tree


def test_mece_validation(tree):
    """Test MECE validation."""
    print("\n" + "=" * 70)
    print("TEST 2: MECE Validation")
    print("=" * 70)

    result = validate_mece_structure(tree)

    print(f"\n✓ MECE validation completed!")
    print(f"  Is MECE: {result['is_mece']}")
    print(f"  Overlaps found: {len(result['issues']['overlaps'])}")
    print(f"  Gaps found: {len(result['issues']['gaps'])}")
    print(f"  Inconsistencies: {len(result['issues']['level_inconsistencies'])}")

    if result['suggestions']:
        print(f"\nSuggestions ({len(result['suggestions'])}):")
        for i, suggestion in enumerate(result['suggestions'][:3], 1):
            print(f"  {i}. {suggestion}")

    return result


def test_priority_matrix():
    """Test 2x2 matrix generation."""
    print("\n" + "=" * 70)
    print("TEST 3: Priority Matrix (2x2)")
    print("=" * 70)

    # Sample items to prioritize (as strings)
    items = [
        "User demand validation",
        "Technical feasibility proof",
        "Pricing model validation",
        "Integration complexity"
    ]

    # Assessment scores for each item
    assessments = {
        "User demand validation": {"x": 3, "y": 9},  # Low effort, high impact
        "Technical feasibility proof": {"x": 7, "y": 8},  # High effort, high impact
        "Pricing model validation": {"x": 2, "y": 7},  # Low effort, med-high impact
        "Integration complexity": {"x": 8, "y": 5}  # High effort, med impact
    }

    matrix = generate_2x2_matrix(
        items=items,
        x_axis="Effort",
        y_axis="Impact",
        matrix_type="prioritization",
        assessments=assessments
    )

    print(f"\n✓ Priority matrix generated!")
    print(f"  Matrix type: {matrix['matrix_type']}")
    print(f"  X-axis: {matrix['x_axis']}")
    print(f"  Y-axis: {matrix['y_axis']}")
    print(f"  Total items: {len(matrix['items'])}")
    print(f"\n  Placements: {matrix['placements']}")

    return matrix


def test_persistence(tree):
    """Test persistence."""
    print("\n" + "=" * 70)
    print("TEST 4: Persistence")
    print("=" * 70)

    # Save
    result = save_analysis(
        project_name="test_fall_detection",
        analysis_type="hypothesis_tree",
        content=tree
    )

    print(f"\n✓ Analysis saved!")
    print(f"  File: {result['filepath']}")
    print(f"  Version: {result['version']}")

    # Load
    loaded = load_analysis(
        project_name="test_fall_detection",
        analysis_type="hypothesis_tree"
    )

    print(f"\n✓ Analysis loaded!")
    print(f"  Framework: {loaded.get('framework', 'N/A')}")
    print(f"  Problem: {loaded.get('problem', 'N/A')[:60]}...")

    return loaded


def main():
    """Run all tests."""
    print("\n" + "*" * 70)
    print("DIRECT TOOL TESTING".center(70))
    print("Testing all core tools without full agent system".center(70))
    print("*" * 70)

    try:
        # Test 1: Generate hypothesis tree
        tree = test_hypothesis_tree()

        # Test 2: Validate MECE
        validation = test_mece_validation(tree)

        # Test 3: Generate priority matrix
        matrix = test_priority_matrix()

        # Test 4: Persistence
        loaded = test_persistence(tree)

        # Summary
        print("\n" + "*" * 70)
        print("ALL TESTS PASSED ✓".center(70))
        print("*" * 70)
        print("\nCore tools are working correctly!")
        print("All components ready for agent integration.")
        print("*" * 70)
        print()

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
