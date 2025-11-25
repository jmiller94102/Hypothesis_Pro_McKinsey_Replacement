# HypothesisTree Pro

**Don't get blindsided. Spot decision gaps before you scale or invest.**

Build in 5 minutes what consultants build in 5 weeks. HypothesisTree Pro turns vague "should we?" debates into a clear set of bets, tradeoffs, and experiments your team can act on **today**.

---

## What It Does

**Input:** A strategic question like:
- "Should we scale deployment of a Computer Vision Fall Detection system in Senior Living?"
- "Should we launch a new telehealth product for rural hospitals?"
- "Should we enter the European eldercare market?"

**Output:** A complete strategic decision framework with:
- **MECE Hypothesis Trees** - 3 levels of analysis (L1 → L2 → L3) with measurable questions
- **Priority Matrices** - 2x2 matrices for hypothesis prioritization, risk assessment, task planning
- **AI-Powered Research** - Automated market and competitor research with live search
- **Validation & Iteration** - MECE compliance checking with iterative refinement

---

## Quick Start

### 1. Install Dependencies

```bash
# Clone the repository
git clone https://github.com/jmiller94102/Hypothesis_Pro_McKinsey_Replacement.git
cd Hypothesis_Pro_McKinsey_Replacement

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd hypothesis-tree-ui
npm install
cd ..
```

### 2. Set Up API Key

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Google API Key
# GOOGLE_API_KEY=your_api_key_here
```

### 3. Run the Application

**Start the backend:**
```bash
uvicorn strategic_consultant_agent.api.main:app --reload --port 8000
```

**Start the frontend (in a new terminal):**
```bash
cd hypothesis-tree-ui
npm run dev
```

**Open in browser:**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

---

## Features

### MECE Hypothesis Trees
- **8 Framework Templates**: Scale decision, product launch, market entry, investment, operations, risk assessment, hypothesis issue tree, custom
- **3-Level Structure**: L1 categories → L2 branches → L3 testable leaves
- **Rich Content**: Each leaf includes questions, metrics, targets, and data sources
- **LLM-Powered Generation**: Context-aware content based on market research

### Priority Matrices (2x2)
- **4 Matrix Types**: Hypothesis prioritization, risk register, task prioritization, measurement priorities
- **AI-Powered Placement**: Automatically places items in quadrants based on analysis
- **Drag & Drop Editing**: Move items between quadrants
- **Color-Coded Quadrants**: Quick Wins (green), Strategic Bets (yellow), Fill Later (gray), Deprioritize (red)

### Research & Analysis
- **Parallel Research Agents**: Market and competitor research run concurrently
- **Live Web Search**: Real-time data gathering using Google Search
- **MECE Validation**: Automatic detection of overlaps and gaps
- **Iterative Refinement**: Loop until quality threshold met

### Modern Web UI
- **Real-Time Progress**: Server-Sent Events for live generation updates
- **Tree Visualization**: Expandable/collapsible hierarchy with zoom controls
- **Project Management**: Save, load, and version your analyses
- **Export**: Download as JSON for further processing

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

**Tech Stack:**
- **Backend**: Python, FastAPI, Google ADK, Gemini 2.5 Flash
- **Frontend**: Next.js 15, React, TypeScript, Tailwind CSS
- **Agents**: Google ADK (SequentialAgent, ParallelAgent, LoopAgent)
- **Storage**: JSON file-based persistence with versioning

---

## Project Structure

```
Hypothesis_Pro_McKinsey_Replacement/
├── README.md                       # This file
├── QUICKSTART.md                   # Detailed setup guide
├── project_description.md          # Full project overview
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Python package config
│
├── strategic_consultant_agent/     # Python backend
│   ├── api/                        # FastAPI endpoints
│   ├── agent.py                    # Root SequentialAgent
│   ├── sub_agents/                 # Research, analysis, prioritizer agents
│   ├── tools/                      # Hypothesis tree, matrix, MECE validator
│   ├── prompts/                    # Agent instructions & matrix generation
│   └── data/                       # Framework templates
│
├── hypothesis-tree-ui/             # Next.js frontend
│   ├── app/                        # Pages (home, editor)
│   ├── components/                 # React components
│   └── lib/                        # API client, types
│
├── tests/                          # Test suite (342 tests)
├── evaluation/                     # ADK evaluation configs
├── demos/                          # Demo scripts
└── docs/                           # Documentation & archives
```

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
| `risk_assessment` | What are the key risks and mitigations? |
| `hypothesis_issue_tree` | Root cause analysis (McKinsey issue tree style) |
| `custom` | User-defined L1 categories |

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/frameworks` | GET | List available frameworks |
| `/api/projects` | GET | List saved projects |
| `/api/tree/generate` | POST | Generate hypothesis tree |
| `/api/tree/generate-stream` | GET | Generate with SSE progress |
| `/api/tree/save` | POST | Save tree to project |
| `/api/tree/load` | GET | Load tree from project |
| `/api/projects/{id}/matrices/{type}` | GET/POST | Get or generate matrix |
| `/api/mece/validate` | POST | Validate MECE compliance |

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=strategic_consultant_agent tests/ --cov-report=term-missing

