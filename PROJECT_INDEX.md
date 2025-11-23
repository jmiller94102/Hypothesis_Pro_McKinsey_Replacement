# HypothesisTree Pro - Project Index

**Generated**: 2025-11-23
**Project Status**: Phase 2 Complete (67% overall - 10/15 PRPs)
**Total Code**: 4,571 lines of Python
**Test Coverage**: 267 tests passing (115 Phase 1 + 152 Phase 2)

---

## PROJECT OVERVIEW

**Name**: HypothesisTree Pro - Strategic Decision Support Agent
**Purpose**: AI-powered strategic consultant using Google ADK to generate MECE hypothesis trees
**Tech Stack**: Python 3.11+, Google ADK, Google Gemini 2.0 Flash, SQLite (optional)
**Target**: Kaggle 5-Day AI Agents Course Capstone Project

### Core Value Proposition
Transform strategic questions like "Should we scale deployment of fall detection in senior living?" into professional MBB-quality hypothesis trees with:
- MECE (Mutually Exclusive, Collectively Exhaustive) structure
- 3-level analysis framework (L1 → L2 → L3)
- Prioritization matrices (2x2 BCG, Eisenhower, etc.)
- Iterative validation loops
- Persistent cross-session memory

---

## ARCHITECTURE OVERVIEW

### Multi-Agent Hierarchy (Google ADK)

```
strategic_analyzer (SequentialAgent - Root Orchestrator)
│
├─ Phase 1: research_phase (ParallelAgent)
│   ├─ market_researcher (Agent + google_search)
│   │   └─ output_key: "market_research"
│   └─ competitor_researcher (Agent + google_search)
│       └─ output_key: "competitor_research"
│
├─ Phase 2: analysis_phase (LoopAgent - max 3 iterations)
│   ├─ hypothesis_generator (Agent + generate_hypothesis_tree)
│   │   └─ output_key: "hypothesis_tree"
│   │   └─ references: {market_research}, {competitor_research}
│   └─ mece_validator (Agent + validate_mece_structure + exit_loop)
│       └─ output_key: "validation_result"
│       └─ references: {hypothesis_tree}
│       └─ calls exit_loop() when is_mece: true
│
└─ Phase 3: prioritizer (Agent + generate_2x2_matrix)
    └─ output_key: "priority_matrix"
    └─ references: {hypothesis_tree}
```

### Key Design Decisions

**ADK Pattern**: Uses `Agent` class (NOT `LlmAgent`) - critical for compatibility
**State Passing**: `output_key` → `{key}` references in instruction prompts
**Loop Control**: MECE validator calls `exit_loop()` when validation passes
**Framework Templates**: Pre-defined MECE structures loaded from JSON
**Persistence**: JSON file storage in `storage/projects/` with auto-versioning

---

## PROJECT STRUCTURE

