# Component Diagram & Relationships

Visual and textual representation of how components interact.

## System Component Diagram

```mermaid
graph TB
    subgraph "Presentation Layer"
        WEB["🌐 Web Browser<br/>(Static SPA)"]
        CLI["💻 Terminal<br/>(CLI)"]
    end

    subgraph "API Layer"
        FASTAPI["⚡ FastAPI<br/>(REST)"]
        TYPER["📝 Typer<br/>(CLI)"]
    end

    subgraph "Business Logic"
        QUIZ["🎯 quiz.py<br/>(Core Logic)"]
        SEED["🌱 seed.py<br/>(Data)"]
    end

    subgraph "Data Access"
        ORM["🔗 SQLAlchemy<br/>(ORM)"]
    end

    subgraph "Database"
        DB["🐘 PostgreSQL<br/>(Persistence)"]
    end

    subgraph "Infrastructure"
        DOCKER["🐳 Docker<br/>(Containers)"]
        CI["🔄 GitHub Actions<br/>(CI/CD)"]
    end

    WEB -->|HTTP| FASTAPI
    CLI -->|Direct Import| TYPER

    FASTAPI -->|Business Logic| QUIZ
    TYPER -->|Business Logic| QUIZ
    TYPER -->|Seed Data| SEED

    QUIZ -->|ORM Queries| ORM
    SEED -->|ORM Inserts| ORM

    ORM -->|SQL| DB

    FASTAPI -->|Container| DOCKER
    DB -->|Container| DOCKER

    DOCKER -->|CI/CD| CI
```

## Module Interaction Matrix

| From | To | Method | Purpose |
|------|----|---------| ---------|
| CLI | quiz.py | Import | Get shuffled verbs, validate answer |
| CLI | seed.py | Import | Load verbs into DB |
| CLI | database.py | SessionLocal | Get DB session |
| FastAPI | quiz.py | Import | Business logic functions |
| FastAPI | schemas.py | Import | Request/response validation |
| quiz.py | models.py | ORM queries | Create/read UserAttempt, Verb |
| quiz.py | database.py | Import | Use SessionLocal |
| models.py | database.py | Import | Base class for ORM |
| seed.py | models.py | Import | Create Verb instances |
| tests | quiz.py | Import | Unit test business logic |
| tests | models.py | Import | Test ORM models |
| tests | database.py | Import | In-memory SQLite setup |

## Data Flow Between Components

### Web UI → FastAPI → Business Logic → Database

```
1. Web UI (JavaScript)
   └─> const data = fetch('/api/attempts', {method: 'POST', body: JSON.stringify({...})})
       └─> HTTP POST Request

2. FastAPI (api/main.py)
   └─> @app.post("/api/attempts")
       └─> submit_attempt(attempt: AttemptRequest)
           └─> Pydantic validates input
               └─> convert to Python types

3. Business Logic (app/quiz.py)
   └─> validate_and_log(db, verb, past_input, participle_input)
       └─> verb.check_answer(past_input, participle_input)
           └─> compare strings (Python)

       └─> create UserAttempt
           └─> db.add() + db.commit()

4. ORM (SQLAlchemy)
   └─> Generate SQL: INSERT INTO user_attempts (...)

5. Database (PostgreSQL)
   └─> Execute SQL
   └─> Return confirmation

6. Return to Web UI
   └─> AttemptResponse (JSON)
   └─> JavaScript updates UI
```

### CLI → Business Logic → Database

```
1. User (Terminal)
   └─> python main.py quiz

2. CLI (main.py)
   └─> @app.command()
       └─> quiz(verb, rounds)
           └─> Display questions
           └─> Prompt for input

3. Business Logic (app/quiz.py)
   └─> get_shuffled_verbs(db, limit)
       └─> fetch from DB + shuffle in Python

   └─> validate_and_log(db, verb, past, part)
       └─> check answer + log to DB

4. Database (PostgreSQL)
   └─> Execute queries

5. Display Results (Terminal)
   └─> Print ✅/❌
   └─> Print stats
```

## Dependency Graph

```
                    ┌─────────────────┐
                    │   requirements  │
                    │     .txt        │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
         SQLAlchemy       FastAPI        Typer
              │              │              │
              └──────────────┼──────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
    app/database         api/main            main.py
        │                    │                    │
        │            ┌───────┴────────┐          │
        │            │                │          │
    app/models    app/schemas    app/quiz ←─────┘
        │                │           │
        └────────────────┴───────────┘
                    │
             app/seed.py
```

## Concurrency Model

