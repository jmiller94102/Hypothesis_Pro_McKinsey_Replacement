"""Create properly formatted ADK evalset.json file."""

from google.adk.evaluation.eval_set import EvalSet
from google.adk.evaluation.eval_case import EvalCase, Invocation, SessionInput
from google.genai.types import Content, Part
import json
import time

# Create invocations for each test case
def create_invocation(user_message: str) -> Invocation:
    """Create an Invocation with user content."""
    user_content = Content(
        role="user",
        parts=[Part(text=user_message)]
    )
    return Invocation(user_content=user_content)

# Define test cases with session_input to provide the 'problem' variable
eval_cases = [
    EvalCase(
        eval_id="tc-001-scale-decision",
        session_input=SessionInput(
            app_name="strategic_consultant_agent",
            user_id="eval_user",
            state={"problem": "Should we scale deployment of our Computer Vision Fall Detection system in Senior Living facilities?"}
        ),
        conversation=[
            create_invocation(
                "Should we scale deployment of our Computer Vision Fall Detection system in Senior Living facilities?"
            )
        ]
    ),
    EvalCase(
        eval_id="tc-002-market-entry",
        session_input=SessionInput(
            app_name="strategic_consultant_agent",
            user_id="eval_user",
            state={"problem": "Should we enter the European eldercare market with our telehealth platform?"}
        ),
        conversation=[
            create_invocation(
                "Should we enter the European eldercare market with our telehealth platform?"
            )
        ]
    ),
    EvalCase(
        eval_id="tc-003-product-launch",
        session_input=SessionInput(
            app_name="strategic_consultant_agent",
            user_id="eval_user",
            state={"problem": "Should we launch a new AI-powered medication adherence tracking product for chronic disease patients?"}
        ),
        conversation=[
            create_invocation(
                "Should we launch a new AI-powered medication adherence tracking product for chronic disease patients?"
            )
        ]
    ),
    EvalCase(
        eval_id="tc-004-mece-validation",
        session_input=SessionInput(
            app_name="strategic_consultant_agent",
            user_id="eval_user",
            state={"problem": "Should we expand our wearable health monitoring devices? Analyze using custom categories: Revenue, Financial Impact, and Market Size"}
        ),
        conversation=[
            create_invocation(
                "Should we expand our wearable health monitoring devices? Analyze using custom categories: Revenue, Financial Impact, and Market Size"
            )
        ]
    ),
    EvalCase(
        eval_id="tc-005-investment-decision",
        session_input=SessionInput(
            app_name="strategic_consultant_agent",
            user_id="eval_user",
            state={"problem": "Should we invest in acquiring a telemedicine startup specializing in rural healthcare?"}
        ),
        conversation=[
            create_invocation(
                "Should we invest in acquiring a telemedicine startup specializing in rural healthcare?"
            )
        ]
    ),
    EvalCase(
        eval_id="tc-006-prioritization",
        session_input=SessionInput(
            app_name="strategic_consultant_agent",
            user_id="eval_user",
            state={"problem": "What are the top priority hypotheses to test first for scaling fall detection in senior living?"}
        ),
        conversation=[
            create_invocation(
                "What are the top priority hypotheses to test first for scaling fall detection in senior living?"
            )
        ]
    )
]

# Create EvalSet
eval_set = EvalSet(
    eval_set_id="strategic-consultant-evalset-v1",
    name="Strategic Consultant Agent Evaluation",
    description="Test cases for HypothesisTree Pro strategic consultant agent using Google ADK multi-agent architecture",
    eval_cases=eval_cases,
    creation_timestamp=time.time()
)

# Save to JSON
output_file = "evaluation/strategic_consultant_adk.evalset.json"
with open(output_file, "w") as f:
    f.write(eval_set.model_dump_json(indent=2))

print(f"✓ Created ADK-compliant evalset: {output_file}")
print(f"✓ Total test cases: {len(eval_cases)}")
print("\nTest cases:")
for i, case in enumerate(eval_cases, 1):
    print(f"  {i}. {case.eval_id}")