```
strategic-evaluation-tree/
├── CLAUDE.md                     # Primary instructions for Claude Code (20.9 KB)
├── TASKS.md                      # Implementation tracker - 15 PRPs (19.9 KB)
├── PROJECT_INDEX.md              # This file - comprehensive project index
├── README.md                     # Quick start guide (7.4 KB)
├── .env                          # Environment variables (gitignored)
├── .env.example                  # Template for API keys
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies (5 packages)
├── pyproject.toml                # Package configuration
│
├── .claude/                      # Claude Code configuration
│   ├── settings.local.json       # Local settings
│   ├── SHARED-PATTERNS.md        # Validation patterns for sub-agents
│   ├── commands/                 # Slash commands
│   │   ├── recover-context.md    # Fast context recovery after /clear
│   │   ├── generate-prp.md       # Generate implementation guides
│   │   ├── execute-prp.md        # Execute single PRP with validation
│   │   └── execute-phase.md      # Automated batch PRP execution
│   └── skills/
│       └── save-session/         # Save progress before /clear
│           └── SKILL.md
│
├── docs/                         # Project documentation
│   └── project-requirements/     # Reference specifications
│       ├── README.md             # Project overview
│       ├── agent_prompts.md      # **CRITICAL**: ADK code patterns & prompts
│       ├── capstone_architecture_plan.md  # Architecture decisions
│       ├── user_experience_workflow.md    # User journey
│       ├── framework_templates.json       # 6 framework definitions
│       └── examples/
│           └── mece_tree_fall_detection.json  # Example output
│
├── PRPs/                         # Product Requirement Prompts (implementation guides)
│   ├── PRP-TEMPLATE.md           # Template for creating new PRPs
│   ├── tools/
│   │   └── prp-001-framework-templates-loading.md  # Completed
│   ├── agents/                   # Agent creation PRPs
│   ├── evaluation/               # Evaluation setup PRPs
│   └── integration/              # Integration PRPs
│
├── strategic_consultant_agent/   # Application code (4,571 lines total)
│   ├── __init__.py               # Package exports (root_agent)
│   ├── agent.py                  # Root SequentialAgent (strategic_analyzer)
│   │
│   ├── tools/                    # Custom FunctionTools (Phase 1 - COMPLETE)
│   │   ├── __init__.py
│   │   ├── framework_loader.py   # Load/validate framework templates
│   │   ├── hypothesis_tree.py    # Generate MECE hypothesis trees
│   │   ├── mece_validator.py     # Validate for overlaps/gaps
│   │   ├── matrix_2x2.py         # Generate prioritization matrices
│   │   └── persistence.py        # Save/load analyses (JSON storage)
│   │
│   ├── prompts/                  # System prompts (Phase 2 - COMPLETE)
│   │   ├── __init__.py
│   │   └── instructions.py       # All agent system prompts
│   │
│   ├── sub_agents/               # Individual agents (Phase 2 - COMPLETE)
│   │   ├── __init__.py
│   │   ├── research_agents.py    # ParallelAgent + researchers
│   │   ├── analysis_agents.py    # LoopAgent + generator + validator
│   │   └── prioritizer_agent.py  # Prioritizer agent
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   └── framework_templates.json  # Framework data (symlink)
│   │
│   └── storage/
│       └── projects/             # JSON persistence directory
│
├── tests/                        # Test suite (267 tests passing)
│   ├── __init__.py
│   ├── test_agent.py             # Root agent tests (29 tests)
│   │
│   ├── tools/                    # Tool tests (115 tests - Phase 1)
│   │   ├── __init__.py
│   │   ├── test_framework_loader.py      # 14 tests, 94% coverage
│   │   ├── test_hypothesis_tree.py       # 23 tests, 100% coverage
│   │   ├── test_mece_validator.py        # 16 tests
│   │   ├── test_matrix_2x2.py            # 28 tests, 99% coverage
│   │   └── test_persistence.py           # 34 tests, 96% coverage
│   │
│   ├── prompts/                  # Prompt tests (35 tests - Phase 2)
│   │   └── test_instructions.py
│   │
│   └── sub_agents/               # Agent tests (88 tests - Phase 2)
│       ├── test_research_agents.py       # 32 tests
│       ├── test_analysis_agents.py       # 40 tests
│       └── test_prioritizer_agent.py     # 16 tests
│
├── evaluation/                   # Evaluation test cases (NOT YET CREATED)
│   ├── strategic_consultant.evalset.json  # Test cases for adk eval
│   └── test_config.json          # Evaluation configuration
│
├── logs/                         # Log files directory
└── venv/                         # Virtual environment (gitignored)
```

---

## IMPLEMENTATION STATUS

### Overall Progress: 67% (10/15 PRPs)

| Phase | Status | PRPs | Tests | Coverage |
|-------|--------|------|-------|----------|
| **Phase 1: Core Tools** | ✓ COMPLETE | 5/5 | 115 | >90% avg |
| **Phase 2: Agent Architecture** | ✓ COMPLETE | 5/5 | 152 | N/A |
| **Phase 3: Memory & Persistence** | NOT STARTED | 0/2 | 0 | N/A |
| **Phase 4: Observability & Evaluation** | NOT STARTED | 0/3 | 0 | N/A |

### Phase 1: Core Tools ✓ COMPLETE

