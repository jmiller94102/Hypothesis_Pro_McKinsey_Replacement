# 2x2 Matrix Visualization Implementation Guide

## Current Status

**Backend**: ✅ Fully implemented
- `generate_2x2_matrix()` tool exists
- Prioritizer agent generates matrix
- **Problem**: Matrix data is NOT being saved or passed to frontend

**Frontend**: ❌ Not implemented
- No visualization component
- No data structure to receive matrix
- No UI to display quadrants

---

## Implementation Plan

### Phase 1: Backend - Save Priority Matrix Data

#### Step 1: Update API to Include Priority Matrix

Edit `strategic_consultant_agent/api/main.py`:

```python
# In the generate_tree_stream function, after agent completes:

# Current code saves only tree:
project_storage.save_tree(
    project_id=project_id,
    content=hypothesis_tree,
    version=1,
    description="Initial version"
)

# NEW: Also save priority matrix as separate file:
if 'priority_matrix' in agent_result:  # Check if prioritizer ran
    project_storage.save_priority_matrix(
        project_id=project_id,
        matrix_data=agent_result['priority_matrix'],
        version=1
    )
```

#### Step 2: Add save_priority_matrix Method

Edit `strategic_consultant_agent/tools/persistence.py`:

```python
def save_priority_matrix(
    self,
    project_id: str,
    matrix_data: dict,
    version: int,
    description: str = ""
) -> dict:
    """
    Save priority matrix data.

    Args:
        project_id: Unique project identifier
        matrix_data: Priority matrix dict from prioritizer agent
        version: Version number
        description: Optional description

    Returns:
        dict: Save result with version and timestamp
    """
    project_dir = self.storage_path / project_id
    project_dir.mkdir(parents=True, exist_ok=True)

    filepath = project_dir / f"priority_matrix_v{version}.json"

    data = {
        "metadata": {
            "project_id": project_id,
            "version": version,
            "timestamp": datetime.now().isoformat(),
            "description": description or f"Priority Matrix v{version}",
        },
        "content": matrix_data
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return {
        "version": version,
        "timestamp": data["metadata"]["timestamp"],
        "filepath": str(filepath)
    }


def load_priority_matrix(self, project_id: str, version: int = None) -> dict:
    """Load priority matrix data."""
    project_dir = self.storage_path / project_id

    if version is None:
        # Find latest version
        matrix_files = list(project_dir.glob("priority_matrix_v*.json"))
        if not matrix_files:
            raise FileNotFoundError(f"No priority matrix found for project {project_id}")

        latest_file = max(matrix_files, key=lambda p: int(p.stem.split('_v')[1]))
    else:
        latest_file = project_dir / f"priority_matrix_v{version}.json"

    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)
```

#### Step 3: Add API Endpoint to Fetch Matrix

Edit `strategic_consultant_agent/api/main.py`:

```python
@app.get("/api/matrix/{project_id}")
async def get_priority_matrix(project_id: str, version: int = Query(None)):
    """
    Get priority matrix for a project.

    Args:
        project_id: Project UUID
        version: Optional version number (defaults to latest)

    Returns:
        dict: Priority matrix data
    """
    try:
        matrix_data = project_storage.load_priority_matrix(project_id, version)
        return {
            "success": True,
            "data": matrix_data
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

### Phase 2: Frontend - Add Matrix Visualization Component

#### Step 1: Create Matrix2x2 Component

Create `hypothesis-tree-ui/components/prioritization/Matrix2x2.tsx`:

```typescript
import React from 'react';

interface QuadrantData {
  name: string;
  position: string;
  description: string;
  action: string;
}

interface MatrixData {
  matrix_type: string;
  x_axis: string;
  y_axis: string;
  quadrants: {
    Q1: QuadrantData;
    Q2: QuadrantData;
    Q3: QuadrantData;
    Q4: QuadrantData;
  };
  placements: {
    Q1: string[];
    Q2: string[];
    Q3: string[];
    Q4: string[];
  };
  recommendations: string[];
}

interface Matrix2x2Props {
  matrixData: MatrixData;
}

