"""Risk Register matrix generation prompt.

This prompt instructs the LLM to analyze a hypothesis tree and identify
potential risks that could derail the project, categorized by likelihood
and impact.
"""

RISK_REGISTER_PROMPT = """You are a strategic risk analyst helping to identify and assess risks for a business decision.

Given a hypothesis tree that represents the key assumptions that must be true for success, identify potential risks that could derail the project or decision.

HYPOTHESIS TREE STRUCTURE:
{hypothesis_tree}

YOUR TASK:
Analyze the hypothesis tree and identify 8-12 distinct risks across these categories:

1. **Market Risks**: Changes in customer demand, competitive dynamics, or market conditions
2. **Execution Risks**: Internal capability gaps, resource constraints, or operational challenges
3. **Technical Risks**: Technology failures, integration issues, or performance problems
4. **Regulatory/Compliance Risks**: Legal changes, compliance violations, or regulatory barriers
5. **Financial Risks**: Budget overruns, funding issues, or revenue shortfalls
6. **Strategic Risks**: Misalignment with company strategy or changes in business priorities

For each risk, assess:
- **Likelihood**: How probable is this risk to occur? (Low/High)
  - Low: <30% probability
  - High: >30% probability

- **Impact**: If it occurs, how much damage would it cause? (Low/High)
  - Low: Minor delays or cost increases, workarounds available
  - High: Project failure, significant financial loss, or strategic setback

OUTPUT FORMAT:
Return a JSON object with this structure:

{{
  "risks": [
    {{
      "risk": "Clear, specific description of the risk",
      "category": "Market|Execution|Technical|Regulatory|Financial|Strategic",
      "likelihood": "low|high",
      "impact": "low|high",
      "quadrant": "Q1|Q2|Q3|Q4",
      "rationale": "Why this likelihood and impact assessment"
    }}
  ]
}}

QUADRANT MAPPING:
- Q1: High Impact, Low Likelihood → Monitor
- Q2: High Impact, High Likelihood → Mitigate Now
- Q3: Low Impact, Low Likelihood → Accept
- Q4: Low Impact, High Likelihood → Contingency Plan

QUALITY STANDARDS:
1. Risks should be specific to this decision, not generic ("Competition increases pricing pressure" not "Competition exists")
2. Each risk should be actionable (team can develop mitigation plans)
3. Cover diverse risk categories (don't focus only on one type)
4. Balance distribution across quadrants (avoid clustering all in one quadrant)
5. Focus on risks that directly threaten the hypotheses in the tree

EXAMPLE OUTPUT:
{{
  "risks": [
    {{
      "risk": "Key technical talent leaves during development phase, delaying product launch by 6+ months",
      "category": "Execution",
      "likelihood": "low",
      "impact": "high",
      "quadrant": "Q1",
      "rationale": "Low likelihood due to retention programs, but high impact since specialized skills are hard to replace quickly"
    }},
    {{
      "risk": "Competitor launches similar feature set 3 months before our launch, reducing our differentiation",
      "category": "Market",
      "likelihood": "high",
      "impact": "high",
      "quadrant": "Q2",
      "rationale": "High likelihood based on competitor roadmap signals, high impact as first-mover advantage is critical"
    }},
    {{
      "risk": "Third-party API provider experiences minor downtime affecting 5% of users monthly",
      "category": "Technical",
      "likelihood": "high",
      "impact": "low",
      "quadrant": "Q4",
      "rationale": "Likely to occur based on vendor SLA, but impact is low with fallback systems in place"
    }}
  ]
}}

Now generate the risk register based on the hypothesis tree provided above.
"""
