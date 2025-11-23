---
description: Auto-execute entire phases or PRP ranges sequentially
---

# Execute Phase (Batch PRP Execution)

**Purpose**: Automatically generate and execute multiple PRPs sequentially with full validation.

**Usage**:
```bash
/execute-phase phase-1                  # Execute all PRPs in Phase 1
/execute-phase PRP-001 to PRP-005      # Execute specific range
/execute-phase phase-2 --continue      # Continue from last failure
```

---

## What This Command Does

1. **Identifies PRPs**: Reads TASKS.md to find all PRPs in the phase/range
2. **Generates PRPs**: Auto-generates any missing PRP files from TASKS.md definitions
3. **Sequential Execution**: For each PRP in order:
   - Execute PRP (using `/execute-prp` workflow)
   - Run all validation checkpoints
   - Pass all 5 quality gates
   - Update TASKS.md
   - Commit code
   - Move to next PRP
4. **Error Handling**: Stops on failure, saves progress, provides clear next steps
5. **Resume Capability**: Can resume from where it stopped

---

## Instructions for Claude Code

### Phase 1: Planning

#### Step 1: Parse Command
Determine what to execute:
- If `phase-X`: Look in TASKS.md for all PRPs in Phase X
- If `PRP-XXX to PRP-YYY`: Execute that specific range
- If `--continue` flag: Resume from last failure

#### Step 2: Read TASKS.md
Extract for each PRP in range:
- PRP number and title
- Feature description
- Acceptance criteria
- Dependencies
- Status (completed, in-progress, not-started)

#### Step 3: Validate Dependencies
For each PRP in execution order:
- Check if dependencies are marked complete in TASKS.md
- If dependency not met, warn user
- Ask if they want to:
  1. Skip PRPs with unmet dependencies
  2. Execute anyway (may cause issues)
  3. Cancel and complete dependencies first

#### Step 4: Create Master Todo List
Use TodoWrite to create high-level todos:
```
→ In Progress: Generate all PRPs for phase-X
  Pending: Execute PRP-001 - [title]
  Pending: Execute PRP-002 - [title]
  Pending: Execute PRP-003 - [title]
  ...
  Pending: Phase complete - summary
```

---

### Phase 2: PRP Generation

#### Step 5: Generate Missing PRPs
For each PRP that doesn't have a file in PRPs/ directory:
- Use `/generate-prp PRP-XXX` workflow
- Generate complete implementation guide from TASKS.md
- Save to appropriate directory
- Verify file was created successfully

#### Step 6: Confirm Generation
Show user:
```
## PRPs Generated

Phase X contains [N] PRPs:
✓ PRP-001 - [title] (PRPs/backend/prp-001-name.md)
✓ PRP-002 - [title] (PRPs/frontend/prp-002-name.md)
...

Ready to execute [N] PRPs sequentially.
Estimated time: [N × 30-60] minutes

Continue? (yes/no)
```

---

### Phase 3: Sequential Execution

For each PRP in the phase:

#### Step 7: Mark PRP Todo as In Progress
Update TodoWrite to show current PRP in_progress.

#### Step 8: Execute PRP
Use the full `/execute-prp` workflow:
1. Read PRP file
2. Create detailed todo list for PRP steps
3. Implement each step
4. Write tests
5. Run sub-agent validation at checkpoints
6. Pass all 5 quality gates
7. Update documentation
8. Update TASKS.md
9. Commit code

**See execute-prp.md for complete workflow**

#### Step 9: Verify Success
After PRP execution:
- [ ] All todos marked complete
- [ ] All tests passing
- [ ] All quality gates passed
- [ ] TASKS.md updated
- [ ] Code committed
- [ ] No blockers documented

#### Step 10: Mark PRP Todo Complete
Update TodoWrite to mark PRP complete, move to next PRP.

#### Step 11: Continue to Next PRP
Repeat steps 7-10 for each remaining PRP in the phase.

---

### Phase 4: Error Handling

If **any** PRP fails (tests fail, quality gate fails, validation fails):

#### Step 12: Stop Execution
- Do NOT continue to next PRP
- Mark current PRP as "blocked" or "in-progress"
- Keep remaining PRPs as "pending"

#### Step 13: Document Failure
Update TASKS.md:
```markdown
## CURRENT STATUS (Session [N] - 2025-11-09)

### In Progress
- **PRP-XXX**: [Title]
  - Status: BLOCKED
  - Issue: [Specific failure - test failure, quality gate X failed, etc.]
  - Next step: [What needs to be fixed]

### Pending (Phase X)
- PRP-YYY: [Next PRP]
- PRP-ZZZ: [Following PRP]
...

### Blockers
1. **PRP-XXX**: [Detailed description of blocker]
   - Error: [Exact error message]
   - Failed at: [Which step/gate]
   - To resolve: [Suggested fix]
```

