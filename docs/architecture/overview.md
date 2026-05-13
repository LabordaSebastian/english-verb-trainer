# Architecture Overview

High-level system design and technology choices.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interfaces                          │
├──────────────────────┬──────────────────────────────────────┤
│  Web Browser (SPA)   │  Terminal (CLI)                      │
│  http://localhost:8  │  python main.py quiz                 │
│  000                 │                                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Application Layer                              │
├──────────────────────┬──────────────────────────────────────┤
│  FastAPI REST API    │  Typer CLI                           │
│  - GET /api/verbs    │  - quiz                              │
│  - POST /api/attempts│  - stats                             │
│  - GET /api/stats    │  - seed                              │
│  - GET /api/seed     │                                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Business Logic Layer                           │
├──────────────────────────────────────────────────────────────┤
│  app/quiz.py - Core functions:                             │
│  • validate_and_log(verb, past, participle)                │
│  • get_shuffled_verbs(limit)                               │
│  • get_stats()                                              │
│  • get_verb_by_base(name)                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Data Access Layer (ORM)                        │
├──────────────────────────────────────────────────────────────┤
│  SQLAlchemy 2.0:                                            │
│  • app/models.py (Verb, UserAttempt)                       │
│  • app/database.py (engine, sessions)                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Database Layer                                 │
├──────────────────────────────────────────────────────────────┤
│  PostgreSQL 15                                              │
│  - verbs table (100 rows)                                  │
│  - user_attempts table (logs every answer)                 │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack Rationale

### Backend Framework: FastAPI

**Why FastAPI?**
- ✅ Automatic API documentation (Swagger/OpenAPI)
- ✅ Type hints → automatic request validation (Pydantic)
- ✅ Async support (though not needed here)
- ✅ Lightweight and fast

**Alternatives considered:**
- Django — overkill, too heavy
- Flask — no automatic validation
- FastAPI — Goldilocks choice ✓

### CLI Framework: Typer

**Why Typer?**
- ✅ Built on Click, most popular CLI library
- ✅ Type hints → automatic `--help`
- ✅ Command composition
- ✅ Minimal boilerplate

**Alternatives considered:**
- argparse — too verbose
- Click — works, but Typer is nicer
- Typer — modern, type-driven ✓

### ORM: SQLAlchemy 2.0

**Why SQLAlchemy?**
- ✅ Industry standard for Python ORMs
- ✅ Works with any SQL database (PostgreSQL, MySQL, SQLite)
- ✅ Powerful query builder
- ✅ Good type hint support

**Alternatives considered:**
- Django ORM — tied to Django
- Tortoise ORM — async-only
- SQLAlchemy — battle-tested ✓

### Database: PostgreSQL 15

**Why PostgreSQL?**
- ✅ Production-ready relational database
- ✅ JSONB for semi-structured data
- ✅ Window functions, CTEs
- ✅ Excellent query optimizer

**Alternatives considered:**
- SQLite — fine for local, not for production
- MySQL — no advantage over PostgreSQL
- PostgreSQL — feature-complete, robust ✓

### Testing: pytest

**Why pytest?**
- ✅ Most popular Python test framework
- ✅ Fixtures for test setup/teardown
- ✅ Parametrized tests
- ✅ plugins ecosystem (pytest-cov, pytest-xdist)

**Alternatives considered:**
- unittest — built-in but verbose
- nose2 — declining popularity
- pytest — industry standard ✓

### Containerization: Docker

**Why Docker?**
- ✅ Reproducible environments
- ✅ Eliminates "works on my machine"
- ✅ Industry standard for DevOps
- ✅ Easy deployment anywhere

## Data Model

### Verb Table

```sql
CREATE TABLE verbs (
    id INTEGER PRIMARY KEY,
    base VARCHAR(50) UNIQUE NOT NULL,        -- "read"
    past VARCHAR(50) NOT NULL,                -- "read"
    participle VARCHAR(50) NOT NULL,          -- "read"
    meaning VARCHAR(150),                     -- "leer" (Spanish)
    past_alt VARCHAR(50),                     -- Alternative: "learnt"
    participle_alt VARCHAR(50)                -- Alternative: "learnt"
);
```

