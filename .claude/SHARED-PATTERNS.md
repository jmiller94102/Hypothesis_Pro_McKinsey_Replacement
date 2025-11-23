# Shared Patterns and Best Practices

**Version**: 1.0
**Last Updated**: 2025-11-09
**Purpose**: Common validation patterns, efficiency techniques, and quality standards

---

## TABLE OF CONTENTS

1. [Mandatory Validation Checkpoints](#mandatory-validation-checkpoints)
2. [TodoWrite Usage Patterns](#todowrite-usage-patterns)
3. [Context Efficiency Techniques](#context-efficiency-techniques)
4. [Testing Patterns](#testing-patterns)
5. [Security Patterns](#security-patterns)
6. [Performance Patterns](#performance-patterns)
7. [Error Handling Patterns](#error-handling-patterns)
8. [Git Commit Patterns](#git-commit-patterns)

---

## MANDATORY VALIDATION CHECKPOINTS

**CRITICAL**: Use sub-agent validation at these 6 points. Never skip.

### Checkpoint 1: After Service/Component Implementation

**When**: After creating or significantly modifying a service, component, or module

**What to Validate**:
- [ ] Code follows project patterns (see CLAUDE.md)
- [ ] Type safety enforced (TypeScript types, Python type hints)
- [ ] Error handling comprehensive (try/catch, error boundaries)
- [ ] Edge cases handled (null, undefined, empty arrays, etc.)
- [ ] Logging added for debugging
- [ ] Code is DRY (no unnecessary duplication)
- [ ] Functions/methods have single responsibility
- [ ] Comments explain "why", not "what"

**How to Validate**:
```bash
# Use Task tool with validation sub-agent
Create sub-agent to review:
- Files: [list modified files]
- Focus: Code quality, patterns, type safety, error handling
- Check against: CLAUDE.md project rules
```

**Expected Outcome**: Sub-agent confirms code meets quality standards or provides specific fixes needed.

---

### Checkpoint 2: After Database/State Changes

**When**: After modifying schemas, migrations, state management, or data structures

**What to Validate**:
- [ ] Schema design normalized (no data duplication)
- [ ] Indexes created on frequently queried columns
- [ ] Foreign keys defined with proper cascade rules
- [ ] Required fields vs. optional fields correct
- [ ] Data types appropriate (INT vs BIGINT, VARCHAR length, etc.)
- [ ] Default values specified where needed
- [ ] Timestamps included (created_at, updated_at)
- [ ] Soft delete support (if required)
- [ ] Migration reversible (down migration works)

**How to Validate**:
```bash
# Use Task tool with validation sub-agent
Create sub-agent to review:
- Schema files: [list schema/migration files]
- Focus: Design, indexing, relationships, data integrity
- Check: Performance implications of queries
```

**Expected Outcome**: Sub-agent confirms schema is well-designed and performant.

---

### Checkpoint 3: After Security-Related Code

**When**: After implementing authentication, authorization, input validation, or data protection

**What to Validate**:
- [ ] Input validation on all user inputs (whitelist approach)
- [ ] SQL injection prevented (parameterized queries, ORM)
- [ ] XSS prevented (sanitized outputs, CSP headers)
- [ ] CSRF tokens implemented (for state-changing operations)
- [ ] Authentication working correctly (JWT, session, etc.)
- [ ] Authorization enforced (role/permission checks)
- [ ] Secrets not committed (API keys, passwords in .env only)
- [ ] HTTPS enforced for external APIs
- [ ] Rate limiting implemented (where appropriate)
- [ ] Sensitive data encrypted (passwords hashed, PII encrypted)

**How to Validate**:
```bash
# Use Task tool with validation sub-agent
Create sub-agent to review:
- Files: [list security-related files]
- Focus: OWASP Top 10 vulnerabilities
- Check: Input validation, output sanitization, auth/authz
- Verify: No secrets in code, proper encryption
```

**Expected Outcome**: Sub-agent confirms no security vulnerabilities found.

---

### Checkpoint 4: After External API Integration

**When**: After integrating with third-party APIs, webhooks, or external services

**What to Validate**:
- [ ] Error handling for API failures (network, timeout, 500 errors)
- [ ] Retry logic implemented (exponential backoff)
- [ ] Rate limiting respected (check API limits)
- [ ] Timeout configured (don't hang indefinitely)
- [ ] Response validation (check status codes, validate response schema)
- [ ] API keys secured (environment variables, never committed)
- [ ] Logging for debugging (request/response logged in dev)
- [ ] Graceful degradation (app works if API is down)
- [ ] Webhooks verified (signature validation if supported)

**How to Validate**:
```bash
# Use Task tool with validation sub-agent
Create sub-agent to review:
- Files: [list API integration files]
- Focus: Error handling, retry logic, rate limiting
- Check: Resilience to API failures, security of API keys
```

**Expected Outcome**: Sub-agent confirms API integration is robust and secure.

---

### Checkpoint 5: After Performance-Critical Code

**When**: After implementing database queries, API endpoints, data processing, or rendering logic

**What to Validate**:
- [ ] Database queries optimized (use EXPLAIN for SQL)
- [ ] No N+1 query problems (use eager loading, joins)
- [ ] Indexes exist on queried columns
- [ ] Pagination implemented (for large result sets)
- [ ] Caching considered (Redis, in-memory, CDN)
- [ ] API response time acceptable (<500ms target)
- [ ] Large files processed in chunks (streaming)
- [ ] Memory usage reasonable (no memory leaks)
- [ ] Frontend rendering optimized (lazy loading, code splitting)

**How to Validate**:
```bash
# Use Task tool with validation sub-agent
Create sub-agent to review:
- Files: [list performance-critical files]
- Focus: Query optimization, response times, resource usage
- Check: Database indexes, N+1 problems, caching opportunities

# Also run performance tests
npm run test:performance
# or
pytest tests/performance/
```

**Expected Outcome**: Sub-agent confirms performance meets targets, no obvious bottlenecks.

---

### Checkpoint 6: Before Every Commit (MANDATORY)

**When**: Before creating any git commit

**What to Validate**:
- [ ] All tests passing (unit + integration)
- [ ] Linting passed (zero errors)
- [ ] Type checking passed (zero errors)
- [ ] Security scan passed (no vulnerabilities)
- [ ] Code coverage >80% (or project target)
- [ ] Documentation updated (README, API docs, comments)
- [ ] TASKS.md updated with current status
- [ ] No console.log / print statements left in code
- [ ] No commented-out code blocks
- [ ] No TODO comments without issue tracking

**How to Validate**:
```bash
# Use Task tool with validation sub-agent
Create sub-agent to review entire PRP implementation:
- All modified files
- Focus: Completeness, quality, all gates passed
- Check: Tests, linting, security, documentation

# Also run quality gates manually
npm run lint
npm run type-check
npm test -- --coverage
```

**Expected Outcome**: Sub-agent confirms ready to commit, all quality gates passed.

---

## TODOWRITE USAGE PATTERNS

**Purpose**: Track progress, keep user informed, ensure nothing is forgotten.

### Pattern 1: Create Todos at Start of PRP

**When**: Beginning PRP execution

**What to Create**:
```javascript
[
  {
    content: "Implement feature X",
    activeForm: "Implementing feature X",
    status: "in_progress"
  },
  {
    content: "Write tests for feature X",
    activeForm: "Writing tests for feature X",
    status: "pending"
  },
  {
    content: "Run sub-agent validation checkpoint 1",
    activeForm: "Running sub-agent validation checkpoint 1",
    status: "pending"
  },
  // ... more steps
]
```

**Why**: Gives user visibility into what will be done, estimated steps.

---

### Pattern 2: ONE Task In Progress at a Time

**Rule**: Exactly ONE task should have `status: "in_progress"` at any moment.

**Why**: Clear indication of current work, easy to track progress.

**Example**:
```javascript
// CORRECT ✓
[
  { content: "Setup database", status: "completed", activeForm: "..." },
  { content: "Create API endpoint", status: "in_progress", activeForm: "..." },
  { content: "Write tests", status: "pending", activeForm: "..." }
]

// INCORRECT ✗ - Multiple in_progress
[
  { content: "Setup database", status: "in_progress", activeForm: "..." },
  { content: "Create API endpoint", status: "in_progress", activeForm: "..." },
  { content: "Write tests", status: "pending", activeForm: "..." }
]
```

---

### Pattern 3: Mark Completed Immediately

**Rule**: Mark todo as `completed` immediately after finishing, not in batch.

**Why**: User sees progress in real-time, easier to resume if interrupted.

**Example**:
```javascript
// After implementing feature:
TodoWrite([
  { content: "Implement feature X", status: "completed", activeForm: "..." },
  { content: "Write tests", status: "in_progress", activeForm: "..." },
  { content: "Validate", status: "pending", activeForm: "..." }
])

// INCORRECT ✗ - Batching completions
// Implement feature, write tests, validate, THEN update todos
```

---

### Pattern 4: Update at Each PRP Step

**When**: After each implementation step, validation checkpoint, or quality gate

**What to Do**: Update TodoWrite to reflect current status.

**Example Flow**:
```
Step 1: Implement feature
  → Update: "Implement feature" = completed, "Write tests" = in_progress

Step 2: Write tests
  → Update: "Write tests" = completed, "Validate" = in_progress

Step 3: Validate
  → Update: "Validate" = completed, "Next step" = in_progress
```

---

### Pattern 5: Break Down Complex Tasks

**When**: Task will take >10 minutes or involves multiple files

**What to Do**: Break into smaller todos.

**Example**:
```javascript
// Instead of one large task:
{ content: "Implement authentication", status: "in_progress", activeForm: "..." }

// Break down:
[
  { content: "Create user model", status: "completed", activeForm: "..." },
  { content: "Implement JWT generation", status: "completed", activeForm: "..." },
  { content: "Create login endpoint", status: "in_progress", activeForm: "..." },
  { content: "Create register endpoint", status: "pending", activeForm: "..." },
  { content: "Add auth middleware", status: "pending", activeForm: "..." }
]
```

**Why**: User sees granular progress, easier to resume if interrupted.

---

## CONTEXT EFFICIENCY TECHNIQUES

**Goal**: Stay under token limits, enable long-running projects.

### Technique 1: Avoid Redundant File Reads

**Problem**: Reading same file multiple times wastes 500-2000 tokens per read.

**Solution**:
```javascript
// GOOD ✓
// Read once
const fileContent = await Read('src/app.ts')
// Analyze and make ALL planned edits
Edit('src/app.ts', oldString1, newString1)
Edit('src/app.ts', oldString2, newString2)
Edit('src/app.ts', oldString3, newString3)

// BAD ✗
Read('src/app.ts')
Edit('src/app.ts', oldString1, newString1)
Read('src/app.ts')  // Unnecessary! Already read it
Edit('src/app.ts', oldString2, newString2)
Read('src/app.ts')  // Unnecessary again!
Edit('src/app.ts', oldString3, newString3)
```

**Savings**: 1000-4000 tokens (2-4 file reads avoided)

**Exception**: Only re-read if user or linter modified the file between edits.

---

### Technique 2: Use Parallel Tool Calls

**Problem**: Sequential tool calls take longer and use more messages.

**Solution**:
```javascript
// GOOD ✓ - Parallel reads
await Promise.all([
  Read('src/app.ts'),
  Read('src/config.ts'),
  Read('src/utils.ts')
])

// BAD ✗ - Sequential reads
await Read('src/app.ts')
await Read('src/config.ts')
await Read('src/utils.ts')
```

**Savings**: Faster execution, fewer message turns.

**When**: Files are independent (no dependencies between them).

---

### Technique 3: TASKS.md as Single Source of Truth

**Problem**: Multiple progress files (PROGRESS.md, SESSION-NOTES.md, STATUS.md) create confusion and token waste.

**Solution**:
- **ONLY** update TASKS.md
- **NEVER** create separate progress tracking files
- **ALWAYS** update TASKS.md before `/clear`

**Savings**: 2000-5000 tokens per session (avoid redundant files).

---

### Technique 4: Archive When Files Grow

**Problem**: Files >800 lines consume excessive tokens when read.

**Solution**:
```bash
# When file exceeds 800 lines:
mv docs/OLD-DOCUMENTATION.md docs/archive/OLD-DOCUMENTATION-2025-11.md
# Keep only current/active content in main directory
```

**Savings**: 1000-3000 tokens per large file avoided.

**When**: Files exceed 800 lines and are not actively modified.

---

### Technique 5: Use /recover-context Efficiently

**Problem**: Manually re-reading multiple files after `/clear` wastes tokens.

**Solution**:
- Use `/recover-context` command
- Loads only essential files (CLAUDE.md, TASKS.md)
- Shows git status and recent commits
- Total: ~800 tokens in 30 seconds

**Savings**: 3000-8000 tokens vs. manual recovery.

---

## TESTING PATTERNS

### Pattern 1: Write Tests Alongside Implementation

**When**: After implementing each feature, write tests before moving to next feature.

**Why**: Fresh in mind, catch issues early, ensure testability.

**Example Flow**:
```
1. Implement function calculateTotal()
2. Write tests for calculateTotal()
3. Run tests, fix any issues
4. Move to next function
```

---

### Pattern 2: Test Structure (AAA Pattern)

**Structure**: Arrange, Act, Assert

**Example (JavaScript/Jest)**:
```javascript
describe('calculateTotal', () => {
  it('should calculate total with tax', () => {
    // Arrange
    const items = [{ price: 100 }, { price: 200 }]
    const taxRate = 0.1

    // Act
    const result = calculateTotal(items, taxRate)

    // Assert
    expect(result).toBe(330) // 300 + 30 tax
  })
})
```

**Example (Python/pytest)**:
```python
def test_calculate_total_with_tax():
    # Arrange
    items = [{"price": 100}, {"price": 200}]
    tax_rate = 0.1

    # Act
    result = calculate_total(items, tax_rate)

    # Assert
    assert result == 330  # 300 + 30 tax
```

---

### Pattern 3: Test Edge Cases

**Always test**:
- Empty inputs (empty array, null, undefined)
- Boundary values (0, negative, maximum)
- Invalid inputs (wrong type, malformed data)
- Error conditions (network failure, database error)

**Example**:
```javascript
describe('calculateTotal edge cases', () => {
  it('should return 0 for empty items', () => {
    expect(calculateTotal([], 0.1)).toBe(0)
  })

  it('should handle zero tax rate', () => {
    expect(calculateTotal([{ price: 100 }], 0)).toBe(100)
  })

  it('should throw error for negative prices', () => {
    expect(() => calculateTotal([{ price: -10 }], 0.1)).toThrow()
  })
})
```

---

### Pattern 4: Integration Tests for Workflows

**When**: After implementing multi-step workflows (API request → database → response)

**What to Test**: Full flow from input to output.

**Example (API endpoint test)**:
```javascript
describe('POST /api/users', () => {
  it('should create user and return 201', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({ name: 'John', email: 'john@example.com' })

    expect(response.status).toBe(201)
    expect(response.body).toHaveProperty('id')
    expect(response.body.name).toBe('John')

    // Verify database
    const user = await db.users.findOne({ email: 'john@example.com' })
    expect(user).toBeDefined()
  })
})
```

---

### Pattern 5: Maintain >80% Coverage

**Rule**: Aim for >80% code coverage, all tests passing.

**How to Check**:
```bash
npm test -- --coverage
# or
pytest --cov=src tests/ --cov-report=term-missing
```

**What to Cover**:
- All business logic functions
- All API endpoints
- All database operations
- All error handling paths

**What to Skip** (acceptable to not test):
- Trivial getters/setters
- Configuration files
- Third-party library wrappers (test your usage, not the library)

---

## SECURITY PATTERNS

### Pattern 1: Input Validation (Whitelist Approach)

**Rule**: Validate all user inputs against expected format, reject anything else.

**Example (JavaScript)**:
```javascript
// GOOD ✓ - Whitelist validation
function createUser(data) {
  const schema = {
    name: { type: 'string', minLength: 1, maxLength: 100 },
    email: { type: 'string', format: 'email' },
    age: { type: 'number', min: 0, max: 150 }
  }

  const validated = validate(data, schema)
  if (!validated.valid) {
    throw new ValidationError(validated.errors)
  }

  // Use validated.data, not raw data
  return db.users.create(validated.data)
}

// BAD ✗ - No validation
function createUser(data) {
  return db.users.create(data) // Trusting user input!
}
```

---

### Pattern 2: SQL Injection Prevention

**Rule**: Always use parameterized queries or ORM, never string concatenation.

**Example (Good)**:
```javascript
// GOOD ✓ - Parameterized query
db.query('SELECT * FROM users WHERE email = $1', [userEmail])

// GOOD ✓ - ORM
db.users.findOne({ where: { email: userEmail } })
```

**Example (Bad)**:
```javascript
// BAD ✗ - String concatenation
db.query(`SELECT * FROM users WHERE email = '${userEmail}'`)
// Vulnerable to: userEmail = "'; DROP TABLE users; --"
```

---

### Pattern 3: XSS Prevention

**Rule**: Sanitize all outputs, use templating engines with auto-escaping.

**Example (React - Good)**:
```jsx
// GOOD ✓ - React auto-escapes
function UserProfile({ user }) {
  return <div>{user.name}</div> // Safe, auto-escaped
}
```

**Example (Plain HTML - Bad)**:
```javascript
// BAD ✗ - innerHTML with user input
element.innerHTML = `<div>${userName}</div>` // XSS vulnerable!

// GOOD ✓ - textContent or DOMPurify
element.textContent = userName
// or
element.innerHTML = DOMPurify.sanitize(userHtml)
```

---

### Pattern 4: Secrets Management

**Rule**: Never commit secrets, use environment variables.

**Setup**:
```bash
# .env (gitignored)
DATABASE_URL=postgresql://user:pass@localhost/db
API_KEY=secret-key-here
JWT_SECRET=super-secret-jwt-key

# .env.example (committed)
DATABASE_URL=postgresql://user:pass@localhost/dbname
API_KEY=your-api-key
JWT_SECRET=your-jwt-secret
```

**Usage**:
```javascript
// GOOD ✓
const apiKey = process.env.API_KEY

// BAD ✗
const apiKey = 'sk-1234567890abcdef' // Hardcoded!
```

---

### Pattern 5: Authentication & Authorization

**Authentication Pattern (JWT)**:
```javascript
// Login endpoint
async function login(email, password) {
  const user = await db.users.findOne({ email })
  if (!user || !await bcrypt.compare(password, user.passwordHash)) {
    throw new UnauthorizedError('Invalid credentials')
  }

  const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET, {
    expiresIn: '24h'
  })

  return { token, user }
}

// Auth middleware
function requireAuth(req, res, next) {
  const token = req.headers.authorization?.replace('Bearer ', '')
  if (!token) {
    return res.status(401).json({ error: 'No token provided' })
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET)
    req.userId = decoded.userId
    next()
  } catch (err) {
    return res.status(401).json({ error: 'Invalid token' })
  }
}
```

**Authorization Pattern (Role-Based)**:
```javascript
function requireRole(role) {
  return async (req, res, next) => {
    const user = await db.users.findById(req.userId)
    if (user.role !== role) {
      return res.status(403).json({ error: 'Forbidden' })
    }
    next()
  }
}

// Usage
app.delete('/api/users/:id', requireAuth, requireRole('admin'), deleteUser)
```

---

## PERFORMANCE PATTERNS

### Pattern 1: Database Query Optimization

**Use EXPLAIN to analyze queries**:
```sql
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';
```

**Add indexes on frequently queried columns**:
```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_products_category_id ON products(category_id);
```

**Avoid N+1 queries**:
```javascript
// BAD ✗ - N+1 problem
const users = await db.users.findAll()
for (const user of users) {
  user.posts = await db.posts.findAll({ where: { userId: user.id } })
}

// GOOD ✓ - Eager loading
const users = await db.users.findAll({
  include: [{ model: db.posts }]
})
```

---

### Pattern 2: Pagination for Large Result Sets

**Rule**: Never return all records, always paginate.

**Example**:
```javascript
// API endpoint
app.get('/api/products', async (req, res) => {
  const page = parseInt(req.query.page) || 1
  const limit = parseInt(req.query.limit) || 20
  const offset = (page - 1) * limit

  const products = await db.products.findAll({
    limit,
    offset,
    order: [['createdAt', 'DESC']]
  })

  const total = await db.products.count()

  res.json({
    products,
    pagination: {
      page,
      limit,
      total,
      totalPages: Math.ceil(total / limit)
    }
  })
})
```

---

### Pattern 3: Caching

**When to Cache**:
- Expensive computations
- Frequently accessed data
- Rarely changing data

**Example (In-Memory Cache)**:
```javascript
const cache = new Map()

async function getUser(id) {
  // Check cache
  if (cache.has(`user:${id}`)) {
    return cache.get(`user:${id}`)
  }

  // Fetch from database
  const user = await db.users.findById(id)

  // Cache for 5 minutes
  cache.set(`user:${id}`, user)
  setTimeout(() => cache.delete(`user:${id}`), 5 * 60 * 1000)

  return user
}
```

**Example (Redis)**:
```javascript
async function getUser(id) {
  // Check Redis
  const cached = await redis.get(`user:${id}`)
  if (cached) {
    return JSON.parse(cached)
  }

  // Fetch from database
  const user = await db.users.findById(id)

  // Cache in Redis for 5 minutes
  await redis.setex(`user:${id}`, 300, JSON.stringify(user))

  return user
}
```

---

## ERROR HANDLING PATTERNS

### Pattern 1: Try/Catch with Specific Error Types

**Example**:
```javascript
async function getUser(id) {
  try {
    const user = await db.users.findById(id)
    if (!user) {
      throw new NotFoundError(`User ${id} not found`)
    }
    return user
  } catch (error) {
    if (error instanceof NotFoundError) {
      // Handle not found
      throw error
    } else if (error instanceof DatabaseError) {
      // Handle database error
      logger.error('Database error:', error)
      throw new ServiceUnavailableError('Database temporarily unavailable')
    } else {
      // Unexpected error
      logger.error('Unexpected error:', error)
      throw new InternalServerError('An unexpected error occurred')
    }
  }
}
```

---

### Pattern 2: API Error Responses (RFC 7807)

**Example**:
```javascript
// Error response format
{
  "type": "https://example.com/errors/not-found",
  "title": "Resource Not Found",
  "status": 404,
  "detail": "User with ID 123 not found",
  "instance": "/api/users/123"
}

// Implementation
class ApiError extends Error {
  constructor(status, title, detail) {
    super(detail)
    this.status = status
    this.title = title
  }

  toJSON() {
    return {
      type: `https://example.com/errors/${this.constructor.name}`,
      title: this.title,
      status: this.status,
      detail: this.message,
      instance: req.path
    }
  }
}

// Error handling middleware
app.use((error, req, res, next) => {
  if (error instanceof ApiError) {
    return res.status(error.status).json(error.toJSON())
  }

  // Unexpected error
  logger.error('Unexpected error:', error)
  res.status(500).json({
    type: 'https://example.com/errors/internal-server-error',
    title: 'Internal Server Error',
    status: 500,
    detail: 'An unexpected error occurred'
  })
})
```

---

## GIT COMMIT PATTERNS

### Pattern 1: Conventional Commits

**Format**:
```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, semicolons, etc.)
- `refactor`: Code refactoring (no feature change or bug fix)
- `test`: Adding or updating tests
- `chore`: Maintenance tasks (dependencies, config, etc.)

**Examples**:
```
feat(auth): add JWT token refresh endpoint

Implemented automatic token refresh when access token expires.
Users are now re-authenticated seamlessly without re-login.

Closes #123

---

fix(api): handle null values in user profile endpoint

Previously threw error when user had no avatar.
Now returns default avatar URL.

---

docs(readme): update installation instructions

Added missing step for database setup.

---

chore(deps): upgrade react to v18.2.0
```

---

### Pattern 2: PRP Reference in Commits

**When**: Committing code from PRP execution

**Format**:
```
feat: [PRP-XXX] Brief description

Implemented:
- Feature 1
- Feature 2

Quality Gates:
✓ Code Quality
✓ Testing (XX% coverage)
✓ Security
✓ [Project-specific]
✓ Performance

PRP: PRPs/domain/prp-xxx-name.md

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## SUMMARY

These patterns represent best practices across:
- **Validation**: 6 mandatory checkpoints ensure quality
- **Tracking**: TodoWrite keeps everyone informed
- **Efficiency**: Context techniques enable long-running projects
- **Testing**: >80% coverage with edge case handling
- **Security**: OWASP Top 10 prevention patterns
- **Performance**: Query optimization, caching, pagination
- **Errors**: Comprehensive error handling and reporting
- **Commits**: Clear commit messages with PRP references

**Remember**: These are living patterns. Update this file when you discover new best practices or project-specific patterns.
