"""LLM-powered generators for problem-specific tree content.

These generators use Gemini via google.genai client to create customized L2 branches
and L3 leaves that are specific to the problem statement and incorporate
research context.
"""

import json
import os
from typing import Dict, List, Optional, Any, Tuple

from google import genai


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


def generate_l1_category_batch(
    l1_key: str,
    l1_data: Dict[str, Any],
    problem_statement: str,
    market_research: Optional[str] = None,
    competitor_research: Optional[str] = None,
    num_leaves_per_branch: int = 3,
    model_name: str = "gemini-2.5-flash",
) -> Dict[str, List[Dict]]:
    """
    Generate all L3 leaves for a single L1 category in one LLM call.

    This batches by L1 category: 3 calls for scale_decision (DESIRABILITY, FEASIBILITY, VIABILITY).
    Much faster than 9 sequential calls, and more manageable than 1 giant call.

    Args:
        l1_key: L1 category identifier (e.g., "DESIRABILITY")
        l1_data: L1 category data including label, question, and L2 branches
        problem_statement: The strategic question being analyzed
        market_research: Market research context (optional)
        competitor_research: Competitive analysis context (optional)
        num_leaves_per_branch: Number of L3 leaves per L2 branch (default: 3)
        model_name: Gemini model to use

    Returns:
        dict: {L2_key: [L3_leaves]} for this L1 category
    """
    # Build context section
    context_section = ""
    if market_research:
        context_section += f"\n**Market Research Context:**\n{market_research}\n"
    if competitor_research:
        context_section += f"\n**Competitor Research Context:**\n{competitor_research}\n"

    # Build L2 branch structure for this L1
    l1_label = l1_data.get("label", l1_key)
    l1_question = l1_data.get("question", "")
    l1_description = l1_data.get("description", "")

    l2_structure = []
    for l2_key, l2_data in l1_data.get("L2_branches", {}).items():
        l2_label = l2_data.get("label", l2_key)
        l2_question = l2_data.get("question", "")
        l2_structure.append(f"  - **{l2_key}**: {l2_label}")
        l2_structure.append(f"    Question: {l2_question}")

    l2_structure_text = "\n".join(l2_structure)

    prompt = f"""You are a senior strategy consultant generating problem-specific L3 hypotheses for a strategic decision tree.

**Strategic Question:** {problem_statement}

**L1 Category:** {l1_key} - {l1_label}
- Question: {l1_question}
- Description: {l1_description}

**L2 Branches in this category:**
{l2_structure_text}
{context_section}

**Task:** For EACH L2 branch, determine how many L3 leaves (3-7) are needed for MECE completeness, then generate them.

**CRITICAL Requirements:**

1. **Adaptive Leaf Count**: Generate 3-7 L3 leaves per L2 branch based on problem complexity
   - Simple aspects: 3-4 leaves may suffice
   - Complex aspects: 5-7 leaves may be needed for completeness
   - **MECE**: Leaves must be Mutually Exclusive and Collectively Exhaustive

2. **Label Rules**: Concise key phrases (3-6 words), NO vendor names, NO specific numbers
   - ✓ Good: "Fall Incident Reduction", "Response Time Improvement", "Care Workflow Efficiency"
   - ✗ Bad: "Resident-Reported Fear via Teton.ai", "30% Fall Reduction"

3. **Question Rules**: Clean, simple questions (1 sentence max), NO vendor names
   - ✓ Good: "What is the measured reduction in fall incidents?"
   - ✗ Bad: Long paragraphs with vendor references

4. **Targets**: Include benchmarks and citations HERE (not in labels)
   - ✓ Good: ">25% reduction vs baseline (KLAS 2024 benchmark)"

5. **Data Sources**: Put vendor names HERE (not in labels/questions)
   - ✓ Good: "Pilot logs, Teton.ai case study, KLAS 2024 report"

**Output Format (JSON):**
Return a JSON object where:
- Keys are L2_branch identifiers (from the list above)
- Values are arrays of 3-7 L3 leaf objects (you decide the count for MECE completeness)

Each L3 leaf must contain:
- "label": Concise key phrase (3-6 words, NO vendors)
- "question": Simple question (1 sentence, NO vendors)
- "metric_type": One of ["quantitative", "qualitative", "binary"]
- "target": Specific target with benchmark citations
- "data_source": Specific sources including vendor studies
- "assessment_criteria": How to evaluate

**Example structure:**
```json
{{
  "L2_BRANCH_1": [
    {{
      "label": "Fall Incident Reduction",
      "question": "What is the measured reduction in fall incidents?",
      "metric_type": "quantitative",
      "target": ">25% reduction vs baseline (KLAS 2024)",
      "data_source": "Pilot logs, ER visit logs, vendor case studies",
      "assessment_criteria": "Compare pre/post incident rates"
    }},
    ... (2-6 more leaves based on completeness needs)
  ],
  "L2_BRANCH_2": [ ... (3-7 leaves based on complexity) ... ],
  ...
}}
```

**CRITICAL - Remember:**
- Decide leaf count (3-7) based on MECE completeness
- Labels: 3-6 words, NO vendors, NO numbers
- Questions: Simple, 1 sentence, NO vendors
- Ensure MECE compliance within each L2 branch

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

        # Extract JSON from response (handle markdown code blocks)
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        l2_leaves = json.loads(response_text)

        # Clean up labels and add IDs and status fields
        leaf_counter = 1
        for l2_key, leaves in l2_leaves.items():
            for leaf in leaves:
                # CRITICAL: Enforce label conciseness (max 6 words)
                if "label" in leaf:
                    leaf["label"] = _cleanup_label(leaf["label"], max_words=6)

                leaf["id"] = f"L3_{leaf_counter:03d}"
                leaf["status"] = "UNTESTED"
                leaf["confidence"] = None
                leaf["components"] = []
                leaf_counter += 1

        return l2_leaves

    except (json.JSONDecodeError, AttributeError, KeyError) as e:
        # Fallback: return empty structure
        print(f"Warning: Failed to parse L1-batched LLM response for {l1_key}: {e}")
        print(f"Response was: {response}")
        return {}


def generate_entire_tree_l3_leaves_batch(
    framework_structure: Dict[str, Any],
    problem_statement: str,
    market_research: Optional[str] = None,
    competitor_research: Optional[str] = None,
    num_leaves_per_branch: int = 3,
    model_name: str = "gemini-2.5-flash",
) -> Dict[str, Dict[str, List[Dict]]]:
    """
    Generate ALL L3 leaves for the entire tree, batched by L1 category.

    This makes 3 LLM calls (one per L1) instead of 9 (one per L2).
    Better balance: smaller prompts than full-tree batch, but still much faster than sequential.

    Args:
        framework_structure: The framework template with L1 categories and L2 branches
        problem_statement: The strategic question being analyzed
        market_research: Market research context (optional)
        competitor_research: Competitive analysis context (optional)
        num_leaves_per_branch: Number of L3 leaves per L2 branch (default: 3)
        model_name: Gemini model to use

    Returns:
        dict: Nested dict structure {L1_key: {L2_key: [L3_leaves]}}
    """
    # Generate L3 leaves for each L1 category (can be parallelized)
    all_leaves = {}

    for l1_key, l1_data in framework_structure.items():
        l2_leaves = generate_l1_category_batch(
            l1_key=l1_key,
            l1_data=l1_data,
            problem_statement=problem_statement,
            market_research=market_research,
            competitor_research=competitor_research,
            num_leaves_per_branch=num_leaves_per_branch,
            model_name=model_name,
        )
        all_leaves[l1_key] = l2_leaves

    return all_leaves


def generate_entire_tree_l3_leaves_batch_OLD(
    framework_structure: Dict[str, Any],
    problem_statement: str,
    market_research: Optional[str] = None,
    competitor_research: Optional[str] = None,
    num_leaves_per_branch: int = 3,
    model_name: str = "gemini-2.5-flash",
) -> Dict[str, Dict[str, List[Dict]]]:
    """
    OLD VERSION: Generate ALL L3 leaves for the entire tree in a single batched LLM call.

    This was too slow (~142s) because the prompt was too large.
    Keeping for reference.

    Args:
        framework_structure: The framework template with L1 categories and L2 branches
        problem_statement: The strategic question being analyzed
        market_research: Market research context (optional)
        competitor_research: Competitive analysis context (optional)
        num_leaves_per_branch: Number of L3 leaves per L2 branch (default: 3)
        model_name: Gemini model to use

    Returns:
        dict: Nested dict structure {L1_key: {L2_key: [L3_leaves]}}
    """
    # Build context section
    context_section = ""
    if market_research:
        context_section += f"\n**Market Research Context:**\n{market_research}\n"
    if competitor_research:
        context_section += f"\n**Competitor Research Context:**\n{competitor_research}\n"

    # Build tree structure description for prompt
    tree_structure = []
    for l1_key, l1_data in framework_structure.items():
        l1_label = l1_data.get("label", l1_key)
        l1_question = l1_data.get("question", "")

        tree_structure.append(f"\n### {l1_key}: {l1_label}")
        tree_structure.append(f"Question: {l1_question}")
        tree_structure.append("L2 Branches:")

        for l2_key, l2_data in l1_data.get("L2_branches", {}).items():
            l2_label = l2_data.get("label", l2_key)
            l2_question = l2_data.get("question", "")
            tree_structure.append(f"  - {l2_key}: {l2_label}")
            tree_structure.append(f"    Question: {l2_question}")

    tree_structure_text = "\n".join(tree_structure)

    prompt = f"""You are a senior strategy consultant generating a complete MECE hypothesis tree for strategic decision-making.

