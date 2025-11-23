---
description: Execute a single PRP step-by-step with comprehensive validation
---

# Execute Product Requirement Prompt (PRP)

**Purpose**: Execute a PRP implementation guide with full validation and quality gates.

**Usage**:
```bash
/execute-prp PRPs/backend/prp-001-feature-name.md
/execute-prp PRPs/frontend/prp-005-ui-component.md
```

---

## What This Command Does

1. **Reads PRP**: Loads the implementation guide
2. **Creates Todo List**: Breaks down steps into trackable tasks
3. **Implements Each Step**: Follows instructions with validation
4. **Runs Tests**: Executes test suite after each significant change
5. **Validates Quality**: Runs all quality gates before completion
6. **Updates Progress**: Updates TASKS.md with completion status
7. **Commits Code**: Creates git commit with PRP reference

---

## Instructions for Claude Code

### Phase 1: Setup and Planning

#### Step 1: Read the PRP
Read the specified PRP file completely to understand:
- Objective and success criteria
- All implementation steps
- Validation requirements
- Quality gates
- Testing requirements

#### Step 2: Create Todo List
Use TodoWrite to create tasks for:
- Each implementation step from the PRP
- Each validation checkpoint
- Each quality gate
- Documentation updates
- Final completion checklist

**Example Todo Structure**:
```
→ In Progress: Implement [first feature]
  Pending: Write tests for [first feature]
  Pending: Run sub-agent validation checkpoint 1
  Pending: Implement [second feature]
  Pending: Write tests for [second feature]
  Pending: Run sub-agent validation checkpoint 2
  Pending: Pass all quality gates
  Pending: Update TASKS.md
  Pending: Commit code
```

#### Step 3: Check Dependencies
Verify that any dependent PRPs have been completed:
- Check TASKS.md for dependency status
- If dependencies not met, warn user and ask if they want to continue

---

### Phase 2: Implementation

For each implementation step in the PRP:

#### Step 4: Implement Feature
- Follow the PRP instructions exactly
- Create or modify files as specified
- Add code following project patterns (see CLAUDE.md)
- Include error handling
- Add logging where appropriate

#### Step 5: Write Tests
After each significant feature:
- Write unit tests for new functions/components
- Write integration tests for workflows
- Aim for >80% code coverage
- Follow testing patterns from CLAUDE.md

#### Step 6: Run Tests
```bash
# Run project-specific test commands from CLAUDE.md
npm test -- --coverage
# or
pytest --cov=src tests/
```
- All tests must pass before continuing
- If tests fail, fix issues before moving to next step

#### Step 7: Sub-Agent Validation (MANDATORY)
At validation checkpoints (see SHARED-PATTERNS.md):
- Use Task tool with a validation sub-agent
- Ask sub-agent to review:
  - Code quality and patterns
  - Security vulnerabilities
  - Performance issues
  - Test coverage
  - Documentation completeness
- Address any issues found before continuing

**When to Validate**:
1. After service/component implementation
2. After database/state changes
3. After security-related code
4. After external API integration
5. After performance-critical code
6. Before commit (MANDATORY)

---

### Phase 3: Quality Gates

#### Step 8: Quality Gate 1 - Code Quality
```bash
# Run linting and type checking
npm run lint
npm run type-check
# or
python -m pylint src/
mypy src/
```
**Must Pass**: Zero linting errors, zero type errors

#### Step 9: Quality Gate 2 - Testing
```bash
# Run full test suite with coverage
npm test -- --coverage
# or
pytest --cov=src tests/ --cov-report=term-missing
```
**Must Pass**: >80% coverage, all tests passing

#### Step 10: Quality Gate 3 - Security
Check for:
- [ ] Input validation on all user inputs
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (sanitized outputs)
- [ ] API keys/secrets not committed (check .env.example vs .env)
- [ ] Authentication/authorization working correctly
- [ ] HTTPS used for external API calls
- [ ] Sensitive data encrypted at rest (if applicable)

