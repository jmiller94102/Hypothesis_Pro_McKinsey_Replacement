"""LLM-powered generators for problem-specific tree content.

These generators use Gemini via google.genai client to create customized L2 branches
and L3 leaves that are specific to the problem statement and incorporate
research context.
"""

import json
import os
from typing import Dict, List, Optional

import google.genai as genai


def _cleanup_label(label: str, max_words: int = 6) -> str:
    """
    Clean up LLM-generated labels to enforce conciseness rules.

    Rules:
    - Remove common verbose prefixes/suffixes
    - Truncate to max_words (default: 6)
    - Remove vendor names
    - Capitalize properly

    Args:
        label: Original label from LLM
        max_words: Maximum number of words allowed (default: 6)

    Returns:
        str: Cleaned, concise label
    """
    # Remove common verbose patterns (case-insensitive)
    # Target: 3-6 words (balanced conciseness without losing meaning)
    verbose_patterns = [
        # Remove only the most verbose prefixes
        ("Improvement in ", ""),
        ("Reduction in ", ""),
        ("Enhancement of ", ""),
        ("Assessment of ", ""),
        ("Evaluation of ", ""),
        ("Analysis of ", ""),

        # Remove overly specific suffixes
        (" with Computer Vision", ""),
        (" Requiring Medical Intervention", ""),
        (" Due to Fall Response", ""),
        (" from Direct Incident Response", ""),
        (" Based on Real-time Needs", ""),

        # Keep meaningful words but remove redundancy
        (" and Scalability Potential", ""),  # "Scalability" alone is clear
        (" and Accuracy", ""),  # "Robustness" alone is clear
    ]

    cleaned = label
    for pattern, replacement in verbose_patterns:
        # Case-insensitive replacement
        import re
        cleaned = re.sub(re.escape(pattern), replacement, cleaned, flags=re.IGNORECASE)

    # Truncate to max_words
    words = cleaned.split()
    if len(words) > max_words:
        cleaned = " ".join(words[:max_words])

    # Remove trailing "and", "or", "&" if they're the last word
    words = cleaned.split()
    if words and words[-1].lower() in ["and", "or", "&"]:
        words = words[:-1]
        cleaned = " ".join(words)

    # Clean up any double spaces
    cleaned = " ".join(cleaned.split())

    # Capitalize properly (preserve acronyms like "AI")
    return cleaned.strip()


def generate_problem_specific_l3_leaves(
    l1_category: str,
    l1_question: str,
    l2_branch: str,
    l2_question: str,
    problem_statement: str,
    market_research: Optional[str] = None,
    competitor_research: Optional[str] = None,
    num_leaves: int = 3,
    model_name: str = "gemini-2.5-flash",
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

**Task:** Generate {num_leaves} problem-specific L3 leaves (hypotheses) that follow MECE principles.

**CRITICAL Label/Question Rules:**

1. **Labels**: Concise key phrases (2-4 words max), NO vendor names, NO specific numbers
   - ✓ Good: "Fall Incident Reduction", "Response Time Improvement", "Injury Severity Reduction"
   - ✗ Bad: "Resident-Reported Fear via Teton.ai", "Fall Detection Using X Vendor", "30% Fall Reduction"

2. **Questions**: Clean, simple questions about the metric (1 sentence max), NO vendor names
   - ✓ Good: "What is the measured reduction in fall incidents?"
   - ✗ Bad: Long paragraphs with vendor references

3. **Targets**: Include benchmarks, numbers, and citations HERE (not in labels)
   - ✓ Good: ">25% reduction vs baseline (KLAS 2024 benchmark)"

4. **Data Sources**: Put vendor names and specific studies HERE (not in labels/questions)
   - ✓ Good: "Pilot incident logs, Teton.ai case study, KLAS 2024 report"

**Output Format (JSON):**
Return a JSON array with {num_leaves} objects, each containing:
- "label": Concise key phrase (2-4 words, NO vendors)
- "question": Simple question (1 sentence, NO vendors)
- "metric_type": One of ["quantitative", "qualitative", "binary"]
- "target": Specific target with benchmark citations
- "data_source": Specific sources including vendor case studies
- "assessment_criteria": How to evaluate

**Example for "fall detection" problem:**
```json
[
  {{
    "label": "Fall Incident Reduction",
    "question": "What is the measured reduction in fall incidents?",
    "metric_type": "quantitative",
    "target": ">25% reduction vs baseline (KLAS 2024 Fall Management benchmark)",
    "data_source": "Pilot incident logs, ER visit logs, Teton.ai case study",
    "assessment_criteria": "Compare pre/post incident rates, validate against KLAS benchmark"
  }}
]
```

**CRITICAL - Remember:**
- Labels: 2-4 words, NO vendors, NO numbers (e.g., "Fall Incident Reduction")
- Questions: Simple, 1 sentence, NO vendors (e.g., "What is the measured reduction?")
- Targets: Include benchmarks and numbers HERE
- Data sources: Include vendor names and studies HERE

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

        # Clean up labels and add IDs and status fields
        for i, leaf in enumerate(leaves):
            # CRITICAL: Enforce label conciseness (max 6 words)
            if "label" in leaf:
                leaf["label"] = _cleanup_label(leaf["label"], max_words=6)

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
    model_name: str = "gemini-2.5-flash",
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

**Task:** Generate {num_branches} problem-specific L2 branches following MECE principles.

**CRITICAL Label/Question Rules:**

1. **Labels**: Concise phrases (2-5 words), descriptive but not overly specific, NO vendor names
   - ✓ Good: "Clinical Impact", "Financial Impact", "Stakeholder Value"
   - ✗ Bad: "Teton.ai Clinical Results", "30% Cost Reduction Analysis"

2. **Questions**: Clean, focused questions (1 sentence), NO vendor names
   - ✓ Good: "Does it meaningfully improve resident outcomes?"
   - ✗ Bad: Long paragraphs or vendor-specific questions

**MECE Requirements:**
1. **Mutually Exclusive** - No overlap between branches
2. **Collectively Exhaustive** - Cover all important aspects of the L1 category
3. **Problem-Specific** - Tailored to this specific question
4. **Actionable** - Each branch analyzable with available data

**Output Format (JSON):**
Return a JSON object where keys are branch identifiers (UPPERCASE_SNAKE_CASE) and values contain:
- "label": Concise phrase (2-5 words, NO vendors)
- "question": Clean, focused question (1 sentence, NO vendors)

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

**CRITICAL - Remember:**
- Labels: 2-5 words, descriptive, NO vendors (e.g., "Clinical Impact")
- Questions: 1 sentence, focused, NO vendors
- Ensure MECE compliance (no overlap, full coverage)
- Reflect problem domain, not generic categories

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

        # Clean up L2 branch labels (max 6 words)
        for branch_key, branch_data in branches.items():
            if "label" in branch_data:
                branch_data["label"] = _cleanup_label(branch_data["label"], max_words=6)

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