| PRP | Tool | Status | Tests | Coverage | Pylint |
|-----|------|--------|-------|----------|--------|
| PRP-001 | Framework Templates Loading | ✓ | 14 | 94% | 10.00/10 |
| PRP-002 | generate_hypothesis_tree | ✓ | 23 | 100% | 9.29/10 |
| PRP-003 | validate_mece_structure | ✓ | 16 | N/A | N/A |
| PRP-004 | generate_2x2_matrix | ✓ | 28 | 99% | 9.35/10 |
| PRP-005 | Persistence Tools | ✓ | 34 | 96% | 9.71/10 |

**Total**: 115 tests, average 97% coverage, average Pylint 9.59/10

### Phase 2: Agent Architecture ✓ COMPLETE

| PRP | Component | Status | Tests | Pylint |
|-----|-----------|--------|-------|--------|
| PRP-006 | System Prompts | ✓ | 35 | 10.00/10 |
| PRP-007 | Research Agents (ParallelAgent) | ✓ | 32 | 10.00/10 |
| PRP-008 | Analysis Agents (LoopAgent) | ✓ | 40 | 10.00/10 |
| PRP-009 | Prioritizer Agent | ✓ | 16 | 10.00/10 |
| PRP-010 | Root Orchestrator (SequentialAgent) | ✓ | 29 | 10.00/10 |

**Total**: 152 tests, perfect Pylint scores (10.00/10)

### Phase 3: Memory & Persistence (NOT STARTED)

- PRP-011: Session Memory Integration
- PRP-012: Cross-Session Persistence

### Phase 4: Observability & Evaluation (NOT STARTED)

- PRP-013: Logging and Observability
- PRP-014: Evaluation Test Suite
- PRP-015: Documentation and Demo

---

## KEY COMPONENTS DETAIL

### 1. Framework Templates System

**File**: `strategic_consultant_agent/tools/framework_loader.py`
**Purpose**: Load and validate pre-defined MECE framework templates

**Supported Frameworks** (6 total):
1. **scale_decision** - Should we scale/expand an existing pilot?
   - L1: DESIRABILITY, FEASIBILITY, VIABILITY
   - Triggers: "scale", "expand", "rollout"

2. **product_launch** - Should we launch a new product?
   - L1: MARKET_ATTRACTIVENESS, COMPETITIVE_POSITION, INTERNAL_CAPABILITIES
   - Triggers: "launch", "new product", "introduce"

3. **market_entry** - Should we enter a new market?
   - L1: MARKET_ATTRACTIVENESS, COMPETITIVE_DYNAMICS, ENTRY_BARRIERS
   - Triggers: "market entry", "enter market", "geographic expansion"

4. **investment_decision** - Should we invest/acquire?
   - L1: STRATEGIC_FIT, FINANCIAL_RETURNS, RISK_PROFILE
   - Triggers: "invest", "acquire", "M&A"

5. **operations_improvement** - Should we implement this improvement?
   - L1: COST_REDUCTION, QUALITY_IMPROVEMENT, SPEED_GAINS
   - Triggers: "operations", "process improvement", "efficiency"

6. **custom** - User-defined L1 categories
   - Triggers: "custom framework"

**Key Functions**:
- `FrameworkLoader.load_frameworks()` - Singleton pattern for efficiency
- `FrameworkLoader.get_framework(name)` - Retrieve by name
- `FrameworkLoader.find_matching_framework(question)` - Auto-select by trigger phrases

### 2. Hypothesis Tree Generator

**File**: `strategic_consultant_agent/tools/hypothesis_tree.py`
**Purpose**: Generate MECE hypothesis trees from framework templates

**Function Signature**:
```python
def generate_hypothesis_tree(
    strategic_question: str,
    framework: str = "scale_decision",
    custom_l1_categories: list[str] | None = None,
    context: str = ""
) -> dict
```

