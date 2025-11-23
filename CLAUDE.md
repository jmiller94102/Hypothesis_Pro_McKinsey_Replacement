# CLAUDE.md - HypothesisTree Pro Strategic Consultant Agent

**Version**: 1.0
**Last Updated**: 2025-11-20
**Purpose**: Primary instruction file for Claude Code when working in this repository
**Philosophy**: Build Professional MBB-Quality Strategic Frameworks with Google ADK

---

## PROJECT OVERVIEW

**Project Name**: HypothesisTree Pro - Strategic Decision Support Agent
**Type**: AI-Powered Strategic Consultant using Google ADK
**Tech Stack**: Python, Google ADK (Agent Development Kit), Google Gemini, SQLite (optional)
**Target**: Kaggle 5-Day AI Agents Course Capstone Project

### Quick Description
Build an AI-powered strategic consultant that helps users decompose complex business problems into MECE hypothesis trees, prioritize with 2x2 matrices, and iteratively refine analysis with validation loops. Uses Google ADK's multi-agent architecture (SequentialAgent, ParallelAgent, LoopAgent) to produce professional MBB-quality strategic frameworks.

### Core Architecture Decisions

**CRITICAL: Google ADK Multi-Agent Pattern**
- **Root Orchestrator**: SequentialAgent (strategic_analyzer) → 3-phase workflow
- **Research Phase**: ParallelAgent (market_researcher + competitor_researcher)
- **Analysis Phase**: LoopAgent (hypothesis_generator + mece_validator) → Iterative refinement
- **Prioritization Phase**: Single Agent (prioritizer) → 2x2 matrix generation
- **LLM**: Google Gemini 2.0 Flash with retry configuration
- **Tools**: Custom FunctionTools (generate_hypothesis_tree, generate_2x2_matrix, validate_mece_structure)
- **Storage**: JSON files for persistent memory + optional SQLite for feedback
- **Framework Templates**: Pre-defined MECE structures (Scale, Product Launch, Market Entry, etc.)

**Why ADK Matters**: Demonstrates all course concepts - multi-agent orchestration, custom tools, loops, parallel execution, sessions, memory, and evaluation.

---

## QUICK START (30 SECONDS)

When starting a new session or recovering context:

1. **Recover Context**: `/recover-context` (loads this file + TASKS.md)
2. **Check Progress**: Review `TASKS.md` for current status and blockers
3. **Reference Specs**: See `docs/project-requirements/` for complete specifications
4. **Execute Work**:
   - Option A: `/execute-phase phase-1` (automated batch execution)
   - Option B: `/execute-prp PRPs/tools/prp-001-name.md` (manual step-by-step)

---

## CONTEXT EFFICIENCY RULES

**CRITICAL for Long-Running Projects**: These rules keep sessions under token limits

### Rule 1: TASKS.md is the Single Source of Truth
- **NEVER** create separate progress files (PROGRESS.md, SESSION-NOTES.md, etc.)
- **ALWAYS** update TASKS.md with current status
- **BEFORE /clear**: Update TASKS.md CURRENT STATUS section

### Rule 2: Archive When Files Grow
- Archive files that exceed 800 lines to `docs/archive/`
- Keep only active/recent content in main directory
- Reference archived files when needed

### Rule 3: Avoid Redundant File Reads
- Read a file once to understand its structure
- Make all planned edits
- Only re-read if user or linter modified the file
- **Savings**: 1000+ tokens per unnecessary read

### Rule 4: Use Parallel Tool Calls
- Read multiple files simultaneously when independent
- Execute independent bash commands in parallel
- **Savings**: Significant time and token reduction

---

## PRP-BASED DEVELOPMENT WORKFLOW

### What is a PRP?
**PRP = Product Requirement Prompt**: A detailed, executable implementation guide for a specific component.

### PRP Workflow Options

**Option 1: Fully Automated (Recommended for Speed)**
```bash
/execute-phase phase-1
```
- Auto-generates all PRPs in the phase from TASKS.md
- Executes sequentially with full validation
- Updates TASKS.md automatically
- Commits code after each PRP
- Pauses on failure with clear next steps

