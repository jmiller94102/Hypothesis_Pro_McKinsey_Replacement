# Multi-Matrix Feature - Next Steps

**Current Status**: Backend + API + Types Complete (5 commits), Frontend UI Remaining
**Branch**: `feature/multi-matrix`
**Last Updated**: 2025-11-24 (Session 2)

## ✅ What's Been Completed

### Backend Infrastructure (100% Complete)
1. **Matrix Type Definitions** (`strategic_consultant_agent/config/matrix_types.py`)
   - 4 matrix types configured with quadrants, axes, recommendations

2. **AI Generation Prompts** (`strategic_consultant_agent/prompts/matrix_generation/`)
   - Risk Register, Task Prioritization, Measurement Priorities prompts
   - Total 13,077 characters of carefully crafted prompts

3. **Multi-Matrix Persistence** (`strategic_consultant_agent/tools/persistence.py`)
   - `save_matrix()`, `load_matrix()`, `list_project_matrices()`, `get_all_project_data()`
   - Independent versioning per matrix type

4. **AI Matrix Generator** (`strategic_consultant_agent/tools/matrix_generator.py`)
   - Google Gemini integration
   - Auto-generation from hypothesis trees
   - Individual item refinement

### API Endpoints (100% Complete)
5. **Matrix Management APIs** (`strategic_consultant_agent/api/main.py`)
   - `GET /api/projects/{project_id}/matrices` - List all matrices with metadata
   - `GET /api/projects/{project_id}/matrices/{matrix_type}` - Get specific matrix
   - `POST /api/projects/{project_id}/matrices/{matrix_type}` - Generate & save matrix (AI-powered)
   - `PUT /api/projects/{project_id}/matrices/{matrix_type}/items` - Update placements
   - All endpoints tested and working

### Frontend Types (100% Complete)
6. **TypeScript Definitions** (`hypothesis-tree-ui/lib/types.ts`)
   - `MatrixType` union type (4 matrix types)
   - `MatrixData` interface matching backend schema
   - `ProjectData` interface (tree + 4 matrices)
   - `ProjectMatricesResponse` for API responses
   - Extended `QuadrantData` with color and priority fields

## 🎯 Remaining Work (Est. 5-7 hours)

### Phase 3: Generic MatrixView Component (3-4 hours) - NEXT PRIORITY

**File**: `strategic_consultant_agent/api/main.py`

Add these endpoints to the existing FastAPI app:

```python
# 1. Get all matrices for a project
@app.get("/api/projects/{project_id}/matrices")
async def get_project_matrices(project_id: str):
    """List all matrices for a project with metadata."""
    from strategic_consultant_agent.tools.persistence import list_project_matrices
    try:
        result = list_project_matrices(project_id)
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")

# 2. Get specific matrix
@app.get("/api/projects/{project_id}/matrices/{matrix_type}")
async def get_matrix(project_id: str, matrix_type: str):
    """Get a specific matrix by type."""
    from strategic_consultant_agent.tools.persistence import load_matrix
    try:
        data = load_matrix(project_id, matrix_type)
        return data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Matrix not found")

# 3. Generate/Save matrix
@app.post("/api/projects/{project_id}/matrices/{matrix_type}")
async def create_matrix(project_id: str, matrix_type: str):
    """Generate and save a new matrix."""
    from strategic_consultant_agent.tools.persistence import load_analysis, save_matrix
    from strategic_consultant_agent.tools.matrix_generator import generate_matrix_from_tree

    # Load hypothesis tree
    tree_data = load_analysis(project_id, "hypothesis_tree")
    tree = tree_data.get("content")

    # Generate matrix
    matrix = generate_matrix_from_tree(tree, matrix_type)

    # Save matrix
    result = save_matrix(project_id, matrix_type, matrix)

    return {"matrix": matrix, "save_info": result}

# 4. Update matrix items
@app.put("/api/projects/{project_id}/matrices/{matrix_type}/items")
async def update_matrix_items(
    project_id: str,
    matrix_type: str,
    placements: dict  # {'Q1': [...], 'Q2': [...], etc.}
):
    """Update matrix item placements."""
    from strategic_consultant_agent.tools.persistence import load_matrix, save_matrix

    # Load existing matrix
    matrix_data = load_matrix(project_id, matrix_type)
    matrix = matrix_data.get("content")

    # Update placements
    matrix["placements"] = placements

    # Save updated matrix
    result = save_matrix(project_id, matrix_type, matrix)

    return {"matrix": matrix, "save_info": result}
```

