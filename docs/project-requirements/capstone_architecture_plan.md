# Strategic Consultant Agent - Capstone Architecture Plan

## Project Overview

**Project Name:** HypothesisTree Pro - Strategic Decision Support Agent

**Core Value Proposition:** An AI-powered strategic consultant that helps users decompose complex business problems into MECE hypothesis trees, prioritize with 2x2 matrices, and iteratively refine analysis with validation loops.

**Key Differentiator:** Unlike one-shot analysis tools, this agent produces professional MBB-quality strategic frameworks with research-grounded hypotheses, test designs, and critical path identification.

**Use Case Example:** "Should we launch a fall detection product for eldercare facilities?"

---

## Course Alignment Checklist

### Day 1A: From Prompt to Action âœ…
| Feature | Implementation |
|---------|----------------|
| LlmAgent creation | Main strategic_consultant_agent |
| Tool integration | Custom MBB framework tools |
| Instruction design | Strategic consultant persona |
| Model configuration | Gemini with retry options |

### Day 1B: Agent Architectures âœ…
| Feature | Implementation |
|---------|----------------|
| SequentialAgent | Main workflow: Research â†’ Analysis â†’ Prioritization |
| ParallelAgent | Concurrent research streams (market + competitor) |
| LoopAgent | MECE validation refinement loops |
| Multi-agent orchestration | Specialized agents for each phase |

### Day 2A: Agent Tools âœ…
| Feature | Implementation |
|---------|----------------|
| FunctionTool creation | generate_hypothesis_tree, generate_2x2_matrix, validate_mece_structure |
| Google Search integration | Research agent for benchmarks |
| Tool parameter design | Framework selection, custom inputs |
| Tool output structure | Structured JSON/dict returns |

### Day 2B: Tools Best Practices âš ï¸
| Feature | Implementation |
|---------|----------------|
| MCP integration | NOT USED (design decision) |
| Tool validation patterns | MECE validator tool |
| Error handling | Tool error responses |

### Day 3A: Agent Sessions âœ…
| Feature | Implementation |
|---------|----------------|
| Session memory | Multi-turn conversation context |
| InMemorySessionService | Active session management |
| Context preservation | Link analyses together |

### Day 3B: Agent Memory âœ…
| Feature | Implementation |
|---------|----------------|
| Persistent memory | JSON files for analysis documents |
| Memory retrieval | Load previous project analyses |
| Cross-session recall | Return to projects days/weeks later |

### Day 4A: Agent Observability âœ…
| Feature | Implementation |
|---------|----------------|
| LoggingPlugin | Debug traces for all tool calls |
| Debug logging | Decision path visibility |
| Error tracing | Tool failure logging |

### Day 4B: Agent Evaluation âœ…
| Feature | Implementation |
|---------|----------------|
| Test case design | Tool trajectory tests |
| Evaluation criteria | Tool selection accuracy |
| evalset.json files | Multiple test scenarios |
| adk eval command | CLI evaluation |
| Tool trajectory validation | Core evaluation method |

### Day 5B: Agent Deployment âš ï¸
| Feature | Implementation |
|---------|----------------|
| Production patterns | Basic implementation |
| Error handling | Implemented in tools |

---

## Architecture Design

### High-Level Architecture

```
strategic_analyzer (SequentialAgent) â† Main Orchestrator
â”‚
â”œâ”€ PHASE 1: research_phase (ParallelAgent) â† PERFORMANCE
â”‚   â”œâ”€ market_researcher (LlmAgent + google_search)
â”‚   â””â”€ competitor_researcher (LlmAgent + google_search)
â”‚
â”œâ”€ PHASE 2: analysis_phase (LoopAgent) â† QUALITY
â”‚   â”œâ”€ hypothesis_generator (LlmAgent)
â”‚   â””â”€ mece_validator (FunctionTool)
â”‚   â””â”€ [loops until MECE compliant or max_iterations]
â”‚
â””â”€ PHASE 3: prioritizer (LlmAgent) â† OUTPUT
    â””â”€ Creates 2x2 matrix from validated hypotheses
```