**Output Structure**:
```json
{
  "strategic_question": "Should we scale deployment of fall detection?",
  "framework_used": "scale_decision",
  "L1_DESIRABILITY": {
    "label": "Desirability",
    "question": "Is there user need?",
    "L2_USER_DEMAND": {
      "label": "User Demand",
      "question": "Do users want this?",
      "L3_leaves": [
        {
          "label": "Willingness to Pay",
          "question": "Will users pay for this?",
          "metric_type": "percentage",
          "target": "≥70% adoption rate",
          "data_source": "User surveys, pilot data"
        }
      ]
    }
  },
  "scoring_rubric": {...},
  "decision_thresholds": {...}
}
```

**Key Features**:
- Auto-generates L3 leaves with complete metric definitions
- Supports all 6 framework types
- Custom framework builder for user-defined L1 categories
- Scoring rubric with Go/Maybe/No-Go thresholds

### 3. MECE Validator

**File**: `strategic_consultant_agent/tools/mece_validator.py`
**Purpose**: Validate hypothesis trees for MECE compliance

**Function Signature**:
```python
def validate_mece_structure(structure: dict) -> dict
```

**Validation Checks**:
1. **Mutually Exclusive**: No overlap between categories
   - Keyword overlap detection (e.g., "Cost" vs "Financial")
   - Semantic overlap detection (e.g., "Risk" vs "Safety")

2. **Collectively Exhaustive**: No major gaps
   - Problem-specific gap detection (e.g., missing "Regulatory" for healthcare)
   - Coverage completeness check

3. **Level Consistency**: Not mixing strategic and tactical
   - Checks for tactical terms at strategic level

**Output Structure**:
```json
{
  "is_mece": true,
  "issues": {
    "overlaps": [],
    "gaps": [],
    "level_inconsistencies": []
  },
  "suggestions": []
}
```

### 4. 2x2 Matrix Generator

**File**: `strategic_consultant_agent/tools/matrix_2x2.py`
**Purpose**: Generate prioritization matrices for hypothesis prioritization

**Supported Matrix Types** (5 total):
1. **prioritization** - Impact/Effort
2. **bcg** - Market Growth/Market Share
3. **risk** - Probability/Impact
4. **eisenhower** - Urgency/Importance
5. **custom** - User-defined axes

**Function Signature**:
```python
def generate_2x2_matrix(
    items: list[dict],
    matrix_type: str = "prioritization",
    x_axis_label: str | None = None,
    y_axis_label: str | None = None
) -> dict
```

**Output Structure**:
```json
{
  "matrix_type": "prioritization",
  "x_axis": {"label": "Effort", "low": "Low", "high": "High"},
  "y_axis": {"label": "Impact", "low": "Low", "high": "High"},
  "quadrants": {
    "Q1_high_y_high_x": {
      "label": "Strategic Bets",
      "description": "High impact, high effort",
      "recommendation": "Plan carefully",
      "items": [...]
    }
  }
}
```

### 5. Persistence System

**File**: `strategic_consultant_agent/tools/persistence.py`
**Purpose**: Save/load analyses for cross-session access

**Key Functions**:
- `save_analysis(project_name, analysis_data, metadata)` - Save with auto-versioning
- `load_analysis(project_name, version)` - Load specific version
- `get_latest_version(project_name)` - Get most recent version number
- `delete_analysis(project_name, version)` - Remove saved analysis

**Storage Structure**:
```
storage/projects/
├── fall_detection_v1.json
├── fall_detection_v2.json
├── fall_detection_v3.json
└── market_entry_telehealth_v1.json
```

**Metadata Included**:
- Timestamp
- Framework used
- Version number
- User-provided tags

---

## AGENT SYSTEM PROMPTS

**File**: `strategic_consultant_agent/prompts/instructions.py`

**7 System Prompts Defined**:

1. **MARKET_RESEARCHER_PROMPT** - Research market trends, size, growth
2. **COMPETITOR_RESEARCHER_PROMPT** - Analyze competitive landscape
3. **HYPOTHESIS_GENERATOR_PROMPT** - Create MECE hypothesis trees
4. **MECE_VALIDATOR_PROMPT** - Validate for overlaps/gaps, call exit_loop when passing
5. **PRIORITIZER_PROMPT** - Generate 2x2 prioritization matrices
6. **ROOT_ORCHESTRATOR_PROMPT** - Coordinate 3-phase workflow
7. **LOOP_EXIT_MESSAGE** - Success message when MECE validation passes