**Testing**:
```bash
# Test matrix list
curl http://localhost:8000/api/projects/test_project/matrices

# Test matrix generation
curl -X POST http://localhost:8000/api/projects/test_project/matrices/risk_register

# Test matrix retrieval
curl http://localhost:8000/api/projects/test_project/matrices/risk_register
```

### Phase 2: Frontend Types (30 minutes)

**File**: `hypothesis-tree-ui/lib/types.ts`

Add these type definitions:

```typescript
// Matrix types
export type MatrixType =
  | 'hypothesis_prioritization'
  | 'risk_register'
  | 'task_prioritization'
  | 'measurement_priorities'

// Matrix data structure (extends existing PriorityMatrix if needed)
export interface MatrixData {
  matrix_type: MatrixType
  quadrants: {
    Q1: QuadrantInfo
    Q2: QuadrantInfo
    Q3: QuadrantInfo
    Q4: QuadrantInfo
  }
  placements: {
    Q1: string[]
    Q2: string[]
    Q3: string[]
    Q4: string[]
  }
  x_axis: string
  y_axis: string
  recommendations: string[]
}

export interface QuadrantInfo {
  name: string
  position: string
  description: string
  color: string
  priority: number
}

// Project data with all matrices
export interface ProjectData {
  hypothesis_tree: HypothesisTree | null
  matrices: {
    [K in MatrixType]: MatrixData | null
  }
}
```

### Phase 3: Generic MatrixView Component (3-4 hours)

**File**: `hypothesis-tree-ui/components/prioritization/MatrixView.tsx` (NEW)

Refactor existing `Matrix2x2Editor.tsx` to be generic:

```typescript
interface MatrixViewProps {
  projectId: string
  matrixType: MatrixType  // New prop!
  matrixData: MatrixData
  onMatrixUpdate: (updated: MatrixData) => void
  onAddItem: (quadrant: string, item: string) => Promise<void>
  onDeleteItem: (quadrant: string, index: number) => Promise<void>
  onEditItem: (quadrant: string, index: number, text: string) => Promise<void>
  onMoveItem: (from: string, to: string, index: number) => Promise<void>
}

export function MatrixView({ matrixType, matrixData, ... }: MatrixViewProps) {
  // Use matrixData.quadrants for dynamic colors/labels
  // Use matrixData.x_axis and y_axis for labels
  // Use matrixData.recommendations for guidance

  // All existing edit/add/delete/drag-drop logic stays the same!
}
```

Key changes:
1. Accept `matrixType` and `matrixData` props
2. Use `matrixData.quadrants` for quadrant configs (colors, labels, descriptions)
3. Use `matrixData.x_axis` and `y_axis` for axis labels
4. Keep all existing interaction logic (edit, add, delete, drag-drop)

### Phase 4: 5-Tab Navigation (2-3 hours)

**File**: `hypothesis-tree-ui/app/editor/page.tsx`

Add tab navigation:

