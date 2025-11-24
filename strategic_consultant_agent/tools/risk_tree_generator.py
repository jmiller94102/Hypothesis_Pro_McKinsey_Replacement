"""Risk assessment tree generator with probability-impact scoring."""

import json
import os
from typing import Dict, List, Optional

from google import genai

from strategic_consultant_agent.tools.hypothesis_tree import generate_hypothesis_tree


def generate_risk_assessment_tree(
    problem: str,
    market_research: Optional[str] = None,
    competitor_research: Optional[str] = None,
    use_llm_generation: bool = True,
    model_name: str = "gemini-2.5-flash",
) -> Dict:
    """
    Generate a risk assessment tree with probability-impact scoring.

    Args:
        problem: The strategic question or initiative to assess
        market_research: Market research context (optional)
        competitor_research: Competitive analysis context (optional)
        use_llm_generation: If True, use LLM for risk-specific generation (default: True)
        model_name: Gemini model to use

    Returns:
        dict: Risk assessment tree with probability/impact scores on L3 leaves
    """
    # Generate base tree using risk_assessment framework
    tree = generate_hypothesis_tree(
        problem=problem,
        framework="risk_assessment",
        market_research=market_research,
        competitor_research=competitor_research,
        use_llm_generation=use_llm_generation,
    )

    # Add risk-specific metadata
    tree["risk_scoring"] = {
        "probability_scale": {
            "1": "Very Low (0-10%)",
            "2": "Low (10-30%)",
            "3": "Medium (30-50%)",
            "4": "High (50-70%)",
            "5": "Very High (70-100%)",
        },
        "impact_scale": {
            "1": "Negligible",
            "2": "Minor",
            "3": "Moderate",
            "4": "Major",
            "5": "Critical",
        },
        "risk_score": "Probability (1-5) × Impact (1-5) = Risk Score (1-25)",
    }

    # Enhance L3 leaves with probability/impact scores if using LLM
    if use_llm_generation and (market_research or competitor_research):
        tree = _add_risk_scores_to_leaves(
            tree=tree,
            problem=problem,
            market_research=market_research,
            competitor_research=competitor_research,
            model_name=model_name,
        )

    return tree


def _add_risk_scores_to_leaves(
    tree: Dict,
    problem: str,
    market_research: Optional[str],
    competitor_research: Optional[str],
    model_name: str,
) -> Dict:
    """
    Add probability and impact scores to L3 risk leaves using LLM.

    Args:
        tree: The risk assessment tree
        problem: The strategic question
        market_research: Market context
        competitor_research: Competitive context
        model_name: Model to use

    Returns:
        dict: Tree with risk scores added to L3 leaves
    """
    # Build context
    context_section = ""
    if market_research:
        context_section += f"\n**Market Research:**\n{market_research}\n"
    if competitor_research:
        context_section += f"\n**Competitor Research:**\n{competitor_research}\n"

    # Process each L1 category
    for l1_key, l1_data in tree["tree"].items():
        for l2_key, l2_data in l1_data.get("L2_branches", {}).items():
            l3_leaves = l2_data.get("L3_leaves", [])

            if not l3_leaves:
                continue

            # Prepare leaves for scoring
            leaves_for_scoring = [
                {
                    "id": leaf["id"],
                    "label": leaf["label"],
                    "question": leaf["question"],
                }
                for leaf in l3_leaves
            ]

            # Generate scores using LLM
            scored_leaves = _generate_risk_scores_llm(
                problem=problem,
                l1_category=l1_data["label"],
                l2_branch=l2_data["label"],
                leaves=leaves_for_scoring,
                context=context_section,
                model_name=model_name,
            )

            # Update leaves with scores
            for i, leaf in enumerate(l3_leaves):
                if i < len(scored_leaves):
                    scored_leaf = scored_leaves[i]
                    leaf["probability"] = scored_leaf.get("probability", 3)
                    leaf["impact"] = scored_leaf.get("impact", 3)
                    leaf["risk_score"] = leaf["probability"] * leaf["impact"]
                    leaf["mitigation"] = scored_leaf.get("mitigation", "Develop mitigation plan")
                else:
                    # Fallback scores
                    leaf["probability"] = 3
                    leaf["impact"] = 3
                    leaf["risk_score"] = 9
                    leaf["mitigation"] = "Develop mitigation plan"

    return tree