**Option 2: Manual (Recommended for Learning)**
```bash
/generate-prp PRP-001
/execute-prp PRPs/tools/prp-001-name.md
```
- Step-by-step control
- Review each PRP before execution
- Learn the codebase incrementally

**Option 3: Partial Automation (Balanced)**
```bash
/execute-phase PRP-001 to PRP-003
# Review results, then:
/execute-phase PRP-004 to PRP-006
```

### PRP Execution Flow
```
Read PRP → Create Todo List → For Each Step:
  ├─ Implement Feature
  ├─ Run Tests
  ├─ Sub-Agent Validation (MANDATORY - see SHARED-PATTERNS.md)
  ├─ Project-specific validations (ADK patterns, MECE compliance, tool selection)
  └─ Mark Complete
→ All Quality Gates → PRP Complete → Update TASKS.md → Commit
```

---

## MANDATORY VALIDATION CHECKPOINTS

**CRITICAL**: Use sub-agent validation at these 6 points (see `.claude/SHARED-PATTERNS.md` for patterns):

1. **After Tool Implementation**
   - FunctionTool signature correct
   - Returns proper structured output
   - Error handling comprehensive

2. **After Agent Creation**
   - Agent class pattern correct (`Agent`, not `LlmAgent`)
   - System prompt clear and actionable
   - output_key properly set for state passing
   - Tools correctly attached

3. **After Multi-Agent Composition**
   - SequentialAgent/ParallelAgent/LoopAgent structure valid
   - State passing works (output_key → instruction references)
   - Loop exit conditions correct

4. **After Framework/Template Code**
   - MECE compliance validation logic correct
   - Framework templates load properly
   - L3 leaf generation produces complete structures

5. **After Evaluation Setup**
   - evalset.json format correct
   - Tool trajectory expectations match agent behavior
   - Test coverage sufficient for course requirements

6. **Before Every Commit (MANDATORY)**
   - All tests passing
   - Imports from google.adk correct
   - ADK patterns followed (Agent, not LlmAgent)
   - Documentation updated

---

## QUALITY GATES (ALL MUST PASS)

Before marking a PRP complete, verify:

### Gate 1: Code Quality ✓
```bash
# Linting
black strategic_consultant_agent/ --check
pylint strategic_consultant_agent/

# Type checking (if used)
mypy strategic_consultant_agent/
```
**Pass Criteria**: Zero errors

### Gate 2: Testing ✓
```bash
# Run tests with coverage
pytest --cov=strategic_consultant_agent tests/ --cov-report=term-missing
```
**Pass Criteria**: >80% coverage, all tests passing

### Gate 3: ADK Pattern Compliance ✓
**Project-Specific Gate for Google ADK**
- [ ] Uses `Agent` class (NOT `LlmAgent`)
- [ ] Uses correct imports from `google.adk.agents`, `google.adk.tools`, etc.
- [ ] FunctionTools wrap custom functions correctly
- [ ] output_key used for state passing between agents
- [ ] Multi-agent composition correct (Sequential/Parallel/Loop)
- [ ] Retry configuration properly set
- [ ] No MCP integration (design decision)

**Validation Commands**:
```bash
# Test agent execution
python -c "from strategic_consultant_agent import root_agent; print(root_agent)"

# Test tool imports
python -c "from strategic_consultant_agent.tools.hypothesis_tree import generate_hypothesis_tree; print(generate_hypothesis_tree)"
```

### Gate 4: MECE & Framework Quality ✓
**Project-Specific Requirements**:
- [ ] Framework templates load from JSON correctly
- [ ] MECE validator detects overlaps and gaps
- [ ] Hypothesis tree structure matches expected schema
- [ ] L3 leaves have required fields (label, question, metric_type, target, data_source)
- [ ] 2x2 matrix correctly plots items in quadrants
- [ ] Scoring rubric and thresholds defined

**Quality Check**:
```python
# Test framework loading
from strategic_consultant_agent.tools.hypothesis_tree import generate_hypothesis_tree
tree = generate_hypothesis_tree("Test question", framework="scale_decision")
assert "L1_DESIRABILITY" in tree
assert "L1_FEASIBILITY" in tree
assert "L1_VIABILITY" in tree
```

