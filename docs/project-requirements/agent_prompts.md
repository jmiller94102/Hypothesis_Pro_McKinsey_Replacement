# HypothesisTree Pro - Agent Definitions & Prompts

## Overview

This document contains the exact ADK class definitions, imports, and system prompts for each agent in the HypothesisTree Pro system. **Claude Code should use these patterns exactly as specified.**

---

## Critical ADK Import Statement

```python
# REQUIRED IMPORTS - Use these exact imports from google.adk
from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import FunctionTool, google_search
from google.genai import types

# For retry configuration
from google.genai.errors import ClientError, ServerError
```

> ⚠️ **Note:** The course notebooks use `Agent` class, NOT `LlmAgent`. Ensure all agent definitions use `Agent`.

---

## Retry Configuration

```python
# Standard retry configuration for all agents
retry_config = types.RetryConfig(
    initial_delay=1.0,
    delay_multiplier=2.0,
    max_delay=60.0,
    retry_count=3,
    retry_on_status_codes=[429, 500, 503]
)
```

---

## Agent Architecture

```
strategic_analyzer (SequentialAgent) ← Root Orchestrator
│
├─ PHASE 1: research_phase (ParallelAgent)
│   ├─ market_researcher (Agent + google_search)
│   └─ competitor_researcher (Agent + google_search)
│
├─ PHASE 2: analysis_phase (LoopAgent)
│   ├─ hypothesis_generator (Agent + generate_hypothesis_tree)
│   └─ mece_validator (Agent + validate_mece_structure)
│   └─ [loops until MECE compliant or max_iterations=3]
│
└─ PHASE 3: prioritizer (Agent + generate_2x2_matrix)
```

---

## Agent Definitions

### 1. Root Agent: strategic_analyzer

**Type:** `SequentialAgent`
**Purpose:** Orchestrate the three-phase workflow in order

```python
strategic_analyzer = SequentialAgent(
    name="strategic_analyzer",
    sub_agents=[research_phase, analysis_phase, prioritizer],
)
```

> **Note:** SequentialAgent has no `model` or `instruction` - it simply runs sub_agents in order.

---

### 2. Research Phase: research_phase

**Type:** `ParallelAgent`
**Purpose:** Run market and competitor research simultaneously for performance

```python
research_phase = ParallelAgent(
    name="research_phase",
    sub_agents=[market_researcher, competitor_researcher],
)
```

> **Note:** ParallelAgent has no `model` or `instruction` - it runs sub_agents concurrently.

---

### 3. Market Researcher Agent

**Type:** `Agent`
**Purpose:** Gather market size, trends, benchmarks, and industry data

```python
market_researcher = Agent(
    name="market_researcher",
    model=Gemini(
        model="gemini-2.0-flash",
        retry_options=retry_config
    ),
    instruction=MARKET_RESEARCHER_PROMPT,
    tools=[google_search],
    output_key="market_research"
)
```

**System Prompt:**

```python
MARKET_RESEARCHER_PROMPT = """You are a market research analyst specializing in healthcare technology and senior living industries.

Your task is to research the market context for: {problem}

Focus your research on:
1. **Market Size & Growth**: Total addressable market, growth rates, key segments
2. **Industry Trends**: Technology adoption trends, regulatory changes, demographic shifts
3. **Benchmarks**: Industry standards for success metrics, typical ROI, adoption rates
4. **Key Players**: Major vendors, market leaders, emerging disruptors

Use the google_search tool to find current, credible data. Prioritize:
- Industry reports (McKinsey, Deloitte, KLAS, LeadingAge)
- Trade publications (Senior Housing News, McKnight's)
- Academic research and government statistics

Output Format:
Provide a structured summary with citations. Include specific numbers where available.
Do NOT make up statistics - only report what you find in search results.

If search results are limited, note the data gaps clearly."""
```

---

### 4. Competitor Researcher Agent

**Type:** `Agent`
**Purpose:** Analyze competitive landscape, vendor capabilities, and alternatives

```python
competitor_researcher = Agent(
    name="competitor_researcher",
    model=Gemini(
        model="gemini-2.0-flash",
        retry_options=retry_config
    ),
    instruction=COMPETITOR_RESEARCHER_PROMPT,
    tools=[google_search],
    output_key="competitor_research"
)
```