def _generate_risk_scores_llm(
    problem: str,
    l1_category: str,
    l2_branch: str,
    leaves: List[Dict],
    context: str,
    model_name: str,
) -> List[Dict]:
    """
    Use LLM to generate probability, impact, and mitigation for risk leaves.

    Args:
        problem: Strategic question
        l1_category: L1 category label
        l2_branch: L2 branch label
        leaves: List of leaves to score
        context: Research context
        model_name: Model to use

    Returns:
        list: Leaves with probability, impact, and mitigation added
    """
    prompt = f"""You are a senior risk analyst assessing strategic risks.

**Strategic Question/Initiative:** {problem}

**Risk Category:** {l1_category} > {l2_branch}

**Context:**{context}

**Risks to Assess:**
{json.dumps(leaves, indent=2)}

**Task:** For each risk, assess:

1. **Probability** (1-5):
   - 1 = Very Low (0-10%)
   - 2 = Low (10-30%)
   - 3 = Medium (30-50%)
   - 4 = High (50-70%)
   - 5 = Very High (70-100%)

2. **Impact** (1-5):
   - 1 = Negligible
   - 2 = Minor
   - 3 = Moderate
   - 4 = Major
   - 5 = Critical

3. **Mitigation**: Specific, actionable mitigation strategy

**Output Format (JSON):**
Return a JSON array with one object per risk:

```json
[
  {{
    "id": "L3_001",
    "probability": 4,
    "impact": 5,
    "mitigation": "Specific mitigation strategy based on context"
  }}
]
```

**CRITICAL:**
- Base scores on the problem context and research insights
- Mitigation should be specific and actionable
- Consider industry-specific factors from research

Return ONLY the JSON array, no other text."""

    try:
        # Initialize client
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

        # Generate content
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )

        # Parse JSON
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        scored_leaves = json.loads(response_text)
        return scored_leaves

    except Exception as e:
        print(f"Warning: Failed to generate risk scores: {e}")
        # Fallback: return default scores
        return [
            {
                "id": leaf["id"],
                "probability": 3,
                "impact": 3,
                "mitigation": "Develop comprehensive mitigation plan",
            }
            for leaf in leaves
        ]


def generate_risk_matrix(tree: Dict) -> Dict:
    """
    Generate a 2x2 (actually 5x5) probability-impact matrix from risk tree.

    Args:
        tree: Risk assessment tree with scored leaves

    Returns:
        dict: Risk matrix with quadrant assignments
    """
    # Collect all risks with scores
    all_risks = []

    for l1_key, l1_data in tree["tree"].items():
        for l2_key, l2_data in l1_data.get("L2_branches", {}).items():
            for leaf in l2_data.get("L3_leaves", []):
                if "probability" in leaf and "impact" in leaf:
                    all_risks.append({
                        "id": leaf["id"],
                        "label": leaf["label"],
                        "category": f"{l1_data['label']} > {l2_data['label']}",
                        "probability": leaf["probability"],
                        "impact": leaf["impact"],
                        "risk_score": leaf["risk_score"],
                        "mitigation": leaf.get("mitigation", ""),
                    })

    # Sort by risk score (descending)
    all_risks.sort(key=lambda x: x["risk_score"], reverse=True)

    # Categorize into quadrants
    critical_risks = [r for r in all_risks if r["probability"] >= 4 and r["impact"] >= 4]
    high_priority = [r for r in all_risks if r["risk_score"] >= 12 and r not in critical_risks]
    monitor = [r for r in all_risks if 6 <= r["risk_score"] < 12]
    low_priority = [r for r in all_risks if r["risk_score"] < 6]

    return {
        "matrix_type": "probability_impact",
        "total_risks": len(all_risks),
        "quadrants": {
            "critical": {
                "label": "CRITICAL (High Probability, High Impact)",
                "criteria": "Probability ≥4 AND Impact ≥4",
                "action": "Immediate mitigation required",
                "risks": critical_risks,
                "count": len(critical_risks),
            },
            "high_priority": {
                "label": "HIGH PRIORITY (Risk Score ≥12)",
                "criteria": "Probability × Impact ≥ 12",
                "action": "Develop detailed mitigation plans",
                "risks": high_priority,
                "count": len(high_priority),
            },
            "monitor": {
                "label": "MONITOR (Risk Score 6-11)",
                "criteria": "6 ≤ Probability × Impact < 12",
                "action": "Monitor and prepare contingencies",
                "risks": monitor,
                "count": len(monitor),
            },
            "low_priority": {
                "label": "LOW PRIORITY (Risk Score <6)",
                "criteria": "Probability × Impact < 6",
                "action": "Accept or monitor passively",
                "risks": low_priority,
                "count": len(low_priority),
            },
        },
        "top_risks": all_risks[:10],  # Top 10 risks by score
    }
