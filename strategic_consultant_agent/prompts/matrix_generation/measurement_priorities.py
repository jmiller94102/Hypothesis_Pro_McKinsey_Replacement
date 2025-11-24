"""Measurement Priorities matrix generation prompt.

This prompt instructs the LLM to analyze a hypothesis tree and identify
key metrics to track, categorized by strategic value and measurement feasibility.
"""

MEASUREMENT_PRIORITIES_PROMPT = """You are a strategic analytics consultant helping to prioritize which metrics to track for a business decision.

Given a hypothesis tree that represents key assumptions to validate, identify the most important metrics and KPIs to measure success.

HYPOTHESIS TREE STRUCTURE:
{hypothesis_tree}

YOUR TASK:
Analyze the hypothesis tree (especially the L3 leaves which contain metric_type and target fields) and identify 10-15 distinct metrics that should be tracked. Consider:

1. **Leading Indicators**: Metrics that predict future success (e.g., user activation rate predicts retention)
2. **Lagging Indicators**: Metrics that measure actual outcomes (e.g., revenue, churn rate)
3. **Input Metrics**: Metrics measuring resources invested (e.g., ad spend, engineering hours)
4. **Output Metrics**: Metrics measuring results achieved (e.g., conversions, product launches)
5. **Health Metrics**: Metrics indicating system or business health (e.g., uptime, customer satisfaction)

For each metric, assess:
- **Strategic Value**: How critical is this metric for decision-making? (Low/High)
  - Low: Nice-to-know, doesn't drive key decisions
  - High: Directly impacts strategic choices, critical for success assessment

- **Feasibility of Measurement**: How easy is it to accurately track this metric? (Easy/Hard)
  - Easy: Data already available, automated collection, reliable
  - Hard: Requires new infrastructure, manual work, or has data quality issues

OUTPUT FORMAT:
Return a JSON object with this structure:

{{
  "metrics": [
    {{
      "metric": "Clear, specific metric name with unit",
      "definition": "How this metric is calculated or measured",
      "category": "Leading|Lagging|Input|Output|Health",
      "strategic_value": "low|high",
      "feasibility": "easy|hard",
      "quadrant": "Q1|Q2|Q3|Q4",
      "rationale": "Why this value and feasibility assessment",
      "target": "Specific target or threshold if applicable"
    }}
  ]
}}

QUADRANT MAPPING:
- Q1: High Value, Easy to Measure → Core KPIs (track in real-time dashboards)
- Q2: High Value, Hard to Measure → Strategic Metrics (invest in measurement infrastructure)
- Q3: Low Value, Easy to Measure → Nice to Have (track only if zero incremental effort)
- Q4: Low Value, Hard to Measure → Deprioritize (don't waste resources measuring)

QUALITY STANDARDS:
1. Metrics should be specific with clear units ("Daily Active Users (DAU)" not "User engagement")
2. Each metric should have a clear definition of how it's measured
3. Cover diverse metric categories (leading, lagging, input, output, health)
4. Balance distribution across quadrants (avoid clustering all in one)
5. Focus on metrics that directly relate to hypotheses in the tree
6. Prefer actionable metrics over vanity metrics

EXAMPLE OUTPUT:
{{
  "metrics": [
    {{
      "metric": "7-Day User Retention Rate (%)",
      "definition": "Percentage of new users who return to product within 7 days of signup",
      "category": "Leading",
      "strategic_value": "high",
      "feasibility": "easy",
      "quadrant": "Q1",
      "rationale": "High value as leading indicator of product-market fit; easy to measure with existing analytics instrumentation",
      "target": ">40% retention"
    }},
    {{
      "metric": "Net Promoter Score (NPS)",
      "definition": "Survey-based score measuring likelihood customers would recommend product (scale -100 to +100)",
      "category": "Health",
      "strategic_value": "high",
      "feasibility": "hard",
      "quadrant": "Q2",
      "rationale": "High strategic value for customer satisfaction insights; hard due to survey fatigue and response bias challenges",
      "target": "NPS > 50"
    }},
    {{
      "metric": "Daily Email Opens",
      "definition": "Number of marketing emails opened per day",
      "category": "Output",
      "strategic_value": "low",
      "feasibility": "easy",
      "quadrant": "Q3",
      "rationale": "Easy to track with email platform, but low strategic value as vanity metric not tied to revenue or retention",
      "target": "N/A"
    }},
    {{
      "metric": "Customer Lifetime Value by Acquisition Cohort (LTV)",
      "definition": "Total revenue generated per customer segmented by signup month and marketing channel",
      "category": "Lagging",
      "strategic_value": "low",
      "feasibility": "hard",
      "quadrant": "Q4",
      "rationale": "Hard to measure accurately due to attribution complexity and long time horizons; low value since simpler proxies exist",
      "target": "N/A"
    }}
  ]
}}

STRATEGIC GUIDANCE:
- Q1 (Core KPIs) should be your primary dashboard - track in real-time with automated alerts
- Q2 (Strategic Metrics) are worth investing in measurement infrastructure and data quality
- Q3 (Nice to Have) metrics can be included if already available at zero cost
- Q4 (Deprioritize) metrics waste resources - focus on Q1 and Q2 instead

IMPORTANT:
Pay special attention to the L3 leaves in the hypothesis tree, as they often contain specific metric_type, target, and data_source fields that should inform your metric selection.

Now generate the measurement priorities matrix based on the hypothesis tree provided above.
"""