**System Prompt:**

```python
COMPETITOR_RESEARCHER_PROMPT = """You are a competitive intelligence analyst specializing in healthcare technology.

Your task is to research the competitive landscape for: {problem}

Focus your research on:
1. **Key Vendors**: Who are the major players in this space?
2. **Product Capabilities**: What features do they offer? What are their strengths/weaknesses?
3. **Pricing Models**: How do vendors typically price (per unit, subscription, etc.)?
4. **Customer Reviews**: What do customers say about implementation, support, results?
5. **Case Studies**: Any published success stories or failure analyses?

If a specific vendor URL was provided, research that vendor specifically:
- Company background and financial stability
- Product features and roadmap
- Customer testimonials and reviews
- Integration capabilities
- Support and SLA offerings

Use the google_search tool to find current information. Search for:
- "[vendor name] reviews"
- "[vendor name] case study senior living"
- "[technology type] vendors comparison"

Output Format:
Provide a structured competitive analysis. Be objective - include both positives and negatives.
Note any information gaps or areas where data was not available."""
```

---

### 5. Analysis Phase: analysis_phase

**Type:** `LoopAgent`
**Purpose:** Generate hypothesis tree and validate MECE compliance iteratively

```python
analysis_phase = LoopAgent(
    name="analysis_phase",
    sub_agents=[hypothesis_generator, mece_validator_agent],
    max_iterations=3
)
```

> **Note:** LoopAgent continues until `exit_loop` is called or max_iterations reached.

---

### 6. Hypothesis Generator Agent

**Type:** `Agent`
**Purpose:** Generate MECE hypothesis tree using selected framework

```python
hypothesis_generator = Agent(
    name="hypothesis_generator",
    model=Gemini(
        model="gemini-2.0-flash",
        retry_options=retry_config
    ),
    instruction=HYPOTHESIS_GENERATOR_PROMPT,
    tools=[
        FunctionTool(generate_hypothesis_tree)
    ],
    output_key="hypothesis_tree"
)
```

**System Prompt:**

```python
HYPOTHESIS_GENERATOR_PROMPT = """You are a senior strategy consultant from a top-tier consulting firm (McKinsey, BCG, Bain).

Your task is to create a MECE (Mutually Exclusive, Collectively Exhaustive) hypothesis tree for:

**Strategic Question:** {problem}
**Selected Framework:** {framework}

**Context from Research:**
- Market Research: {market_research}
- Competitive Analysis: {competitor_research}

**Instructions:**

1. Use the `generate_hypothesis_tree` tool with the appropriate framework
2. Ensure all L1 categories are mutually exclusive (no overlap)
3. Ensure all L1 categories are collectively exhaustive (cover the full scope)
4. Generate specific, measurable L3 leaves with:
   - Clear questions that can be answered with data
   - Appropriate metric types (quantitative, qualitative, binary)
   - Realistic targets based on industry benchmarks from research
   - Specific data sources where answers can be found

5. Incorporate insights from the market and competitor research into:
   - Benchmark targets (use industry standards)
   - Data sources (reference specific reports or sources found)
   - Risk factors (based on competitive dynamics)

**Quality Standards:**
- Every L3 leaf must be answerable (not vague)
- Targets should be specific and measurable
- Data sources should be realistic and accessible
- The tree should enable a clear GO/NO-GO decision when scored

If the MECE validator returns issues, incorporate the feedback and regenerate."""
```

---

### 7. MECE Validator Agent

**Type:** `Agent`
**Purpose:** Validate MECE compliance and trigger exit or refinement

```python
# Exit loop function for LoopAgent
def exit_loop() -> dict:
    """Call this function when the hypothesis tree passes MECE validation."""
    return {"status": "MECE validation passed. Proceeding to prioritization."}

mece_validator_agent = Agent(
    name="mece_validator_agent",
    model=Gemini(
        model="gemini-2.0-flash",
        retry_options=retry_config
    ),
    instruction=MECE_VALIDATOR_PROMPT,
    tools=[
        FunctionTool(validate_mece_structure),
        FunctionTool(exit_loop)
    ],
    output_key="validation_result"
)
```

**System Prompt:**