### Gate 5: Evaluation & Course Alignment ✓
**Project-Specific Requirements**:
- [ ] evalset.json has test cases for framework selection
- [ ] Tool trajectory tests pass
- [ ] adk eval command runs successfully
- [ ] Demonstrates all required ADK patterns (Sequential, Parallel, Loop, Tools, Sessions, Memory)
- [ ] Course alignment checklist complete (Day 1A-5B concepts)

**Validation**:
```bash
adk eval strategic_consultant_agent evaluation/strategic_consultant.evalset.json \
    --config_file_path=evaluation/test_config.json \
    --print_detailed_results
```

---

## PROJECT-SPECIFIC RULES

### Rule 1: Always Use `Agent` Class (Not `LlmAgent`)
**CRITICAL for ADK Compatibility**

```python
# CORRECT ✓
from google.adk.agents import Agent

market_researcher = Agent(
    name="market_researcher",
    model=Gemini(model="gemini-2.0-flash"),
    instruction=MARKET_RESEARCHER_PROMPT,
    tools=[google_search],
    output_key="market_research"
)

# INCORRECT ✗
from google.adk.agents import LlmAgent  # DON'T USE THIS

researcher = LlmAgent(...)  # This is old pattern
```

### Rule 2: State Passing with output_key
**CRITICAL for Multi-Agent Communication**

Every agent that produces output for other agents must use `output_key`:

```python
# Producer agent
market_researcher = Agent(
    ...,
    output_key="market_research"  # Stored in session state
)

# Consumer agent references it in instruction
hypothesis_generator = Agent(
    ...,
    instruction="""
    Use this market research: {market_research}

    Create hypothesis tree based on:
    ...
    """
)
```

**State Keys Used in This Project**:
- `market_research` - Market researcher output
- `competitor_research` - Competitor researcher output
- `hypothesis_tree` - Hypothesis generator output
- `validation_result` - MECE validator output
- `priority_matrix` - Prioritizer output

### Rule 3: MECE Compliance Enforcement
**CRITICAL for Strategic Quality**

Every hypothesis tree must pass MECE validation:

**Mutually Exclusive**:
- No overlap between L1 categories (e.g., "Cost" and "Financial" would overlap)
- No overlap between L2 branches within an L1

**Collectively Exhaustive**:
- All L1 categories cover the full scope of the strategic question
- No major gaps (e.g., missing "Regulatory" for healthcare decisions)

**Validation Function**:
```python
def validate_mece_structure(structure: dict) -> dict:
    """
    Returns:
        {
            "is_mece": bool,
            "issues": {
                "overlaps": [...],
                "gaps": [...],
                "level_inconsistencies": [...]
            },
            "suggestions": [...]
        }
    """
    # Implementation checks for overlaps and gaps
    pass
```

### Rule 4: Loop Exit Conditions
**CRITICAL for LoopAgent Control**

The analysis_phase LoopAgent must exit when MECE validation passes:

```python
def exit_loop() -> dict:
    """Call this function when hypothesis tree passes MECE validation."""
    return {"status": "MECE validation passed. Proceeding to prioritization."}

mece_validator_agent = Agent(
    ...,
    tools=[
        FunctionTool(validate_mece_structure),
        FunctionTool(exit_loop)  # Validator calls this when quality met
    ]
)
```

**Loop Logic**:
- If `is_mece: true` → Call exit_loop() → Proceed to prioritization
- If `is_mece: false` → Provide feedback → Loop continues (max 3 iterations)

---

## DEVELOPMENT ENVIRONMENT

### Prerequisites
- Python 3.11+
- Google API Key (for Gemini)
- Google ADK installed

### Environment Variables
```bash
# Copy template and fill in
cp .env.example .env

# Required variables
GOOGLE_API_KEY=your_google_api_key_here

# Optional
PROJECT_NAME=hypothesis_tree_pro
STORAGE_PATH=./storage/projects
```

### Starting Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install google-adk pytest black pylint

# Test installation
python -c "from google.adk.agents import Agent; print('ADK installed successfully')"

# Run agent (when implemented)
adk web  # Launches web UI
# or
python run_agent.py
```

### Testing Commands
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=strategic_consultant_agent tests/ --cov-report=term-missing

# Run evaluation
adk eval strategic_consultant_agent evaluation/strategic_consultant.evalset.json --print_detailed_results

# Test specific tool
python -c "from strategic_consultant_agent.tools.hypothesis_tree import generate_hypothesis_tree; print(generate_hypothesis_tree('Test', 'scale_decision'))"
```

