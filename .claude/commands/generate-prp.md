---
description: Generate a PRP from TASKS.md or planning documents
---

# Generate Product Requirement Prompt (PRP)

**Purpose**: Auto-generate implementation guides (PRPs) from high-level requirements.

**Usage**:
```bash
/generate-prp PRP-001              # Generate specific PRP by number
/generate-prp phase-1              # Generate all PRPs for a phase
/generate-prp docs/feature-spec.md # Generate from planning document
```

---

## What This Command Does

1. **Reads Source Document**: TASKS.md or specified planning document
2. **Analyzes Requirements**: Understands feature goals and acceptance criteria
3. **Breaks Down Implementation**: Creates step-by-step implementation guide
4. **Adds Validation Gates**: Inserts quality gates and validation checkpoints
5. **Generates PRP File**: Saves to appropriate directory in PRPs/

---

## Instructions for Claude Code

### Step 1: Identify Source
Determine what to generate from:
- If `PRP-XXX` format: Look in TASKS.md for that PRP definition
- If `phase-X` format: Look in TASKS.md for all PRPs in that phase
- If file path: Read that planning document

### Step 2: Read Source Document
Read the source to extract:
- Feature description and goals
- Acceptance criteria
- Technical requirements
- Dependencies on other PRPs
- Success metrics

### Step 3: Analyze Requirements
Determine:
- What files need to be created or modified
- What technologies/libraries are involved
- What tests need to be written
- What validation is required
- Estimated complexity

### Step 4: Generate PRP Using Template
Use the template from `PRPs/PRP-TEMPLATE.md` and fill in:

**Header Section**:
- PRP number and title
- Domain (backend, frontend, fullstack, infrastructure, etc.)
- Phase and dependencies
- Status (should be "NOT STARTED")

**Objective**:
- Clear, measurable goal
- Success criteria
- Why this is important

**Critical Requirements**:
- Project-specific requirements (from CLAUDE.md)
- Performance targets
- Security considerations

**Implementation Steps**:
For each step:
- Clear instructions
- Specific file paths
- Code examples where helpful
- Expected outcomes

**Validation Checkpoints**:
- When to run sub-agent validation
- What to validate
- How to verify success

**Quality Gates**:
All 5 gates from CLAUDE.md:
1. Code Quality (linting, type checking)
2. Testing (>80% coverage)
3. Security (input validation, auth, etc.)
4. [Project-specific gate]
5. Performance (response times, resource usage)

**Testing Strategy**:
- Unit tests to write
- Integration tests to write
- How to run tests
- Expected coverage

**Documentation**:
- What files to update
- API documentation needs
- README updates

**Completion Checklist**:
- Final verification steps
- Confirmation that all gates passed
- TASKS.md update instructions

### Step 5: Save PRP File
Save to appropriate directory:
- Backend PRPs → `PRPs/backend/prp-XXX-feature-name.md`
- Frontend PRPs → `PRPs/frontend/prp-XXX-feature-name.md`
- Fullstack PRPs → `PRPs/fullstack/prp-XXX-feature-name.md`
- Infrastructure PRPs → `PRPs/infrastructure/prp-XXX-feature-name.md`

### Step 6: Confirm with User
Show the user:
```
## PRP Generated

**File**: PRPs/[domain]/prp-XXX-feature-name.md
**Title**: [PRP title]
**Estimated Steps**: [number of implementation steps]
**Dependencies**: [list any dependencies]

**Next Steps**:
1. Review the generated PRP
2. Modify if needed
3. Execute with: /execute-prp PRPs/[domain]/prp-XXX-feature-name.md

Would you like me to:
1. Execute this PRP now
2. Generate another PRP
3. Review and modify this PRP first
```

---

## Example Usage

### Example 1: Generate Single PRP
```bash
/generate-prp PRP-001
```
Reads TASKS.md, finds PRP-001 definition, generates implementation guide.

### Example 2: Generate Entire Phase
```bash
/generate-prp phase-1
```
Reads TASKS.md, finds all Phase 1 PRPs, generates all implementation guides.

### Example 3: Generate from Planning Doc
```bash
/generate-prp docs/planning/authentication-feature.md
```
Reads planning document, generates PRP with implementation steps.

---

## Quality Checks

Before saving the PRP, ensure it includes:
- [ ] Clear objective with success criteria
- [ ] Step-by-step implementation instructions
- [ ] Specific file paths and code examples
- [ ] All 6 validation checkpoints (from SHARED-PATTERNS.md)
- [ ] All 5 quality gates (from CLAUDE.md)
- [ ] Testing strategy with coverage targets
- [ ] Completion checklist

---

## Notes

- Generated PRPs are starting points - review and customize as needed
- PRPs should be self-contained and executable by another developer
- Include enough detail that someone unfamiliar with the project can execute it
- Reference CLAUDE.md for project-specific rules to include
- Reference SHARED-PATTERNS.md for validation patterns to include