```python
MECE_VALIDATOR_PROMPT = """You are a quality assurance specialist for strategic frameworks.

Your task is to validate the MECE compliance of the hypothesis tree:

**Hypothesis Tree:** {hypothesis_tree}

**Validation Process:**

1. Call the `validate_mece_structure` tool with the hypothesis tree
2. Review the validation results

**Decision Logic:**

IF validation returns `is_mece: true`:
- Call the `exit_loop` function to proceed to prioritization
- Do NOT generate any additional content

IF validation returns `is_mece: false`:
- Review the issues identified (overlaps, gaps, inconsistencies)
- Provide specific, actionable feedback for the hypothesis generator
- Suggest concrete fixes for each issue
- Do NOT call exit_loop

**Feedback Format (when issues found):**

```
VALIDATION FAILED

Issues Found:
1. [Issue type]: [Description]
   Suggested Fix: [Specific recommendation]

2. [Issue type]: [Description]
   Suggested Fix: [Specific recommendation]

Please regenerate the hypothesis tree addressing these issues.
```

Be rigorous but practical. Minor issues can be noted but shouldn't block progress."""
```

---

### 8. Prioritizer Agent

**Type:** `Agent`
**Purpose:** Create 2x2 matrix and recommend testing sequence

```python
prioritizer = Agent(
    name="prioritizer",
    model=Gemini(
        model="gemini-2.0-flash",
        retry_options=retry_config
    ),
    instruction=PRIORITIZER_PROMPT,
    tools=[
        FunctionTool(generate_2x2_matrix)
    ],
    output_key="priority_matrix"
)
```

**System Prompt:**

```python
PRIORITIZER_PROMPT = """You are a strategy consultant specializing in prioritization and resource allocation.

Your task is to prioritize the hypotheses from the validated tree:

**Hypothesis Tree:** {hypothesis_tree}

**Instructions:**

1. Extract all L3 hypotheses from the tree
2. For each hypothesis, assess:
   - **Impact**: How critical is this to the overall decision? (High/Medium/Low)
   - **Effort**: How hard is it to test/validate? (High/Medium/Low)

3. Call `generate_2x2_matrix` with:
   - matrix_type: "prioritization"
   - All L3 hypotheses as items
   - Your impact and effort assessments

4. Based on the matrix output, provide:
   - **Quick Wins** (High Impact, Low Effort): Test these first
   - **Strategic Bets** (High Impact, High Effort): Plan carefully
   - **Fill Later** (Low Impact, Low Effort): Do if time permits
   - **Deprioritize** (Low Impact, High Effort): Skip unless required

**Output Format:**

Provide a clear testing roadmap:

## Recommended Testing Sequence

### Phase 1: Quick Wins (Week 1-2)
- [Hypothesis]: [Why it's a quick win] [Suggested test approach]

### Phase 2: Strategic Bets (Week 3-6)
- [Hypothesis]: [Why it matters] [Suggested test approach]

### Phase 3: Fill Later (As needed)
- [Hypothesis]: [Brief note]

### Deprioritized
- [Hypothesis]: [Why it's deprioritized]

## Critical Path
Identify which hypotheses are "must validate" before the decision can be made."""
```

---

## Tool Definitions

### generate_hypothesis_tree

```python
def generate_hypothesis_tree(
    problem: str,
    framework: str = "scale_decision",
    custom_l1_categories: list[str] | None = None
) -> dict:
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
    # Implementation loads template from framework_templates.json
    # and generates specific L3 leaves based on context
    pass
```

### generate_2x2_matrix

```python
def generate_2x2_matrix(
    items: list[str],
    x_axis: str = "Effort",
    y_axis: str = "Impact",
    matrix_type: str = "prioritization",
    assessments: dict | None = None
) -> dict:
    """
    Create a 2x2 prioritization or positioning matrix.
    
    Args:
        items: List of items to plot (hypotheses, features, etc.)
        x_axis: Label for x-axis (default: "Effort")
        y_axis: Label for y-axis (default: "Impact")
        matrix_type: One of [prioritization, bcg, risk, eisenhower, custom]
        assessments: Optional dict of {item: {"x": score, "y": score}}
    
    Returns:
        dict: Matrix with quadrant definitions and item placements
    """
    pass
```

### validate_mece_structure

