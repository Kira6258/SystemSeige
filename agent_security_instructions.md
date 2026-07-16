# 🛡️ Agent Security Instructions — Hackathon Edition

> Paste this at the START of every coding session with your AI agent.  
> These rules make every line of generated code secure by default.

---

## ✂️ COPY-PASTE THIS INTO YOUR AGENT

```
You are a secure-by-default software engineer. Every piece of code you write 
must follow these non-negotiable security rules. Never skip them, even if I 
ask for speed. Security is built in, not added later.
```

---

## 📋 The Master Security Rules (Give These to Your Agent)

---

### RULE 1 — Dependencies: Always Use Latest Stable

```
When adding ANY npm or pip package:
- Always use the latest stable version, never a specific old version
- After suggesting packages, remind me to run: npm audit fix
- Never suggest packages with known CVEs
- Always include exact versions in package.json (no ^ or ~ prefixes for 
  production security-critical packages like JWT libraries)
- Preferred packages: use well-maintained libraries with recent commits
```

**Why**: Old packages = `npm audit` finds CVEs = attackers file bugs against you

---

### RULE 2 — Rate Limiting: Every Auth Route Must Be Throttled

```
EVERY endpoint you write must have rate limiting applied.
For auth routes (/login, /register, /forgot-password):
  - Max 5 requests per minute per IP
For general API routes:
  - Max 100 requests per minute per IP
Never create an endpoint without attaching rate limiting middleware.

Node.js: use express-rate-limit
Python: use slowapi

Always add rate limiting BEFORE the route handler, not after.
```

**Code to always generate:**
```javascript
// Node.js — add to EVERY route file
import rateLimit from 'express-rate-limit';

const authLimiter = rateLimit({
  windowMs: 60 * 1000,   // 1 minute
  max: 5,                 // 5 attempts
  message: { error: 'Too many attempts. Try again in 1 minute.' },
  standardHeaders: true,
  legacyHeaders: false,
});

app.post('/api/auth/login', authLimiter, loginHandler);
```

```python
# FastAPI — add to EVERY route
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, body: LoginSchema):
    ...
```

---

### RULE 3 — Input Validation: Validate EVERYTHING

```
Every API endpoint that accepts input MUST validate it before processing.
Never trust req.body, request.json(), query params, or path params.

Node.js: use Zod for all request body validation
Python: use Pydantic models for all request bodies (FastAPI does this natively)

Rules:
- Define a schema for EVERY request body
- Validate types, lengths, formats (email regex, password strength)
- Strip unknown fields (no extra fields pass through)
- Return 400 with clear error messages for invalid input
- Never pass raw user input to database queries
```

**Code to always generate:**
```typescript
// Node.js — Zod validation on every route
import { z } from 'zod';

const LoginSchema = z.object({
  email: z.string().email().max(255),
  password: z.string().min(8).max(128),
});

app.post('/api/auth/login', async (req, res) => {
  const result = LoginSchema.safeParse(req.body);
  if (!result.success) {
    return res.status(400).json({ error: result.error.flatten() });
  }
  const { email, password } = result.data; // safe, validated data
});
```

```python
# FastAPI — Pydantic on every route (built-in)
class LoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    
    model_config = ConfigDict(extra='forbid')  # Block extra fields!

@app.post("/api/auth/login")
async def login(body: LoginSchema):  # auto-validated
    ...
```

---

### RULE 4 — SQL: Never Use Raw String Queries

```
NEVER concatenate user input into SQL strings.
ALWAYS use:
  - ORM (Prisma, SQLAlchemy, Drizzle) — preferred
  - Parameterized queries if raw SQL is needed

Forbidden patterns:
  - f"SELECT * FROM users WHERE email = '{email}'"
  - `SELECT * FROM users WHERE id = ${req.params.id}`
  - cursor.execute("SELECT * FROM users WHERE id = " + user_id)

Required patterns:
  - db.query("SELECT * FROM users WHERE id = $1", [userId])
  - User.query.filter_by(email=email).first()
  - prisma.user.findUnique({ where: { email } })
```

---

### RULE 5 — Authentication: Secure JWT Setup

```
When implementing JWT authentication:
- JWT secret must be minimum 32 characters, randomly generated
- Store JWT secret in environment variable (never hardcode)
- Set token expiry: access token = 15 minutes, refresh token = 7 days
- Use httpOnly cookies for storing tokens (NOT localStorage)
- Always verify the token signature — never skip verification
- Check token expiry on every protected route
- Never put sensitive data inside the JWT payload (passwords, credit cards)

For protected routes, always add the auth middleware FIRST.
```

**Code to always generate:**
```typescript
// Secure JWT middleware
import jwt from 'jsonwebtoken';

const authMiddleware = (req, res, next) => {
  const token = req.cookies.accessToken; // httpOnly cookie
  if (!token) return res.status(401).json({ error: 'Unauthorized' });
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET); // always verify
    req.user = decoded;
    next();
  } catch (err) {
    return res.status(401).json({ error: 'Invalid or expired token' });
  }
};
```

---

### RULE 6 — Secrets: Never Hardcode Anything

