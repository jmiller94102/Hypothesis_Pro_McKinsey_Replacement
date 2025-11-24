"""Create example projects demonstrating all framework capabilities."""

import json
import os
from pathlib import Path

from strategic_consultant_agent.tools.hypothesis_tree import generate_hypothesis_tree
from strategic_consultant_agent.tools.risk_tree_generator import (
    generate_risk_assessment_tree,
    generate_risk_matrix,
)

# Create storage directory
STORAGE_DIR = Path("storage/projects")
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def create_fall_detection_example():
    """Example 1: Scale Decision with LLM-generated content."""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Fall Detection Scale Decision (LLM-Generated)")
    print("=" * 80)

    problem = "Should we scale fall detection technology across all senior living facilities?"

    market_research = """
Market Size: Fall detection market growing at 8.2% CAGR, reaching $2.1B by 2026.
Industry Benchmarks: Leading implementations show 30-40% reduction in fall-related ER visits (KLAS 2024).
Key Players: Teton.ai (35% market share), SafelyYou (25%), Vayyar Care (15%).
Adoption: 45% of senior living facilities have deployed fall detection systems.
ROI: Average 18-month payback period, $150K annual savings per 100-bed facility.
"""

    competitor_research = """
Teton.ai: AI-powered, 95% accuracy, $150/unit/month, strong staff adoption.
Case Study: Sunrise Senior Living - 35% reduction in fall hospitalizations after 12 months.
SafelyYou: Computer vision-based, $180/unit/month, privacy concerns noted.
Vayyar Care: Radar-based, no cameras, $120/unit/month, lower accuracy (85%).
Customer Reviews: Integration complexity is common pain point across all vendors.
"""

    # Generate tree WITHOUT LLM (template-based)
    tree_template = generate_hypothesis_tree(
        problem=problem,
        framework="scale_decision",
        use_llm_generation=False,
    )

    # Save template version
    output_file = STORAGE_DIR / "fall_detection_template.json"
    with open(output_file, "w") as f:
        json.dump(tree_template, f, indent=2)
    print(f"\n✓ Template-based tree saved to {output_file}")

    # Note: LLM-generated version would be created here if API quota available
    print("\nNOTE: LLM-generated version requires API quota. Template version created.")
    print("To generate LLM version, set use_llm_generation=True and provide research context.")


def create_revenue_decline_example():
    """Example 2: Hypothesis-Driven Issue Tree."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Revenue Decline Root Cause Analysis (Hypothesis Issue Tree)")
    print("=" * 80)

    problem = "Why did Q4 revenue decline 15% year-over-year in our SaaS product?"

    market_research = """
Market Trends: SaaS industry grew 12% in Q4 2024 overall.
Competitive Landscape: 3 new competitors launched similar products in Q3-Q4.
Pricing Analysis: Average industry pricing dropped 8% due to increased competition.
Customer Behavior: Shift towards multi-product bundles vs. standalone solutions.
"""

    competitor_research = """
Competitor A: Launched aggressive pricing ($99/mo vs. our $149/mo) in Q3.
Competitor B: Bundled offering with CRM integration (our integration incomplete).
Competitor C: AI-powered features that we lack.
Win/Loss Analysis: Lost 12 deals in Q4 due to pricing, 8 due to feature gaps.
"""

    tree = generate_hypothesis_tree(
        problem=problem,
        framework="hypothesis_issue_tree",
        market_research=market_research,
        competitor_research=competitor_research,
        use_llm_generation=False,  # Template version for demo
    )

    output_file = STORAGE_DIR / "revenue_decline_hypothesis_tree.json"
    with open(output_file, "w") as f:
        json.dump(tree, f, indent=2)
    print(f"\n✓ Hypothesis issue tree saved to {output_file}")
    print(f"  Framework: {tree['framework']}")
    print(f"  L1 Categories: {list(tree['tree'].keys())}")


def create_product_launch_risk_example():
    """Example 3: Risk Assessment Framework."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Product Launch Risk Assessment")
    print("=" * 80)

    problem = "Assess risks for launching AI-powered medical diagnosis assistant in Q2 2025"

    market_research = """
Market Readiness: 67% of healthcare providers express interest in AI diagnostics.
Regulatory Environment: FDA issued new draft guidance for AI/ML-based medical devices (2024).
Time to Approval: Average 18-24 months for FDA clearance of similar products.
Competitive Timing: 2 major competitors planning launches in late 2025.
"""

    competitor_research = """
Competitor A: FDA submission pending, expected approval Q3 2025.
Competitor B: Launched limited pilot, facing accuracy concerns (78% vs. 95% claim).
Market Leader: Established player with 60% market share, strong hospital relationships.
Barriers: High switching costs, integration complexity with EMR systems.
"""

    tree = generate_risk_assessment_tree(
        problem=problem,
        market_research=market_research,
        competitor_research=competitor_research,
        use_llm_generation=False,  # Template version for demo
    )

    # Generate risk matrix
    risk_matrix = generate_risk_matrix(tree)

    output_file = STORAGE_DIR / "product_launch_risk_assessment.json"
    with open(output_file, "w") as f:
        json.dump(tree, f, indent=2)
    print(f"\n✓ Risk assessment tree saved to {output_file}")
    print(f"  Framework: {tree['framework']}")
    print(f"  L1 Risk Categories: {list(tree['tree'].keys())}")

    matrix_file = STORAGE_DIR / "product_launch_risk_matrix.json"
    with open(matrix_file, "w") as f:
        json.dump(risk_matrix, f, indent=2)
    print(f"\n✓ Risk matrix saved to {matrix_file}")
    print(f"  Total Risks: {risk_matrix['total_risks']}")
    print(f"  Critical Risks: {risk_matrix['quadrants']['critical']['count']}")
    print(f"  High Priority: {risk_matrix['quadrants']['high_priority']['count']}")


def main():
    """Create all example projects."""
    print("\n" + "=" * 80)
    print("CREATING EXAMPLE PROJECTS")
    print("=" * 80)
    print("\nThese examples demonstrate:")
    print("1. Scale Decision framework with dynamic L2/L3 generation")
    print("2. Hypothesis-Driven Issue Tree for root cause analysis")
    print("3. Risk Assessment framework with probability-impact scoring")
    print("\nNote: Template versions created (LLM generation requires API quota)")

    create_fall_detection_example()
    create_revenue_decline_example()
    create_product_launch_risk_example()

    print("\n" + "=" * 80)
    print("EXAMPLE PROJECTS CREATED SUCCESSFULLY")
    print("=" * 80)
    print(f"\nOutput directory: {STORAGE_DIR.absolute()}")
    print("\nFiles created:")
    for file in STORAGE_DIR.glob("*.json"):
        print(f"  - {file.name}")


if __name__ == "__main__":
    main()
