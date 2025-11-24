"""LLM-powered generators for problem-specific tree content.

These generators use Gemini via google.genai client to create customized L2 branches
and L3 leaves that are specific to the problem statement and incorporate
research context.
"""

import json
import os
from typing import Dict, List, Optional

import google.genai as genai


def generate_problem_specific_l3_leaves(
    l1_category: str,
    l1_question: str,
    l2_branch: str,
    l2_question: str,
    problem_statement: str,
    market_research: Optional[str] = None,
    competitor_research: Optional[str] = None,
    num_leaves: int = 3,
    model_name: str = "gemini-2.5-flash-lite",
) -> List[Dict]:
    """
    Generate problem-specific L3 leaves using LLM with research context.

    Args:
        l1_category: L1 category label (e.g., "DESIRABILITY")
        l1_question: L1 question (e.g., "Is it worth doing?")
        l2_branch: L2 branch label (e.g., "Clinical/Safety Impact")
        l2_question: L2 question (e.g., "Does it improve outcomes?")
        problem_statement: The strategic question being analyzed
        market_research: Market research context (optional)
        competitor_research: Competitive analysis context (optional)
        num_leaves: Number of L3 leaves to generate (default: 3)
        model_name: Gemini model to use

    Returns:
        list: List of L3 leaf dictionaries with problem-specific content
    """
    # Build context section
    context_section = ""
    if market_research:
        context_section += f"\n**Market Research Context:**\n{market_research}\n"
    if competitor_research:
        context_section += f"\n**Competitor Research Context:**\n{competitor_research}\n"

    prompt = f"""You are a senior strategy consultant generating specific, measurable hypotheses for a strategic decision tree.

**Strategic Question:** {problem_statement}

**Tree Context:**
- L1 Category: {l1_category}
  Question: {l1_question}
- L2 Branch: {l2_branch}
  Question: {l2_question}
{context_section}

**Task:** Generate {num_leaves} problem-specific L3 leaves (hypotheses) that:

1. **Are highly specific to this problem statement** - NOT generic templates
2. **Reference specific data from research context** when setting targets and data sources
3. **Use industry benchmarks** from the research to set realistic targets
4. **Mention specific vendors/competitors** when relevant (e.g., "Teton.ai integration capability")
5. **Are measurable and testable** with clear success criteria

**Output Format (JSON):**
Return a JSON array with {num_leaves} objects, each containing:
- "label": Specific hypothesis label (e.g., "Fall-Related ER Visit Reduction")
- "question": Specific, answerable question (e.g., "Does it reduce fall-related ER visits by >30%?")
- "metric_type": One of ["quantitative", "qualitative", "binary"]
- "target": Specific target with benchmark citation if available (e.g., ">30% reduction per KLAS 2024 study")
- "data_source": Specific data source (e.g., "ER visit logs, incident reports, Teton.ai case study")
- "assessment_criteria": How to evaluate this hypothesis (be specific)

**Example for "fall detection" problem:**
```json
[
  {{
    "label": "Fall-Related Hospitalization Reduction",
    "question": "Does fall detection reduce hospitalization rates from fall-related injuries?",
    "metric_type": "quantitative",
    "target": "30-40% reduction in fall-related ER visits (KLAS 2024 Fall Management benchmark)",
    "data_source": "Incident reports from pilot study, ER visit logs, competitor case study from Teton.ai deployment",
    "assessment_criteria": "Compare pre/post hospitalization rates, validate against KLAS benchmark, review incident report trends"
  }}
]
```

**CRITICAL:**
- Do NOT use generic questions like "What is the X?"
- DO reference specific elements from the problem statement
- DO use benchmarks from research context when available
- DO mention specific vendors/products from competitor research
- DO make targets specific and measurable

Return ONLY the JSON array, no other text."""

    # Initialize client
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    # Generate content
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
    )

    # Parse JSON response
    try:
        # Extract response text
        response_text = response.text.strip()

        # Extract JSON from response (handle markdown code blocks if present)
        if response_text.startswith("```json"):
            response_text = response_text[7:]  # Remove ```json
        if response_text.startswith("```"):
            response_text = response_text[3:]  # Remove ```
        if response_text.endswith("```"):
            response_text = response_text[:-3]  # Remove ```
        response_text = response_text.strip()

        leaves = json.loads(response_text)

        # Add IDs and status fields
        for i, leaf in enumerate(leaves):
            leaf["id"] = f"L3_{i+1:03d}"
            leaf["status"] = "UNTESTED"
            leaf["confidence"] = None
            leaf["components"] = []

        return leaves

    except (json.JSONDecodeError, AttributeError) as e:
        # Fallback: return generic structure if LLM fails
        print(f"Warning: Failed to parse LLM response as JSON: {e}")
        print(f"Response was: {response}")
        return _generate_fallback_l3_leaves(l2_branch, num_leaves)


