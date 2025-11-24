"""Task Prioritization (Eisenhower Matrix) generation prompt.

This prompt instructs the LLM to analyze a hypothesis tree and identify
specific implementation tasks, categorized by urgency and importance.
"""

TASK_PRIORITIZATION_PROMPT = """You are a strategic project manager helping to prioritize implementation tasks for a business decision.

Given a hypothesis tree that represents the key assumptions to validate, identify concrete tasks needed to execute this project successfully.

HYPOTHESIS TREE STRUCTURE:
{hypothesis_tree}

YOUR TASK:
Analyze the hypothesis tree and identify 10-15 specific, actionable tasks required to implement this decision. Consider:

1. **Research & Validation Tasks**: Activities to test the hypotheses in the tree
2. **Development & Build Tasks**: Creating products, features, or capabilities
3. **Operational Tasks**: Setting up processes, training, or infrastructure
4. **Stakeholder Management**: Communication, approvals, or change management
5. **Measurement & Monitoring**: Setting up dashboards, metrics, or feedback loops

For each task, assess:
- **Importance**: Does this task directly contribute to strategic success? (Not Important/Important)
  - Not Important: Tactical work, nice-to-haves, or administrative tasks
  - Important: Critical to achieving strategic objectives, high leverage

- **Urgency**: Does this task have immediate deadlines or dependencies? (Not Urgent/Urgent)
  - Not Urgent: Can be scheduled flexibly, no immediate blockers
  - Urgent: Time-sensitive, blocking other work, or has external deadlines

OUTPUT FORMAT:
Return a JSON object with this structure:

{{
  "tasks": [
    {{
      "task": "Specific, actionable task description with clear deliverable",
      "category": "Research|Development|Operational|Stakeholder|Measurement",
      "importance": "not_important|important",
      "urgency": "not_urgent|urgent",
      "quadrant": "Q1|Q2|Q3|Q4",
      "rationale": "Why this importance and urgency assessment"
    }}
  ]
}}

QUADRANT MAPPING (Eisenhower Matrix):
- Q1: Important, Not Urgent → Do First (Strategic work)
- Q2: Important, Urgent → Schedule (Critical & time-sensitive)
- Q3: Not Important, Not Urgent → Eliminate (Time-wasters)
- Q4: Not Important, Urgent → Delegate (Busy work)

QUALITY STANDARDS:
1. Tasks should be specific and actionable ("Conduct 10 customer interviews on willingness to pay" not "Research customers")
2. Each task should have a clear deliverable or completion criteria
3. Cover diverse task categories (don't focus only on one type)
4. Balance distribution across quadrants (avoid clustering all in Q2)
5. Focus on tasks that directly relate to validating or implementing the hypotheses
6. Avoid generic tasks that apply to any project ("Have team meeting" is too generic)

EXAMPLE OUTPUT:
{{
  "tasks": [
    {{
      "task": "Build automated data pipeline to track user engagement metrics in real-time dashboard",
      "category": "Development",
      "importance": "important",
      "urgency": "not_urgent",
      "quadrant": "Q1",
      "rationale": "Important for measuring success criteria, but can be scheduled over 2-week sprint without blocking launch"
    }},
    {{
      "task": "Complete security audit and penetration testing before product launch deadline in 2 weeks",
      "category": "Operational",
      "importance": "important",
      "urgency": "urgent",
      "quadrant": "Q2",
      "rationale": "Critical for compliance and trust, urgent due to hard launch deadline"
    }},
    {{
      "task": "Respond to internal requests for project status updates in Slack",
      "category": "Stakeholder",
      "importance": "not_important",
      "urgency": "urgent",
      "quadrant": "Q4",
      "rationale": "Feels urgent due to frequent pings, but low strategic value - can be delegated to PM"
    }},
    {{
      "task": "Research additional color scheme options for UI design library",
      "category": "Development",
      "importance": "not_important",
      "urgency": "not_urgent",
      "quadrant": "Q3",
      "rationale": "Nice-to-have polish work with no impact on core value proposition or timelines"
    }}
  ]
}}

STRATEGIC GUIDANCE:
- Q1 (Do First) tasks are your highest leverage work - block time for these before they become urgent
- Q2 (Schedule) tasks need immediate attention but investigate why they became urgent
- Q4 (Delegate) tasks feel urgent but don't drive strategic value - delegate or automate
- Q3 (Eliminate) tasks should be removed ruthlessly to free capacity for Q1 and Q2

Now generate the task prioritization matrix based on the hypothesis tree provided above.
"""