### Single-threaded but async-ready

```
FastAPI (ASGI Server - Uvicorn)
│
├─ Can handle multiple concurrent requests
│  (via event loop, not actual threads)
│
├─ SQLAlchemy Session
│  └─ Each request gets own session
│  └─ DB connection pool handles concurrency
│
└─ No locks needed (SQLAlchemy handles it)
```

### CLI (Single-threaded)

```
main.py
│
├─ Runs questions sequentially
│  1. Get question
│  2. Prompt user
│  3. Log answer
│  4. Repeat
│
└─ No concurrency needed
```

## Integration Points

### 1. FastAPI ↔ PostgreSQL

**Protocol**: psycopg2-binary (PostgreSQL driver)
**Connection**: DATABASE_URL environment variable
**Pooling**: SQLAlchemy handles connection pool

```python
# Connection string
DATABASE_URL = "postgresql://user:pass@localhost:5432/db"

# SQLAlchemy creates pool of 5 connections by default
engine = create_engine(DATABASE_URL)
```

### 2. CLI ↔ PostgreSQL

**Same as above** — uses same SQLAlchemy engine

### 3. Frontend ↔ FastAPI

**Protocol**: HTTP/REST
**Format**: JSON request/response
**Port**: 8000 (default)

```
Browser                 FastAPI Server
   │                          │
   │  GET /api/verbs/quiz     │
   ├─────────────────────────>│
   │                          │
   │  200 OK                  │
   │  [QuizVerb, ...]         │
   |<─────────────────────────┤
   │                          │
```

### 4. GitHub Actions ↔ Repository

**Trigger**: Push to `main` or create version tag
**Artifacts**: Test reports, Docker image
**Deployment**: Push to GitHub Container Registry

## Scalability Considerations

### Current (Single Instance)

```
┌─────────────────────────────────┐
│  FastAPI (1 instance)            │
│  ├─ Uvicorn (4 workers)         │
│  └─ 20 requests/sec capacity    │
└───────────┬─────────────────────┘
            │
┌───────────▼─────────────────────┐
│  PostgreSQL (1 instance)         │
│  ├─ Connection pool (5 conns)   │
│  └─ Basic queries (<10ms)       │
└─────────────────────────────────┘
```

### Future (Phase 3+)

```
┌──────────────────────────────────┐
│  Kubernetes Cluster              │
├──────────────────────────────────┤
│  FastAPI Deployment              │
│  ├─ Replica 1                    │
│  ├─ Replica 2                    │
│  ├─ Replica 3                    │
│  └─ Auto-scaling (HPA)           │
├──────────────────────────────────┤
│  PostgreSQL StatefulSet          │
│  ├─ Master                       │
│  ├─ Read Replicas (2)            │
│  └─ PersistentVolume             │
├──────────────────────────────────┤
│  Redis Cache                     │
│  (future optimization)           │
└──────────────────────────────────┘
```

## Error Propagation

```
User Input
   │
   ├─> Validation Error (Pydantic)
   │   └─> 422 Unprocessable Entity
   │
   ├─> Database Error (SQLAlchemy)
   │   └─> 500 Internal Server Error
   │
   ├─> Not Found (verb_id not in DB)
   │   └─> 404 Not Found
   │
   └─> Success
       └─> 200 OK
```

## Configuration Management

### Environment Variables

```
.env
└─ DATABASE_URL
   ├─ Local: postgresql://localhost:5432/...
   ├─ Docker: postgresql://db:5432/...
   └─ Production: Cloud RDS connection string
```

### future (Phase 2+): ConfigMap (Kubernetes)

```yaml
ConfigMap:
  database_url: postgresql://postgres-service:5432/db
  log_level: INFO
  cache_ttl: 3600
```

## Testing Architecture

### Unit Tests (In-Memory)

```
test_quiz.py
   │
   ├─> Uses: create_engine("sqlite:///:memory:")
   │   (No external dependencies)
   │
   ├─> Tests: app/quiz.py functions
   │
   └─> Fast: <1 second execution
```

### Integration Tests (Full Stack)

```
(Future - Phase 2)

test_integration.py
   │
   ├─> Spins up: docker-compose
   │
   ├─> Tests: FastAPI endpoints
   │   with real PostgreSQL
   │
   └─> Slower: ~5 seconds
```

### System Tests (End-to-End)

```
(Future - Phase 5)

test_system.py
   │
   ├─> Deploy to K8s
   ├─> Test: CLI + API + UI
   ├─> Monitor: Logs, metrics
   └─> Cleanup: Uninstall
```
