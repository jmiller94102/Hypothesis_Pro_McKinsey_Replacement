"""FastAPI backend for HypothesisTree visualization.

Provides REST API endpoints for tree generation, validation, and persistence.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
import json
from typing import Any, Optional, Dict, AsyncGenerator
import asyncio
import uuid

from strategic_consultant_agent.tools.hypothesis_tree import generate_hypothesis_tree
from strategic_consultant_agent.tools.framework_loader import FrameworkLoader
from strategic_consultant_agent.tools.persistence import save_analysis, load_analysis, _sanitize_filename
from strategic_consultant_agent.tools.matrix_2x2 import generate_2x2_matrix
import re

# Import for Google Search research
import os
import asyncio
from google import genai

app = FastAPI(title="HypothesisTree Pro API", version="1.0.0")


def sanitize_project_name_for_frontend(problem: str) -> str:
    """
    Sanitize project name to match frontend logic.
    Frontend: problem.toLowerCase().replace(/[^a-z0-9]+/g, '_').substring(0, 50)
    """
    # Convert to lowercase
    sanitized = problem.lower()
    # Replace non-alphanumeric with underscores
    sanitized = re.sub(r'[^a-z0-9]+', '_', sanitized)
    # Trim to 50 characters
    sanitized = sanitized[:50]
    # Remove trailing underscore if present
    sanitized = sanitized.rstrip('_')
    return sanitized


# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helper functions for Google Search research
def perform_research(problem: str) -> tuple[str, str]:
    """
    Perform comprehensive market and competitor research using Google GenAI with Google Search.

    OPTIMIZATION: Combines market + competitor research into 1 LLM call instead of 2 sequential calls.
    Uses google.genai directly to avoid ADK API compatibility issues.

    Returns:
        tuple: (market_research, competitor_research)
    """
    print(f"  → Running comprehensive research with Google Search...")

    try:
        # Initialize genai client
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

        # Combined research prompt
        research_prompt = f"""You are a senior strategy consultant conducting comprehensive market and competitive research.

Your task is to research the complete strategic context for: {problem}

Use the google_search tool to find current, credible data. Your research must cover TWO areas:

## PART 1: MARKET RESEARCH
Focus on:
1. **Market Size & Growth**: Total addressable market, growth rates, key segments
2. **Industry Trends**: Technology adoption trends, regulatory changes, demographic shifts
3. **Benchmarks**: Industry standards for success metrics, typical ROI, adoption rates (cite specific sources like KLAS, McKinsey, LeadingAge)
4. **Market Drivers**: Key factors driving adoption or resistance

## PART 2: COMPETITIVE LANDSCAPE
Focus on:
1. **Key Vendors**: Major players in this space (include specific company names like Teton.ai, SafelyYou, etc.)
2. **Product Capabilities**: Features, strengths, weaknesses
3. **Pricing Models**: How vendors price (per unit, subscription, etc.) - include specific prices if available
4. **Customer Reviews**: Implementation experience, support quality, results achieved
5. **Case Studies**: Published success stories or failure analyses

**Output Format:**
Provide TWO clearly separated sections:

### MARKET RESEARCH
[Your market research findings with numbers and citations]

### COMPETITIVE LANDSCAPE
[Your competitive analysis with specific vendor names and sources]

**Search Strategy**: Use multiple targeted searches like:
- "[technology] market size [year]"
- "[industry] adoption rates benchmark"
- "[vendor name] pricing"
- "[vendor name] customer reviews"
- "[technology type] vendors comparison"

Provide specific numbers, citations, and objective analysis. Note any data gaps clearly."""

        # Generate with Google Search tool
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=research_prompt,
            config={
                "tools": [{"google_search": {}}],
                "temperature": 0.7,
            }
        )

        # Extract text from response
        full_research = response.text if hasattr(response, 'text') else str(response)

    except Exception as e:
        print(f"  ✗ Research failed: {e}")
        # Return fallback research
        full_research = f"""### MARKET RESEARCH
No market research available due to API error: {str(e)}