**Key Pattern**: All prompts reference available tools and expected state keys
- Market researcher: References google_search
- Hypothesis generator: References {market_research}, {competitor_research}
- MECE validator: References {hypothesis_tree}, calls exit_loop
- Prioritizer: References {hypothesis_tree}

---

## GOOGLE ADK PATTERNS USED

### Pattern 1: Agent Class (NOT LlmAgent)

```python
# CORRECT ✓
from google.adk.agents import Agent

agent = Agent(
    name="market_researcher",
    model=Gemini(model="gemini-2.0-flash"),
    instruction=MARKET_RESEARCHER_PROMPT,
    tools=[google_search],
    output_key="market_research"
)

# INCORRECT ✗ (old pattern)
from google.adk.agents import LlmAgent
agent = LlmAgent(...)
```

### Pattern 2: State Passing with output_key

```python
# Producer agent sets output_key
market_researcher = Agent(
    ...,
    output_key="market_research"  # Stores result in session state
)

# Consumer agent references with {curly braces}
hypothesis_generator = Agent(
    ...,
    instruction="""
    Use this market research: {market_research}

    Create hypothesis tree...
    """
)
```

**State Keys Used**:
- `market_research` - Market researcher output
- `competitor_research` - Competitor researcher output
- `hypothesis_tree` - Hypothesis generator output
- `validation_result` - MECE validator output
- `priority_matrix` - Prioritizer output

### Pattern 3: LoopAgent with Exit Condition

```python
def exit_loop() -> dict:
    """Call this when hypothesis tree passes MECE validation."""
    return {"status": "MECE validation passed. Proceeding to prioritization."}

mece_validator = Agent(
    ...,
    tools=[
        FunctionTool(validate_mece_structure),
        FunctionTool(exit_loop)  # Validator calls this when quality met
    ]
)

analysis_phase = LoopAgent(
    name="analysis_phase",
    agents=[hypothesis_generator, mece_validator],
    max_iterations=3
)
```

**Loop Logic**:
- If `is_mece: true` → Validator calls exit_loop() → Loop exits
- If `is_mece: false` → Validator provides feedback → Loop continues (max 3 iterations)

### Pattern 4: Multi-Agent Composition

```python
# ParallelAgent - Concurrent execution
research_phase = ParallelAgent(
    name="research_phase",
    agents=[market_researcher, competitor_researcher]
)

# LoopAgent - Iterative refinement
analysis_phase = LoopAgent(
    name="analysis_phase",
    agents=[hypothesis_generator, mece_validator],
    max_iterations=3
)

# SequentialAgent - Orchestration
strategic_analyzer = SequentialAgent(
    name="strategic_analyzer",
    agents=[research_phase, analysis_phase, prioritizer]
)
```

---

## QUALITY GATES (ALL 5 MUST PASS)

### Gate 1: Code Quality ✓
```bash
black strategic_consultant_agent/ --check
pylint strategic_consultant_agent/
```
**Status**: All Phase 1 & 2 code passing (avg Pylint 9.8/10)

### Gate 2: Testing ✓
```bash
pytest --cov=strategic_consultant_agent tests/ --cov-report=term-missing
```
**Status**: 267 tests passing, avg 97% coverage (Phase 1 & 2)

### Gate 3: ADK Pattern Compliance ✓
**Checklist**:
- [x] Uses `Agent` class (NOT `LlmAgent`)
- [x] Correct imports from `google.adk.agents`, `google.adk.tools`
- [x] FunctionTools wrap custom functions correctly
- [x] output_key used for state passing
- [x] Multi-agent composition correct (Sequential/Parallel/Loop)
- [x] Retry configuration properly set
- [x] No MCP integration (design decision)

**Status**: All Phase 1 & 2 code compliant

### Gate 4: MECE & Framework Quality ✓
**Checklist**:
- [x] Framework templates load from JSON correctly
- [x] MECE validator detects overlaps and gaps
- [x] Hypothesis tree structure matches expected schema
- [x] L3 leaves have required fields
- [x] 2x2 matrix correctly plots items in quadrants
- [x] Scoring rubric and thresholds defined

