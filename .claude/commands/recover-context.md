---
description: Quickly recover project context after /clear or session loss
---

# Context Recovery Protocol

**Purpose**: Restore full project context in ~30 seconds after `/clear` or starting a new session.

**Usage**: `/recover-context`

---

## What This Command Does

1. **Loads Core Instructions**: Reads CLAUDE.md for project rules and architecture
2. **Loads Current Progress**: Reads TASKS.md for current status and next steps
3. **Shows Recent Activity**: Displays recent git commits (if git repo)
4. **Identifies Next Actions**: Highlights current PRP and pending tasks
5. **Displays Blockers**: Shows any documented blockers requiring attention

---

## Instructions for Claude Code

Execute the following steps:

### Step 1: Load CLAUDE.md
Read `/Users/johnney-fivemiller/PythonLearning/hackathons/11-2025-project/strategic-evaluation-tree/CLAUDE.md` to understand:
- Project architecture and tech stack
- Quality gates and validation requirements
- Project-specific rules
- Development workflow

### Step 2: Load TASKS.md
Read `/Users/johnney-fivemiller/PythonLearning/hackathons/11-2025-project/strategic-evaluation-tree/TASKS.md` to understand:
- Current session number and date
- Recently completed work
- Current status (what's in progress)
- Next PRPs to execute
- Known blockers or issues

### Step 3: Check Git Status (if applicable)
```bash
# Only if .git directory exists
git log --oneline -10
git status
```

### Step 4: Summarize Context
Present to the user:
```
## Context Recovered

**Current Session**: [Session number and date from TASKS.md]

**Recent Progress**:
- [Last 2-3 completed items from TASKS.md]

**Current Status**:
- [What's currently in progress from TASKS.md]

**Next Actions**:
- [Next PRP or phase to work on]

**Blockers** (if any):
- [Any blockers listed in TASKS.md]

**Ready to proceed with**: [Suggested next step]
```

### Step 5: Ask for Confirmation
Ask the user:
```
Would you like me to:
1. Continue with [next PRP/phase]
2. Address blockers first
3. Work on something else
```

---

## Expected Output

**Token Usage**: ~800-1000 tokens
**Time Required**: ~30 seconds
**Result**: Full context restored, ready to continue work

---

## Notes

- This command is designed for context efficiency
- It relies on TASKS.md being kept up-to-date
- Before using `/clear`, always update TASKS.md CURRENT STATUS section
- If TASKS.md is missing or outdated, recovery will be incomplete