#### Step 14: Commit Progress
If any PRPs completed before failure:
```bash
git add .
git commit -m "$(cat <<'EOF'
chore: phase-X partial completion (PRP-001 to PRP-XXX)

Completed:
- PRP-001: [title] ✓
- PRP-002: [title] ✓
...

Blocked at:
- PRP-XXX: [title]
- Issue: [failure reason]

Remaining:
- [N] PRPs pending in phase-X

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

#### Step 15: Inform User
```
## Phase Execution Stopped

**Completed**: [N] PRPs
- PRP-001: [title] ✓
- PRP-002: [title] ✓

**Blocked at**: PRP-XXX - [title]
**Issue**: [Specific failure]
**Next Step**: [What needs to be fixed]

**Remaining**: [M] PRPs in phase-X

To resume after fixing:
/execute-phase phase-X --continue

Would you like me to:
1. Attempt to fix the blocker now
2. Review what failed
3. Skip this PRP and continue (not recommended)
```

---

### Phase 5: Completion

If all PRPs in phase execute successfully:

#### Step 16: Mark All Todos Complete
Use TodoWrite to mark phase complete.

#### Step 17: Update TASKS.md
```markdown
## CURRENT STATUS (Session [N] - 2025-11-09)

### Recently Completed
- **Phase X Complete**: [Phase name]
  - PRP-001: [title] ✓
  - PRP-002: [title] ✓
  - ...
  - All [N] PRPs completed successfully
  - All quality gates passed
  - [XX]% test coverage achieved

### Next Steps
- Begin Phase [X+1]: [Next phase name]
- Starting with PRP-YYY: [Next PRP title]
```

#### Step 18: Summary Report
Show user:
```
## Phase X Complete ✓

**PRPs Executed**: [N]
**Files Modified**: [Total files]
**Tests Added**: [Total tests]
**Coverage**: [Overall percentage]%
**Commits**: [N] commits
**Time**: [Approximate duration]

**Quality Metrics**:
✓ All [N] PRPs passed code quality gates
✓ All [N] PRPs passed testing gates (>80% coverage)
✓ All [N] PRPs passed security gates
✓ All [N] PRPs passed project-specific gates
✓ All [N] PRPs passed performance gates

**Next Phase**: Phase [X+1] - [Name]
- Contains [M] PRPs
- Estimated time: [M × 30-60] minutes

Would you like me to:
1. Start Phase [X+1] now
2. Review Phase X implementation
3. Take a break (use /clear to save context)
```

---

## Resume Capability

### Using --continue Flag

If execution was stopped (failure or user interrupt):

```bash
/execute-phase phase-X --continue
```

#### Step 19: Read TASKS.md Status
Identify:
- Which PRPs are marked complete
- Which PRP was in-progress or blocked
- Which PRPs are pending

#### Step 20: Resume from Failure Point
- Skip PRPs marked complete (already committed)
- Start from first in-progress or pending PRP
- Continue sequential execution

---

## Best Practices

### Before Starting Phase Execution

1. **Review TASKS.md**: Ensure all dependencies from previous phases are complete
2. **Check environment**: Ensure dev environment is running (databases, services)
3. **Clean state**: Commit or stash any uncommitted changes
4. **Estimate time**: Phase 1 typically 3-6 hours for 6 PRPs

### During Phase Execution

1. **Don't interrupt**: Let it run to completion or failure
2. **Monitor progress**: Watch TodoWrite updates to see current status
3. **Note blockers**: If stopped, read TASKS.md for detailed blocker info

### After Phase Completion

1. **Review code**: Scan through implemented features
2. **Run full test suite**: `npm test` or `pytest` to verify everything
3. **Manual testing**: Test critical user flows manually
4. **Update TASKS.md**: Add any discovered issues or enhancements

---

## Performance Optimization

### Parallel Execution (Advanced)
**Not implemented by default** - PRPs execute sequentially for safety.

If PRPs are truly independent (no shared files, no dependencies):
- User can manually execute multiple PRPs in parallel
- Use separate terminal sessions
- Merge conflicts must be resolved manually

**Recommendation**: Keep sequential execution for reliability.

---

## Critical Rules

1. **NEVER skip a failed PRP** - Fix or document blocker
2. **NEVER continue if quality gates fail** - All 5 must pass
3. **ALWAYS commit after each PRP** - Preserve incremental progress
4. **ALWAYS update TASKS.md** - Single source of truth
5. **ALWAYS stop on first failure** - Don't cascade errors
6. **ONE PRP in_progress at a time** - Sequential execution only

---

## Notes

- Phase execution is the fastest way to implement features
- Requires well-defined PRPs in TASKS.md
- Best for phases with independent PRPs
- Can take several hours for large phases (plan accordingly)
- Use `/clear` between sessions if needed (progress saved in TASKS.md)
- Use `/recover-context` to resume in next session