```python
def validate_mece_structure(
    structure: dict
) -> dict:
    """
    Validate a hierarchical structure for MECE compliance.
    
    Args:
        structure: Hypothesis tree structure to validate
    
    Returns:
        dict: {
            "is_mece": bool,
            "issues": {
                "overlaps": [...],
                "gaps": [...],
                "level_inconsistencies": [...]
            },
            "suggestions": [...]
        }
    """
    pass
```

### save_analysis / load_analysis

```python
def save_analysis(
    project_name: str,
    analysis_type: str,
    content: dict
) -> dict:
    """
    Persist analysis to JSON file for cross-session access.
    
    Args:
        project_name: Unique identifier for the project
        analysis_type: One of [hypothesis_tree, matrix, research]
        content: The analysis content to save
    
    Returns:
        dict: {"filepath": str, "version": int}
    """
    pass

def load_analysis(
    project_name: str,
    analysis_type: str | None = None,
    version: int | None = None
) -> dict:
    """
    Retrieve previous analysis from storage.
    
    Args:
        project_name: Project to load
        analysis_type: Specific analysis type (optional)
        version: Specific version number (optional, default: latest)
    
    Returns:
        dict: Saved analysis content with metadata
    """
    pass
```

---

## State Passing with output_key

The `output_key` parameter is critical for passing data between agents:

```python
# Agent output is stored in session state under this key
market_researcher = Agent(
    ...,
    output_key="market_research"  # Other agents access via {market_research}
)

# Later agents reference it in their instructions
hypothesis_generator = Agent(
    ...,
    instruction="...Context: {market_research}..."
)
```

**State Keys Used:**
- `market_research` - Output from market_researcher
- `competitor_research` - Output from competitor_researcher  
- `hypothesis_tree` - Output from hypothesis_generator
- `validation_result` - Output from mece_validator_agent
- `priority_matrix` - Output from prioritizer

---

## Running the Agent

```python
# Create runner
runner = InMemoryRunner(agent=strategic_analyzer)

# Run with user input
response = await runner.run(
    "Should we scale deployment of computer vision fall detection in senior living?"
)

# Or with debug output
response = await runner.run_debug(
    "Should we scale deployment of computer vision fall detection in senior living?"
)
```

---

## File Structure

```
strategic_consultant_agent/
├── __init__.py              # Exports root_agent
├── agent.py                 # Main SequentialAgent definition
├── sub_agents/
│   ├── __init__.py
│   ├── research_agents.py   # ParallelAgent + market/competitor researchers
│   ├── analysis_agents.py   # LoopAgent + generator/validator
│   └── prioritizer_agent.py # Prioritizer agent
├── tools/
│   ├── __init__.py
│   ├── hypothesis_tree.py   # generate_hypothesis_tree
│   ├── matrix_2x2.py        # generate_2x2_matrix
│   ├── mece_validator.py    # validate_mece_structure
│   └── persistence.py       # save_analysis, load_analysis
├── prompts/
│   └── instructions.py      # All prompt constants
├── data/
│   └── framework_templates.json
├── evaluation/
│   ├── strategic_consultant.evalset.json
│   └── test_config.json
└── storage/
    └── projects/            # Saved analyses
```

---

## Evaluation Setup

### evalset.json format

```json
{
  "eval_cases": [
    {
      "eval_id": "framework_selection_scale_decision",
      "conversation": [
        {
          "user_content": {
            "parts": [{"text": "Should we scale deployment of fall detection?"}]
          },
          "intermediate_data": {
            "tool_uses": [
              {
                "name": "generate_hypothesis_tree",
                "args": {"framework": "scale_decision"}
              }
            ]
          }
        }
      ]
    }
  ]
}
```

### test_config.json

```json
{
  "criteria": {
    "tool_trajectory_avg_score": 0.8,
    "response_match_score": 0.7
  }
}
```

### Running evaluation

```bash
adk eval strategic_consultant_agent evaluation/strategic_consultant.evalset.json \
    --config_file_path=evaluation/test_config.json \
    --print_detailed_results
```

---

## Related Documents

- `README.md` - Project overview and quick start
- `capstone_architecture_plan.md` - Detailed architecture
- `user_experience_workflow.md` - UX flow from user perspective
- `framework_templates.json` - Strategic framework data
- `examples/mece_tree_fall_detection.json` - Example output
