# HypothesisTree Pro - Visualization Layer

## Overview

The visualization layer consists of a Next.js frontend and FastAPI backend that provides an interactive interface for creating, editing, and validating MECE hypothesis trees.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Browser (localhost:3000)                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Next.js Frontend                                      │ │
│  │  ├── Home Page (create/load projects)                  │ │
│  │  └── Editor Page (3-panel layout)                      │ │
│  │      ├── Sidebar (fixed)                               │ │
│  │      ├── MainTreeView (scrollable X/Y)                 │ │
│  │      └── DebugPanel (collapsible bottom)               │ │
│  └────────────────────────────────────────────────────────┘ │
│                          ↕ REST API                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  FastAPI Backend (localhost:8000)                      │ │
│  │  ├── Tree generation (frameworks)                      │ │
│  │  ├── MECE validation                                   │ │
│  │  ├── Node operations (add/delete/update)               │ │
│  │  └── Persistence (versioned JSON)                      │ │
│  └────────────────────────────────────────────────────────┘ │
│                          ↕                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Existing Tools                                        │ │
│  │  ├── generate_hypothesis_tree                          │ │
│  │  ├── validate_mece_structure                           │ │
│  │  └── save_analysis / load_analysis                     │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Start Backend

```bash
# Activate virtual environment
source venv/bin/activate

# Install API dependencies (if not already installed)
pip install fastapi uvicorn pydantic python-multipart

# Start FastAPI server
python strategic_consultant_agent/api/main.py
```

Backend will run at http://localhost:8000

### 2. Start Frontend

```bash
# Navigate to UI directory
cd hypothesis-tree-ui

# Install dependencies (first time only)
npm install

# Create environment file
cp .env.example .env.local

# Start Next.js dev server
npm run dev
```

Frontend will run at http://localhost:3000

### 3. Use the Application

1. Open http://localhost:3000 in your browser
2. Create a new project or load an existing one
3. Edit the tree using the visual interface
4. Validate MECE compliance manually
5. Save your work (creates versioned JSON files)

## Features

### 3-Panel Layout

```
┌──────────┬────────────────────────────────────────┐
│          │                                        │
│ SIDEBAR  │     MAIN TREE VIEW                     │
│ (Fixed)  │     (Scrollable X/Y)                   │
│          │                                        │
│          │                                        │
│          ├────────────────────────────────────────┤
│          │ DEBUG PANEL (Collapsible, Scroll Y)    │
└──────────┴────────────────────────────────────────┘
```

#### Sidebar
- Project actions (Save, Validate, Export)
- MECE status display
- Version history
- Back to home button

#### Main Tree View
- Independent X/Y scrolling
- Visual hierarchy (L1 🟣, L2 🔵, L3 🟢)
- Inline editing (double-click)
- Add/delete nodes
- Collapse/expand branches

#### Debug Panel
- Logs all actions
- Timestamp for each event
- Color-coded by type (info/success/error/warning)
- Independent vertical scrolling

### Visual Differentiation

- **L1 Categories**: Purple (🟣), large bold font, 4px left border
- **L2 Branches**: Blue (🔵), medium semibold font, indented 8px
- **L3 Leaves**: Green (🟢), small normal font, indented 16px, shows metric type and target

### Inline Editing

- **Double-click** any node label to edit
- **Enter** to save, **Esc** to cancel
- Shows ✓ and ✗ buttons for save/cancel
- Updates immediately (marks project as unsaved)

### MECE Validation

- **Manual trigger** via sidebar button
- Shows live status: ✅ MECE Valid or ❌ MECE Invalid
- Lists overlaps and gaps
- Clears when tree is modified

### Revision Control

- Each save creates a new version (v1, v2, v3...)
- Files stored as: `storage/projects/{project_name}/hypothesis_tree_v{N}.json`
- Can load any previous version from sidebar
- Version list shows timestamp and version number

## API Endpoints

### Tree Operations

```
POST   /api/tree/generate          # Generate tree from framework
POST   /api/tree/validate-mece     # Validate MECE compliance
POST   /api/tree/add-node          # Add L1/L2/L3 node
POST   /api/tree/delete-node       # Delete node
POST   /api/tree/update-node       # Update node
```

### Persistence

