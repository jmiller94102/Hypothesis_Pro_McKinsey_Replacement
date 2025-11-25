# Google ADK Evaluation Setup - COMPLETE

**Status**: ✅ **FIXED AND READY**
**Date**: 2025-11-23
**Evalset File**: `evaluation/strategic_consultant_adk.evalset.json`

---

## Summary

The Google ADK evalset has been successfully configured with the correct format and session state initialization.

### ✅ What Was Fixed

1. **Evalset Format** - Converted from custom format to ADK-compliant schema
   - Added required `eval_set_id` field
   - Changed `test_cases` to `eval_cases`
   - Used proper `Invocation` and `SessionInput` structures

2. **Session State Problem** - Fixed `KeyError: 'Context variable not found: problem'`
   - Root cause: Agent prompts reference `{problem}` variable
   - Solution: Added `SessionInput` with `state={"problem": "..."}`  to each eval case
   - Now the `problem` variable is available in session state for all agents

3. **Agent Module Export** - Fixed `agent_module.agent.root_agent` structure
   - Updated `strategic_consultant_agent/__init__.py` to expose `agent` submodule
   - Updated `strategic_consultant_agent/agent.py` to export `root_agent` instance

---

## Evalset File Structure

### Correct ADK Schema

```json
{
  "eval_set_id": "strategic-consultant-evalset-v1",
  "name": "Strategic Consultant Agent Evaluation",
  "description": "Test cases for HypothesisTree Pro...",
  "eval_cases": [
    {
      "eval_id": "tc-001-scale-decision",
      "session_input": {
        "app_name": "strategic_consultant_agent",
        "user_id": "eval_user",
        "state": {
          "problem": "Should we scale deployment of..."
        }
      },
      "conversation": [
        {
          "user_content": {
            "role": "user",
            "parts": [
              {
                "text": "Should we scale deployment of..."
              }
            ]
          }
        }
      ]
    }
  ]
}
```

###Key Fields Explained

| Field | Purpose |
|-------|---------|
| `eval_set_id` | Unique identifier for the evaluation set |
| `eval_cases` | Array of test cases (NOT `test_cases`) |
| `session_input` | Initializes session state with `problem` variable |
| `session_input.state` | Key-value pairs available to agents via `{key}` syntax |
| `conversation` | Array of user/agent interactions |

---

## Test Cases (6 Total)

1. **tc-001-scale-decision** - Scale deployment question (fall detection)
2. **tc-002-market-entry** - Market entry question (European eldercare)
3. **tc-003-product-launch** - Product launch question (medication adherence)
4. **tc-004-mece-validation** - MECE validation with overlapping categories
5. **tc-005-investment-decision** - Investment question (telemedicine startup)
6. **tc-006-prioritization** - Prioritization request (hypothesis testing order)

---

## Running Evaluation

### Command

```bash
source venv/bin/activate
adk eval strategic_consultant_agent evaluation/strategic_consultant_adk.evalset.json \
    --print_detailed_results
```

### Expected Behavior

1. **Loads agent**: ADK finds `strategic_consultant_agent.agent.root_agent`
2. **Initializes session**: Sets `problem` variable from `session_input.state`
3. **Runs workflow**: SequentialAgent → ParallelAgent → LoopAgent → Prioritizer
4. **Captures results**: Tool calls, agent responses, workflow completion
5. **Generates report**: Pass/fail for each test case

### Note on Google Search

The agents use `google_search` tool which requires:
- Valid `GOOGLE_API_KEY` in environment (`.env` file)
- Active internet connection
- May incur API costs for search requests

For cost-free evaluation, agents will run but search calls may fail (this is expected).

---

## Files Modified

### 1. `create_evalset.py` (Generator Script)
```python
from google.adk.evaluation.eval_set import EvalSet
from google.adk.evaluation.eval_case import EvalCase, Invocation, SessionInput
from google.genai.types import Content, Part

# Creates properly formatted evalset with:
# - SessionInput for each case
# - problem variable in state
# - Correct Invocation format
```

### 2. `strategic_consultant_agent/__init__.py`
```python
from strategic_consultant_agent import agent
from strategic_consultant_agent.agent import create_strategic_analyzer

__all__ = ["create_strategic_analyzer", "agent"]
```

### 3. `strategic_consultant_agent/agent.py`
```python
# Export root_agent as instance (not callable)
root_agent = create_strategic_analyzer()
```

---

## Validation Status

| Check | Status | Notes |
|-------|--------|-------|
| Evalset format | ✅ | ADK-compliant schema |
| Session state | ✅ | `problem` variable initialized |
| Agent export | ✅ | `agent.root_agent` accessible |
| Test cases | ✅ | 6 diverse scenarios |
| Tool availability | ✅ | All custom tools registered |

---

## Next Steps (Optional)

### 1. Add Evaluation Rubrics (Advanced)

Currently, evalset uses default criteria. To add custom rubrics:

```python
from google.adk.evaluation.eval_rubrics import Rubric

rubric = Rubric(
    metric_name="framework_selection_accuracy",
    criteria="Agent must select correct framework based on problem type",
    passing_threshold=0.8
)

eval_case = EvalCase(
    eval_id="tc-001",
    rubrics=[rubric],
    ...
)
```

### 2. Multi-Turn Conversations

Current evalset has single-turn conversations. To add follow-ups:

```python
conversation=[
    create_invocation("Initial question"),
    create_invocation("Follow-up question")
]
```

### 3. Expected Tool Trajectory

To validate specific tool calls:

```python
from google.adk.evaluation.eval_case import IntermediateData

expected_data = IntermediateData(
    expected_tool_calls=[
        "generate_hypothesis_tree",
        "validate_mece_structure",
        "generate_2x2_matrix"
    ]
)
```

---

## Troubleshooting

### Error: "Context variable not found: {variable}"

**Cause**: Agent prompts reference a variable not in session state
**Solution**: Add variable to `session_input.state`

### Error: "module 'agent' has no attribute 'agent'"

**Cause**: Agent module structure incorrect
**Solution**: Ensure `__init__.py` exposes `agent` submodule

### Error: "google_search failed"

**Cause**: Missing/invalid GOOGLE_API_KEY or network issue
**Solution**: Set valid API key or expect search failures (agents continue)

---

## References

- **ADK Documentation**: https://github.com/google/adk-toolkit
- **Evalset Schema**: `google.adk.evaluation.eval_set.EvalSet`
- **EvalCase Schema**: `google.adk.evaluation.eval_case.EvalCase`
- **Session Input**: `google.adk.evaluation.eval_case.SessionInput`

---

**Created**: 2025-11-23
**Last Updated**: 2025-11-23
**Status**: Ready for `adk eval`