---

## TODOWRITE DISCIPLINE

**CRITICAL for Progress Tracking**:

1. **Create todos** at the start of PRP execution
2. **ONE task `in_progress`** at a time (not less, not more)
3. **Mark `completed`** immediately after finishing each task
4. **Update todos** at each PRP step

**Example**:
```
✓ Completed: Implement generate_hypothesis_tree tool
→ In Progress: Create market_researcher agent with google_search
  Pending: Build ParallelAgent for research phase
  Pending: Implement MECE validator
```

---

## COMMON PATTERNS

### Pattern 1: Tool Function Signature
All custom tools must follow this pattern:

```python
def tool_function(
    param1: str,
    param2: int = 0,
    optional_param: list[str] | None = None
) -> dict:
    """
    Clear description of what this tool does.

    Args:
        param1: Description of param1
        param2: Description of param2 (default: 0)
        optional_param: Description (optional)

    Returns:
        dict: Structured output description
    """
    # Implementation
    return {
        "status": "success",
        "data": {...}
    }

# Wrap with FunctionTool
from google.adk.tools import FunctionTool
tool = FunctionTool(tool_function)
```

### Pattern 2: Agent System Prompts
System prompts should be clear, actionable, and reference available tools:

```python
AGENT_PROMPT = """You are a [role description].

Your task is to [specific task].

Use the following approach:
1. [Step 1]
2. [Step 2]
3. [Step 3]

Tools Available:
- tool_name: [When to use it]

Output Format:
[Description of expected output structure]

Quality Standards:
- [Standard 1]
- [Standard 2]
"""
```

### Pattern 3: Framework Template Structure
Framework templates in `framework_templates.json` follow this pattern:

```json
{
  "framework_name": {
    "name": "Human-Readable Name",
    "description": "When to use this framework",
    "trigger_phrases": ["keyword1", "keyword2"],
    "L1_categories": {
      "CATEGORY1": {
        "label": "Category 1",
        "question": "What does this category answer?",
        "description": "Detailed description",
        "L2_branches": {
          "BRANCH1": {
            "label": "Branch 1",
            "question": "Specific question",
            "suggested_L3": ["Leaf 1", "Leaf 2", "Leaf 3"]
          }
        }
      }
    }
  }
}
```

---

## FILE ORGANIZATION

```
strategic-evaluation-tree/
├── CLAUDE.md                    # This file - primary instructions
├── TASKS.md                     # Single source of truth for progress
├── .claude/                     # Claude Code configuration
│   ├── commands/               # Slash commands
│   │   ├── recover-context.md
│   │   ├── generate-prp.md
│   │   ├── execute-prp.md
│   │   └── execute-phase.md
│   ├── skills/                 # Reusable skills
│   │   └── save-session/SKILL.md
│   └── SHARED-PATTERNS.md      # Validation patterns
├── PRPs/                       # Product Requirement Prompts
│   ├── tools/                  # Tool implementation PRPs
│   ├── agents/                 # Agent creation PRPs
│   ├── evaluation/             # Evaluation setup PRPs
│   ├── integration/            # Integration PRPs
│   └── PRP-TEMPLATE.md         # Template
├── docs/                       # Project documentation
│   ├── project-requirements/   # Reference specifications
│   │   ├── README.md           # Project overview
│   │   ├── capstone_architecture_plan.md
│   │   ├── user_experience_workflow.md
│   │   ├── agent_prompts.md    # ADK code patterns (CRITICAL REFERENCE)
│   │   ├── framework_templates.json
│   │   └── examples/
│   └── archive/                # Archived files >800 lines
├── strategic_consultant_agent/ # Application code
│   ├── __init__.py
│   ├── agent.py                # Main SequentialAgent
│   ├── sub_agents/
│   │   ├── research_agents.py  # ParallelAgent
│   │   ├── analysis_agents.py  # LoopAgent
│   │   └── prioritizer_agent.py
│   ├── tools/
│   │   ├── hypothesis_tree.py
│   │   ├── matrix_2x2.py
│   │   ├── mece_validator.py
│   │   └── persistence.py
│   ├── prompts/
│   │   └── instructions.py     # All system prompts
│   ├── data/
│   │   └── framework_templates.json (symlink or copy)
│   └── storage/
│       └── projects/           # JSON persistence
├── evaluation/
│   ├── strategic_consultant.evalset.json
│   └── test_config.json
├── tests/                      # Test suite
├── .env                        # Environment variables (gitignored)
├── .env.example                # Template
├── .gitignore
├── requirements.txt            # Dependencies
└── README.md
```

