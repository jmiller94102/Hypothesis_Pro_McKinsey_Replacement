# HypothesisTree Pro - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

### 1. Setup Backend (2 minutes)

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies (if not already installed)
pip install -r requirements.txt
pip install -r requirements-api.txt

# Start FastAPI server
python strategic_consultant_agent/api/main.py
```

Backend will run at **http://localhost:8000**

### 2. Setup Frontend (2 minutes)

```bash
# Navigate to UI directory
cd hypothesis-tree-ui

# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Start Next.js dev server
npm run dev
```

Frontend will run at **http://localhost:3000**

### 3. Use the Application (1 minute)

1. Open **http://localhost:3000** in your browser
2. Enter a problem statement:
   - Example: "Should we scale deployment of fall detection in senior living?"
3. Select a framework (e.g., "Scale Decision Framework")
4. Click **"Create Project"**
5. Start editing your hypothesis tree!

---

## 🎯 Key Features

### Visual Tree Editor

- **3-Panel Layout**: Sidebar (controls) + Main View (tree) + Debug Panel (logs)
- **Visual Hierarchy**: L1 (🟣 purple), L2 (🔵 blue), L3 (🟢 green)
- **Inline Editing**: Double-click any node to edit
- **Collapse/Expand**: Click [+]/[-] to show/hide branches

### MECE Validation

- Click **"Validate MECE"** in sidebar
- See live status: ✅ MECE Valid or ❌ MECE Invalid
- Get detailed feedback on overlaps and gaps

### Version Control

- Every save creates a new version (v1, v2, v3...)
- View version history in sidebar
- Click any version to load it

### Debug Logging

- All actions logged in bottom panel
- Timestamp for each event
- Collapsible with independent scrolling

---

## 📁 Project Structure

```
strategic-evaluation-tree/
├── strategic_consultant_agent/   # Python backend
│   ├── api/main.py               # FastAPI server
│   ├── tools/                    # Core tools
│   └── sub_agents/               # Multi-agent system
├── hypothesis-tree-ui/           # Next.js frontend
│   ├── app/                      # Pages
│   ├── components/               # React components
│   └── lib/                      # API client + types
├── storage/projects/             # Saved projects (versioned JSON)
├── tests/                        # Test suite (342 tests)
└── docs/                         # Documentation
```

---

## 🧪 Testing

### Run Python Tests

```bash
pytest --cov=strategic_consultant_agent tests/
```

**Expected**: 342 tests passing, >90% coverage

### Test Backend API

```bash
# List frameworks
curl http://localhost:8000/api/frameworks

# Generate tree
curl -X POST http://localhost:8000/api/tree/generate \
  -H "Content-Type: application/json" \
  -d '{"problem": "Test?", "framework": "scale_decision"}'
```

### Test Frontend

1. Create a new project
2. Edit nodes (double-click)
3. Add/delete nodes
4. Validate MECE
5. Save and load versions

---

## 📖 Documentation

- **VISUALIZATION.md**: Complete architecture and API reference
- **hypothesis-tree-ui/README.md**: Frontend setup and development
- **TASKS.md**: Implementation progress and status
- **CLAUDE.md**: Project instructions and patterns

---

## 🎓 Framework Templates

6 pre-built frameworks available:

1. **Scale Decision**: For expanding existing pilots
2. **Product Launch**: For new product evaluations
3. **Market Entry**: For new market opportunities
4. **Investment Decision**: For capital allocation
5. **Operations Improvement**: For process optimization
6. **Custom**: Build your own structure

---

## 🔧 Common Operations

### Edit a Node

1. Double-click the node label
2. Type new text
3. Press Enter to save (or Esc to cancel)

### Add a Node

1. Click **[+ Add L2 Branch]** or **[+ Add L3 Leaf]**
2. Edit the default "New L2/L3" label
3. Fill in the question

### Delete a Node

1. Click 🗑️ on the node
2. Click again to confirm
3. Node and all children are deleted

### Save Your Work

1. Make edits (see `*` indicator in sidebar)
2. Click **"Save"** button
3. New version created (v1 → v2 → v3...)

### Validate MECE

1. Click **"Validate MECE"** in sidebar
2. Check status: ✅ Valid or ❌ Invalid
3. Review suggestions if invalid
4. Make edits and validate again

### Export to JSON

1. Click **"Export JSON"** in sidebar
2. File downloads automatically
3. Can be imported later or used elsewhere

---

## ⚠️ Troubleshooting

### Frontend can't reach backend

- Check FastAPI is running on port 8000
- Verify `.env.local` has `NEXT_PUBLIC_API_URL=http://localhost:8000`
- Check browser console for CORS errors

### Changes not saving

- Check backend terminal for errors
- Verify `storage/projects/` directory exists
- Check debug panel for error messages

### Tree not rendering

- Check browser console for errors
- Verify project was created successfully
- Try refreshing the page

---

## 🎉 Next Steps

1. **Create your first project** with a real business problem
2. **Explore all 6 frameworks** to see different structures
3. **Test MECE validation** by creating overlaps/gaps
4. **Try version control** by saving multiple versions
5. **Export your analysis** to JSON for documentation

---

## 📝 Example Workflow

### Scenario: Fall Detection Scaling Decision

1. **Create Project**
   - Problem: "Should we scale deployment of fall detection in senior living?"
   - Framework: Scale Decision

2. **Review Generated Tree**
   - L1: Desirability, Feasibility, Viability
   - L2: Clinical Impact, Financial Impact, etc.
   - L3: Specific metrics with targets

3. **Customize for Your Needs**
   - Edit L3 leaves to match your metrics
   - Add new L2 branches if needed
   - Delete irrelevant sections

4. **Validate Structure**
   - Click "Validate MECE"
   - Fix any overlaps or gaps
   - Re-validate until ✅

5. **Save and Export**
   - Save version 1
   - Make iterative edits
   - Save version 2, 3, etc.
   - Export final JSON

6. **Present to Stakeholders**
   - Use tree as discussion framework
   - Track progress on L3 metrics
   - Version control for iterations

---

## 🏆 Project Stats

- **Total Tests**: 342 passing
- **Code Quality**: Pylint 9.7/10 average
- **Coverage**: >90% across all modules
- **Components**: 8 React components
- **API Endpoints**: 10+ REST endpoints
- **Framework Templates**: 6 pre-built
- **Lines of Code**: ~18,000

---

## 💡 Pro Tips

- **Double-click** is faster than clicking the ✏️ icon
- **Debug panel** shows what happened when something goes wrong
- **Version history** lets you experiment freely
- **MECE validation** is manual - make all edits first, then validate
- **Save often** - each save is a checkpoint you can return to

---

**Ready to build strategic frameworks? Start at http://localhost:3000!** 🚀