### Agent Definitions

#### 1. strategic_analyzer (SequentialAgent)
- **Role:** Main orchestrator that coordinates the three phases
- **Flow:** Research â†’ Analysis â†’ Prioritization (in order)

#### 2. research_phase (ParallelAgent)
- **Role:** Gathers external data simultaneously
- **Sub-agents:**
  - market_researcher: Market size, growth, trends
  - competitor_researcher: Competitive landscape, benchmarks
- **Why Parallel:** Faster execution, independent research streams

#### 3. analysis_phase (LoopAgent)
- **Role:** Generates and validates hypothesis tree
- **Sub-agents:**
  - hypothesis_generator: Creates hypotheses using chosen framework
  - mece_validator: Checks for overlaps and gaps
- **Loop Logic:** Continues until MECE compliant OR max 3 iterations
- **Why Loop:** Iterative refinement ensures quality output

#### 4. prioritizer (LlmAgent)
- **Role:** Takes validated hypotheses, creates prioritization matrix
- **Output:** 2x2 Impact vs Effort matrix with recommendations

---

## Custom Tools (FunctionTools)

### Tool 1: generate_hypothesis_tree
```
Purpose: Generate MECE hypothesis structure for strategic problems

Parameters:
- problem (str): The strategic question to analyze
- framework (str): One of [product_launch, market_entry, strategy, operations, growth, custom]
- custom_levels (List[str], optional): User-defined MECE categories

Returns:
- Dict with framework structure, levels, and hypothesis placeholders

Frameworks Supported:
1. product_launch: Desirability / Feasibility / Scalability
2. market_entry: Porter's Five Forces
3. strategy: 3Cs (Customer / Company / Competition)
4. operations: Cost / Quality / Speed
5. growth: Market / Product / Channel / Pricing
6. custom: User-defined levels
```

### Tool 2: generate_2x2_matrix
```
Purpose: Create prioritization or positioning matrix

Parameters:
- items (List[str]): Items to plot (hypotheses, features, etc.)
- x_axis (str): X-axis label (default: "Effort")
- y_axis (str): Y-axis label (default: "Impact")
- matrix_type (str): One of [prioritization, bcg, ansoff, eisenhower, risk, custom]

Returns:
- Dict with quadrant definitions, item placements, and recommendations

Matrix Types Supported:
1. prioritization: Impact vs Effort (Quick Wins, Strategic Bets, Fill Later, Hard Slogs)
2. bcg: Growth-Share Matrix (Stars, Cash Cows, Question Marks, Dogs)
3. risk: Likelihood vs Impact (Monitor, Mitigate, Accept, Contingency)
4. eisenhower: Urgency vs Importance
5. custom: User-defined axes
```

### Tool 3: validate_mece_structure
```
Purpose: Check if a structure is Mutually Exclusive, Collectively Exhaustive

Parameters:
- structure (Dict): Structure with 'levels' key containing categories

Returns:
- is_mece (bool): Whether structure passes validation
- issues (Dict): Overlaps found, gaps identified
- suggestions (List[str]): Improvement recommendations

Validation Checks:
1. Overlap detection (e.g., "Cost" and "Scalability" may overlap)
2. Gap detection (e.g., missing "Regulatory" in healthcare)
3. Level consistency (not mixing strategic and tactical)
```

### Tool 4: save_analysis
```
Purpose: Persist analysis to JSON file for cross-session access

Parameters:
- project_name (str): Unique identifier for the project
- analysis_type (str): hypothesis_tree, matrix, research
- content (Dict): The analysis content to save

Returns:
- filepath (str): Where the file was saved
- version (int): Version number of this save
```

### Tool 5: load_analysis
```
Purpose: Retrieve previous analysis from storage

Parameters:
- project_name (str): Project to load
- analysis_type (str, optional): Specific analysis type
- version (int, optional): Specific version (default: latest)

Returns:
- Dict with saved analysis content and metadata
```