```
NEVER hardcode these in source code:
  - API keys (OpenAI, Google, Stripe, etc.)
  - Database URLs or connection strings
  - JWT secrets
  - Passwords of any kind
  - Webhook secrets

ALWAYS:
  - Use process.env.VARIABLE_NAME (Node.js) or os.environ["VARIABLE"] (Python)
  - Add the variable to .env.example with a placeholder value
  - Add .env to .gitignore BEFORE the first commit
  - If you accidentally commit a secret: rotate the key immediately

When you generate code that needs a secret value, write it as:
  process.env.VARIABLE_NAME and remind me to add it to .env
```

**.gitignore must always include:**
```
.env
.env.local
.env.production
*.pem
*.key
secrets/
```

---

### RULE 7 — Error Handling: Never Leak Stack Traces

```
In production, API errors must NEVER expose:
  - Stack traces
  - Database error messages
  - File paths
  - Library names or versions
  - SQL query details
  - Internal server state

Always return generic error messages to the client.
Always log the full error server-side only.

Pattern to always use:
  try {
    // logic
  } catch (error) {
    console.error('[ERROR]', error); // server-side only
    return res.status(500).json({ error: 'Internal server error' }); // generic
  }

Never: res.status(500).json({ error: error.message })
Never: res.status(500).json({ error: error.stack })
```

---

### RULE 8 — Security Headers: Add Helmet on Day 1

```
For Node.js/Express: install and use helmet immediately
For Python/FastAPI: manually set security headers

Add this to the very TOP of the main server file, before any routes.
```

```typescript
// Node.js — first thing in server.ts
import helmet from 'helmet';
app.use(helmet()); // Sets: X-Frame-Options, CSP, X-Content-Type-Options, etc.
```

```python
# FastAPI — add middleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

---

### RULE 9 — CORS: Explicit Whitelist Only

```
NEVER use: app.use(cors()) with no options
NEVER use: origins: '*'

ALWAYS specify exact allowed origins:
```

```typescript
app.use(cors({
  origin: [
    'https://your-frontend.vercel.app',
    'http://localhost:3000',  // dev only
  ],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
}));
```

---

### RULE 10 — IDOR: Always Check Ownership

```
EVERY route that accesses user-specific data MUST verify:
  "Does the logged-in user own this resource?"

Never: fetch resource by ID alone
Always: fetch resource by ID AND user ID together

Forbidden:
  const order = await db.orders.findById(req.params.id)

Required:
  const order = await db.orders.findOne({ 
    id: req.params.id, 
    userId: req.user.id  // ownership check!
  })

If the resource doesn't belong to the user: return 403 Forbidden
Never return 404 for unauthorized resources (reveals existence)
```

---

### RULE 11 — Race Conditions: Use Database Transactions

```
For ANY operation that involves:
  - Reading a value then writing based on it (check-then-act)
  - Multiple related database writes
  - Inventory/balance/quota updates

ALWAYS wrap in a database transaction with proper locking.
```

```typescript
// Prisma transaction example
const result = await prisma.$transaction(async (tx) => {
  const item = await tx.inventory.findUnique({ 
    where: { id: itemId },
    // Row-level lock
  });
  if (item.stock < quantity) throw new Error('Insufficient stock');
  return await tx.inventory.update({
    where: { id: itemId },
    data: { stock: { decrement: quantity } },
  });
});
```

```python
# SQLAlchemy transaction
async with db.begin():
    item = await db.execute(
        select(Inventory).where(Inventory.id == item_id).with_for_update()
    )
    # with_for_update() = row lock = no race condition
```

---

### RULE 12 — Git & Repository Hygiene

```
Before the first git commit, ensure:
  1. .gitignore is created with .env, node_modules, __pycache__, *.pyc
  2. .env.example exists with placeholder values (not real values)
  3. No API keys or secrets in any file

Forbidden in any commit:
  - Real API keys
  - Database passwords
  - JWT secrets
  - Private keys (.pem, .key)

Also:
  - Never enable DEBUG=True in production
  - Remove all /debug, /test, /seed endpoints before deploy
  - Disable FastAPI auto-docs in production:
      app = FastAPI(docs_url=None, redoc_url=None)  # hide /docs
```

---

## ✅ Pre-Deploy Security Checklist

Run these commands before Phase 3 starts:

```bash
# 1. Zero vulnerabilities in dependencies
npm audit
# Expected: "found 0 vulnerabilities"

# 2. No secrets in git history
git log --all --full-history -- ".env"
# Expected: no output

# 3. .env is gitignored
cat .gitignore | grep ".env"
# Expected: .env is listed

# 4. Test your own rate limiting
curl -X POST https://YOUR_APP/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"a@b.com","password":"wrong"}' \
  --head -s -o /dev/null -w "%{http_code}\n"
# Run 10 times — should return 429 after 5 attempts

# 5. Check security headers
curl -I https://YOUR_APP/api/health
# Expected: X-Frame-Options, X-Content-Type-Options present

# 6. Confirm /docs is hidden (FastAPI)
curl https://YOUR_APP/docs
# Expected: 404
```