**Strategic Question:** {problem_statement}

**Framework Structure:**{tree_structure_text}
{context_section}

**Task:** Generate {num_leaves_per_branch} problem-specific L3 leaves (testable hypotheses) for EACH L2 branch in the tree above.

**CRITICAL Label/Question Rules:**

1. **Labels**: Concise key phrases (3-6 words), NO vendor names, NO specific numbers
   - ✓ Good: "Fall Incident Reduction", "Response Time Improvement", "Care Workflow Efficiency"
   - ✗ Bad: "Resident-Reported Fear via Teton.ai", "Fall Detection Using X Vendor", "30% Fall Reduction"

2. **Questions**: Clean, simple questions about the metric (1 sentence max), NO vendor names
   - ✓ Good: "What is the measured reduction in fall incidents?"
   - ✗ Bad: Long paragraphs with vendor references

3. **Targets**: Include benchmarks, numbers, and citations HERE (not in labels)
   - ✓ Good: ">25% reduction vs baseline (KLAS 2024 benchmark)"

4. **Data Sources**: Put vendor names and specific studies HERE (not in labels/questions)
   - ✓ Good: "Pilot incident logs, Teton.ai case study, KLAS 2024 report"

**MECE Requirements:**
- Within each L2 branch, the {num_leaves_per_branch} L3 leaves must be Mutually Exclusive (no overlap) and Collectively Exhaustive (cover all key aspects)
- Ensure leaves are specific to the problem statement and informed by the research context