---

## Memory & Storage Architecture

### Session Memory (InMemorySessionService)
**Purpose:** Track conversation context within a single chat
**Contents:**
- Current project name
- Tools called this session
- Previous analysis outputs
- User clarifications and refinements

### Persistent Memory (JSON Files)
**Purpose:** Store analysis documents across sessions
**Location:** `/user_data/projects/`
**Structure:**
```
/user_data/
â”œâ”€â”€ projects/
â”‚   â”œâ”€â”€ fall_detection_analysis/
â”‚   â”‚   â”œâ”€â”€ hypothesis_tree_v1.json
â”‚   â”‚   â”œâ”€â”€ hypothesis_tree_v2.json
â”‚   â”‚   â”œâ”€â”€ research_findings.json
â”‚   â”‚   â”œâ”€â”€ priority_matrix.json
â”‚   â”‚   â””â”€â”€ project_metadata.json
â”‚   â””â”€â”€ telehealth_market_entry/
â”‚       â””â”€â”€ ...
â””â”€â”€ user_preferences.json
```

### Feedback Storage (SQLite)
**Purpose:** Capture user feedback for tool improvement
**Tables:**
```
user_feedback:
- id, user_id, session_id
- tool_used (hypothesis_tree, matrix, mece_validator)
- rating (1-5)
- feedback_text
- timestamp
- project_name

usage_analytics:
- id, tool_used
- parameters_used
- success (bool)
- duration_ms
- timestamp
```

---

## Output Documents

### Primary Output: Hypothesis Tree (Markdown)
```markdown
# [Project Name] - Strategic Hypothesis Map

**Framework:** [Selected framework]
**Created:** [Date]
**Last Updated:** [Date]
**MECE Validated:** âœ…

## Executive Summary
[2-3 sentence overview]

## Hypothesis Structure

### 1. [Category 1 - e.g., Desirability]

#### H1: [Hypothesis statement]
**Status:** ðŸ”´ UNTESTED | ðŸŸ¡ IN PROGRESS | âœ… VALIDATED | âŒ INVALIDATED
**Confidence:** [X]%

**Test Design:**
- Method: [How to test]
- Data Needed: [What data]
- Timeline: [Duration]
- Cost: [Budget]
- Success Criteria: [Threshold]
- Owner: [Who]

**Risks:**
- Risk: [What could go wrong]
- So-What: [Business impact]
- Mitigation: [How to address]

**Benchmarks:**
- [External data points]

[Repeat for each hypothesis]

## Critical Path
[Ordered sequence of hypothesis validation]

## MECE Validation
âœ… Mutually Exclusive: [Status]
âœ… Collectively Exhaustive: [Status]
```

### Secondary Output: Priority Matrix (Markdown)
```markdown
# [Project Name] - Prioritization Matrix

**Matrix Type:** [Impact vs Effort]
**Items Analyzed:** [Count]

## Visual Matrix
[ASCII or description of 2x2 grid]

## Quadrant Analysis

### Q1 - Quick Wins (High Impact, Low Effort)
[Items with rationale]

### Q2 - Strategic Bets (High Impact, High Effort)
[Items with rationale]

### Q3 - Fill Later (Low Impact, Low Effort)
[Items with rationale]

### Q4 - Hard Slogs (Low Impact, High Effort)
[Items with rationale]

## Recommended Sequence
[Ordered action plan]
```

---

## Evaluation Strategy

### Test File: strategic_consultant.evalset.json

#### Test Case 1: Correct Framework Selection
```json
{
  "eval_id": "framework_selection_product_launch",
  "conversation": [{
    "user_content": {"parts": [{"text": "Should we launch a telehealth product?"}]}
  }],
  "criteria": {
    "tool_trajectory": {
      "expected_tools": [{
        "name": "generate_hypothesis_tree",
        "args_contain": {"framework": "product_launch"}
      }]
    }
  }
}
```

