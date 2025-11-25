"""Hypothesis Prioritization matrix generation prompt.

This prompt instructs the LLM to analyze L3 hypotheses from a hypothesis tree
and prioritize them based on strategic impact and validation effort, helping
teams decide which hypotheses to test first.
"""

HYPOTHESIS_PRIORITIZATION_PROMPT = """You are a strategic analyst helping to prioritize hypothesis validation for a business decision.

Given a hypothesis tree with L3 leaves representing testable hypotheses, assess each hypothesis to determine validation priority based on strategic impact and effort required.

HYPOTHESIS TREE STRUCTURE:
{hypothesis_tree}

YOUR TASK:
Analyze the L3 leaves in the hypothesis tree and categorize 10-15 key hypotheses for prioritization.

Each L3 leaf contains:
- **label**: The hypothesis name
- **question**: What this hypothesis tests
- **metric_type**: Type of validation (quantitative, qualitative, comparative)
- **target**: Success criteria or measurement goal
- **data_source**: Where validation data comes from
- **assessment_criteria**: How to evaluate the hypothesis

For each hypothesis, assess:

**STRATEGIC IMPACT**: How critical is validating this hypothesis to the decision?
- **High**: Core decision driver, high uncertainty, large financial/strategic stakes, failure would kill the project
  - Examples: Market demand exists, unit economics work, technical feasibility proven
- **Low**: Nice-to-know information, low uncertainty, minor impact on go/no-go decision, can be validated later
  - Examples: Brand preference details, minor feature requests, secondary market segments

**VALIDATION EFFORT**: How difficult/expensive is it to test this hypothesis?
- **Low**: Quick to validate, existing data available, desk research, simple surveys, <2 weeks, <$10K
  - Examples: Analyze existing data, 10 customer interviews, competitive analysis
- **High**: Requires pilots, complex studies, significant time/budget, >1 month, >$50K
  - Examples: 6-month clinical trial, build full prototype, regulatory approval process

OUTPUT FORMAT:
Return a JSON object with this structure:

{{
  "hypotheses": [
    {{
      "hypothesis": "Label from L3 leaf",
      "question": "The validation question being tested",
      "strategic_impact": "low|high",
      "validation_effort": "low|high",
      "quadrant": "Q1|Q2|Q3|Q4",
      "rationale": "Why this impact and effort assessment - cite specific details from target, data_source, or assessment_criteria"
    }}
  ]
}}

QUADRANT MAPPING:
- Q1: High Impact, Low Effort → **Quick Wins** (validate first - these de-risk quickly)
- Q2: High Impact, High Effort → **Strategic Bets** (plan carefully with adequate resources)
- Q3: Low Impact, Low Effort → **Fill Later** (test only if time permits after Q1/Q2)
- Q4: Low Impact, High Effort → **Deprioritize** (skip unless required by stakeholders)

QUALITY STANDARDS:
1. Focus on hypotheses that truly test assumptions (not just metrics to track)
2. Impact assessment should consider: uncertainty level, financial stakes, strategic criticality
3. Effort assessment should be realistic based on data_source and assessment_criteria fields
4. Distribute across quadrants realistically (don't force everything into Q1)
5. Rationale should cite specific evidence from the L3 leaf (target values, data sources, etc.)
6. Prioritize hypotheses that address DESIRABILITY, FEASIBILITY, and VIABILITY questions

EXAMPLE OUTPUT:
{{
  "hypotheses": [
    {{
      "hypothesis": "Fall Incident Reduction",
      "question": "What is the measured reduction in fall incidents after deployment?",
      "strategic_impact": "high",
      "validation_effort": "low",
      "quadrant": "Q1",
      "rationale": "High impact: 67-83% fall reduction is the core value proposition driving ROI. Low effort: Data source is 'resident incident reports' which facilities already track, allowing immediate analysis."
    }},
    {{
      "hypothesis": "Staff Satisfaction Improvement",
      "question": "How does staff satisfaction change with the technology?",
      "strategic_impact": "high",
      "validation_effort": "high",
      "quadrant": "Q2",
      "rationale": "High impact: Staff satisfaction >4.5/5 is critical for adoption and retention. High effort: Requires surveys across multiple facilities over 6+ months to establish baseline and measure change."
    }},
    {{
      "hypothesis": "System Uptime Reliability",
      "question": "What is the system uptime percentage in production?",
      "strategic_impact": "low",
      "validation_effort": "low",
      "quadrant": "Q3",
      "rationale": "Low impact: While important, >99% uptime is table stakes for any SaaS. Low effort: System logs provide automatic tracking."
    }},
    {{
      "hypothesis": "Brand Preference Among Competitors",
      "question": "How do facilities perceive our brand vs competitors?",
      "strategic_impact": "low",
      "validation_effort": "high",
      "quadrant": "Q4",
      "rationale": "Low impact: Decision doesn't hinge on brand perception, clinical outcomes drive adoption. High effort: Requires extensive market research across competitive landscape."
    }}
  ]
}}

PRIORITIZATION GUIDANCE:
- Q1 (Quick Wins): These should be your immediate focus. Test within first 2-4 weeks.
- Q2 (Strategic Bets): Plan these carefully with proper budget and timeline (months).
- Q3 (Fill Later): Only validate if you complete Q1 and Q2 and have spare capacity.
- Q4 (Deprioritize): Skip unless explicitly required for regulatory, compliance, or stakeholder management.

Now generate the hypothesis prioritization matrix based on the hypothesis tree provided above. Focus on L3 leaves that represent true validation hypotheses with clear strategic implications.
"""
