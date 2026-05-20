# Project Structure

Complete map of the repository and what each directory contains.

## Directory Tree

```
english-verb-trainer/
│
├── app/                        # Core application logic
│   ├── __init__.py
│   ├── cli.py                  # CLI entry point (Typer — verb-trainer)
│   ├── database.py             # SQLAlchemy engine + session factory
│   ├── models.py               # ORM models (Verb, UserAttempt)
│   ├── quiz.py                 # Business logic (validation, stats, shuffling)
│   └── seed.py                 # Database seeding (100 irregular verbs)
│
├── api/                        # REST API (FastAPI)
│   ├── __init__.py
│   ├── main.py                 # API endpoints + static file serving
│   └── schemas.py              # Pydantic models (request/response)
│
├── static/                     # Frontend (Single Page App)
│   └── index.html              # HTML UI + JavaScript
│
├── docker/                     # Docker configuration
│   ├── Dockerfile              # Container image definition
│   ├── docker-compose.yml      # Multi-container orchestration (PostgreSQL + FastAPI)
│   ├── entrypoint.sh           # Container startup script (seed + uvicorn)
│   └── .dockerignore           # Docker build exclusions
│
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py             # Shared fixtures (db, sample_verb, three_verbs)
│   ├── test_api.py             # FastAPI endpoint integration tests (TestClient)
│   ├── test_cli.py             # Typer CLI command tests (CliRunner)
│   ├── test_quiz.py            # Unit tests for quiz logic
│   └── test_seed.py            # Unit tests for seed function
│
├── docs/                       # MkDocs documentation source
│   ├── index.md                # Homepage
│   ├── quick-start.md          # Getting started guide
│   ├── structure.md            # This file
│   ├── cli-reference.md        # CLI commands
│   ├── architecture/           # System design
│   ├── api/                    # API documentation
│   ├── database/               # Database schema
│   └── development/            # Dev setup & contributing
│
├── assets/                     # Static assets (screenshots, diagrams)
│   ├── Diagrama_infraestructura.png
│   ├── home.png
│   ├── quiz.png
│   ├── results.png
│   └── stats.png
│
├── promo-video/                # Remotion promo video project
│   ├── src/
│   ├── out/                    # Rendered MP4s (gitignored)
│   └── ...
│
├── .github/                    # CI/CD and project automation
│   ├── workflows/
│   │   ├── ci.yml              # Continuous Integration (lint + test)
│   │   ├── cd.yml              # Continuous Delivery (release + Docker push)
│   │   └── docs.yml            # Docs deployment to GitHub Pages
│   ├── dependabot.yml          # Automatic dependency updates
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md
│       └── feature_request.md
│
├── .opencode/                  # Opencode AI skills configuration
│
├── pyproject.toml              # Python project metadata + tool configs
├── Makefile                    # Convenience commands (make up, make test, etc.)
├── .env.example                # Environment variables template
├── .pre-commit-config.yaml     # Pre-commit hooks
├── mkdocs.yml                  # Documentation site config
├── requirements.txt            # Dev dependencies
├── requirements-dev.txt        # Dev + docs dependencies
├── requirements-prod.txt       # Pinned production dependencies
├── .gitignore                  # Git exclusions
├── README.md                   # Main repository README
├── CHANGELOG.md                # Version history
├── LICENSE                     # MIT license
└── AGENTS.md                   # AI agent instructions
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

**`docker/Dockerfile`** — Builds the container image:
- Non-root user for security
- Python 3.12 slim base image
- FastAPI + uvicorn to serve the app

**`docker/.dockerignore`** — Excludes development files from Docker build context:
- Virtual environment, git history, caches, docs, tests
- Reduces build context size and improves security

**`docker/docker-compose.yml`** — Orchestrates multiple containers:
- PostgreSQL 15 service with persistent volume
- FastAPI app service with health checks
- Credentials via environment variables (overridable via `.env`)

**`docker/entrypoint.sh`** — Container startup script:
- Seeds database with 100 irregular verbs
- Starts uvicorn web server on port 8000

### 3. Application Modules

#### `app/database.py`
SQLAlchemy engine, session factory, and `run_migrations()` for schema management. Reads `DATABASE_URL` from environment.

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

#### `app/cli.py`
Typer-based CLI entry point exposing three commands:
- `verb-trainer seed` — Load verbs into PostgreSQL
- `verb-trainer quiz` — Start an interactive quiz session
- `verb-trainer stats` — Show user progress and hardest verbs

### 4. API Layer (`api/`)

**`api/main.py`** — FastAPI application with endpoints:
- `GET /api/verbs/quiz` — Get shuffled verbs for a quiz
- `POST /api/attempts` — Submit an answer
- `GET /api/stats` — View user statistics
- `POST /api/seed` — Reload verb database

**`api/schemas.py`** — Pydantic models for request/response validation:
- `QuizVerb` — Verb data (without correct answers)
- `AttemptRequest` — User's submitted answer (validates `verb_id > 0`)
- `AttemptResponse` — Result with correct answer
- `HardestVerb` — Typed entry in the hardest-verbs ranking
- `StatsResponse` — User statistics with typed `list[HardestVerb]`
- `SeedResponse` — Seed operation result

### 5. Frontend (`static/index.html`)

Single-page application (SPA) with 9 screens, all in a single HTML file:

| Screen | Description |
|--------|-------------|
| **Home** | Verb count selector (10/20/50/75/100) + navigation |
| **Quiz** | Verb form input (past tense + past participle) |
| **Results** | Score circle + mistake list |
| **Stats** | Accuracy metrics + hardest verbs ranking |
| **Review** | 15 tense explanations with collapsible accordion |
| **Tense Quiz Select** | Checkbox selection of tenses to practice |
| **Tense Quiz** | Multiple-choice questions (usage + structure) |
| **Tense Quiz Results** | Score + mistakes per tense |
| **Tense Quiz Stats** | Per-tense accuracy (localStorage) |

Key frontend characteristics:
- **Vanilla JavaScript** (no framework), **HTML5**, **Fetch API**
- **SVG icon sprite** — 11 icons (target, play, chart, book, refresh, trophy, check, x, flame, warning, star)
- **CSS custom properties** color system
- **Glass morphism cards** with `backdrop-filter: blur(20px)`
- **Accessible**: skip link, `:focus-visible` outlines, `role`/`aria` attributes
- Communicates with FastAPI backend via REST at `/api/*`
- `localStorage` for tense quiz statistics persistence

### 6. Testing (`tests/`)

Unit/integration tests across 4 test files:
- **In-memory SQLite** for isolation (no PostgreSQL needed)
- **pytest** as the test runner
- **Fixtures** in `conftest.py` for shared test data
- Tests cover: validation, shuffling, logging, statistics, API endpoints, CLI commands, seed function

### 7. CI/CD Workflows

**`.github/workflows/ci.yml`** — Runs on every push/PR:
- Lint with ruff + format check
- Security scan with Bandit (SAST) + pip-audit (dependencies)
- Run pytest with coverage across Python 3.10, 3.11, 3.12
- Concurrency: cancels stale runs on the same branch

**`.github/workflows/cd.yml`** — Runs on version tags (v1.0.0):
- Run tests (safety gate)
- Vulnerability scan with Trivy (filesystem + Docker image)
- Build Docker image with provenance attestation
- Push to GitHub Container Registry with semver + SHA tags
- Create GitHub Release with auto-generated changelog

**`.github/workflows/docs.yml`** — Builds and deploys MkDocs documentation:
- Triggers on all pushes to main
- Deploys to GitHub Pages via `actions/deploy-pages@v4`

**`.github/dependabot.yml`** — Automatic dependency updates:
- Weekly checks for pip, Docker, and GitHub Actions updates
- Creates pull requests automatically

## Module Dependencies

```mermaid
graph TB
    A["app/cli.py<br/>(CLI Entry)"] --> B["app/database.py<br/>(SQLAlchemy)"]
    A --> C["app/models.py<br/>(ORM Models)"]
    A --> D["app/quiz.py<br/>(Business Logic)"]
    A --> E["app/seed.py<br/>(Data)"]

    F["api/main.py<br/>(FastAPI)"] --> B
    F --> C
    F --> D
    F --> G["api/schemas.py<br/>(Pydantic)"]

    H["tests/*.py<br/>(pytest)"] --> C
    H --> D
    H --> B

    B --> I["PostgreSQL<br/>(Database)"]
```

## Important Directories

### `app/` — Core Logic
Contains business logic, database models, CLI entry point, and utilities. **Single source of truth** for application behavior.

### `api/` — REST Layer
Exposes `app/` functionality as REST endpoints. Can be replaced with another interface (e.g., GraphQL) without touching core logic.

### `docker/` — Container Configuration
All Docker-related files in one place: Dockerfile, Compose, entrypoint, and dockerignore.

### `tests/` — Quality Assurance
Unit and integration tests using in-memory SQLite for fast isolation.

### `docs/` — Documentation
MkDocs source files. Auto-deployed to GitHub Pages on each commit to `main`.

### `.github/` — Automation
Contains workflows (CI/CD/docs), Dependabot config, and issue templates for GitHub.

## File Naming Conventions

| Pattern | Meaning | Example |
|---------|---------|---------|
| `module.py` | Public module | `quiz.py` |
| `test_*.py` | Test file | `test_quiz.py` |
| `conftest.py` | Pytest configuration | |
| `.*.yml` | Configuration | `.pre-commit-config.yaml` |
| `*.md` | Markdown docs | `README.md` |

## Size Overview

```
Source code:       ~700 lines (app + api)
Tests:             ~160 lines
Docs:              ~2000+ lines (this documentation!)
Dependencies:      16 packages (production + dev)
Docker image:      ~200MB (Python 3.12 slim base)
```

## Environment Variables

See `.env.example` for the required variable:

```bash
POSTGRES_PASSWORD=your_secure_password_here
DATABASE_URL=postgresql://trainer_user:${POSTGRES_PASSWORD}@localhost:5432/english_trainer
```

> **Note:** `DATABASE_URL` is **required** — the application will not start without it.

Environment-specific configs can be managed via:
- `.env` files (local development)
- Docker Compose environment sections
- Kubernetes ConfigMaps