---

## COMMIT CONVENTIONS

```
<type>(<scope>): <subject>

Types: feat, fix, docs, test, refactor, chore
Scope: tool, agent, evaluation, framework
Subject: Imperative mood, lowercase, no period

Examples:
feat(tool): add generate_hypothesis_tree with MECE framework templates
feat(agent): implement ParallelAgent for concurrent research
fix(tool): correct MECE validator overlap detection logic
test(evaluation): add tool trajectory tests for framework selection
```

---

## TROUBLESHOOTING

### Common Issues

**Issue 1**: ImportError: cannot import name 'LlmAgent'
```bash
# Solution: Use Agent instead
from google.adk.agents import Agent  # CORRECT
from google.adk.agents import LlmAgent  # INCORRECT - old pattern
```

**Issue 2**: Agent not finding google_search tool
```bash
# Check import
from google.adk.tools import google_search

# Verify tool is in list
agent = Agent(
    ...,
    tools=[google_search]  # Must be in list
)
```

**Issue 3**: State passing not working (output_key)
```python
# Producer must set output_key
producer = Agent(
    ...,
    output_key="my_output"  # REQUIRED
)

# Consumer references with {curly braces}
consumer = Agent(
    ...,
    instruction="Use this data: {my_output}"  # Correct format
)
```

**Issue 4**: LoopAgent never exits
```python
# Ensure exit_loop is defined and attached
def exit_loop() -> dict:
    return {"status": "Exiting loop"}

validator = Agent(
    ...,
    tools=[
        FunctionTool(validate_mece_structure),
        FunctionTool(exit_loop)  # Must be attached
    ]
)

# In validator prompt, tell agent when to call exit_loop
```

---

## REFERENCES

**Primary Specifications**:
- `docs/project-requirements/agent_prompts.md` - **CRITICAL: ADK code patterns and prompts**
- `docs/project-requirements/capstone_architecture_plan.md` - Architecture decisions
- `docs/project-requirements/user_experience_workflow.md` - User journey
- `docs/project-requirements/framework_templates.json` - Framework data
- `docs/project-requirements/README.md` - Quick start

**External Documentation**:
- Google ADK Documentation: https://github.com/google/adk-toolkit
- Kaggle AI Agents Course: https://www.kaggle.com/learn-guide/ai-agents
- Google Gemini API: https://ai.google.dev/

---

## NOTES FOR CLAUDE CODE

### On First Session
1. Read this file completely
2. Read TASKS.md to understand current progress
3. Read `docs/project-requirements/agent_prompts.md` for ADK patterns
4. Ask user which phase/PRP to work on
5. Execute using appropriate workflow option

### Before Using /clear
1. Update TASKS.md CURRENT STATUS section
2. Commit any uncommitted work
3. Note blockers or next steps

### On Session Recovery
1. Run `/recover-context`
2. Review TASKS.md blockers
3. Continue from where you left off

### PRP References
PRPs will reference specific documentation sections:
- "See agent_prompts.md lines 12-38 for Agent class pattern"
- "See framework_templates.json for framework structure"
- "See capstone_architecture_plan.md lines 460-510 for implementation roadmap"

---

**Remember**:
- This file evolves with your project
- Reference `docs/project-requirements/agent_prompts.md` for exact ADK patterns
- Use `Agent` class, not `LlmAgent`
- State passing requires `output_key` → `{key}` in instructions
- MECE validation is non-negotiable for quality
- All 5 quality gates must pass before PRP completion

**Philosophy**: Build Professional MBB-Quality Strategic Frameworks with Google ADK

---

**Version**: 1.0
**Last Updated**: 2025-11-20
**Status**: Ready for Implementation