**Output Format (JSON):**
Return a JSON object where:
- Keys are L1_category identifiers (e.g., "DESIRABILITY", "FEASIBILITY", "VIABILITY")
- Values are objects with L2_branch identifiers as keys
- Each L2 branch maps to an array of {num_leaves_per_branch} L3 leaf objects

Each L3 leaf object must contain:
- "label": Concise key phrase (3-6 words, NO vendors)
- "question": Simple question (1 sentence, NO vendors)
- "metric_type": One of ["quantitative", "qualitative", "binary"]
- "target": Specific target with benchmark citations
- "data_source": Specific sources including vendor case studies
- "assessment_criteria": How to evaluate

**Example structure:**
```json
{{
  "DESIRABILITY": {{
    "RESIDENT_HEALTH_OUTCOMES": [
      {{
        "label": "Fall Incident Reduction",
        "question": "What is the measured reduction in fall incidents?",
        "metric_type": "quantitative",
        "target": ">25% reduction vs baseline (KLAS 2024 benchmark)",
        "data_source": "Pilot incident logs, ER visit logs, vendor case studies",
        "assessment_criteria": "Compare pre/post incident rates against benchmark"
      }},
      ... {num_leaves_per_branch - 1} more leaves
    ]
  }},
  "FEASIBILITY": {{
    "TECHNICAL_SCALABILITY": [ ... {num_leaves_per_branch} leaves ... ]
  }},
  ...
}}
```

**CRITICAL - Remember:**
- Labels: 3-6 words, NO vendors, NO numbers
- Questions: Simple, 1 sentence, NO vendors
- Targets: Include benchmarks and numbers HERE
- Data sources: Include vendor names and studies HERE
- Ensure MECE compliance within each L2 branch
- Generate {num_leaves_per_branch} leaves for EVERY L2 branch

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

        all_leaves = json.loads(response_text)

        # Clean up labels and add IDs and status fields
        leaf_counter = 1
        for l1_key, l2_branches in all_leaves.items():
            for l2_key, leaves in l2_branches.items():
                for leaf in leaves:
                    # CRITICAL: Enforce label conciseness (max 6 words)
                    if "label" in leaf:
                        leaf["label"] = _cleanup_label(leaf["label"], max_words=6)

                    leaf["id"] = f"L3_{leaf_counter:03d}"
                    leaf["status"] = "UNTESTED"
                    leaf["confidence"] = None
                    leaf["components"] = []
                    leaf_counter += 1

        return all_leaves

    except (json.JSONDecodeError, AttributeError, KeyError) as e:
        # Fallback: return empty structure and log error
        print(f"Warning: Failed to parse batched LLM response: {e}")
        print(f"Response was: {response}")
        return {}


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