#### Step 11: Quality Gate 4 - [Project-Specific]
Execute project-specific validation from CLAUDE.md:
- Data accuracy checks
- API response time validation
- Accessibility checks
- Integration tests
- etc.

#### Step 12: Quality Gate 5 - Performance
Check:
- [ ] API endpoints respond in <500ms (or project-specific target)
- [ ] Database queries optimized (no N+1 problems)
- [ ] Proper indexing on database tables
- [ ] No memory leaks detected
- [ ] Frontend performance acceptable (Lighthouse >90 if applicable)

---

### Phase 4: Documentation and Completion

#### Step 13: Update Documentation
- Update README.md if user-facing changes
- Update API documentation if endpoints changed
- Add inline code comments for complex logic
- Update CLAUDE.md if new patterns discovered

#### Step 14: Final Validation (Sub-Agent)
**MANDATORY before commit**:
- Use Task tool with validation sub-agent
- Ask sub-agent to review entire PRP implementation
- Verify all quality gates passed
- Check completion checklist from PRP

#### Step 15: Update TASKS.md
Mark PRP as completed in TASKS.md:
```markdown
## CURRENT STATUS (Session [N] - 2025-11-09)

### Recently Completed
- **PRP-XXX**: [Feature name] - [Brief description]
  - [Key accomplishment 1]
  - [Key accomplishment 2]
  - All quality gates passed ✓

### Next Steps
- PRP-YYY: [Next feature]
```

#### Step 16: Commit Code
Create git commit (if git repo exists):
```bash
git add .
git commit -m "$(cat <<'EOF'
feat: [PRP-XXX] [Brief description]

Implemented:
- [Feature 1]
- [Feature 2]
- [Feature 3]

Quality Gates:
✓ Code Quality (linting, type checking)
✓ Testing (>80% coverage, all passing)
✓ Security (input validation, no vulnerabilities)
✓ [Project-specific gate]
✓ Performance ([specific metrics])

PRP: PRPs/[domain]/prp-XXX-feature-name.md

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

### Phase 5: Completion

#### Step 17: Mark All Todos Complete
Use TodoWrite to mark all PRP-related todos as completed.

#### Step 18: Summarize Results
Show user:
```
## PRP-XXX Completed ✓

**Feature**: [Feature name]
**Files Modified**: [Number] files
**Tests Added**: [Number] tests
**Coverage**: [Percentage]%

**Quality Gates**:
✓ Code Quality
✓ Testing
✓ Security
✓ [Project-specific]
✓ Performance

**Next PRP**: [Next PRP number and title]

Would you like me to:
1. Continue with next PRP
2. Review the implementation
3. Take a different action
```

---

## Error Handling

### If Tests Fail
1. Mark current todo as still in_progress
2. Analyze test failures
3. Fix issues
4. Re-run tests
5. Do NOT proceed until all tests pass

### If Quality Gate Fails
1. Mark current todo as still in_progress
2. Identify specific failures
3. Fix issues
4. Re-run quality gate
5. Do NOT proceed until gate passes

### If Sub-Agent Identifies Issues
1. Mark current todo as still in_progress
2. Address each issue raised
3. Re-run sub-agent validation
4. Do NOT proceed until validation passes

### If Dependencies Not Met
1. Warn user that dependencies are not complete
2. Suggest completing dependencies first
3. Ask if user wants to continue anyway
4. If yes, note in commit message that dependencies were assumed

---

## Critical Rules

1. **NEVER skip validation checkpoints** - They catch issues early
2. **NEVER mark PRP complete if ANY quality gate fails** - All 5 must pass
3. **ALWAYS use TodoWrite** - Keep user informed of progress
4. **ALWAYS update TASKS.md** - Single source of truth
5. **ALWAYS commit after successful completion** - Preserve progress
6. **ONE todo in_progress at a time** - Clear tracking

---

## Notes

- Estimated time per PRP: 15-60 minutes depending on complexity
- If PRP takes >60 minutes, consider breaking it into smaller PRPs
- Save progress frequently by completing individual todos
- If session needs to end mid-PRP, update TASKS.md with current status
- Use `/recover-context` to resume in next session