**Status**: All Phase 1 tools passing

### Gate 5: Evaluation & Course Alignment (NOT YET STARTED)
**Requirements**:
- [ ] evalset.json has ≥5 test cases
- [ ] Tool trajectory tests pass
- [ ] adk eval command runs successfully
- [ ] Demonstrates all required ADK patterns
- [ ] Course alignment checklist complete

**Status**: Phase 4 - PRP-014 not started

---

## DEVELOPMENT ENVIRONMENT

### Prerequisites
- Python 3.11+
- Google API Key (for Gemini)
- Google ADK installed

### Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set API key
export GOOGLE_API_KEY="your_api_key_here"
```

### Dependencies (requirements.txt)
```
google-adk
pytest
pytest-cov
black
pylint
```

### Testing Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=strategic_consultant_agent tests/ --cov-report=term-missing

# Run specific tool tests
pytest tests/tools/test_hypothesis_tree.py -v

# Run specific agent tests
pytest tests/sub_agents/test_analysis_agents.py -v

# Format code
black strategic_consultant_agent/

# Lint code
pylint strategic_consultant_agent/
```

### Evaluation Commands (when Phase 4 complete)

```bash
# Run evaluation
adk eval strategic_consultant_agent \
    evaluation/strategic_consultant.evalset.json \
    --config_file_path=evaluation/test_config.json \
    --print_detailed_results
```

---

## COMMON ISSUES & TROUBLESHOOTING

### Issue 1: ImportError - cannot import 'LlmAgent'
**Cause**: Using old ADK pattern
**Solution**: Use `Agent` class instead
```python
from google.adk.agents import Agent  # CORRECT
from google.adk.agents import LlmAgent  # INCORRECT
```

### Issue 2: Agent not finding google_search tool
**Cause**: Tool not in tools list
**Solution**: Ensure tool is in list
```python
from google.adk.tools import google_search

agent = Agent(
    ...,
    tools=[google_search]  # Must be in list
)
```

### Issue 3: State passing not working
**Cause**: Missing output_key or incorrect reference format
**Solution**: Set output_key on producer, reference with {brackets} in consumer
```python
# Producer
producer = Agent(..., output_key="my_output")

# Consumer
consumer = Agent(..., instruction="Use: {my_output}")
```

### Issue 4: LoopAgent never exits
**Cause**: exit_loop not attached or not called
**Solution**: Ensure exit_loop is a tool and validator calls it
```python
def exit_loop() -> dict:
    return {"status": "Exiting loop"}

validator = Agent(
    ...,
    tools=[validate_mece_structure, exit_loop]  # Both required
)
```

### Issue 5: Framework templates not loading
**Cause**: Missing JSON file or incorrect path
**Solution**: Verify symlink or copy framework_templates.json to data/
```bash
ls strategic_consultant_agent/data/framework_templates.json
```

---

## COURSE ALIGNMENT CHECKLIST

| Day | Concept | Implementation | Status |
|-----|---------|----------------|--------|
| 1A | `Agent`, `FunctionTool` | All agent definitions | ✓ Complete |
| 1B | `SequentialAgent` | strategic_analyzer root | ✓ Complete |
| 1B | `ParallelAgent` | research_phase | ✓ Complete |
| 1B | `LoopAgent` | analysis_phase | ✓ Complete |
| 2A | Custom FunctionTools | 5 tools (tree, validator, matrix, persistence, loader) | ✓ Complete |
| 2A | `google_search` | Research agents | ✓ Complete |
| 2B | Tool validation | validate_mece_structure | ✓ Complete |
| 3A | `InMemoryRunner`, sessions | Session management | Not Started |
| 3B | Persistent memory | JSON file storage | Tools done, integration pending |
| 4A | Observability | LoggingPlugin | Not Started |
| 4B | `adk eval` | Evaluation test cases | Not Started |

**Progress**: 7/11 concepts demonstrated (64%)

---

## NEXT STEPS