def generate_entire_tree_l2_branches_batch(
    framework_structure: Dict[str, Any],
    problem_statement: str,
    market_research: Optional[str] = None,
    competitor_research: Optional[str] = None,
    model_name: str = "gemini-2.5-flash",
) -> Dict[str, Dict[str, Dict]]:
    """
    Generate ALL L2 branches for the entire tree in a single batched LLM call.

    This generates context-aware L2 branch labels and questions that match
    the problem domain, ensuring consistency with L3 leaves.

    Args:
        framework_structure: The framework template with L1 categories
        problem_statement: The strategic question being analyzed
        market_research: Market research context (optional)
        competitor_research: Competitive analysis context (optional)
        model_name: Gemini model to use

    Returns:
        dict: Nested dict structure {L1_key: {L2_key: {"label": ..., "question": ...}}}
    """
    # Build context section
    context_section = ""
    if market_research:
        context_section += f"\n**Market Research Context:**\n{market_research}\n"
    if competitor_research:
        context_section += f"\n**Competitor Research Context:**\n{competitor_research}\n"

    # Build framework structure description
    framework_desc = []
    for l1_key, l1_data in framework_structure.items():
        l1_label = l1_data.get("label", l1_key)
        l1_question = l1_data.get("question", "")
        l1_description = l1_data.get("description", "")

        framework_desc.append(f"\n### {l1_key}: {l1_label}")
        framework_desc.append(f"Question: {l1_question}")
        framework_desc.append(f"Description: {l1_description}")

    framework_desc_text = "\n".join(framework_desc)

    prompt = f"""You are a senior strategy consultant generating problem-specific L2 branches for a strategic decision tree.

**Strategic Question:** {problem_statement}

**Framework Structure:**{framework_desc_text}
{context_section}

**Task:** For EACH L1 category, determine how many L2 branches (3-7) are needed for MECE completeness, then generate them.

**CRITICAL Requirements:**

1. **Adaptive Branch Count**: Generate 3-7 L2 branches per L1 based on problem complexity
   - Simple problems: 3-4 branches may suffice
   - Complex problems: 5-7 branches may be needed for completeness
   - **MECE**: Branches must be Mutually Exclusive and Collectively Exhaustive

2. **Context-Aware Labels**: Customize labels to match the problem domain
   - For sales tools: "Sales Impact", "Revenue Generation", "Team Adoption"
   - For healthcare: "Patient Safety", "Clinical Outcomes", "Care Quality"
   - For tech products: "User Engagement", "Technical Performance", "Market Fit"
   - ✗ Bad: Generic labels like "Clinical/Safety Impact" for non-clinical problems

3. **Clear Questions**: One focused question per L2 branch (1 sentence, NO vendor names)
   - ✓ Good: "Does it meaningfully improve team productivity?"
   - ✗ Bad: Long paragraphs or vendor-specific questions

4. **MECE Compliance**: Ensure branches are Mutually Exclusive and Collectively Exhaustive within each L1

**Output Format (JSON):**
Return a JSON object where:
- Keys are L1 category identifiers (e.g., "DESIRABILITY", "FEASIBILITY", "VIABILITY")
- Values are objects with L2 branch keys mapping to:
  - "label": Context-specific label (2-5 words, NO vendors)
  - "question": Focused question (1 sentence, NO vendors)

**Example for "Should we scale AI meeting notetaker to sales team" (SALES context):**
```json
{{
  "DESIRABILITY": {{
    "CLINICAL_SAFETY": {{
      "label": "Sales Team Productivity",
      "question": "Does it measurably improve sales team efficiency and outcomes?"
    }},
    "FINANCIAL_ROI": {{
      "label": "Revenue Impact",
      "question": "Does it drive measurable revenue growth or cost savings?"
    }},
    "STAKEHOLDER_VALUE": {{
      "label": "Team Adoption",
      "question": "Will the sales team actively use and value this tool?"
    }}
  }},
  "FEASIBILITY": {{
    "TECHNICAL_SCALABILITY": {{
      "label": "Integration Complexity",
      "question": "Can it integrate smoothly with existing sales tools and workflows?"
    }},
    "OPERATIONAL_CAPACITY": {{
      "label": "Deployment Effort",
      "question": "Do we have the resources to roll this out to all sales teams?"
    }},
    "REGULATORY_COMPLIANCE": {{
      "label": "Security & Compliance",
      "question": "Does it meet data security and compliance requirements?"
    }}
  }},
  "VIABILITY": {{
    "FINANCIAL_SUSTAINABILITY": {{
      "label": "Cost Structure",
      "question": "Is the ongoing cost sustainable for our budget?"
    }},
    "STRATEGIC_FIT": {{
      "label": "Strategic Alignment",
      "question": "Does it align with our go-to-market strategy?"
    }},
    "COMPETITIVE_POSITIONING": {{
      "label": "Competitive Advantage",
      "question": "Does it provide meaningful competitive differentiation?"
    }}
  }}
}}
```

**CRITICAL - Remember:**
- Keep original L2 keys from template (e.g., "CLINICAL_SAFETY", "FINANCIAL_ROI")
- Customize labels to match problem domain (NOT generic)
- Labels: 2-5 words, NO vendors
- Questions: 1 sentence, focused, NO vendors

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

        # Extract JSON from response (handle markdown code blocks)
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        all_l2_branches = json.loads(response_text)

        # Clean up labels (max 6 words)
        for l1_key, l2_branches in all_l2_branches.items():
            for l2_key, l2_data in l2_branches.items():
                if "label" in l2_data:
                    l2_data["label"] = _cleanup_label(l2_data["label"], max_words=6)

        return all_l2_branches

    except (json.JSONDecodeError, AttributeError, KeyError) as e:
        # Fallback: return template structure if LLM fails
        print(f"Warning: Failed to parse L2 batch LLM response: {e}")
        print(f"Response was: {response}")

        # Return template L2 structure as fallback
        fallback = {}
        for l1_key, l1_data in framework_structure.items():
            fallback[l1_key] = {}
            for l2_key, l2_data in l1_data.get("L2_branches", {}).items():
                fallback[l1_key][l2_key] = {
                    "label": l2_data.get("label", l2_key),
                    "question": l2_data.get("question", ""),
                }
        return fallback


def generate_entire_tree_l2_branches_batch_with_validation(
    framework_structure: Dict[str, Any],
    problem_statement: str,
    market_research: Optional[str] = None,
    competitor_research: Optional[str] = None,
    model_name: str = "gemini-2.5-flash",
    max_attempts: int = 3,
) -> Tuple[Dict[str, Dict[str, Dict]], Dict]:
    """
    Generate L2 branches with incremental MECE validation and memory-based feedback.

    This wraps generate_entire_tree_l2_branches_batch() with a validation loop that:
    1. Generates L2 branches for all L1 categories
    2. Validates each L1's L2 branches separately
    3. Tracks failures in ValidationMemory
    4. Provides feedback to LLM for regeneration
    5. Only regenerates failed L1 categories (targeted regeneration)

    Args:
        framework_structure: The framework template with L1 categories
        problem_statement: The strategic question
        market_research: Market research context (optional)
        competitor_research: Competitive analysis context (optional)
        model_name: Gemini model to use
        max_attempts: Maximum regeneration attempts per L1 (default: 3)

    Returns:
        tuple: (l2_branches_dict, validation_results)
            - l2_branches_dict: {L1_key: {L2_key: {"label": ..., "question": ...}}}
            - validation_results: {
                "all_passed": bool,
                "l1_results": {L1_key: validation_result},
                "attempts": {L1_key: int}
            }
    """
    from .validation_memory import ValidationMemory
    from .mece_validator import validate_l2_branches

    memory = ValidationMemory()
    validation_results = {
        "all_passed": False,
        "l1_results": {},
        "attempts": {}
    }

    # Initial generation
    l2_branches = generate_entire_tree_l2_branches_batch(
        framework_structure=framework_structure,
        problem_statement=problem_statement,
        market_research=market_research,
        competitor_research=competitor_research,
        model_name=model_name
    )

    # Build temporary tree structure for validation
    temp_tree = {}
    for l1_key in framework_structure.keys():
        temp_tree[l1_key] = {
            "label": framework_structure[l1_key].get("label", l1_key),
            "L2": {}
        }
        if l1_key in l2_branches:
            for l2_key, l2_data in l2_branches[l1_key].items():
                temp_tree[l1_key]["L2"][l2_key] = l2_data

    # Validate each L1 category's L2 branches
    failed_l1_keys = []
    for l1_key in framework_structure.keys():
        validation_result = validate_l2_branches(temp_tree, l1_key)
        validation_results["l1_results"][l1_key] = validation_result
        validation_results["attempts"][l1_key] = 1

        if not validation_result["is_mece"]:
            failed_l1_keys.append(l1_key)
            memory.record_failure(
                level="L2",
                component=l1_key,
                validation_result=validation_result,
                iteration=1
            )

    # Regeneration loop for failed L1 categories only
    attempt = 2
    while failed_l1_keys and attempt <= max_attempts:
        print(f"L2 Validation: Regenerating {len(failed_l1_keys)} failed L1 categories (attempt {attempt}/{max_attempts})")

        for l1_key in failed_l1_keys[:]:  # Copy list to allow modification during iteration
            # Get feedback from memory
            feedback = memory.get_feedback_prompt(level="L2", component=l1_key)

            # Regenerate just this L1's L2 branches
            regenerated_l2 = generate_single_l1_l2_branches(
                l1_key=l1_key,
                l1_data=framework_structure[l1_key],
                problem_statement=problem_statement,
                feedback=feedback,
                model_name=model_name
            )

            # Update the tree
            l2_branches[l1_key] = regenerated_l2
            temp_tree[l1_key]["L2"] = regenerated_l2

            # Re-validate
            validation_result = validate_l2_branches(temp_tree, l1_key)
            validation_results["l1_results"][l1_key] = validation_result
            validation_results["attempts"][l1_key] = attempt

            if validation_result["is_mece"]:
                failed_l1_keys.remove(l1_key)
            else:
                memory.record_failure(
                    level="L2",
                    component=l1_key,
                    validation_result=validation_result,
                    iteration=attempt
                )

        attempt += 1

    validation_results["all_passed"] = len(failed_l1_keys) == 0

    return l2_branches, validation_results


def generate_single_l1_l2_branches(
    l1_key: str,
    l1_data: Dict,
    problem_statement: str,
    feedback: str = "",
    model_name: str = "gemini-2.5-flash",
) -> Dict[str, Dict]:
    """
    Generate L2 branches for a single L1 category with optional feedback from previous failures.

    Args:
        l1_key: L1 category identifier
        l1_data: L1 category data from framework
        problem_statement: Strategic question
        feedback: Formatted feedback from ValidationMemory (optional)
        model_name: Gemini model to use

    Returns:
        dict: {L2_key: {"label": ..., "question": ...}}
    """
    import json
    import os

    l1_label = l1_data.get("label", l1_key)
    l1_question = l1_data.get("question", "")
    l1_description = l1_data.get("description", "")

    prompt = f"""You are a senior strategy consultant generating L2 branches for a strategic decision tree.

