# PRP-XXX: [Feature/Component Name]

**Domain**: [Backend / Frontend / Fullstack / Infrastructure / Data / DevOps]
**Phase**: [Phase number or name]
**Dependencies**: [List any PRPs that must be completed first, or "None"]
**Status**: NOT STARTED
**Estimated Complexity**: [Low / Medium / High]

---

## OBJECTIVE

[1-2 sentences describing what this PRP accomplishes and why it's important]

### Success Criteria
- [ ] [Specific, measurable outcome 1]
- [ ] [Specific, measurable outcome 2]
- [ ] [Specific, measurable outcome 3]
- [ ] All 5 quality gates passed
- [ ] TASKS.md updated with completion status

---

## CRITICAL REQUIREMENTS

[Reference any critical requirements from CLAUDE.md that apply to this PRP]

### [Requirement Category 1 - e.g., Data Accuracy]
[Specific requirements for this category]
- Requirement 1
- Requirement 2

### [Requirement Category 2 - e.g., Security]
[Specific security requirements]
- Requirement 1
- Requirement 2

### [Requirement Category 3 - e.g., Performance]
[Specific performance requirements]
- Target: [e.g., API response <500ms]
- Optimization: [e.g., Database queries use indexes]

---

## IMPLEMENTATION STEPS

### Step 1: [First Major Step]

**Goal**: [What this step accomplishes]

**Files to Create/Modify**:
- `path/to/file1.ext` - [What changes to make]
- `path/to/file2.ext` - [What changes to make]

**Instructions**:
1. [Detailed instruction 1]
2. [Detailed instruction 2]
3. [Detailed instruction 3]

**Code Example** (if helpful):
```language
// Example code showing the pattern to follow
function exampleFunction() {
  // Implementation
}
```

**Expected Outcome**: [What should be true after this step]

**Validation**: [How to verify this step worked]
```bash
# Commands to verify
npm run test:step1
```

---

### Step 2: [Second Major Step]

**Goal**: [What this step accomplishes]

**Files to Create/Modify**:
- `path/to/file3.ext` - [What changes to make]

**Instructions**:
1. [Detailed instruction 1]
2. [Detailed instruction 2]

**Code Example** (if helpful):
```language
// Example code
```

**Expected Outcome**: [What should be true after this step]

**Validation**: [How to verify this step worked]

---

### Step 3: [Third Major Step]

[Continue pattern for remaining steps...]

---

### Step N: Write Tests

**Goal**: Achieve >80% test coverage for implemented features

**Files to Create**:
- `tests/path/to/test-file.test.ext` - [What to test]

**Instructions**:
1. Write unit tests for all functions/components
   - Test happy path (expected inputs)
   - Test edge cases (empty, null, boundary values)
   - Test error conditions (invalid inputs, failures)
2. Write integration tests for workflows
   - Test end-to-end user flows
   - Test API endpoints with real requests
   - Test database operations
3. Ensure all tests pass
4. Check coverage meets >80% target

**Test Examples**:
```language
// Unit test example
describe('functionName', () => {
  it('should handle expected input', () => {
    // Arrange
    const input = 'test'

    // Act
    const result = functionName(input)

    // Assert
    expect(result).toBe('expected')
  })

  it('should handle edge case', () => {
    expect(functionName('')).toBe('default')
  })

  it('should throw on invalid input', () => {
    expect(() => functionName(null)).toThrow()
  })
})
```

**Expected Outcome**: All tests passing, >80% coverage

**Validation**:
```bash
npm test -- --coverage
# or
pytest --cov=src tests/
```

---

## SUB-AGENT VALIDATION CHECKPOINTS

[Reference: See `.claude/SHARED-PATTERNS.md` for detailed validation patterns]

### Checkpoint 1: After [Step X] - [Validation Type]

**When**: After completing Step X ([specific step name])

**Use Task Tool**: Create validation sub-agent

**What to Validate**:
- [ ] [Specific validation point 1]
- [ ] [Specific validation point 2]
- [ ] [Specific validation point 3]

**Validation Prompt for Sub-Agent**:
```
Review the following files for [validation focus]:
- path/to/file1
- path/to/file2

Check for:
1. [Specific check 1]
2. [Specific check 2]
3. [Specific check 3]

Verify against project rules in CLAUDE.md.
```

**Expected Outcome**: Sub-agent confirms quality or provides specific fixes needed.

**Do NOT Proceed Until**: All validation issues are resolved.

---

### Checkpoint 2: After [Step Y] - [Validation Type]

[Repeat pattern for each major validation point]

**Common Validation Checkpoints** (see SHARED-PATTERNS.md):
1. After service/component implementation → Code quality validation
2. After database changes → Schema design validation
3. After security code → Security vulnerability validation
4. After API integration → Resilience and error handling validation
5. After performance-critical code → Performance optimization validation
6. Before commit → Comprehensive final validation (MANDATORY)

---

## QUALITY GATES (ALL MUST PASS)

### Gate 1: Code Quality ✓

**Run**:
```bash
# Linting
npm run lint
# or
python -m pylint src/

# Type checking
npm run type-check
# or
mypy src/
```

**Pass Criteria**:
- Zero linting errors
- Zero type errors
- Code follows project patterns (CLAUDE.md)

**If Fails**: Fix all errors before proceeding.

---

### Gate 2: Testing ✓

**Run**:
```bash
npm test -- --coverage
# or
pytest --cov=src tests/ --cov-report=term-missing
```

**Pass Criteria**:
- All tests passing (100% pass rate)
- Coverage >80% (or project-specific target)
- All edge cases tested
- All error conditions tested

**If Fails**: Write missing tests or fix failing tests.

---

### Gate 3: Security ✓

**Manual Checklist**:
- [ ] All user inputs validated (whitelist approach)
- [ ] SQL injection prevented (parameterized queries/ORM)
- [ ] XSS prevented (sanitized outputs, auto-escaping templates)
- [ ] CSRF protection (if state-changing operations)
- [ ] Authentication working correctly
- [ ] Authorization enforced (role/permission checks)
- [ ] No secrets committed (check .env vs .env.example)
- [ ] HTTPS used for external APIs
- [ ] Rate limiting implemented (where appropriate)
- [ ] Sensitive data encrypted (passwords hashed, PII encrypted)

**Security Scan** (if available):
```bash
npm audit
# or
safety check
```

**Pass Criteria**: All security checks passed, no vulnerabilities.

**If Fails**: Fix security issues immediately (highest priority).

---

### Gate 4: [Project-Specific Gate] ✓

[Define a quality gate specific to this PRP or project]

**Examples**:
- **Data Accuracy**: Financial data matches source exactly (100% accuracy)
- **API Performance**: Response time <500ms for all endpoints
- **Accessibility**: WCAG 2.1 AA compliance verified
- **Integration**: Third-party services working correctly
- **User Experience**: UI matches design system, responsive on all breakpoints

**Run**:
```bash
[Commands to verify this gate]
```

**Pass Criteria**:
- [Specific criteria for this gate]

**If Fails**: [How to address failures]

---

### Gate 5: Performance ✓

**Checks**:
- [ ] API endpoints respond in <500ms (or project-specific target)
- [ ] Database queries optimized (EXPLAIN shows index usage)
- [ ] No N+1 query problems
- [ ] Proper indexing on queried columns
- [ ] Pagination implemented for large result sets
- [ ] Caching considered and implemented where appropriate
- [ ] Memory usage acceptable (no leaks)
- [ ] Frontend performance acceptable (Lighthouse >90 if applicable)

**Run**:
```bash
# Performance tests
npm run test:performance
# or
pytest tests/performance/

# Frontend (if applicable)
npm run lighthouse
```

**Pass Criteria**: All performance targets met.

**If Fails**: Optimize queries, add caching, implement pagination.

---

## DOCUMENTATION UPDATES

### Files to Update

**README.md** (if user-facing changes):
- [ ] Update installation instructions (if dependencies changed)
- [ ] Update usage examples (if API changed)
- [ ] Add new feature to features list

**API Documentation** (if API changes):
- [ ] Document new endpoints
- [ ] Update request/response examples
- [ ] Document error responses
- [ ] Update authentication requirements

**CLAUDE.md** (if new patterns discovered):
- [ ] Add new project-specific rules
- [ ] Document new common patterns
- [ ] Update architecture decisions

**Code Comments** (inline):
- [ ] Add comments explaining "why" for complex logic
- [ ] Document function parameters and return values
- [ ] Add examples for non-obvious usage

---

## TESTING STRATEGY

### Unit Tests

**Location**: `tests/unit/[feature-name].test.ext`

**What to Test**:
- All business logic functions
- All utility functions
- All data transformations
- All validation logic

**Coverage Target**: >90% for business logic

**Example Test Cases**:
1. Happy path with expected inputs
2. Edge cases (empty, null, zero, max values)
3. Invalid inputs (wrong type, out of range)
4. Error conditions (exceptions, failures)

---

### Integration Tests

**Location**: `tests/integration/[workflow-name].test.ext`

**What to Test**:
- Complete user workflows
- API endpoint flows (request → processing → database → response)
- Service interactions
- Database operations with real database

**Coverage Target**: All critical user paths

**Example Test Cases**:
1. User registration flow
2. Authentication flow
3. Data creation and retrieval
4. Error handling (API failures, database errors)

---

### Performance Tests (if applicable)

**Location**: `tests/performance/[feature-name].perf.test.ext`

**What to Test**:
- API response times under load
- Database query performance with large datasets
- Memory usage over time
- Concurrent request handling

**Performance Targets**:
- [Specific targets from Gate 5]

---

## COMPLETION CHECKLIST

Before marking this PRP as complete:

### Implementation
- [ ] All implementation steps completed
- [ ] All files created/modified as specified
- [ ] Code follows project patterns (CLAUDE.md)
- [ ] No console.log / print statements left in code
- [ ] No commented-out code blocks
- [ ] No TODO comments without issue tracking

### Testing
- [ ] All tests written (unit + integration)
- [ ] All tests passing (100% pass rate)
- [ ] Coverage >80% (or project target)
- [ ] Edge cases tested
- [ ] Error conditions tested

### Validation
- [ ] All sub-agent validation checkpoints passed
- [ ] Code quality validated
- [ ] Security validated
- [ ] Performance validated
- [ ] Project-specific validations passed

### Quality Gates
- [ ] Gate 1: Code Quality ✓
- [ ] Gate 2: Testing ✓
- [ ] Gate 3: Security ✓
- [ ] Gate 4: [Project-Specific] ✓
- [ ] Gate 5: Performance ✓

### Documentation
- [ ] README.md updated (if applicable)
- [ ] API docs updated (if applicable)
- [ ] Code comments added
- [ ] CLAUDE.md updated (if new patterns)

### Progress Tracking
- [ ] TASKS.md updated with completion status
- [ ] All TodoWrite items marked complete
- [ ] Code committed with PRP reference
- [ ] No blockers documented

### Final Validation (MANDATORY)
- [ ] Sub-agent final review completed
- [ ] Sub-agent confirmed ready to commit
- [ ] All quality gates confirmed passing

---

## ROLLBACK PLAN

If issues are discovered after marking complete:

1. **Document Issue**: Add to TASKS.md blockers section
2. **Assess Impact**: Determine if issue blocks other PRPs
3. **Decide**: Fix immediately or create follow-up PRP
4. **If Immediate Fix**:
   - Mark PRP as in-progress again
   - Fix issue
   - Re-run all quality gates
   - Re-validate with sub-agent
   - Mark complete again
5. **If Follow-Up PRP**:
   - Create new PRP for fix
   - Document workaround (if any)
   - Prioritize in TASKS.md

---

## NOTES

[Any additional notes, gotchas, or context about this PRP]

**Common Issues**:
- [Issue 1 and how to resolve]
- [Issue 2 and how to resolve]

**Related Resources**:
- [Link to external docs]
- [Link to design specs]
- [Link to related PRPs]

**Estimated Time**: [X hours based on complexity]

---

**Generated**: [Date]
**Last Updated**: [Date]
**Status**: [NOT STARTED / IN PROGRESS / BLOCKED / COMPLETED]