### Immediate (Phase 3 - Memory & Persistence)

1. **PRP-011: Session Memory Integration** (2 hours)
   - Configure InMemoryRunner with session management
   - Enable multi-turn conversations
   - Test state persistence across turns

2. **PRP-012: Cross-Session Persistence** (2 hours)
   - Integrate save_analysis/load_analysis into workflow
   - Auto-save completed analyses
   - Test save → exit → reload workflow

### Near-Term (Phase 4 - Observability & Evaluation)

3. **PRP-013: Logging and Observability** (1 hour)
   - Add LoggingPlugin
   - Log tool calls, agent transitions, loop iterations
   - Save logs to files

4. **PRP-014: Evaluation Test Suite** (2 hours)
   - Create evalset.json with ≥5 test cases
   - Create test_config.json
   - Run adk eval and achieve >80% pass rate

5. **PRP-015: Documentation and Demo** (2 hours)
   - Update README with usage examples
   - Create 4 demo scenarios
   - Complete COURSE_ALIGNMENT.md
   - Final testing and submission

---

## USEFUL FILE REFERENCES

### For Understanding ADK Patterns
- `docs/project-requirements/agent_prompts.md` - **CRITICAL**: Exact ADK code patterns
- `CLAUDE.md` - Project-specific rules and ADK best practices
- `.claude/SHARED-PATTERNS.md` - Sub-agent validation patterns

### For Implementation Guidance
- `TASKS.md` - 15 PRPs with dependencies and acceptance criteria
- `PRPs/PRP-TEMPLATE.md` - Template for creating new PRPs
- `docs/project-requirements/capstone_architecture_plan.md` - Architecture decisions

### For Framework Understanding
- `docs/project-requirements/framework_templates.json` - 6 framework definitions
- `docs/project-requirements/examples/mece_tree_fall_detection.json` - Example output
- `docs/project-requirements/user_experience_workflow.md` - User journey

### For Development Workflow
- `.claude/commands/recover-context.md` - Fast context recovery
- `.claude/commands/execute-phase.md` - Automated batch execution
- `.claude/commands/execute-prp.md` - Manual step-by-step execution

---

## GIT & VERSION CONTROL

**Current Status**: Not yet a git repository

**Recommended Setup**:
```bash
git init
git add .
git commit -m "feat: initial project scaffold - Phase 1 & 2 complete"
```

**Commit Convention**:
```
<type>(<scope>): <subject>

Types: feat, fix, docs, test, refactor, chore
Scope: tool, agent, evaluation, framework
Subject: Imperative mood, lowercase, no period
```

**Example Commits**:
```
feat(tool): add generate_hypothesis_tree with MECE framework templates
feat(agent): implement ParallelAgent for concurrent research
fix(tool): correct MECE validator overlap detection logic
test(evaluation): add tool trajectory tests for framework selection
```

---

## METRICS & STATISTICS

### Code Statistics
- **Total Python Files**: 29
- **Total Lines**: 4,571
- **Test Files**: 10
- **Test Cases**: 267
- **Average Coverage**: 97% (Phase 1 tools)
- **Average Pylint Score**: 9.8/10

### Implementation Progress
- **Total PRPs**: 15
- **Completed PRPs**: 10 (67%)
- **Remaining PRPs**: 5 (33%)
- **Estimated Time Remaining**: 6-8 hours

### Quality Metrics
- **Phase 1 Tools**: 5/5 complete, 115 tests, 97% avg coverage
- **Phase 2 Agents**: 5/5 complete, 152 tests, 10.00/10 Pylint
- **Phase 3 Memory**: 0/2 complete
- **Phase 4 Evaluation**: 0/3 complete

---

## CONTACT & SUPPORT

**Project Owner**: Claude Code Session
**Target Submission**: Kaggle 5-Day AI Agents Course
**Documentation**: See CLAUDE.md, TASKS.md, README.md
**Issues**: Track in TASKS.md BLOCKERS section

---

**Last Updated**: 2025-11-23
**Index Version**: 1.0
**Project Phase**: Phase 2 Complete - Ready for Phase 3
