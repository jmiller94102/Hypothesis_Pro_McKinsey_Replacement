# HypothesisTree Pro - User Experience Workflow

## Overview

This document describes the complete user journey from initial strategic question to final MECE Tree output. The workflow is designed to be conversational, iterative, and produce MBB-quality strategic analysis.

---

## Example Starting Prompts

Users can initiate analysis with prompts like:

- "Should the company scale deployment of a Computer Vision Fall Detection system in Senior Living?"
- "Should the company scale deployment of a Nurse Call System in Senior Living?"
- "Should the company scale deployment of https://www.teton.ai/ in Senior Living?"

---

## Stage 1: Problem Intake

### User Action
Submits a single strategic question.

### Agent Response
The agent acknowledges the strategic question and performs three actions:

1. **Classifies the problem type** → Determines if this is a scale/expand decision, market entry, new product launch, M&A evaluation, etc.

2. **Recommends a framework** → For scaling decisions, suggests Desirability/Feasibility/Viability framework

3. **Asks clarifying questions** (optional, based on information gaps):
   - "Do you have pilot data from existing deployments?"
   - "What's the current deployment footprint?"
   - "Are there specific constraints I should know about (budget, timeline, regulatory)?"

### User Options
- Answer the clarifying questions
- Skip questions and proceed with defaults
- Provide a URL or document for additional context

---

## Stage 2: Context Gathering (Parallel Research)

Once the user confirms the framework (or accepts the default), the agent initiates parallel research streams.

### Market Researcher Agent
Searches for:
- Industry benchmarks for the technology in question
- Adoption rates and trends
- Regulatory landscape (state privacy laws, HIPAA implications)
- Competitive solutions and pricing

### Competitor Researcher Agent
Searches for:
- Specific vendors (if URL provided)
- Feature comparisons
- Customer reviews and case studies
- Known implementation challenges