**Strategic Question:** {problem_statement}

**L1 Category:**
- Key: {l1_key}
- Label: {l1_label}
- Question: {l1_question}
- Description: {l1_description}

{feedback}

**Task:** Generate 3-7 L2 branches for this L1 category that are MECE (Mutually Exclusive, Collectively Exhaustive).

**Requirements:**
1. **MECE Compliance**: Branches must NOT overlap and must comprehensively cover the L1 category
2. **Context-Aware Labels**: Customize labels to match the problem domain (2-5 words, NO vendor names)
3. **Clear Questions**: One focused question per branch (1 sentence, NO vendor names)
4. **Appropriate Count**: Generate 3-7 branches based on complexity needed for completeness

**Output Format (JSON):**
{{
  "BRANCH_KEY_1": {{
    "label": "Context-specific label",
    "question": "Focused question"
  }},
  "BRANCH_KEY_2": {{
    "label": "Context-specific label",
    "question": "Focused question"
  }}
}}

Return ONLY the JSON object, no other text."""

    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
    )

    try:
        response_text = response.text.strip()

        # Extract JSON from response
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        l2_branches = json.loads(response_text)

        # Clean up labels
        for l2_key, l2_data in l2_branches.items():
            if "label" in l2_data:
                l2_data["label"] = _cleanup_label(l2_data["label"], max_words=6)

        return l2_branches

    except (json.JSONDecodeError, AttributeError, KeyError) as e:
        print(f"Warning: Failed to parse L2 LLM response for {l1_key}: {e}")

        # Fallback: return template structure
        fallback = {}
        for l2_key, l2_data in l1_data.get("L2_branches", {}).items():
            fallback[l2_key] = {
                "label": l2_data.get("label", l2_key),
                "question": l2_data.get("question", ""),
            }
        return fallback


def generate_l1_category_batch_with_validation(
    l1_key: str,
    l1_data: Dict[str, Any],
    problem_statement: str,
    market_research: Optional[str] = None,
    competitor_research: Optional[str] = None,
    num_leaves_per_branch: int = 3,
    model_name: str = "gemini-2.5-flash",
    max_attempts: int = 3,
) -> Tuple[Dict[str, List[Dict]], Dict]:
    """
    Generate L3 leaves for a single L1 category with incremental MECE validation.

    This wraps generate_l1_category_batch() with a validation loop that:
    1. Generates L3 leaves for all L2 branches in this L1
    2. Validates each L2's L3 leaves separately
    3. Tracks failures in ValidationMemory
    4. Provides feedback to LLM for regeneration
    5. Only regenerates failed L2 branches (targeted regeneration)

    Args:
        l1_key: L1 category identifier
        l1_data: L1 category data including L2 branches
        problem_statement: Strategic question
        market_research: Market research context (optional)
        competitor_research: Competitive analysis context (optional)
        num_leaves_per_branch: Number of L3 leaves per L2 branch
        model_name: Gemini model to use
        max_attempts: Maximum regeneration attempts per L2 (default: 3)

    Returns:
        tuple: (l3_leaves_dict, validation_results)
            - l3_leaves_dict: {L2_key: [L3_leaves]}
            - validation_results: {
                "all_passed": bool,
                "l2_results": {L2_key: validation_result},
                "attempts": {L2_key: int}
            }
    """
    from .validation_memory import ValidationMemory
    from .mece_validator import validate_l3_leaves

    memory = ValidationMemory()
    validation_results = {
        "all_passed": False,
        "l2_results": {},
        "attempts": {}
    }

    # Initial generation for all L2 branches in this L1
    l3_leaves = generate_l1_category_batch(
        l1_key=l1_key,
        l1_data=l1_data,
        problem_statement=problem_statement,
        market_research=market_research,
        competitor_research=competitor_research,
        num_leaves_per_branch=num_leaves_per_branch,
        model_name=model_name
    )

    # Build temporary tree structure for validation
    temp_tree = {
        l1_key: {
            "label": l1_data.get("label", l1_key),
            "L2": {}
        }
    }

    for l2_key in l1_data.get("L2_branches", {}).keys():
        temp_tree[l1_key]["L2"][l2_key] = {
            "label": l1_data["L2_branches"][l2_key].get("label", l2_key),
            "L3": {}
        }
        if l2_key in l3_leaves:
            for leaf in l3_leaves[l2_key]:
                leaf_key = f"L3_{leaf.get('label', '').upper().replace(' ', '_')}"
                temp_tree[l1_key]["L2"][l2_key]["L3"][leaf_key] = leaf

    # Validate each L2's L3 leaves
    failed_l2_keys = []
    for l2_key in l1_data.get("L2_branches", {}).keys():
        validation_result = validate_l3_leaves(temp_tree, l1_key, l2_key)
        validation_results["l2_results"][l2_key] = validation_result
        validation_results["attempts"][l2_key] = 1

        if not validation_result["is_mece"]:
            failed_l2_keys.append(l2_key)
            memory.record_failure(
                level="L3",
                component=f"{l1_key}.{l2_key}",
                validation_result=validation_result,
                iteration=1
            )

    # Regeneration loop for failed L2 branches only
    attempt = 2
    while failed_l2_keys and attempt <= max_attempts:
        print(f"L3 Validation ({l1_key}): Regenerating {len(failed_l2_keys)} failed L2 branches (attempt {attempt}/{max_attempts})")

        for l2_key in failed_l2_keys[:]:  # Copy list to allow modification
            # Get feedback from memory
            feedback = memory.get_feedback_prompt(level="L3", component=f"{l1_key}.{l2_key}")

            # Regenerate just this L2's L3 leaves
            regenerated_l3 = generate_single_l2_l3_leaves(
                l1_key=l1_key,
                l1_data=l1_data,
                l2_key=l2_key,
                problem_statement=problem_statement,
                feedback=feedback,
                num_leaves_per_branch=num_leaves_per_branch,
                model_name=model_name
            )

            # Update the leaves
            l3_leaves[l2_key] = regenerated_l3

            # Update temp tree
            temp_tree[l1_key]["L2"][l2_key]["L3"] = {}
            for leaf in regenerated_l3:
                leaf_key = f"L3_{leaf.get('label', '').upper().replace(' ', '_')}"
                temp_tree[l1_key]["L2"][l2_key]["L3"][leaf_key] = leaf

            # Re-validate
            validation_result = validate_l3_leaves(temp_tree, l1_key, l2_key)
            validation_results["l2_results"][l2_key] = validation_result
            validation_results["attempts"][l2_key] = attempt

            if validation_result["is_mece"]:
                failed_l2_keys.remove(l2_key)
            else:
                memory.record_failure(
                    level="L3",
                    component=f"{l1_key}.{l2_key}",
                    validation_result=validation_result,
                    iteration=attempt
                )

        attempt += 1

    validation_results["all_passed"] = len(failed_l2_keys) == 0

    return l3_leaves, validation_results


def generate_single_l2_l3_leaves(
    l1_key: str,
    l1_data: Dict,
    l2_key: str,
    problem_statement: str,
    feedback: str = "",
    num_leaves_per_branch: int = 3,
    model_name: str = "gemini-2.5-flash",
) -> List[Dict]:
    """
    Generate L3 leaves for a single L2 branch with optional feedback from previous failures.

    Args:
        l1_key: L1 category identifier
        l1_data: L1 category data
        l2_key: L2 branch identifier
        problem_statement: Strategic question
        feedback: Formatted feedback from ValidationMemory (optional)
        num_leaves_per_branch: Target number of leaves
        model_name: Gemini model to use

    Returns:
        list: [L3_leaves] - List of leaf dictionaries
    """
    import json
    import os

    l1_label = l1_data.get("label", l1_key)
    l1_question = l1_data.get("question", "")

    l2_data = l1_data.get("L2_branches", {}).get(l2_key, {})
    l2_label = l2_data.get("label", l2_key)
    l2_question = l2_data.get("question", "")

    prompt = f"""You are a senior strategy consultant generating L3 testable hypotheses for a strategic decision tree.

