"""FastAPI backend for HypothesisTree visualization.

Provides REST API endpoints for tree generation, validation, and persistence.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
import json
from typing import Any, Optional

from strategic_consultant_agent.tools.hypothesis_tree import generate_hypothesis_tree
from strategic_consultant_agent.tools.mece_validator import validate_mece_structure
from strategic_consultant_agent.tools.framework_loader import FrameworkTemplateLoader

app = FastAPI(title="HypothesisTree Pro API", version="1.0.0")

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.post("/api/tree/generate")
async def generate_tree(request: TreeGenerateRequest):
    """Generate new tree from framework template."""
    try:
        tree = generate_hypothesis_tree(
            problem=request.problem,
            framework=request.framework
        )
        return {
            "tree": tree,
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
        loader = FrameworkTemplateLoader()
        frameworks = loader.get_all_framework_names()

        # Get detailed info for each framework
        framework_details = []
        for name in frameworks:
            template = loader.get_framework_by_name(name)
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
