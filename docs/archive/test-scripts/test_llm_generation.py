"""Test script for LLM-powered tree generation."""

import json
import os
from dotenv import load_dotenv

from strategic_consultant_agent.tools.hypothesis_tree import generate_hypothesis_tree

# Load environment variables
load_dotenv()

# Test data
problem = "Should we scale fall detection technology across all senior living facilities?"

market_research = """
Market Size: The fall detection market is growing at 8.2% CAGR, reaching $2.1B by 2026.
Industry Benchmarks: Leading implementations show 30-40% reduction in fall-related ER visits (KLAS 2024 Fall Management Study).
Key Players: Teton.ai, SafelyYou, Vayyar Care are market leaders with 60-70% market share.
Adoption Trends: 45% of senior living facilities have implemented some form of fall detection (LeadingAge 2024).
"""

competitor_research = """
Teton.ai: AI-powered fall detection with 95% accuracy, $150/unit/month pricing.
Case Study: Sunrise Senior Living reported 35% reduction in fall-related hospitalizations after 12-month deployment.
Customer Reviews: 4.5/5 stars - praised for accuracy and staff adoption, concerns about initial setup complexity.
SafelyYou: Computer vision-based system, similar pricing, strong in assisted living segment.
"""

print("=" * 80)
print("Testing LLM-Powered Tree Generation")
print("=" * 80)
print(f"\nProblem: {problem}")
print("\n" + "=" * 80)
print("Generating tree WITH research context (LLM-powered)...")
print("=" * 80)

try:
    tree_with_llm = generate_hypothesis_tree(
        problem=problem,
        framework="scale_decision",
        market_research=market_research,
        competitor_research=competitor_research,
        use_llm_generation=True,
    )

    # Pretty print first L1 category to see the structure
    first_l1_key = list(tree_with_llm["tree"].keys())[0]
    first_l1 = tree_with_llm["tree"][first_l1_key]

    print(f"\n✓ Generated tree with {len(tree_with_llm['tree'])} L1 categories")
    print(f"\nExample L1 Category: {first_l1_key}")
    print(f"Label: {first_l1['label']}")
    print(f"Question: {first_l1['question']}")

    # Show first L2 branch
    first_l2_key = list(first_l1["L2_branches"].keys())[0]
    first_l2 = first_l1["L2_branches"][first_l2_key]
    print(f"\n  Example L2 Branch: {first_l2_key}")
    print(f"  Label: {first_l2['label']}")
    print(f"  Question: {first_l2['question']}")

    # Show first L3 leaf
    if first_l2["L3_leaves"]:
        first_l3 = first_l2["L3_leaves"][0]
        print(f"\n    Example L3 Leaf:")
        print(f"    Label: {first_l3['label']}")
        print(f"    Question: {first_l3['question']}")
        print(f"    Target: {first_l3['target']}")
        print(f"    Data Source: {first_l3['data_source']}")

    # Save full tree for inspection
    output_file = "test_tree_output.json"
    with open(output_file, "w") as f:
        json.dump(tree_with_llm, f, indent=2)
    print(f"\n✓ Full tree saved to {output_file}")

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("Generating tree WITHOUT research context (template-based)...")
print("=" * 80)

try:
    tree_without_llm = generate_hypothesis_tree(
        problem=problem,
        framework="scale_decision",
        use_llm_generation=False,
    )

    first_l1_key = list(tree_without_llm["tree"].keys())[0]
    first_l1 = tree_without_llm["tree"][first_l1_key]
    first_l2_key = list(first_l1["L2_branches"].keys())[0]
    first_l2 = first_l1["L2_branches"][first_l2_key]

    print(f"\n✓ Generated tree with {len(tree_without_llm['tree'])} L1 categories")
    print(f"\nExample L2 Branch: {first_l2['label']}")

    if first_l2["L3_leaves"]:
        first_l3 = first_l2["L3_leaves"][0]
        print(f"\n  Example L3 Leaf (template-based):")
        print(f"  Label: {first_l3['label']}")
        print(f"  Question: {first_l3['question']}")
        print(f"  Target: {first_l3['target']}")

    print("\n✓ Template-based generation successful")

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("Test Complete!")
print("=" * 80)