**Strategic Question:** {problem_statement}

**L1 Category:** {l1_key} - {l1_label}
- Question: {l1_question}

**L2 Branch:** {l2_key} - {l2_label}
- Question: {l2_question}

{feedback}

**Task:** Generate 3-7 L3 leaves for this L2 branch that are MECE (Mutually Exclusive, Collectively Exhaustive).

**Requirements:**
1. **MECE Compliance**: Leaves must NOT overlap and must comprehensively cover the L2 branch
2. **Label Rules**: Concise key phrases (3-6 words), NO vendor names, NO specific numbers
3. **Question Rules**: Clean, simple questions (1 sentence max), NO vendor names
4. **Required Fields**: Each leaf must have:
   - label: Concise phrase
   - question: Testable question
   - metric_type: "qualitative" or "quantitative"
   - target: Benchmark with citation
   - data_source: Where to get the data (vendor names OK here)

**Output Format (JSON array):**
[
  {{
    "label": "Leaf label",
    "question": "Testable question?",
    "metric_type": "quantitative",
    "target": ">25% reduction vs baseline (KLAS 2024)",
    "data_source": "Vendor analytics platform"
  }}
]

Return ONLY the JSON array, no other text."""

    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
    )

    try:
        response_text = response.text.strip()

        # Extract JSON from response
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        l3_leaves = json.loads(response_text)

        # Clean up labels
        for leaf in l3_leaves:
            if "label" in leaf:
                leaf["label"] = _cleanup_label(leaf["label"], max_words=6)

        return l3_leaves

    except (json.JSONDecodeError, AttributeError, KeyError) as e:
        print(f"Warning: Failed to parse L3 LLM response for {l1_key}.{l2_key}: {e}")

        # Fallback: return template structure
        fallback = []
        for suggested_leaf in l2_data.get("suggested_L3", [])[:num_leaves_per_branch]:
            fallback.append({
                "label": suggested_leaf,
                "question": f"What is the {suggested_leaf.lower()}?",
                "metric_type": "quantitative",
                "target": "TBD",
                "data_source": "TBD"
            })
        return fallback if fallback else [
            {
                "label": "Placeholder Metric",
                "question": "What is the key metric?",
                "metric_type": "quantitative",
                "target": "TBD",
                "data_source": "TBD"
            }
        ]
