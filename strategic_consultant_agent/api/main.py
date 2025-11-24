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

from strategic_consultant_agent.tools.hypothesis_tree import generate_hypothesis_tree
from strategic_consultant_agent.tools.mece_validator import validate_mece_structure
from strategic_consultant_agent.tools.framework_loader import FrameworkLoader
from strategic_consultant_agent.tools.persistence import save_analysis, load_analysis

# Import for Google Search research
import os
import asyncio
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search

app = FastAPI(title="HypothesisTree Pro API", version="1.0.0")

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helper functions for Google Search research
def run_agent_sync(agent: Agent, input_text: str) -> str:
    """
    Run ADK agent synchronously and extract final output.

    Consumes the async generator from run_live() and returns the final text output.
    """
    async def run():
        events = agent.run_live(input_text)
        final_output = ""

        async for event in events:
            # Extract text output from events
            if hasattr(event, 'output') and event.output:
                final_output = str(event.output)
            elif hasattr(event, 'text') and event.text:
                final_output = str(event.text)

        return final_output if final_output else "No research results available"

    return asyncio.run(run())


def perform_research(problem: str) -> tuple[str, str]:
    """
    Perform market and competitor research using Google Search.

    Returns:
        tuple: (market_research, competitor_research)
    """
    print(f"  → Running market research with Google Search...")

    # Market research agent
    market_agent = Agent(
        name="market_researcher",
        model=Gemini(model="gemini-1.5-flash"),
        instruction=f"""You are a market research analyst specializing in healthcare technology and senior living industries.

Your task is to research the market context for: {problem}

Use the google_search tool to find current, credible data. Focus on:
1. **Market Size & Growth**: Total addressable market, growth rates, key segments
2. **Industry Trends**: Technology adoption trends, regulatory changes, demographic shifts
3. **Benchmarks**: Industry standards for success metrics, typical ROI, adoption rates (cite specific sources like KLAS, McKinsey, LeadingAge)
4. **Key Players**: Major vendors, market leaders, emerging disruptors

Provide a structured summary with specific numbers and citations.
If search results are limited, note the data gaps clearly.""",
        tools=[google_search]
    )

    market_research = run_agent_sync(market_agent, problem)

    print(f"  → Running competitor research with Google Search...")

    # Competitor research agent
    competitor_agent = Agent(
        name="competitor_researcher",
        model=Gemini(model="gemini-1.5-flash"),
        instruction=f"""You are a competitive intelligence analyst specializing in healthcare technology.

Your task is to research the competitive landscape for: {problem}

Use the google_search tool to find current information. Focus on:
1. **Key Vendors**: Who are the major players in this space? Include specific company names
2. **Product Capabilities**: What features do they offer? Strengths/weaknesses?
3. **Pricing Models**: How do vendors price (per unit, subscription, etc.)? Include specific prices if available
4. **Customer Reviews**: What do customers say about implementation, support, results?
5. **Case Studies**: Any published success stories or failure analyses?

Search for terms like "[vendor name] reviews", "[vendor name] pricing", "[technology type] vendors comparison"

Provide an objective analysis with sources. Include both positives and negatives.""",
        tools=[google_search]
    )

    competitor_research = run_agent_sync(competitor_agent, problem)

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
    project_name: str
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


@app.post("/api/tree/generate-stream")
async def generate_tree_stream(request: TreeGenerateRequest):
    """Generate new tree with progress updates via Server-Sent Events."""

    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events for progress updates."""
        try:
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
                    project_name=request.problem,
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
                        None, perform_research, request.problem
                    )
                    yield send_progress("market_research", "✓ Market research complete", 50)
                except Exception as e:
                    yield send_progress("market_research", f"⚠ Research error: {str(e)}", 50)
                    market_research = f"Market research unavailable: {str(e)}"
                    competitor_research = f"Competitor research unavailable: {str(e)}"

                # Stage 3: Save research cache
                yield send_progress("save_cache", "Saving research cache...", 60)
                save_analysis(
                    project_name=request.problem,
                    analysis_type="research",
                    content={
                        "market_research": market_research,
                        "competitor_research": competitor_research
                    }
                )
                yield send_progress("save_cache", "✓ Research cached", 65)

            # Stage 4: Generate tree
            yield send_progress("generate_tree", "Generating hypothesis tree with LLM...", 70)
            await asyncio.sleep(0.1)

            loop = asyncio.get_event_loop()
            tree = await loop.run_in_executor(
                None,
                generate_hypothesis_tree,
                request.problem,
                request.framework,
                market_research,
                competitor_research,
                True  # use_llm_generation
            )

            yield send_progress("generate_tree", "✓ Tree generation complete", 100)

            # Final result
            result = {
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
            save_analysis(
                project_name=request.problem,
                analysis_type="research",
                content={
                    "market_research": market_research,
                    "competitor_research": competitor_research
                }
            )
            print(f"✓ Saved research cache for: {request.problem}")

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
    """Validate MECE compliance."""
    try:
        result = validate_mece_structure(tree)
        return {
            "is_mece": result["is_mece"],
            "issues": result["issues"],
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
        # Get latest version number
        project_dir = Path(f"storage/projects/{request.project_name}")
        project_dir.mkdir(parents=True, exist_ok=True)

        existing_versions = list(project_dir.glob("hypothesis_tree_v*.json"))
        next_version = len(existing_versions) + 1

        filepath = project_dir / f"hypothesis_tree_v{next_version}.json"

        # Save with metadata
        save_data = {
            "metadata": {
                "project_name": request.project_name,
                "version": next_version,
                "timestamp": datetime.now().isoformat(),
                "description": request.description or f"Version {next_version}"
            },
            "content": request.tree
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2)

        return {
            "filepath": str(filepath),
            "version": next_version,
            "timestamp": save_data["metadata"]["timestamp"],
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tree/load/{project_name}")
async def load_tree(project_name: str, version: Optional[int] = None):
    """Load tree (latest version or specific version)."""
    try:
        project_dir = Path(f"storage/projects/{project_name}")

        if not project_dir.exists():
            raise HTTPException(status_code=404, detail="Project not found")

        if version:
            filepath = project_dir / f"hypothesis_tree_v{version}.json"
            if not filepath.exists():
                raise HTTPException(status_code=404, detail=f"Version {version} not found")
        else:
            # Load latest
            versions = sorted(project_dir.glob("hypothesis_tree_v*.json"))
            if not versions:
                raise HTTPException(status_code=404, detail="No versions found")
            filepath = versions[-1]

        with open(filepath, encoding='utf-8') as f:
            data = json.load(f)

        return {
            "data": data,
            "status": "success"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tree/versions/{project_name}")
async def list_versions(project_name: str):
    """List all saved versions of a project."""
    try:
        project_dir = Path(f"storage/projects/{project_name}")

        if not project_dir.exists():
            return {"versions": [], "status": "success"}

        versions = []
        for file in sorted(project_dir.glob("hypothesis_tree_v*.json")):
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
