# HypothesisTree Pro

**Strategic Decision Support Agent built with Google ADK**

An AI-powered strategic consultant that helps users decompose complex business problems into MECE hypothesis trees, prioritize with 2x2 matrices, and iteratively refine analysis with validation loops.

---

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up API Key

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Google API Key
# GOOGLE_API_KEY=your_api_key_here
```

Or export directly:

```bash
export GOOGLE_API_KEY="your-api-key-here"
```

### 3. Run the Agent

```python
from google.adk.runners import InMemoryRunner
from strategic_consultant_agent import root_agent

runner = InMemoryRunner(agent=root_agent)

response = await runner.run(
    "Should we scale deployment of computer vision fall detection in senior living?"
)
```

### 4. Launch Web UI (Optional)

```bash
cd strategic_consultant_agent
adk web
```

---

## What It Does

**Input:** A strategic question like:
- "Should we scale deployment of a Computer Vision Fall Detection system in Senior Living?"
- "Should we launch a new telehealth product for rural hospitals?"
- "Should we enter the European eldercare market?"

**Output:** A complete MECE hypothesis tree with:
- 3 levels of analysis (L1 → L2 → L3)
- Measurable questions at each leaf
- Targets and data sources
- Scoring rubric and decision thresholds
- Prioritized testing roadmap

---

## Architecture

```
strategic_analyzer (SequentialAgent)
│
├─ research_phase (ParallelAgent)
│   ├─ market_researcher (Agent + google_search)
│   └─ competitor_researcher (Agent + google_search)
│
├─ analysis_phase (LoopAgent)
│   ├─ hypothesis_generator (Agent + generate_hypothesis_tree)
│   └─ mece_validator (Agent + validate_mece_structure)
│
└─ prioritizer (Agent + generate_2x2_matrix)
```

**ADK Patterns Used:**
- `SequentialAgent` - Orchestrates 3-phase workflow
- `ParallelAgent` - Concurrent market + competitor research
- `LoopAgent` - Iterative MECE validation until quality threshold met
- `FunctionTool` - Custom tools for hypothesis trees and matrices
- `google_search` - Built-in search for research agents
- `output_key` - State passing between agents

---

## Project Structure

```
strategic-evaluation-tree/
├── CLAUDE.md                    # Primary instructions for Claude Code
├── TASKS.md                     # Implementation tracker (15 PRPs)
├── .claude/                     # Claude Code configuration
│   ├── commands/               # Slash commands (/recover-context, /execute-prp, etc.)
│   ├── skills/                 # Reusable skills
│   └── SHARED-PATTERNS.md      # Validation patterns
├── PRPs/                       # Product Requirement Prompts (implementation guides)
│   ├── tools/                  # Tool implementation PRPs
│   ├── agents/                 # Agent creation PRPs
│   ├── evaluation/             # Evaluation setup PRPs
│   └── integration/            # Integration PRPs
├── docs/
│   └── project-requirements/   # Reference specifications
├── strategic_consultant_agent/ # Application code (to be implemented)
├── evaluation/                 # Evaluation test cases (to be created)
├── tests/                      # Test suite (to be created)
└── requirements.txt
```

---

## Development Workflow

This project uses a **PRP-based development workflow** inspired by McKinsey/BCG delivery frameworks.

### For Claude Code Users

**Start a new session:**
```bash
/recover-context  # Loads CLAUDE.md + TASKS.md in ~30 seconds
```

**Automated implementation:**
```bash
/execute-phase phase-1  # Implements all PRPs in Phase 1 with validation
```

**Manual implementation:**
```bash
/generate-prp PRP-001   # Generate implementation guide
/execute-prp PRPs/tools/prp-001-framework-templates.md
```

### For Manual Implementation

1. Read `CLAUDE.md` - Understand project rules and ADK patterns
2. Read `TASKS.md` - See 15 PRPs across 4 phases
3. Read `docs/project-requirements/agent_prompts.md` - Get exact ADK code patterns
4. Implement PRPs in order (dependencies tracked in TASKS.md)

---

## Tools

| Tool | Purpose |
|------|---------|
| `generate_hypothesis_tree` | Create MECE structure using framework templates |
| `generate_2x2_matrix` | Create prioritization/positioning matrices |
| `validate_mece_structure` | Check for overlaps, gaps, inconsistencies |
| `save_analysis` | Persist to JSON for cross-session access |
| `load_analysis` | Retrieve previous analyses |

---

## Frameworks Supported

| Framework | Use Case |
|-----------|----------|
| `scale_decision` | Should we scale/expand an existing pilot? |
| `product_launch` | Should we launch a new product? |
| `market_entry` | Should we enter a new market? |
| `investment_decision` | Should we invest/acquire? |
| `operations_improvement` | Should we implement this improvement? |
| `custom` | User-defined L1 categories |

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=strategic_consultant_agent tests/ --cov-report=term-missing

# Run evaluation
adk eval strategic_consultant_agent \
    evaluation/strategic_consultant.evalset.json \
    --config_file_path=evaluation/test_config.json \
    --print_detailed_results
```

---

## Example Usage

### Basic Question

```python
response = await runner.run(
    "Should we scale deployment of fall detection in senior living?"
)
```

### With URL Context

```python
response = await runner.run(
    "Should we scale deployment of https://www.teton.ai/ in senior living?"
)
```

### Custom Framework

```python
response = await runner.run(
    "Analyze market entry using Revenue, Risk, and Operations categories"
)
```

### Load Previous Analysis

```python
response = await runner.run(
    "Load my fall detection analysis and show the hypothesis tree"
)
```

---

## Implementation Status

**Current Status**: Scaffold created, ready for implementation

**Total PRPs**: 15 across 4 phases
- **Phase 1**: Core Tools (5 PRPs) - NOT STARTED
- **Phase 2**: Agent Architecture (5 PRPs) - NOT STARTED
- **Phase 3**: Memory & Persistence (2 PRPs) - NOT STARTED
- **Phase 4**: Observability & Evaluation (3 PRPs) - NOT STARTED

See `TASKS.md` for detailed implementation plan.

---

## Course Alignment

This project demonstrates concepts from the Google ADK 5-Day Course:

| Day | Concept | Implementation |
|-----|---------|----------------|
| 1A | `Agent`, `FunctionTool` | All agent definitions |
| 1B | `SequentialAgent`, `ParallelAgent`, `LoopAgent` | Multi-agent workflow |
| 2A | Tool creation, `google_search` | Custom analysis tools |
| 2B | Tool validation | MECE validator |
| 3A | `InMemoryRunner`, sessions | Session management |
| 3B | Persistent memory | JSON file storage |
| 4A | Observability | LoggingPlugin |
| 4B | `adk eval` | Evaluation test cases |

---

## Contributing

This is a capstone project for the Kaggle 5-Day AI Agents Course. Contributions should follow the PRP-based workflow defined in CLAUDE.md.

---

## License

Apache 2.0

---

*Built for the Kaggle 5-Day AI Agents Course Capstone Project*
*November 2025*