### COMPETITIVE LANDSCAPE
No competitive research available due to API error: {str(e)}"""

    # Split the response into market and competitor sections
    if "### COMPETITIVE LANDSCAPE" in full_research or "### COMPETITIVE INTELLIGENCE" in full_research or "## PART 2" in full_research:
        # Try to split on section headers
        parts = full_research.split("###")
        if len(parts) >= 2:
            market_research = parts[0].replace("MARKET RESEARCH", "").replace("## PART 1:", "").strip()
            competitor_research = "\n".join(parts[1:]).replace("COMPETITIVE LANDSCAPE", "").replace("COMPETITIVE INTELLIGENCE", "").replace("## PART 2:", "").strip()
        else:
            # Fallback: split on "PART 2"
            parts = full_research.split("## PART 2")
            if len(parts) == 2:
                market_research = parts[0].replace("## PART 1:", "").strip()
                competitor_research = parts[1].strip()
            else:
                # Fallback: use full research for both
                market_research = full_research
                competitor_research = full_research
    else:
        # No clear sections - use full research for both
        market_research = full_research
        competitor_research = full_research

    return market_research, competitor_research


# Request/Response Models
class TreeGenerateRequest(BaseModel):
    """Request model for generating a new tree."""
    problem: str
    framework: str


class AddNodeRequest(BaseModel):
    """Request model for adding a node."""
    tree: dict[str, Any]
    path: list[str]
    level: str  # "L1", "L2", or "L3"
    node_data: dict[str, Any]


class DeleteNodeRequest(BaseModel):
    """Request model for deleting a node."""
    tree: dict[str, Any]
    path: list[str]


class UpdateNodeRequest(BaseModel):
    """Request model for updating a node."""
    tree: dict[str, Any]
    path: list[str]
    node_data: dict[str, Any]


class SaveRequest(BaseModel):
    """Request model for saving a tree."""
    project_id: str  # UUID-based project ID
    tree: dict[str, Any]
    description: Optional[str] = None


# Endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "HypothesisTree Pro API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/tree/generate-stream")
async def generate_tree_stream(problem: str, framework: str):
    """Generate new tree with progress updates via Server-Sent Events.

    Note: GET endpoint for EventSource compatibility.
    """

    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events for progress updates."""
        try:
            # Generate unique project ID (UUID)
            project_id = str(uuid.uuid4())[:8]  # Short UUID for readability

            # Helper to send progress event
            def send_progress(stage: str, message: str, progress: int):
                event_data = {
                    "stage": stage,
                    "message": message,
                    "progress": progress,
                    "timestamp": datetime.now().isoformat()
                }
                return f"data: {json.dumps(event_data)}\n\n"

            # Stage 1: Check cache
            yield send_progress("cache_check", "Checking for cached research...", 10)
            await asyncio.sleep(0.1)  # Allow UI to update

            market_research = ""
            competitor_research = ""
            cached = False

            try:
                research_data = load_analysis(
                    project_name=project_id,
                    analysis_type="research"
                )
                market_research = research_data["content"].get("market_research", "")
                competitor_research = research_data["content"].get("competitor_research", "")
                cached = True
                yield send_progress("cache_check", "✓ Found cached research", 20)
            except FileNotFoundError:
                yield send_progress("cache_check", "No cache found - running fresh research", 20)

                # Stage 2: Market research
                yield send_progress("market_research", "Running market research with Google Search...", 30)
                await asyncio.sleep(0.1)

                try:
                    # Run research in thread pool to avoid blocking
                    loop = asyncio.get_event_loop()
                    market_research, competitor_research = await loop.run_in_executor(
                        None, perform_research, problem
                    )
                    yield send_progress("market_research", "✓ Market research complete", 50)
                except Exception as e:
                    yield send_progress("market_research", f"⚠ Research error: {str(e)}", 50)
                    market_research = f"Market research unavailable: {str(e)}"
                    competitor_research = f"Competitor research unavailable: {str(e)}"

                # Stage 3: Save research cache
                yield send_progress("save_cache", "Saving research cache...", 60)
                save_analysis(
                    project_name=project_id,
                    analysis_type="research",
                    content={
                        "market_research": market_research,
                        "competitor_research": competitor_research,
                        "problem": problem,  # Store original problem for reference
                        "framework": framework
                    }
                )
                yield send_progress("save_cache", "✓ Research cached", 65)

            # Stage 4: Generate tree with incremental MECE validation
            # Note: Validation now happens inside generate_hypothesis_tree with memory/feedback
            yield send_progress("generate_tree", "Generating hypothesis tree with incremental validation...", 70)
            await asyncio.sleep(0.1)

            # Generate tree (validation happens incrementally during generation)
            loop_executor = asyncio.get_event_loop()
            tree = await loop_executor.run_in_executor(
                None,
                generate_hypothesis_tree,
                problem,
                framework,
                None,  # custom_l1_categories
                market_research,
                competitor_research,
                True  # use_llm_generation
            )

            # Check validation results from metadata
            validation_results = tree.get("metadata", {}).get("validation_results", {})
            all_passed = validation_results.get("all_passed", False)

            if all_passed:
                yield send_progress("mece_validation", "✓ All MECE validations passed", 90)
            else:
                # Report which components had issues
                l2_validation = validation_results.get("l2_validation", {})
                l3_validation = validation_results.get("l3_validation", {})

                failed_l1_count = sum(1 for v in l2_validation.get("l1_results", {}).values() if not v.get("is_mece", True))
                failed_l2_count = sum(
                    sum(1 for l2_result in l1_l3.get("l2_results", {}).values() if not l2_result.get("is_mece", True))
                    for l1_l3 in l3_validation.values()
                )

                yield send_progress(
                    "mece_validation",
                    f"⚠ Validation: {failed_l1_count} L1 categories, {failed_l2_count} L2 branches had issues after max attempts",
                    90
                )

            yield send_progress("generate_tree", "✓ Tree generation complete", 85)
            await asyncio.sleep(0.1)

            # Stage 5: Generate 2x2 prioritization matrix
            yield send_progress("prioritization", "Generating 2x2 prioritization matrix...", 88)
            await asyncio.sleep(0.1)

            # Extract all L3 leaves as items to prioritize
            items = []
            for l1_key, l1_data in tree.get("tree", {}).items():
                for l2_key, l2_data in l1_data.get("L2_branches", {}).items():
                    for l3_leaf in l2_data.get("L3_leaves", []):
                        items.append(l3_leaf.get("label", ""))

            # Generate priority matrix
            try:
                matrix_executor = asyncio.get_event_loop()
                priority_matrix = await matrix_executor.run_in_executor(
                    None,
                    generate_2x2_matrix,
                    items,
                    "Effort",  # x_axis
                    "Impact",  # y_axis
                    "prioritization"  # matrix_type
                )
                yield send_progress("prioritization", "✓ Priority matrix generated", 92)
            except Exception as matrix_error:
                yield send_progress("prioritization", f"⚠ Matrix generation failed: {matrix_error}", 92)
                priority_matrix = None

            # Auto-save the tree before sending completion (eliminates race condition)
            yield send_progress("save", "Saving project to storage...", 95)
            try:
                save_result = save_analysis(
                    project_name=project_id,
                    analysis_type="hypothesis_tree",
                    content=tree
                )
                yield send_progress("save", f"✓ Tree saved as v{save_result['version']}", 97)
            except Exception as save_error:
                yield send_progress("save", f"⚠ Tree auto-save failed: {save_error}", 97)
                # Continue anyway - frontend can retry save

            # Save priority matrix if generated
            if priority_matrix:
                try:
                    matrix_save_result = save_analysis(
                        project_name=project_id,
                        analysis_type="matrix",
                        content=priority_matrix
                    )
                    yield send_progress("save", f"✓ Matrix saved as v{matrix_save_result['version']}", 100)
                except Exception as matrix_save_error:
                    yield send_progress("save", f"⚠ Matrix save failed: {matrix_save_error}", 100)

            # Final result
            result = {
                "project_id": project_id,  # Return project ID to frontend
                "tree": tree,
                "research": {
                    "market": market_research[:500] + "..." if len(market_research) > 500 else market_research,
                    "competitor": competitor_research[:500] + "..." if len(competitor_research) > 500 else competitor_research,
                    "cached": cached
                },
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }

            yield f"data: {json.dumps({'stage': 'complete', 'result': result})}\n\n"

        except Exception as e:
            error_event = {
                "stage": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
            yield f"data: {json.dumps(error_event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.post("/api/tree/generate")
async def generate_tree(request: TreeGenerateRequest):
    """Generate new tree with automated research (cached for performance).

    Non-streaming version for backward compatibility.
    """
    try:
        # Step 1: Try to load cached research from disk
        market_research = ""
        competitor_research = ""
        cached = False

        try:
            research_data = load_analysis(
                project_name=request.problem,
                analysis_type="research"
            )
            # Use cached research from disk
            market_research = research_data["content"].get("market_research", "")
            competitor_research = research_data["content"].get("competitor_research", "")
            cached = True
            print(f"✓ Loaded cached research for: {request.problem}")
        except FileNotFoundError:
            # No cache - run research with Google Search
            print(f"⚡ Running fresh research with Google Search for: {request.problem}")

            try:
                market_research, competitor_research = perform_research(request.problem)
            except Exception as e:
                print(f"Research error: {e}")
                market_research = f"Market research unavailable: {str(e)}"
                competitor_research = f"Competitor research unavailable: {str(e)}"

            # Save research to disk for future use (persists across restarts)
            sanitized_name = sanitize_project_name_for_frontend(request.problem)
            save_analysis(
                project_name=sanitized_name,
                analysis_type="research",
                content={
                    "market_research": market_research,
                    "competitor_research": competitor_research
                }
            )
            print(f"✓ Saved research cache for: {sanitized_name}")

        # Step 2: Generate tree with research context and LLM-powered L2/L3
        tree = generate_hypothesis_tree(
            problem=request.problem,
            framework=request.framework,
            market_research=market_research,
            competitor_research=competitor_research,
            use_llm_generation=True  # Enable dynamic, problem-specific content
        )

        return {
            "tree": tree,
            "research": {
                "market": market_research[:500] + "..." if len(market_research) > 500 else market_research,
                "competitor": competitor_research[:500] + "..." if len(competitor_research) > 500 else competitor_research,
                "cached": cached
            },
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/tree/validate-mece")
async def validate_mece(tree: dict[str, Any]):
    """Validate MECE compliance (for manual validation via UI button)."""
    try:
        from strategic_consultant_agent.tools.mece_validator import validate_mece_structure
        result = validate_mece_structure(tree)
        return {
            "is_mece": result["is_mece"],
            "issues": result["issues"],
            "warnings": result.get("warnings", []),
            "suggestions": result["suggestions"],
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/tree/add-node")
async def add_node(request: AddNodeRequest):
    """Add L1/L2/L3 node to tree."""
    try:
        tree = request.tree.copy()
        path = request.path
        node_data = request.node_data
        level = request.level

        # Navigate to parent and add node
        if level == "L1":
            # Add new L1 category
            new_key = f"L1_{node_data['label'].upper().replace(' ', '_')}"
            tree["tree"][new_key] = {
                "label": node_data["label"],
                "question": node_data["question"],
                "description": node_data.get("description", ""),
                "L2_branches": {}
            }
        elif level == "L2":
            # Add L2 branch to L1
            l1_key = path[0]
            new_key = f"L2_{node_data['label'].upper().replace(' ', '_')}"
            tree["tree"][l1_key]["L2_branches"][new_key] = {
                "label": node_data["label"],
                "question": node_data["question"],
                "L3_leaves": []
            }
        elif level == "L3":
            # Add L3 leaf to L2
            l1_key, l2_key = path[0], path[1]
            tree["tree"][l1_key]["L2_branches"][l2_key]["L3_leaves"].append({
                "id": f"L3_{len(tree['tree'][l1_key]['L2_branches'][l2_key]['L3_leaves']) + 1:03d}",
                "label": node_data["label"],
                "question": node_data["question"],
                "metric_type": node_data.get("metric_type", "qualitative"),
                "target": node_data.get("target", "TBD"),
                "data_source": node_data.get("data_source", "TBD"),
                "status": "UNTESTED",
                "confidence": None,
                "components": [],
                "assessment_criteria": node_data.get("assessment_criteria", "TBD")
            })

        return {
            "tree": tree,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/tree/delete-node")
async def delete_node(request: DeleteNodeRequest):
    """Delete node by path."""
    try:
        tree = request.tree.copy()
        path = request.path

        if len(path) == 1:
            # Delete L1
            del tree["tree"][path[0]]
        elif len(path) == 2:
            # Delete L2
            del tree["tree"][path[0]]["L2_branches"][path[1]]
        elif len(path) == 3:
            # Delete L3
            l1_key, l2_key, l3_index = path[0], path[1], int(path[2])
            tree["tree"][l1_key]["L2_branches"][l2_key]["L3_leaves"].pop(l3_index)

        return {
            "tree": tree,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/tree/update-node")
async def update_node(request: UpdateNodeRequest):
    """Update node label/question/metadata."""
    try:
        tree = request.tree.copy()
        path = request.path
        node_data = request.node_data

        if len(path) == 1:
            # Update L1
            tree["tree"][path[0]].update(node_data)
        elif len(path) == 2:
            # Update L2
            tree["tree"][path[0]]["L2_branches"][path[1]].update(node_data)
        elif len(path) == 3:
            # Update L3
            l1_key, l2_key, l3_index = path[0], path[1], int(path[2])
            tree["tree"][l1_key]["L2_branches"][l2_key]["L3_leaves"][l3_index].update(node_data)

        return {
            "tree": tree,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/tree/save")
async def save_tree(request: SaveRequest):
    """Save tree with revision control (versioned JSON)."""
    try:
        # Add description to tree content if provided
        tree_content = request.tree.copy() if isinstance(request.tree, dict) else request.tree
        if request.description and isinstance(tree_content, dict):
            tree_content["description"] = request.description

        # Use project_id as the storage key
        result = save_analysis(
            project_name=request.project_id,
            analysis_type="hypothesis_tree",
            content=tree_content
        )

        return {
            "filepath": str(result["filepath"]),
            "version": result["version"],
            "timestamp": result["timestamp"],
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tree/load/{project_id}")
async def load_tree(project_id: str, version: Optional[int] = None):
    """Load tree (latest version or specific version)."""
    try:
        # Use project_id to load analysis
        result = load_analysis(
            project_name=project_id,
            analysis_type="hypothesis_tree",
            version=version
        )

        return {
            "data": result,
            "status": "success"
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tree/versions/{project_id}")
async def list_versions(project_id: str):
    """List all saved versions of a project."""
    try:
        # Use project_id directly (UUIDs don't need sanitization)
        from strategic_consultant_agent.tools.persistence import _sanitize_filename

        sanitized_name = _sanitize_filename(project_id)
        project_dir = Path(f"storage/projects/{sanitized_name}")

        if not project_dir.exists():
            return {"versions": [], "status": "success"}

        # Find all hypothesis_tree versions
        versions = []
        for file in sorted(project_dir.glob("hypothesis_tree_v*.json"),
                          key=lambda p: int(p.stem.split("_v")[1])):
            with open(file, encoding='utf-8') as f:
                data = json.load(f)
                versions.append({
                    "version": data["metadata"]["version"],
                    "timestamp": data["metadata"]["timestamp"],
                    "description": data["metadata"].get("description", "")
                })

        return {"versions": versions, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/frameworks")
async def list_frameworks():
    """List all available framework templates."""
    try:
        loader = FrameworkLoader()
        frameworks = loader.list_frameworks()

        # Get detailed info for each framework
        framework_details = []
        for name in frameworks:
            template = loader.get_framework(name)
            if template:
                framework_details.append({
                    "name": name,
                    "display_name": template.get("name", name),
                    "description": template.get("description", "")
                })

        return {
            "frameworks": framework_details,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects")
async def list_projects():
    """List all available projects."""
    try:
        storage_dir = Path("storage/projects")
        if not storage_dir.exists():
            return {"projects": [], "status": "success"}

        projects = []
        for project_dir in storage_dir.iterdir():
            if project_dir.is_dir():
                # Get latest version
                versions = sorted(project_dir.glob("hypothesis_tree_v*.json"))
                if versions:
                    with open(versions[-1], encoding='utf-8') as f:
                        data = json.load(f)
                        projects.append({
                            "name": project_dir.name,
                            "latest_version": data["metadata"]["version"],
                            "last_updated": data["metadata"]["timestamp"],
                            "problem": data["content"].get("problem", "Unknown")
                        })

        return {"projects": projects, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/matrix/{project_id}")
async def get_priority_matrix(project_id: str, version: Optional[int] = None):
    """
    Get priority matrix for a project.

    Args:
        project_id: Project UUID
        version: Optional version number (defaults to latest)

    Returns:
        dict: Priority matrix data
    """
    try:
        result = load_analysis(
            project_name=project_id,
            analysis_type="matrix",
            version=version
        )

        return {
            "success": True,
            "data": result,
            "status": "success"
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
