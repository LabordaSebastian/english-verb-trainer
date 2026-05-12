# Project Structure

Complete map of the repository and what each directory contains.

## Directory Tree

```
english-verb-trainer/
│
├── 📋 Configuration Files
│   ├── pyproject.toml          # Python project metadata + tool configs (ruff, mypy, pytest, coverage)
│   ├── docker-compose.yml      # Multi-container orchestration (PostgreSQL + FastAPI)
│   ├── Dockerfile              # Container image definition
│   ├── Makefile                # Convenience commands (make up, make test, etc.)
│   ├── .env.example            # Environment variables template
│   ├── .gitignore              # Git exclusions
│   ├── .pre-commit-config.yaml # Pre-commit hooks configuration
│   ├── mkdocs.yml              # Documentation site configuration
│   └── requirements.txt        # Python dependencies
│
├── 📁 Application Code
│   ├── main.py                 # CLI entry point (Typer app)
│   │
│   ├── app/                    # Core application logic
│   │   ├── __init__.py
│   │   ├── database.py         # SQLAlchemy engine + session factory
│   │   ├── models.py           # ORM models (Verb, UserAttempt)
│   │   ├── quiz.py             # Business logic (validation, stats, shuffling)
│   │   └── seed.py             # Database seeding (100 irregular verbs)
│   │
│   ├── api/                    # REST API (FastAPI)
│   │   ├── __init__.py
│   │   ├── main.py             # API endpoints + static file serving
│   │   └── schemas.py          # Pydantic models (request/response)
│   │
│   └── static/                 # Frontend (Single Page App)
│       └── index.html          # HTML UI + JavaScript
│
├── 🧪 Testing
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_quiz.py        # 18+ unit tests (in-memory SQLite)
│   │
│   └── .pytest_cache/          # Pytest cache (git ignored)
│
├── 📚 Documentation
│   ├── docs/                   # MkDocs source (this documentation)
│   │   ├── index.md            # Homepage
│   │   ├── quick-start.md      # Getting started guide
│   │   ├── structure.md        # This file
│   │   ├── cli-reference.md    # CLI commands
│   │   ├── architecture/       # System design
│   │   ├── api/                # API documentation
│   │   ├── database/           # Database schema
│   │   └── development/        # Dev setup & contributing
│   │
│   └── site/                   # Generated HTML (git ignored)
│
├── 🚀 CI/CD
│   └── .github/
│       ├── workflows/
│       │   ├── ci.yml          # Continuous Integration (lint + test)
│       │   ├── cd.yml          # Continuous Delivery (release + Docker push)
│       │   └── docs.yml        # Docs deployment to GitHub Pages
│       │
│       └── ISSUE_TEMPLATE/     # GitHub issue templates
│
├── 📦 Docker
│   └── entrypoint.sh           # Container startup script (seed + uvicorn)
│
├── 📄 Metadata
│   ├── README.md               # Main repository README
│   ├── LICENSE                 # MIT license
│   └── CHANGELOG.md            # Version history
│
└── 📁 Cache/Build (git ignored)
    ├── .venv/                  # Python virtual environment
    ├── __pycache__/            # Python bytecode cache
    ├── .ruff_cache/            # Ruff linter cache
    └── .pytest_cache/          # Pytest cache
```

## Key Files Explained

### 1. Python Configuration (`pyproject.toml`)

Centralizes all Python project metadata and tool configurations:

```toml
[project]
name = "english-verb-trainer"
requires-python = ">=3.10"
dependencies = [...]

[tool.ruff]        # Linter configuration
[tool.mypy]        # Type checker configuration
[tool.pytest]      # Test runner configuration
[tool.coverage]    # Coverage report configuration
```

### 2. Docker Configuration

**`Dockerfile`** — Builds the container image:
- Multi-stage build for optimization
- Non-root user for security
- FastAPI + uvicorn to serve the app

**`docker-compose.yml`** — Orchestrates multiple containers:
- PostgreSQL 15 service with persistent volume
- FastAPI app service with health checks
- Environment variable configuration

**`entrypoint.sh`** — Container startup script:
- Seeds database with 100 irregular verbs
- Starts uvicorn web server on port 8000

### 3. Application Modules

#### `app/database.py`
SQLAlchemy engine and session factory. Reads `DATABASE_URL` from environment.

#### `app/models.py`
Two ORM models:
- **Verb**: Stores irregular verbs (base, past, participle, alternatives)
- **UserAttempt**: Logs each quiz attempt (answer, correctness, timestamp)