```typescript
const TABS = [
  { id: 'tree', label: 'Hypothesis Tree' },
  { id: 'hypothesis', label: 'Hypothesis Priority', matrixType: 'hypothesis_prioritization' },
  { id: 'risks', label: 'Risk Register', matrixType: 'risk_register' },
  { id: 'tasks', label: 'Task Priority', matrixType: 'task_prioritization' },
  { id: 'measurements', label: 'Measurement Priority', matrixType: 'measurement_priorities' }
] as const

const [activeTab, setActiveTab] = useState<string>('tree')
const [matrices, setMatrices] = useState<Record<MatrixType, MatrixData | null>>({
  hypothesis_prioritization: null,
  risk_register: null,
  task_prioritization: null,
  measurement_priorities: null
})

// Load all matrices on mount
useEffect(() => {
  if (projectId) {
    fetch(`/api/projects/${projectId}/matrices`)
      .then(res => res.json())
      .then(data => {
        // Load each matrix type
        TABS.filter(t => t.matrixType).forEach(tab => {
          fetch(`/api/projects/${projectId}/matrices/${tab.matrixType}`)
            .then(res => res.json())
            .then(matrixData => {
              setMatrices(prev => ({ ...prev, [tab.matrixType!]: matrixData.content }))
            })
            .catch(() => {
              // Matrix doesn't exist yet, that's okay
            })
        })
      })
  }
}, [projectId])

// Render active tab
{activeTab === 'tree' && <HypothesisTreeView ... />}
{activeTab !== 'tree' && (
  <MatrixView
    matrixType={TABS.find(t => t.id === activeTab)!.matrixType!}
    matrixData={matrices[TABS.find(t => t.id === activeTab)!.matrixType!]}
    ...
  />
)}
```

Add tab UI:
```tsx
<div className="flex border-b border-gray-700 bg-gray-900">
  {TABS.map(tab => (
    <button
      key={tab.id}
      onClick={() => setActiveTab(tab.id)}
      className={`px-4 py-2 text-sm ${
        activeTab === tab.id
          ? 'border-b-2 border-blue-500 text-blue-400'
          : 'text-gray-400 hover:text-gray-200'
      }`}
    >
      {tab.label}
    </button>
  ))}
</div>
```

### Phase 5: Integration & Polish (2-3 hours)

1. **Auto-Create Matrices on Tree Generation**
   - Modify tree generation endpoint to also create hypothesis_prioritization and risk_register matrices

2. **Generate Matrix Button**
   - Add "Generate Matrix" button for matrices that don't exist yet
   - Show loading state during AI generation

3. **Error Handling**
   - Handle API failures gracefully
   - Show user-friendly error messages

4. **Testing**
   - Test complete flow: Generate tree → View hypothesis matrix → Generate risk matrix → Edit items → Save
   - Test all 4 matrix types
   - Test drag-drop across quadrants
   - Test zoom controls on all tabs

### Phase 6: Merge to Main (30 minutes)

```bash
# Final commit
git add .
git commit -m "feat: complete multi-matrix feature with UI

- Backend API endpoints for all matrix operations
- Frontend TypeScript types for matrix data
- Generic MatrixView component
- 5-tab navigation (Tree + 4 matrices)
- Integration testing complete

Closes multi-matrix feature development."

# Merge to main
git checkout main
git merge feature/multi-matrix
git push

# Clean up
git branch -d feature/multi-matrix
```

## Quick Reference

**Backend Tools Available**:
```python
from strategic_consultant_agent.config.matrix_types import get_matrix_type_config
from strategic_consultant_agent.tools.persistence import save_matrix, load_matrix
from strategic_consultant_agent.tools.matrix_generator import generate_matrix_from_tree
```

**Matrix Types**:
- `hypothesis_prioritization` - Auto from L3 leaves
- `risk_register` - AI-generated
- `task_prioritization` - AI-generated
- `measurement_priorities` - AI-generated

**Key Files**:
- Backend API: `strategic_consultant_agent/api/main.py`
- Frontend Types: `hypothesis-tree-ui/lib/types.ts`
- Matrix Component: `hypothesis-tree-ui/components/prioritization/` (refactor existing)
- Editor Page: `hypothesis-tree-ui/app/editor/page.tsx`

## Recovery

If context is lost:
1. Read `MULTI-MATRIX-PROGRESS.md` for complete context
2. Check `git log` on `feature/multi-matrix` branch
3. All backend code is complete and working
4. Focus on: API endpoints → Types → Component → Navigation → Polish
