"""Generate MECE hypothesis trees from framework templates."""

from typing import Dict, List, Optional

from strategic_consultant_agent.tools.framework_loader import load_framework


def generate_hypothesis_tree(
    problem: str,
    framework: str = "scale_decision",
    custom_l1_categories: Optional[List[str]] = None,
) -> Dict:
    """
    Generate a MECE hypothesis tree for a strategic problem.

    Args:
        problem: The strategic question to analyze
        framework: One of [scale_decision, product_launch, market_entry,
                         investment_decision, operations_improvement, custom]
        custom_l1_categories: User-defined L1 categories (only if framework="custom")

    Returns:
        dict: Complete hypothesis tree structure with L1, L2, L3 levels
    """
    # Load framework template
    if framework == "custom":
        if not custom_l1_categories:
            raise ValueError("custom_l1_categories required when framework='custom'")
        template = _build_custom_framework(custom_l1_categories)
    else:
        template = load_framework(framework)
        if template is None:
            raise ValueError(
                f"Unknown framework: {framework}. "
                f"Use one of: scale_decision, product_launch, "
                f"market_entry, investment_decision, operations_improvement, custom"
            )

    # Build hypothesis tree from template
    tree = {
        "problem": problem,
        "framework": framework,
        "framework_name": template.get("name", framework),
        "description": template.get("description", ""),
        "tree": {},
        "metadata": {
            "levels": 3,
            "mece_validated": False,
        },
    }

    # Generate L1, L2, L3 structure from template
    l1_categories = template.get("L1_categories", {})

    for l1_key, l1_data in l1_categories.items():
        tree["tree"][l1_key] = {
            "label": l1_data.get("label", l1_key),
            "question": l1_data.get("question", ""),
            "description": l1_data.get("description", ""),
            "L2_branches": {},
        }

        # Add L2 branches
        l2_branches = l1_data.get("L2_branches", {})
        for l2_key, l2_data in l2_branches.items():
            tree["tree"][l1_key]["L2_branches"][l2_key] = {
                "label": l2_data.get("label", l2_key),
                "question": l2_data.get("question", ""),
                "L3_leaves": [],
            }

            # Generate L3 leaves from suggested leaves
            suggested_l3 = l2_data.get("suggested_L3", [])
            for i, leaf_label in enumerate(suggested_l3):
                l3_leaf = _generate_l3_leaf(
                    label=leaf_label,
                    l1_context=l1_data.get("label", ""),
                    l2_context=l2_data.get("label", ""),
                    problem=problem,
                    index=i + 1,
                )
                tree["tree"][l1_key]["L2_branches"][l2_key]["L3_leaves"].append(l3_leaf)

    return tree


def _build_custom_framework(categories: List[str]) -> Dict:
    """
    Build a custom framework from user-defined L1 categories.

    Args:
        categories: List of L1 category names

    Returns:
        dict: Framework template structure
    """
    framework = {
        "name": "Custom Framework",
        "description": "User-defined framework",
        "L1_categories": {},
    }

    for category in categories:
        # Use simple uppercase key without L1_ prefix to match template pattern
        l1_key = category.upper().replace(" ", "_")
        framework["L1_categories"][l1_key] = {
            "label": category,
            "question": f"How does {category} affect the decision?",
            "description": f"Analysis of {category}",
            "L2_branches": {
                "ANALYSIS": {
                    "label": f"{category} Analysis",
                    "question": f"What are the key {category} considerations?",
                    "suggested_L3": [
                        f"{category} Factor 1",
                        f"{category} Factor 2",
                        f"{category} Factor 3",
                    ],
                }
            },
        }

    return framework


def _generate_l3_leaf(
    label: str,
    l1_context: str,
    l2_context: str,
    problem: str,
    index: int,
) -> Dict:
    """
    Generate a complete L3 leaf with all required fields.

    Args:
        label: Leaf label/name
        l1_context: L1 category label
        l2_context: L2 branch label
        problem: Strategic question
        index: Leaf index within branch

    Returns:
        dict: Complete L3 leaf structure
    """
    # Determine metric type based on label keywords
    metric_type = _infer_metric_type(label)

    # Generate question
    question = f"What is the {label.lower()}?"

    # Generate target (generic - to be customized by user)
    target = _generate_target(label, metric_type)

    # Generate data source suggestion
    data_source = _suggest_data_source(label, l2_context)

    return {
        "id": f"L3_{index:03d}",
        "label": label,
        "question": question,
        "metric_type": metric_type,
        "target": target,
        "data_source": data_source,
        "status": "UNTESTED",
        "confidence": None,
        "components": [],
        "assessment_criteria": f"Evaluate {label.lower()} against target",
    }


def _infer_metric_type(label: str) -> str:
    """
    Infer metric type from label keywords.

    Args:
        label: Leaf label

    Returns:
        str: One of "quantitative", "qualitative", "binary"
    """
    label_lower = label.lower()

    # Binary indicators
    binary_keywords = [
        "exists",
        "available",
        "possible",
        "capable",
        "compliance",
        "ready",
    ]
    if any(keyword in label_lower for keyword in binary_keywords):
        return "binary"

    # Quantitative indicators
    quant_keywords = [
        "rate",
        "cost",
        "time",
        "reduction",
        "improvement",
        "size",
        "growth",
        "revenue",
        "savings",
        "number",
        "percent",
        "roi",
    ]
    if any(keyword in label_lower for keyword in quant_keywords):
        return "quantitative"

    # Default to qualitative
    return "qualitative"


def _generate_target(label: str, metric_type: str) -> str:
    """
    Generate a placeholder target based on metric type.

    Args:
        label: Leaf label
        metric_type: Type of metric

    Returns:
        str: Target description
    """
    if metric_type == "binary":
        return "Yes / Confirmed"
    elif metric_type == "quantitative":
        if "reduction" in label.lower() or "improvement" in label.lower():
            return ">25% improvement vs baseline"
        elif "cost" in label.lower() or "savings" in label.lower():
            return "Positive ROI within 12 months"
        elif "time" in label.lower():
            return "<30 days implementation"
        else:
            return "Measurable positive impact"
    else:  # qualitative
        return "Strong positive assessment from stakeholders"


def _suggest_data_source(label: str, l2_context: str) -> str:
    """
    Suggest appropriate data source based on context.

    Args:
        label: Leaf label
        l2_context: L2 branch context

    Returns:
        str: Data source suggestion
    """
    label_lower = label.lower()

    # Financial data
    if any(word in label_lower for word in ["cost", "revenue", "savings", "roi"]):
        return "Financial reports, budget analysis"

    # Technical data
    if any(
        word in label_lower
        for word in ["system", "integration", "technical", "infrastructure"]
    ):
        return "Technical specifications, vendor documentation"

    # User/stakeholder data
    if any(
        word in label_lower
        for word in ["satisfaction", "acceptance", "value", "experience"]
    ):
        return "Surveys, interviews, user feedback"

    # Operational data
    if any(
        word in label_lower
        for word in ["capacity", "workflow", "operational", "process"]
    ):
        return "Operational metrics, process data"

    # Regulatory/compliance
    if any(
        word in label_lower for word in ["regulatory", "compliance", "legal", "risk"]
    ):
        return "Regulatory documentation, compliance audits"

    # Market data
    if any(
        word in label_lower for word in ["market", "competitive", "industry", "trend"]
    ):
        return "Market research, industry reports"

    # Default
    return f"{l2_context} data and analysis"