#### Test Case 2: Market Entry Uses Porter's
```json
{
  "eval_id": "framework_selection_market_entry",
  "conversation": [{
    "user_content": {"parts": [{"text": "Should we enter the European market?"}]}
  }],
  "criteria": {
    "tool_trajectory": {
      "expected_tools": [{
        "name": "generate_hypothesis_tree",
        "args_contain": {"framework": "market_entry"}
      }]
    }
  }
}
```

#### Test Case 3: MECE Validation Called
```json
{
  "eval_id": "mece_validation_triggered",
  "conversation": [{
    "user_content": {"parts": [{"text": "Analyze using Revenue, Cost, and Risk categories"}]}
  }],
  "criteria": {
    "tool_trajectory": {
      "expected_tools": [
        {"name": "validate_mece_structure", "min_calls": 1}
      ]
    }
  }
}
```

#### Test Case 4: Prioritization Request
```json
{
  "eval_id": "prioritization_uses_matrix",
  "conversation": [{
    "user_content": {"parts": [{"text": "Prioritize these hypotheses: H1, H2, H3, H4"}]}
  }],
  "criteria": {
    "tool_trajectory": {
      "expected_tools": [{
        "name": "generate_2x2_matrix",
        "args_contain": {"matrix_type": "prioritization"}
      }]
    }
  }
}
```

#### Test Case 5: Multi-Tool Workflow
```json
{
  "eval_id": "full_analysis_workflow",
  "conversation": [{
    "user_content": {"parts": [{"text": "Analyze fall detection launch, then prioritize the hypotheses"}]}
  }],
  "criteria": {
    "tool_trajectory": {
      "expected_tools": [
        {"name": "generate_hypothesis_tree"},
        {"name": "generate_2x2_matrix"}
      ],
      "min_total_calls": 2
    }
  }
}
```

### Test Config: test_config.json
```json
{
  "criteria": {
    "tool_trajectory_avg_score": 0.8,
    "response_match_score": 0.7
  }
}
```

---

## Implementation Roadmap

### Phase 1: Core Framework (Saturday Morning)
**Duration:** 3-4 hours

- [ ] Set up project structure
- [ ] Implement FunctionTools:
  - [ ] generate_hypothesis_tree
  - [ ] generate_2x2_matrix
  - [ ] validate_mece_structure
- [ ] Create framework definitions (product_launch, market_entry, etc.)
- [ ] Basic tool testing

### Phase 2: Multi-Agent Architecture (Saturday Afternoon)
**Duration:** 3-4 hours

- [ ] Create individual agents:
  - [ ] market_researcher
  - [ ] competitor_researcher
  - [ ] hypothesis_generator
  - [ ] prioritizer
- [ ] Build ParallelAgent (research_phase)
- [ ] Build LoopAgent (analysis_phase)
- [ ] Build SequentialAgent (strategic_analyzer)
- [ ] Integration testing

### Phase 3: Memory & Persistence (Sunday Morning)
**Duration:** 2-3 hours

- [ ] Implement save_analysis tool
- [ ] Implement load_analysis tool
- [ ] Set up JSON file storage structure
- [ ] SQLite feedback schema
- [ ] Cross-session testing

### Phase 4: Observability & Evaluation (Sunday Afternoon)
**Duration:** 2-3 hours

- [ ] Add LoggingPlugin
- [ ] Create evalset.json test cases
- [ ] Create test_config.json
- [ ] Run adk eval and iterate
- [ ] Debug and refine agent instructions

### Phase 5: Documentation & Demo (Sunday Evening)
**Duration:** 2 hours

- [ ] Clean up Kaggle notebook
- [ ] Add markdown explanations
- [ ] Create demo scenarios
- [ ] Final testing
- [ ] Submit to Kaggle

---

## File Structure