export function Matrix2x2({ matrixData }: Matrix2x2Props) {
  const { quadrants, placements, x_axis, y_axis, recommendations } = matrixData;

  return (
    <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
      <h2 className="text-2xl font-bold mb-4">Prioritization Matrix</h2>
      <p className="text-gray-400 mb-6">
        {y_axis} vs. {x_axis}
      </p>

      {/* 2x2 Grid */}
      <div className="grid grid-cols-2 gap-4 mb-6" style={{ minHeight: '500px' }}>
        {/* Q1: Top-Left (High Y, Low X) - Quick Wins */}
        <div className="bg-green-900/20 border-2 border-green-600 rounded-lg p-4">
          <div className="text-green-400 font-bold text-lg mb-2">{quadrants.Q1.name}</div>
          <div className="text-sm text-gray-400 mb-3">{quadrants.Q1.position}</div>
          <div className="text-xs text-gray-500 mb-4">{quadrants.Q1.description}</div>

          {placements.Q1.length > 0 ? (
            <ul className="space-y-2">
              {placements.Q1.map((item, idx) => (
                <li key={idx} className="text-sm bg-gray-800 rounded px-3 py-2">
                  {item}
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-gray-600 text-sm italic">No items</div>
          )}
        </div>

        {/* Q2: Top-Right (High Y, High X) - Strategic Bets */}
        <div className="bg-yellow-900/20 border-2 border-yellow-600 rounded-lg p-4">
          <div className="text-yellow-400 font-bold text-lg mb-2">{quadrants.Q2.name}</div>
          <div className="text-sm text-gray-400 mb-3">{quadrants.Q2.position}</div>
          <div className="text-xs text-gray-500 mb-4">{quadrants.Q2.description}</div>

          {placements.Q2.length > 0 ? (
            <ul className="space-y-2">
              {placements.Q2.map((item, idx) => (
                <li key={idx} className="text-sm bg-gray-800 rounded px-3 py-2">
                  {item}
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-gray-600 text-sm italic">No items</div>
          )}
        </div>

        {/* Q3: Bottom-Left (Low Y, Low X) - Fill Later */}
        <div className="bg-gray-700/20 border-2 border-gray-600 rounded-lg p-4">
          <div className="text-gray-400 font-bold text-lg mb-2">{quadrants.Q3.name}</div>
          <div className="text-sm text-gray-400 mb-3">{quadrants.Q3.position}</div>
          <div className="text-xs text-gray-500 mb-4">{quadrants.Q3.description}</div>

          {placements.Q3.length > 0 ? (
            <ul className="space-y-2">
              {placements.Q3.map((item, idx) => (
                <li key={idx} className="text-sm bg-gray-800 rounded px-3 py-2">
                  {item}
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-gray-600 text-sm italic">No items</div>
          )}
        </div>

        {/* Q4: Bottom-Right (Low Y, High X) - Hard Slogs */}
        <div className="bg-red-900/20 border-2 border-red-600 rounded-lg p-4">
          <div className="text-red-400 font-bold text-lg mb-2">{quadrants.Q4.name}</div>
          <div className="text-sm text-gray-400 mb-3">{quadrants.Q4.position}</div>
          <div className="text-xs text-gray-500 mb-4">{quadrants.Q4.description}</div>

          {placements.Q4.length > 0 ? (
            <ul className="space-y-2">
              {placements.Q4.map((item, idx) => (
                <li key={idx} className="text-sm bg-gray-800 rounded px-3 py-2">
                  {item}
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-gray-600 text-sm italic">No items</div>
          )}
        </div>
      </div>

      {/* Axis Labels */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="text-center text-sm text-gray-500">
          ← Low {x_axis}
        </div>
        <div className="text-center text-sm text-gray-500">
          High {x_axis} →
        </div>
      </div>

      {/* Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <div className="bg-blue-900/20 border border-blue-700 rounded-lg p-4 mt-4">
          <h3 className="text-blue-400 font-semibold mb-3">Recommendations</h3>
          <ul className="space-y-2">
            {recommendations.map((rec, idx) => (
              <li key={idx} className="text-sm text-gray-300 flex items-start">
                <span className="text-blue-500 mr-2">•</span>
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```

#### Step 2: Add to Editor Page

Edit `hypothesis-tree-ui/app/editor/page.tsx`:

```typescript
import { Matrix2x2 } from '@/components/prioritization/Matrix2x2';

// Add state for priority matrix
const [priorityMatrix, setPriorityMatrix] = useState<MatrixData | null>(null);

// Load priority matrix along with tree
useEffect(() => {
  if (projectId) {
    loadProject();
    loadPriorityMatrix(); // NEW
  }
}, [projectId]);

async function loadPriorityMatrix() {
  try {
    const result = await api.loadPriorityMatrix(projectId);
    setPriorityMatrix(result.data.content);
  } catch (error) {
    console.error('Failed to load priority matrix:', error);
    // Non-fatal - matrix might not exist yet for old projects
  }
}

// In the JSX, add a tab or section for the matrix:
<div className="flex-1 flex flex-col">
  <TreeControls ... />

  {/* Add tab switcher */}
  <div className="flex border-b border-gray-800">
    <button
      className={`px-4 py-2 ${activeTab === 'tree' ? 'border-b-2 border-blue-500' : ''}`}
      onClick={() => setActiveTab('tree')}
    >
      Hypothesis Tree
    </button>
    <button
      className={`px-4 py-2 ${activeTab === 'matrix' ? 'border-b-2 border-blue-500' : ''}`}
      onClick={() => setActiveTab('matrix')}
    >
      Priority Matrix
    </button>
  </div>

  {activeTab === 'tree' && (
    <MainTreeView ... />
  )}

  {activeTab === 'matrix' && priorityMatrix && (
    <div className="flex-1 overflow-auto p-6">
      <Matrix2x2 matrixData={priorityMatrix} />
    </div>
  )}

  <DebugPanel ... />
</div>
```

#### Step 3: Add API Client Method

Edit `hypothesis-tree-ui/lib/api-client.ts`:

```typescript
async loadPriorityMatrix(projectId: string, version?: number) {
  const url = version
    ? `${this.baseURL}/api/matrix/${projectId}?version=${version}`
    : `${this.baseURL}/api/matrix/${projectId}`;

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error('Failed to load priority matrix');
  }
  return response.json();
}
```

---

## Testing the Implementation

### Step 1: Generate New Project with Matrix

Once API quota resets, create a new project:

```bash
# Test via curl
curl -N "http://localhost:8000/api/tree/generate-stream?problem=Should%20we%20launch%20AI%20chatbot&framework=scale_decision"
```

Check that both files are created:
```bash
ls storage/projects/[new-project-id]/
# Should see:
# hypothesis_tree_v1.json
# priority_matrix_v1.json  ← NEW
```

### Step 2: Test Matrix API

```bash
curl http://localhost:8000/api/matrix/[project-id]
```

Should return matrix data structure.

### Step 3: Test Frontend Display

1. Open http://localhost:3000
2. Generate new project
3. Click "Priority Matrix" tab
4. Should see 2x2 grid with items in quadrants

---

## What the 2x2 Matrix Will Show

```
┌────────────────────┬────────────────────┐
│  Quick Wins (Q1)   │ Strategic Bets (Q2)│
│  High Impact       │ High Impact        │
│  Low Effort        │ High Effort        │
│  ✅ Do First       │ ⚡ Plan Carefully  │
│                    │                    │
│  - Hypothesis A    │  - Hypothesis B    │
│  - Hypothesis C    │                    │
├────────────────────┼────────────────────┤
│  Fill Later (Q3)   │  Hard Slogs (Q4)   │
│  Low Impact        │ Low Impact         │
│  Low Effort        │ High Effort        │
│  ⏸️  Defer         │ ❌ Avoid           │
│                    │                    │
│  - Hypothesis E    │  - Hypothesis D    │
└────────────────────┴────────────────────┘

Recommendations:
• Start with 2 Quick Win(s) - highest ROI
• Plan carefully for 1 Strategic Bet(s)
• Suggested sequence: Quick Wins → Strategic Bets
```

---

## Timeline

- **Backend Changes**: 30 minutes (add save/load methods + API endpoint)
- **Frontend Component**: 45 minutes (create Matrix2x2 component)
- **Integration**: 30 minutes (add to editor page with tabs)
- **Testing**: 15 minutes

**Total**: ~2 hours to fully implement and test

---

## Alternative: Quick Mock for Demo

If you need to demo this NOW without API quota:

Create a mock priority matrix file:
```bash
mkdir -p storage/projects/bdbbd4a1
cat > storage/projects/bdbbd4a1/priority_matrix_v1.json << 'EOF'
{
  "metadata": {"version": 1, "project_id": "bdbbd4a1"},
  "content": {
    "matrix_type": "prioritization",
    "x_axis": "Effort",
    "y_axis": "Impact",
    "quadrants": {
      "Q1": {
        "name": "Quick Wins",
        "position": "High Impact, Low Effort",
        "description": "Do these first - high value with minimal investment",
        "action": "Prioritize immediately"
      },
      "Q2": {
        "name": "Strategic Bets",
        "position": "High Impact, High Effort",
        "description": "Invest carefully - requires significant resources",
        "action": "Plan strategically"
      },
      "Q3": {
        "name": "Fill Later",
        "position": "Low Impact, Low Effort",
        "description": "Do if time permits",
        "action": "Deprioritize"
      },
      "Q4": {
        "name": "Hard Slogs",
        "position": "Low Impact, High Effort",
        "description": "Avoid unless required",
        "action": "Eliminate or rethink"
      }
    },
    "placements": {
      "Q1": ["Pilot in 1-2 facilities first", "Track basic metrics"],
      "Q2": ["Full market research study", "Build integration with EMR"],
      "Q3": ["Create marketing materials"],
      "Q4": ["Custom hardware development"]
    },
    "recommendations": [
      "Start with 2 Quick Win(s) - highest ROI with minimal effort",
      "Plan carefully for 2 Strategic Bet(s) - high impact but requires resources",
      "Suggested sequence: Quick Wins → Strategic Bets → Fill Later (if time permits)"
    ]
  }
}
EOF
```

Then implement just the frontend component and API endpoint to display it.

---

## Summary

The 2x2 matrix tool is **implemented in code but not connected to the data pipeline**. To make it visible:

1. **Backend**: Save priority_matrix output from prioritizer agent
2. **Backend**: Add API endpoint to fetch matrix data
3. **Frontend**: Create Matrix2x2 visualization component
4. **Frontend**: Add tab/section to editor page to display matrix

Once implemented, users will see a professional 2x2 prioritization matrix showing which hypotheses to test first, creating an actionable testing roadmap.