### URL Processing (if provided)
When a URL is provided (e.g., https://www.teton.ai/):
- Agent fetches the website to understand the specific product
- Extracts key features, pricing model, integration requirements
- Uses this information to make the tree vendor-specific

---

## Stage 3: Framework Construction

### Agent Presents Draft Structure
The agent presents a draft L1/L2 structure for user validation:

```
Based on your question about scaling fall detection, I recommend this structure:

DESIRABILITY - Is it worth doing?
├── Clinical/Safety Impact
├── Financial Impact
└── Stakeholder Value

FEASIBILITY - Can we do it?
├── Technical Capability
├── Operational Capability
└── Resource Availability

VIABILITY - Will it last?
├── Regulatory/Compliance
├── Sustainability
└── Risk Profile

Does this framework capture your decision dimensions, or would you like to adjust?
```

### User Options
- **Approve as-is** → Proceed to next stage
- **Add a dimension** → "Add 'Competitive Positioning' under Desirability"
- **Remove a dimension** → "We don't need Resource Availability, budget is approved"
- **Rename for terminology** → "Call it 'Scalability' not 'Viability'"

---

## Stage 4: MECE Validation Loop

Before proceeding, the `validate_mece_structure` tool runs automatically.

### Validation Checks
- **Overlaps:** "Warning: 'Financial Impact' and 'Sustainability/Maintenance Costs' may overlap. Clarify boundaries?"
- **Gaps:** "Note: No dimension addresses 'Competitive Response Risk' - is this intentional?"
- **Level consistency:** "All L2 items are strategic-level ✓"

### Loop Behavior
1. If issues found → Agent proposes fixes
2. User approves or modifies proposed fixes
3. Validation runs again
4. Loop continues until structure passes all checks

---

## Stage 5: L3 Leaf Generation

The agent generates detailed, measurable questions (L3 leaves) for each L2 branch.

### Leaf Attributes
For each L3 leaf, the agent determines:

| Attribute | Description |
|-----------|-------------|
| **Label** | Human-readable name |
| **Question** | The specific question this leaf answers |
| **Metric Type** | Quantitative, qualitative, or binary |
| **Target** | What "good" looks like |
| **Data Source** | Where to find the answer |

### Example Output (One Branch)

```
L2: Clinical/Safety Impact

├── Fall Incident Reduction
│   Question: "What is the measured reduction in fall incidents?"
│   Metric: Quantitative
│   Target: >25% reduction vs baseline
│   Source: Pilot incident logs

├── Response Time Improvement
│   Question: "How much faster do staff respond to falls?"
│   Metric: Quantitative
│   Target: >50% faster response
│   Source: Time-to-response logs

└── Injury Severity Reduction
    Question: "Are fall-related injuries less severe when detected?"
    Metric: Quantitative
    Target: Reduction in ER transfers, hospitalizations
    Source: Medical records, insurance claims
```

### User Interaction
The agent presents leaves progressively, branch by branch, allowing user input:
- "Add a leaf for 'False Alarm Rate' under Clinical Impact"
- "Change the target for Response Time to >40%"
- "That data source isn't available - use 'Staff interviews' instead"

---

## Stage 6: Scoring Guidance Generation

Once the tree structure is complete, the agent generates supporting materials.

### 1. Scoring Rubric
How to rate each L3 leaf on a 0-10 scale with anchor descriptions:
- 0-2: No evidence / Major concerns
- 3-4: Limited evidence / Significant gaps
- 5-6: Moderate evidence / Some concerns
- 7-8: Strong evidence / Minor gaps
- 9-10: Conclusive evidence / Exceeds targets

### 2. Weighting Recommendations
- Default: Equal weights across all dimensions
- User can adjust: "Clinical Impact should be 2x weighted vs Financial"
- Weights documented in metadata for transparency

### 3. Decision Thresholds

| Decision | Criteria |
|----------|----------|
| **SCALE** | All L1 dimensions score ≥7.0 |
| **CONDITIONAL SCALE** | All L1 dimensions score ≥5.0 with clear mitigation plans for gaps |
| **NO-GO** | Any L1 dimension scores <5.0 with no viable mitigation path |
| **NEEDS MORE DATA** | Insufficient data to score >50% of L3 leaves |

---

## Stage 7: Output Generation

The agent produces the final deliverable in the user's preferred format.

### Output Options

| Format | Use Case |
|--------|----------|
| **Structured JSON** | Programmatic use, dashboards, further processing |
| **Markdown Document** | Sharing with stakeholders, pasting into documents |
| **Interactive Artifact** | React-based tree visualization with expandable nodes |

### JSON Output Structure
```json
{
  "question": "Should we scale...",
  "framework": "MECE Issue Tree",
  "version": "1.0",
  "date": "2025-11-20",
  "levels": 3,
  "tree": {
    "L1_DESIRABILITY": {...},
    "L1_FEASIBILITY": {...},
    "L1_VIABILITY": {...}
  },
  "metadata": {
    "mece_validation": {...},
    "usage_instructions": {...},
    "decision_logic": {...}
  }
}
```

---

## Stage 8: Persistence & Next Steps

### Automatic Actions
1. **Saves the analysis** to persistent storage (JSON file with versioning)
2. **Records session metadata** for future retrieval

### Offered Next Actions
- "Would you like me to create a 2x2 prioritization matrix for the L3 hypotheses?"
- "Should I generate a research plan to fill data gaps?"
- "Would you like to score this tree now based on what you know?"

### Future Session Access
User can return later with prompts like:
- "Load my fall detection analysis"
- "Show me the hypothesis tree we created last week"
- "Update the fall detection tree with new pilot data"

---

## Variation: URL-Based Input

When the user provides a URL (e.g., `https://www.teton.ai/`), additional processing occurs.

### Additional Steps
1. Agent fetches the URL and extracts product information
2. Tree becomes vendor-specific:
   - "Teton.ai Integration Capability" instead of generic "System Integration"
   - "Teton.ai Vendor Reliability" with specific assessment criteria
3. Research focuses on that specific vendor's track record, pricing, support model
4. L3 questions reference Teton-specific data points

### Example Vendor-Specific Leaf
```
L3: Teton.ai System Integration
Question: "Can Teton.ai integrate with our existing nurse call and EHR systems?"
Metric: Binary
Target: Proven integration with [specific systems in use]
Source: Teton.ai technical documentation, pilot integration testing
```

---

## Summary: User Journey Map

| Stage | User Action | Agent Action | Output |
|-------|-------------|--------------|--------|
| 1. Intake | Asks strategic question | Classifies, recommends framework | Framework recommendation |
| 2. Research | Confirms/provides context | Parallel research | Research findings |
| 3. Framework | Reviews L1/L2 structure | Presents draft framework | Draft tree structure |
| 4. Validation | Approves adjustments | MECE validation loop | Validated structure |
| 5. Leaves | Refines L3 leaves | Generates measurable questions | Complete tree |
| 6. Scoring | Accepts scoring model | Generates rubric & thresholds | Scoring guidance |
| 7. Output | Chooses output format | Produces deliverable | Final MECE Tree |
| 8. Persist | Continues or saves | Persists for future sessions | Saved analysis |

---

## Design Principles

1. **Progressive Disclosure** - Don't overwhelm; reveal complexity gradually
2. **User Control** - Every agent recommendation can be overridden
3. **Transparency** - Show reasoning, not just outputs
4. **Iterative Refinement** - Support multiple passes through the workflow
5. **Persistence** - Never lose work; always recoverable

---

## Related Documents

- `capstone_architecture_plan.md` - Technical architecture
- `README.md` - Project overview
- `MECE_Tree_Example.json` - Sample output format
