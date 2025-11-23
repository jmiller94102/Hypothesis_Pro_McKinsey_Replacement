# HypothesisTree Pro - Visualization UI

Next.js-based visualization interface for the HypothesisTree Pro strategic consultant agent.

## Features

- **3-Panel Layout**: Fixed sidebar, scrollable tree view, collapsible debug panel
- **Visual Differentiation**: L1 (🟣 purple), L2 (🔵 blue), L3 (🟢 green) nodes
- **Inline Editing**: Double-click any node to edit labels/questions
- **MECE Validation**: Manual trigger with live status display
- **Revision Control**: Versioned JSON saves (v1, v2, v3...)
- **Debug Logging**: All actions logged in collapsible bottom panel

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env.local
# Edit .env.local if your Python backend is on a different port
```

### 3. Start Development Server

```bash
npm run dev
```

The UI will be available at http://localhost:3000

### 4. Ensure Backend is Running

The Python FastAPI backend must be running on http://localhost:8000:

```bash
# From project root
source venv/bin/activate
python strategic_consultant_agent/api/main.py
```

## Usage

### Creating a Project

1. Go to http://localhost:3000
2. Enter a problem statement (e.g., "Should we scale deployment of fall detection?")
3. Select a framework template
4. Click "Create Project"

### Editing the Tree

- **Collapse/Expand**: Click `[−]` or `[+]` on any node
- **Edit**: Double-click a node's label or click the ✏️ icon
- **Delete**: Click 🗑️ (click twice to confirm)
- **Add Node**: Click `[+ Add L2 Branch]` or `[+ Add L3 Leaf]` buttons
- **Save**: Click "Save" in sidebar (shows `*` when unsaved changes)
- **Validate MECE**: Click "Validate MECE" to check compliance

### Version History

- All saves create new versions (v1, v2, v3...)
- Click "Version History" in sidebar to see all versions
- Click any version to load it

### Debug Panel

- Shows all actions (edit, delete, add, validate, save)
- Independent scrolling
- Collapsible (click header to toggle)

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **API Client**: Native fetch with type-safe wrapper
- **Backend**: FastAPI (Python)

## Project Structure

```
hypothesis-tree-ui/
├── app/
│   ├── page.tsx                # Home page (create/load projects)
│   ├── editor/page.tsx         # Main editor (3-panel layout)
│   ├── layout.tsx              # Root layout
│   └── globals.css             # Global styles
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx         # Left sidebar
│   │   ├── MainTreeView.tsx    # Center panel
│   │   └── DebugPanel.tsx      # Bottom panel
│   └── tree/
│       ├── TreeNode.tsx        # Individual node
│       └── InlineEditor.tsx    # Inline editing
└── lib/
    ├── types.ts                # TypeScript types
    └── api-client.ts           # API wrapper
```

## API Integration

The frontend communicates with the Python backend via REST API:

- `POST /api/tree/generate` - Generate new tree
- `POST /api/tree/validate-mece` - Validate MECE compliance
- `POST /api/tree/add-node` - Add L1/L2/L3 node
- `POST /api/tree/delete-node` - Delete node
- `POST /api/tree/update-node` - Update node
- `POST /api/tree/save` - Save with versioning
- `GET /api/tree/load/{project}` - Load project
- `GET /api/tree/versions/{project}` - List versions
- `GET /api/frameworks` - List framework templates
- `GET /api/projects` - List all projects

## Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint
npm run lint
```

## Notes

- Desktop-first design (no mobile optimization)
- Single-user (no collaboration features)
- Manual save (no auto-save)
- Manual MECE validation (allows multiple edits before validation)
- Scrolling: Main tree (X/Y), Debug panel (Y only), Sidebar (fixed)
