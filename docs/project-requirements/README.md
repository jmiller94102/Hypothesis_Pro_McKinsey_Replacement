# HypothesisTree Pro

**Strategic Decision Support Agent built with Google ADK**

An AI-powered strategic consultant that helps users decompose complex business problems into MECE hypothesis trees, prioritize with 2x2 matrices, and iteratively refine analysis with validation loops.

---

## Quick Start

### 1. Install Dependencies

```bash
pip install google-adk
```

### 2. Set Up API Key

```bash
export GOOGLE_API_KEY="your-api-key-here"
```

Or in Python:

```python
import os
os.environ["GOOGLE_API_KEY"] = "your-api-key-here"
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

## Project Documentation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | This file - overview and quick start |
| [capstone_architecture_plan.md](capstone_architecture_plan.md) | Detailed technical architecture |
| [user_experience_workflow.md](user_experience_workflow.md) | 8-stage UX flow from prompt to output |
| [agent_prompts.md](agent_prompts.md) | **ADK code patterns and system prompts** |
| [framework_templates.json](framework_templates.json) | Strategic framework definitions |
| [examples/mece_tree_fall_detection.json](examples/mece_tree_fall_detection.json) | Example output |

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

## File Structure

```
strategic_consultant_agent/
├── __init__.py              # Exports root_agent
├── agent.py                 # Main agent definitions
├── sub_agents/
│   ├── research_agents.py   # Market + Competitor researchers
│   ├── analysis_agents.py   # Generator + Validator loop
│   └── prioritizer_agent.py
├── tools/
│   ├── hypothesis_tree.py
│   ├── matrix_2x2.py
│   ├── mece_validator.py
│   └── persistence.py
├── data/
│   └── framework_templates.json
├── evaluation/
│   ├── strategic_consultant.evalset.json
│   └── test_config.json
└── storage/
    └── projects/
```

---

## Evaluation

Run evaluation tests:

```bash
adk eval strategic_consultant_agent \
    evaluation/strategic_consultant.evalset.json \
    --config_file_path=evaluation/test_config.json \
    --print_detailed_results
```

---

## ADK Course Alignment

This project demonstrates concepts from the Google ADK 5-Day Course:

| Day | Concept | Implementation |
|-----|---------|----------------|
| 1A | `Agent`, `FunctionTool` | All agent definitions |
| 1B | `SequentialAgent`, `ParallelAgent`, `LoopAgent` | Multi-agent workflow |
| 2A | Tool creation, `google_search` | Custom analysis tools |
| 2B | Tool validation | MECE validator |
| 3A | `InMemoryRunner`, sessions | Session management |
| 3B | Persistent memory | JSON file storage |
| 4A | Observability | Logging (to be added) |
| 4B | `adk eval` | Evaluation test cases |

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

## Development

### For Claude Code

When implementing this project, refer to these documents in order:

1. **agent_prompts.md** - Contains exact ADK imports, class patterns, and system prompts
2. **framework_templates.json** - Load this data into the `generate_hypothesis_tree` tool
3. **examples/mece_tree_fall_detection.json** - Reference output structure
4. **capstone_architecture_plan.md** - Additional architecture details
5. **user_experience_workflow.md** - UX context for agent behavior

### Key Implementation Notes

```python
# Use Agent, not LlmAgent
from google.adk.agents import Agent  # ✓ Correct
from google.adk.agents import LlmAgent  # ✗ Wrong

# Use output_key for state passing
agent = Agent(
    ...,
    output_key="my_output"  # Stored in session state
)

# Reference state in instructions
next_agent = Agent(
    instruction="Use this context: {my_output}"
)

# Wrap functions with FunctionTool
from google.adk.tools import FunctionTool
tools=[FunctionTool(my_function)]
```

---

## License

Apache 2.0

---

*Built for the Kaggle 5-Day AI Agents Course Capstone Project*
*November 2025*
