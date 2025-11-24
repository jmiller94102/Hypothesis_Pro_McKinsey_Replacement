# Opik Tracing Setup Guide

## Why Opik Instead of ADK Dev UI?

**ADK Dev UI (`http://localhost:3002/dev-ui/`)**
- ❌ Only traces ADK web interface sessions
- ❌ Doesn't capture FastAPI backend calls
- ❌ Session-based (not persistent)
- ❌ Limited to local development

**Opik (Comet)**
- ✅ Traces your production FastAPI backend
- ✅ Captures real user sessions from Next.js UI
- ✅ Persistent trace storage
- ✅ Multi-agent workflow visualization
- ✅ Token usage and cost tracking
- ✅ Production-ready monitoring

---

## Installation

```bash
# Activate virtual environment
source venv/bin/activate

# Install Opik
pip install opik

# Configure Opik
opik configure
```

You'll be prompted for:
- Comet API Key (get from https://www.comet.com/signup)
- Workspace name

---

## Integration with FastAPI Backend

### 1. Add Opik to API Endpoints

Edit `strategic_consultant_agent/api/main.py`:

```python
from opik import track
from opik.integrations.langchain import OpikTracer

# Initialize Opik tracer
opik_tracer = OpikTracer()

@app.get("/api/tree/generate-stream")
@track(name="generate_hypothesis_tree_stream")
async def generate_tree_stream(
    problem: str = Query(...),
    framework: str = Query(...)
):
    """
    Opik will automatically trace:
    - Agent execution (SequentialAgent → ParallelAgent → LoopAgent)
    - Tool calls (generate_hypothesis_tree, validate_mece_structure)
    - LLM interactions (Gemini API calls)
    - Token usage and costs
    """
    async for event in _generate_tree_with_progress(problem, framework):
        yield event
```

### 2. Add Tracing to Core Agent

Edit `strategic_consultant_agent/agent.py`:

```python
from opik import track

@track(name="strategic_consultant_agent")
def run_agent(problem: str, framework: str):
    """Root agent execution - traced by Opik"""
    result = root_agent.run(user_input=problem)
    return result
```

### 3. Trace Tool Calls

Edit `strategic_consultant_agent/tools/llm_tree_generators.py`:

```python
from opik import track

@track(name="generate_hypothesis_tree")
def generate_hypothesis_tree(problem: str, framework: str = "scale_decision") -> dict:
    """
    Opik will track:
    - Input: problem statement, framework
    - Output: Complete hypothesis tree
    - Latency: Time to generate
    - LLM calls: Token usage
    """
    # Existing implementation
    pass

@track(name="validate_mece_structure")
def validate_mece_structure(structure: dict) -> dict:
    """Track MECE validation"""
    # Existing implementation
    pass
```

---

## What You'll See in Opik Dashboard

### Trace View
```
└─ generate_hypothesis_tree_stream (45.2s)
   ├─ strategic_consultant_agent (44.8s)
   │  ├─ research_phase (12.3s)
   │  │  ├─ market_researcher (6.1s)
   │  │  │  └─ google_search_tool (5.8s)
   │  │  └─ competitor_researcher (6.2s)
   │  │     └─ google_search_tool (5.9s)
   │  ├─ analysis_phase (28.4s)
   │  │  ├─ hypothesis_generator (15.2s)
   │  │  │  └─ generate_hypothesis_tree (14.9s)
   │  │  │     └─ gemini-2.0-flash (14.7s, 1250 tokens)
   │  │  └─ mece_validator (13.2s)
   │  │     └─ validate_mece_structure (13.0s)
   │  └─ prioritization_phase (4.1s)
   │     └─ generate_2x2_matrix (3.9s)
   └─ save_to_storage (0.4s)
```

### Metrics Tracked
- **Latency**: Time for each agent/tool
- **Token Usage**: Input/output tokens per LLM call
- **Cost**: Estimated API cost
- **Success Rate**: Pass/fail for each operation
- **MECE Validation**: Pass/fail rate for hypothesis trees

---

## Environment Variables

Add to `.env`:

```bash
# Opik Configuration
OPIK_API_KEY=your_comet_api_key_here
OPIK_WORKSPACE=hypothesis-tree-pro
OPIK_PROJECT_NAME=strategic-consultant-agent

# Enable Opik tracing
OPIK_ENABLED=true
```

---

## Viewing Traces

1. **Web Dashboard**: https://www.comet.com/[your-workspace]/traces
2. **Filter by**:
   - User session ID
   - Agent type (research, analysis, prioritization)
   - Time range
   - Success/failure
   - Framework used (scale_decision, market_entry, etc.)

---

## Comparison: ADK Dev UI vs Opik

| Feature | ADK Dev UI | Opik |
|---------|-----------|------|
| **Captures FastAPI calls** | ❌ No | ✅ Yes |
| **Persistent storage** | ❌ Session only | ✅ Permanent |
| **Multi-user tracking** | ❌ Limited | ✅ Yes |
| **Cost tracking** | ❌ No | ✅ Yes |
| **Production monitoring** | ❌ No | ✅ Yes |
| **Custom dashboards** | ❌ No | ✅ Yes |
| **Trace sharing** | ❌ No | ✅ Yes |
| **Setup complexity** | Easy | Medium |

---

## When to Use Each

**Use ADK Dev UI for:**
- Quick local testing of agent logic
- Debugging ADK-specific issues
- Prototyping new agent architectures

**Use Opik for:**
- ✅ Production monitoring (your use case)
- ✅ Tracing FastAPI backend calls
- ✅ Analyzing real user sessions
- ✅ Tracking costs and performance
- ✅ Sharing traces with team

---

## Next Steps

1. **Install Opik**: `pip install opik`
2. **Configure**: `opik configure`
3. **Add decorators**: Add `@track()` to key functions
4. **Test**: Make a request through your Next.js UI
5. **View traces**: Check Comet dashboard

---

## Example Output

After integration, when a user generates a hypothesis tree through your UI:

```
Trace: generate_hypothesis_tree_stream
Duration: 45.2s
Status: Success
User: anonymous_user_123
Framework: scale_decision
Problem: "Should we scale fall detection system?"

Steps:
  1. Research Phase (12.3s) ✓
     - Market research: 6.1s, 850 tokens
     - Competitor research: 6.2s, 920 tokens

  2. Analysis Phase (28.4s) ✓
     - Generate tree: 15.2s, 1250 tokens
     - MECE validation: 13.2s (passed)

  3. Prioritization (4.1s) ✓
     - 2x2 matrix generated

  4. Save (0.4s) ✓
     - Project ID: bdbbd4a1

Total cost: $0.0047
```

---

## Recommendation

**For your Kaggle submission and future development, use Opik.**

It will give you:
- Better visibility into your production system
- Traces of actual user sessions
- Performance metrics for optimization
- Cost tracking for scaling decisions
- Professional monitoring for your capstone demo