### UserAttempt Table

```sql
CREATE TABLE user_attempts (
    id INTEGER PRIMARY KEY,
    verb_id INTEGER FOREIGN KEY REFERENCES verbs(id),
    past_given VARCHAR(50) NOT NULL,          -- User's answer for past
    participle_given VARCHAR(50) NOT NULL,    -- User's answer for participle
    is_correct BOOLEAN NOT NULL,              -- True if both answers correct
    attempted_at TIMESTAMP DEFAULT NOW()
);
```

## Request/Response Flow

### Quiz Flow (Web UI)

```
1. User opens http://localhost:8000
   ↓
2. Browser loads static/index.html (SPA)
   ↓
3. JavaScript: GET /api/verbs/quiz?count=10
   ↓
4. FastAPI returns: [QuizVerb, QuizVerb, ...]
   (Verb data WITHOUT correct answers)
   ↓
5. User enters answer for past & participle
   ↓
6. JavaScript: POST /api/attempts
   {verb_id: 1, past_given: "read", participle_given: "read"}
   ↓
7. FastAPI:
   - Loads Verb from DB
   - Calls validate_and_log()
   - Logs UserAttempt
   - Returns: {correct: true, correct_past: "read", ...}
   ↓
8. JavaScript updates UI:
   - Show ✅ or ❌
   - Show next question or results
```

### CLI Flow

```
1. User: python main.py quiz
   ↓
2. main.py (Typer):
   - Initializes DB connection
   - Gets shuffled verbs
   ↓
3. For each verb:
   - Show: "Base verb: READ"
   - Prompt: "Your answer: "
   - User enters: "read read"
   ↓
4. Call validate_and_log():
   - Check if past & participle correct
   - Log UserAttempt to PostgreSQL
   - Return True/False
   ↓
5. Show result:
   - ✅ Correct! or ❌ Wrong!
   ↓
6. After all questions:
   - Show: "Result: 8/10 correct (80%)"
```

## Deployment Models

### Local Development
```
Host Machine
├── Python venv
├── PostgreSQL (container)
└── FastAPI (local or container)
```

### Docker Compose (Testing/Demo)
```
Docker Compose
├── PostgreSQL service
├── FastAPI service
└── Shared network
```

### Kubernetes (Phase 3)
```
K8s Cluster
├── PostgreSQL StatefulSet + PersistentVolume
├── FastAPI Deployment + Service + Ingress
└── ConfigMaps + Secrets
```

## Security Model

### Authentication
Currently **none** (open API) — suitable for demo/learning.

Future phases could add:
- API key authentication
- OAuth2 with JWT tokens
- Role-based access control (RBAC)

### Data Protection
- ✅ Non-root user in Docker
- ✅ Database credentials in environment variables (not hardcoded)
- ✅ SQL injection prevention via SQLAlchemy ORM
- ✅ Input validation via Pydantic

## Performance Considerations

### Database
- Indexes on `verbs.base` for fast lookups
- Foreign keys for referential integrity
- Queries use LIMIT clauses

### Caching
Currently **no caching**. Could add:
- Redis for session/stats cache
- HTTP cache headers (future)

### Concurrency
SQLAlchemy handles connection pooling automatically.

## Scalability

### Current Bottleneck
Single PostgreSQL instance — doesn't scale horizontally.

### Future (Phase 3+)
- Read replicas for statistics queries
- Connection pooling (PgBouncer)
- Cache layer (Redis)
- CDN for static assets

## Error Handling

| Layer | Strategy |
|-------|----------|
| FastAPI | HTTPException with status codes |
| CLI | typer.echo with error messages |
| Database | SQLAlchemy exception handling |
| Business Logic | Return False or raise custom exceptions |

## Monitoring & Observability

Currently **minimal**. Future phases will add:
- Application metrics (Prometheus)
- Structured logging (JSON format)
- Request tracing (OpenTelemetry)
- Health checks (planned)