# Run specific test file
pytest tests/tools/test_hypothesis_tree.py -v
```

**Test Coverage:** 342 tests, >90% coverage

---

## Example Usage

### Via Web UI

1. Open http://localhost:3000
2. Enter your strategic question
3. Select a framework (or let AI choose)
4. Click "Generate Tree"
5. View and edit the hypothesis tree
6. Switch to matrix tabs for prioritization views

### Via API

```python
import requests

# Generate a hypothesis tree
response = requests.post("http://localhost:8000/api/tree/generate", json={
    "problem": "Should we scale deployment of fall detection in senior living?",
    "framework": "scale_decision"
})

tree = response.json()
```

### Via Python SDK

```python
from google.adk.runners import InMemoryRunner
from strategic_consultant_agent import root_agent

runner = InMemoryRunner(agent=root_agent)

response = await runner.run(
    "Should we scale deployment of computer vision fall detection in senior living?"
)
```

---

## Performance

- **Tree Generation**: ~25-35 seconds (optimized from 140s)
- **LLM Calls**: 4 calls per tree (reduced from 14)
- **Research**: Parallel execution for market + competitor analysis

---

## Cloud Deployment

This agent is deployed to **Google Cloud Run** using the Google Agent Starter Pack infrastructure.

### Live Deployment

- **Endpoint**: https://hypothesis-tree-agent-up4ilqcfeq-uc.a.run.app
- **Dev UI**: https://hypothesis-tree-agent-up4ilqcfeq-uc.a.run.app/dev-ui/
- **Region**: us-central1
- **Project**: kaggle-479307
- **Framework**: Google ADK (Agent Development Kit)

### Deploy Your Own

```bash
# Prerequisites
# 1. GCP project with billing enabled
# 2. gcloud CLI installed and authenticated

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable aiplatform.googleapis.com run.googleapis.com cloudbuild.googleapis.com

# Deploy using Makefile
make deploy

# Or deploy directly
gcloud run deploy hypothesis-tree-agent \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

### Deployment Architecture

```
Cloud Run Service (hypothesis-tree-agent)
├── Dockerfile (Python 3.11 + uv)
├── strategic_consultant_agent/fast_api_app.py (ADK FastAPI wrapper)
├── Root Agent (SequentialAgent)
│   ├── Research Phase (ParallelAgent)
│   ├── Analysis Phase (LoopAgent)
│   └── Prioritization Phase
└── Artifact Storage (GCS bucket)
```

**Infrastructure Files Added by Agent Starter Pack:**
- `Dockerfile` - Container definition
- `Makefile` - Build and deploy commands
- `.cloudbuild/` - CI/CD pipeline configs
- `deployment/` - Terraform infrastructure

---

## Contributing

Contributions welcome! Please read the development documentation in `docs/` before submitting PRs.

---

## License

Apache 2.0

---

*Built with Google ADK, Gemini, and Next.js*