#### `app/quiz.py`
Business logic functions:
- `get_verb_by_base()` — Fetch a verb
- `get_shuffled_verbs()` — Randomize quiz questions
- `validate_and_log()` — Check answer and record in DB
- `get_stats()` — Compute accuracy and hardest verbs

#### `app/seed.py`
Contains tuple of 100 irregular verbs and `seed_verbs()` function to populate the database.

### 4. API Layer (`api/`)

**`api/main.py`** — FastAPI application with endpoints:
- `GET /api/verbs/quiz` — Get shuffled verbs for a quiz
- `POST /api/attempts` — Submit an answer
- `GET /api/stats` — View user statistics
- `POST /api/seed` — Reload verb database
- `GET /health` — Health check for load balancers

**`api/schemas.py`** — Pydantic models for request/response validation:
- `QuizVerb` — Verb data (without correct answers)
- `AttemptRequest` — User's submitted answer
- `AttemptResponse` — Result with correct answer
- `StatsResponse` — User statistics
- `SeedResponse` — Seed operation result

### 5. Frontend (`static/index.html`)

Single-page application (SPA) with:
- Vanilla JavaScript (no framework)
- HTML5 + Fetch API
- Dark mode CSS
- Communicates with FastAPI backend via REST

### 6. Testing (`tests/test_quiz.py`)

18+ unit tests using:
- **In-memory SQLite** for isolation (no PostgreSQL needed)
- **pytest** as the test runner
- **Fixtures** for test data
- Tests cover: validation, shuffling, logging, statistics

### 7. CI/CD Workflows

**`.github/workflows/ci.yml`** — Runs on every push/PR:
- Lint with ruff
- Type check with mypy
- Run pytest with coverage
- Test matrix: Python 3.10, 3.11, 3.12

**`.github/workflows/cd.yml`** — Runs on version tags (v1.0.0):
- Run tests again (safety)
- Build Docker image
- Push to GitHub Container Registry
- Create GitHub Release with changelog

**`.github/workflows/docs.yml`** — Deploys documentation:
- Builds MkDocs site
- Pushes to GitHub Pages

## Module Dependencies

```mermaid
graph TB
    A["main.py<br/>(CLI Entry)"] --> B["app/database.py<br/>(SQLAlchemy)"]
    A --> C["app/models.py<br/>(ORM Models)"]
    A --> D["app/quiz.py<br/>(Business Logic)"]
    A --> E["app/seed.py<br/>(Data)"]

    F["api/main.py<br/>(FastAPI)"] --> B
    F --> C
    F --> D
    F --> G["api/schemas.py<br/>(Pydantic)"]

    H["tests/test_quiz.py<br/>(pytest)"] --> C
    H --> D
    H --> B

    B --> I["PostgreSQL<br/>(Database)"]
```

## Important Directories

### `app/` — Core Logic
Contains business logic, database models, and utilities. **Single source of truth** for application behavior.

### `api/` — REST Layer
Exposes `app/` functionality as REST endpoints. Can be replaced with another interface (e.g., GraphQL) without touching core logic.

### `tests/` — Quality Assurance
Unit tests that validate business logic in isolation. Uses in-memory SQLite.

### `docs/` — Documentation
MkDocs source files. Auto-deployed to GitHub Pages on each commit to `main`.

### `.github/workflows/` — Automation
GitHub Actions workflows for CI, CD, and documentation deployment.

## File Naming Conventions

| Pattern | Meaning | Example |
|---------|---------|---------|
| `module.py` | Public module | `quiz.py` |
| `test_*.py` | Test file | `test_quiz.py` |
| `conftest.py` | Pytest configuration | |
| `*_test.py` | Alternative test file | Not used here |
| `.*.yml` | Configuration | `.env`, `docker-compose.yml` |
| `*.md` | Markdown docs | `README.md` |

## Size Overview

```
Source code:       ~500 lines (app + api)
Tests:             ~160 lines
Docs:              ~2000+ lines (this documentation!)
Dependencies:      16 packages (production + dev)
Docker image:      ~200MB (Python 3.12 slim base)
```

## Environment Variables

See `.env.example` for available variables:

```bash
DATABASE_URL=postgresql://user:pass@host:5432/db
```

Environment-specific configs can be managed via:
- `.env` files (local development)
- Docker Compose environment sections
- Kubernetes ConfigMaps (Phase 3)