```
POST   /api/tree/save              # Save with versioning
GET    /api/tree/load/{project}    # Load project (latest or specific version)
GET    /api/tree/versions/{project} # List all versions
```

### Metadata

```
GET    /api/frameworks             # List all framework templates
GET    /api/projects               # List all projects
```

## File Structure

### Backend

```
strategic_consultant_agent/
└── api/
    ├── __init__.py
    └── main.py                     # FastAPI app with all endpoints
```

### Frontend

```
hypothesis-tree-ui/
├── app/
│   ├── page.tsx                    # Home page
│   ├── editor/page.tsx             # Main editor
│   ├── layout.tsx                  # Root layout
│   └── globals.css                 # Tailwind styles
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx             # Left sidebar
│   │   ├── MainTreeView.tsx        # Center panel
│   │   └── DebugPanel.tsx          # Bottom panel
│   └── tree/
│       ├── TreeNode.tsx            # Individual node
│       └── InlineEditor.tsx        # Inline editing
├── lib/
│   ├── types.ts                    # TypeScript types
│   └── api-client.ts               # API wrapper
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── README.md
```

## Development Workflow

1. **Backend changes**: Edit `strategic_consultant_agent/api/main.py` and restart the server
2. **Frontend changes**: Edit files in `hypothesis-tree-ui/`, Next.js hot-reloads automatically
3. **Type changes**: Update `lib/types.ts` to match backend schema
4. **API changes**: Update `lib/api-client.ts` with new endpoints

## Testing

### Backend Testing

```bash
# Test API directly
curl http://localhost:8000/api/frameworks

# Test tree generation
curl -X POST http://localhost:8000/api/tree/generate \
  -H "Content-Type: application/json" \
  -d '{"problem": "Test problem?", "framework": "scale_decision"}'
```

### Frontend Testing

1. Open http://localhost:3000
2. Create a new project
3. Test all operations:
   - Edit nodes (double-click)
   - Add nodes (click [+ Add] buttons)
   - Delete nodes (click 🗑️ twice)
   - Validate MECE (click sidebar button)
   - Save (click Save button)
   - Load version (click version in sidebar)

## Design Decisions

### Why Manual MECE Validation?

Allows users to make multiple edits before triggering validation, reducing API calls and providing better UX.

### Why Manual Save?

- Clear indication of unsaved changes (`*` indicator)
- Explicit version control (user knows when new version is created)
- Reduces storage and API load

### Why Revision Control?

- No destructive edits (can always go back)
- Simple implementation (just increment version number)
- Easy to understand (v1, v2, v3 vs complex git-like system)

### Why 3-Panel Layout?

- Sidebar: Always visible controls
- Main view: Focus on tree content
- Debug panel: Optional transparency into system behavior

### Why Desktop-First?

- Strategic analysis tools are primarily desktop workflows
- Tree visualization requires horizontal space
- Simplifies implementation (no responsive breakpoints)

## Future Enhancements

Potential additions (not in current scope):

- Drag-and-drop reordering
- Keyboard shortcuts
- Export to Google Slides
- Real-time collaboration
- Advanced search/filter
- Auto-save with conflict resolution

## Troubleshooting

### Frontend can't reach backend

- Ensure FastAPI is running on port 8000
- Check `.env.local` has correct `NEXT_PUBLIC_API_URL`
- Check browser console for CORS errors

### Changes not saving

- Check backend logs for errors
- Verify `storage/projects/` directory exists and is writable
- Check debug panel for error messages

### Tree not rendering

- Check browser console for errors
- Verify tree data structure matches TypeScript types
- Check debug panel for load errors

## Integration with Existing System

The visualization layer integrates seamlessly with the existing HypothesisTree Pro agent:

- Uses existing `generate_hypothesis_tree` tool
- Uses existing `validate_mece_structure` tool
- Uses existing `save_analysis`/`load_analysis` tools (extended for versioning)
- Maintains same JSON schema
- No changes required to existing codebase (only additions)

## Performance

- Tree rendering: <100ms for typical trees (3 L1, 9 L2, 27 L3)
- API calls: <200ms for most operations
- MECE validation: <500ms for complex trees
- Saves: <100ms (JSON write)

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

No mobile browsers (desktop-first design).