```
strategic_consultant_agent/
â”œâ”€â”€ __init__.py
â”œâ”€â”€ agent.py                    # Main SequentialAgent definition
â”œâ”€â”€ sub_agents/
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ research_agents.py      # ParallelAgent with researchers
â”‚   â”œâ”€â”€ analysis_agents.py      # LoopAgent with generator + validator
â”‚   â””â”€â”€ prioritizer_agent.py    # Final prioritization agent
â”œâ”€â”€ tools/
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ hypothesis_tree.py      # generate_hypothesis_tree
â”‚   â”œâ”€â”€ matrix_2x2.py           # generate_2x2_matrix
â”‚   â”œâ”€â”€ mece_validator.py       # validate_mece_structure
â”‚   â””â”€â”€ storage.py              # save_analysis, load_analysis
â”œâ”€â”€ frameworks/
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ definitions.py          # STANDARD_FRAMEWORKS dict
â”‚   â””â”€â”€ matrix_types.py         # MATRIX_TYPES dict
â”œâ”€â”€ storage/
â”‚   â”œâ”€â”€ projects/               # JSON analysis files
â”‚   â””â”€â”€ feedback.db             # SQLite feedback database
â”œâ”€â”€ evaluation/
â”‚   â”œâ”€â”€ strategic_consultant.evalset.json
â”‚   â””â”€â”€ test_config.json
â””â”€â”€ demo_notebook.ipynb         # Kaggle submission notebook
```

---

## Demo Scenarios for Kaggle Notebook

### Scenario 1: Product Launch Analysis
```
User: "Should we launch a fall detection product for eldercare facilities?"

Expected Flow:
1. Agent selects product_launch framework
2. ParallelAgent researches market + competitors
3. LoopAgent generates hypotheses, validates MECE
4. Outputs hypothesis tree with 9 hypotheses across D/F/S
```

### Scenario 2: Market Entry with Custom Framework
```
User: "Analyze European telehealth market entry using Revenue, Risk, and Operations"

Expected Flow:
1. Agent recognizes custom framework request
2. Validates custom structure with validate_mece_structure
3. Generates hypothesis tree with custom categories
4. Flags any MECE issues for user refinement
```

### Scenario 3: Prioritization Request
```
User: "I have these 6 hypotheses from my analysis. Help me prioritize them."

Expected Flow:
1. Agent calls generate_2x2_matrix with prioritization type
2. Scores each hypothesis on Impact and Effort
3. Places in quadrants
4. Recommends testing sequence (Quick Wins first)
```

### Scenario 4: Return to Previous Project
```
User: "Load my fall detection analysis from last week and update H4 status"

Expected Flow:
1. Agent calls load_analysis to retrieve saved project
2. Displays current state
3. User updates hypothesis status
4. Agent saves new version
```

---

## Success Criteria

### Course Alignment
- [ ] Uses SequentialAgent, ParallelAgent, and LoopAgent (Day 1B)
- [ ] Implements custom FunctionTools (Day 2A)
- [ ] Demonstrates session and persistent memory (Day 3)
- [ ] Includes LoggingPlugin for observability (Day 4A)
- [ ] Has evaluation test cases with tool trajectory (Day 4B)

### Quality Metrics
- [ ] MECE validation correctly identifies overlaps/gaps
- [ ] Framework selection matches problem type
- [ ] Hypothesis trees have complete test designs
- [ ] 2x2 matrices have actionable quadrant recommendations
- [ ] Cross-session persistence works reliably

### Demo Requirements
- [ ] Clear problem â†’ structured analysis workflow
- [ ] Shows iterative refinement via LoopAgent
- [ ] Demonstrates parallel research performance benefit
- [ ] Includes user feedback mechanism
- [ ] Professional MBB-quality output format

---

## Notes for Implementation Session

1. **Start with tools first** - Get FunctionTools working before building agents
2. **Test incrementally** - Verify each agent before composing into SequentialAgent
3. **Keep agent instructions tight** - Clear, specific instructions improve tool selection
4. **Log everything** - LoggingPlugin is essential for debugging multi-agent flows
5. **Eval early** - Write test cases before finishing implementation to guide development

---

*Document Created: November 2025*
*For: Kaggle Agents Intensive Capstone Project*
*Based on: 5-Day Google ADK Course (November 10-14, 2025)*