def generate_problem_specific_l2_branches(
    l1_category: str,
    l1_question: str,
    l1_description: str,
    problem_statement: str,
    market_research: Optional[str] = None,
    competitor_research: Optional[str] = None,
    num_branches: int = 3,
    model_name: str = "gemini-2.5-flash-lite",
) -> Dict[str, Dict]:
    """
    Generate problem-specific L2 branches using LLM with research context.

    Args:
        l1_category: L1 category label (e.g., "DESIRABILITY")
        l1_question: L1 question (e.g., "Is it worth doing?")
        l1_description: L1 description
        problem_statement: The strategic question being analyzed
        market_research: Market research context (optional)
        competitor_research: Competitive analysis context (optional)
        num_branches: Number of L2 branches to generate (default: 3)
        model_name: Gemini model to use

    Returns:
        dict: Dictionary of L2 branches keyed by branch_key
    """
    # Build context section
    context_section = ""
    if market_research:
        context_section += f"\n**Market Research Context:**\n{market_research}\n"
    if competitor_research:
        context_section += f"\n**Competitor Research Context:**\n{competitor_research}\n"

    prompt = f"""You are a senior strategy consultant generating problem-specific analysis dimensions for a strategic decision tree.

**Strategic Question:** {problem_statement}

**L1 Category:** {l1_category}
- Question: {l1_question}
- Description: {l1_description}
{context_section}

**Task:** Generate {num_branches} problem-specific L2 branches that decompose the L1 category into distinct analysis dimensions.

**Requirements:**
1. **Mutually Exclusive** - No overlap between branches
2. **Collectively Exhaustive** - Cover all important aspects of the L1 category
3. **Problem-Specific** - NOT generic templates, but tailored to this specific question
4. **Actionable** - Each branch should be analyzable with available data

**Output Format (JSON):**
Return a JSON object where keys are branch identifiers (UPPERCASE_SNAKE_CASE) and values contain:
- "label": Branch label (e.g., "Patient Safety Impact")
- "question": Specific question this branch answers (e.g., "Does it reduce patient injury rates?")

**Example for "fall detection" problem under DESIRABILITY:**
```json
{{
  "PATIENT_SAFETY_IMPACT": {{
    "label": "Patient Safety Impact",
    "question": "Does fall detection meaningfully reduce injury rates and severity?"
  }},
  "OPERATIONAL_EFFICIENCY": {{
    "label": "Operational Efficiency",
    "question": "Does it reduce staff burden and improve response workflow?"
  }},
  "STAKEHOLDER_CONFIDENCE": {{
    "label": "Stakeholder Confidence",
    "question": "Does it increase family trust and resident peace of mind?"
  }}
}}
```

**CRITICAL:**
- Branch labels should reflect the problem domain (e.g., "Patient Safety" not just "Safety")
- Questions should be specific to the problem statement
- Use insights from research context to identify relevant dimensions
- Ensure MECE compliance (no overlap, full coverage)

Return ONLY the JSON object, no other text."""

    # Initialize client
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    # Generate content
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
    )

    # Parse JSON response
    try:
        # Extract response text
        response_text = response.text.strip()

        # Extract JSON from response (handle markdown code blocks if present)
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        branches = json.loads(response_text)
        return branches

    except (json.JSONDecodeError, AttributeError) as e:
        # Fallback: return generic structure if LLM fails
        print(f"Warning: Failed to parse LLM response as JSON: {e}")
        print(f"Response was: {response}")
        return _generate_fallback_l2_branches(l1_category, num_branches)


def _generate_fallback_l3_leaves(l2_branch: str, num_leaves: int) -> List[Dict]:
    """Generate generic fallback L3 leaves if LLM fails."""
    leaves = []
    for i in range(num_leaves):
        leaves.append({
            "id": f"L3_{i+1:03d}",
            "label": f"{l2_branch} Factor {i+1}",
            "question": f"What is the impact of {l2_branch.lower()} factor {i+1}?",
            "metric_type": "qualitative",
            "target": "Positive assessment from stakeholders",
            "data_source": f"{l2_branch} data and analysis",
            "status": "UNTESTED",
            "confidence": None,
            "components": [],
            "assessment_criteria": f"Evaluate {l2_branch.lower()} factor {i+1} against target",
        })
    return leaves


def _generate_fallback_l2_branches(l1_category: str, num_branches: int) -> Dict[str, Dict]:
    """Generate generic fallback L2 branches if LLM fails."""
    branches = {}
    for i in range(num_branches):
        key = f"{l1_category}_ANALYSIS_{i+1}"
        branches[key] = {
            "label": f"{l1_category} Analysis {i+1}",
            "question": f"What are the key {l1_category.lower()} considerations for aspect {i+1}?",
        }
    return branches
