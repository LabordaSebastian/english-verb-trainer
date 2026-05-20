# English Verb Trainer — Agent Instructions

## Key Commands

```bash
# Setup
pip install -r requirements-dev.txt

# Lint & format (run before commits)
ruff check .
ruff format --check .

# Type check
mypy app/ api/

# Run all tests (requires DATABASE_URL env var)
pytest tests/ -v --tb=short

# Run single test file
pytest tests/test_cli.py -v

# Run single test
pytest tests/test_api.py::test_quiz_api_returns_verbs -v
```

## Environment

- **Database**: PostgreSQL via `DATABASE_URL` env var (e.g., `postgresql://user:pass@localhost/db`)
- **Python**: 3.10-3.12 supported
- **Test DB**: Tests use `conftest.py` which handles DATABASE_URL automatically

## Architecture

- **CLI**: Typer (`app/cli.py` → `verb-trainer` entrypoint)
- **API**: FastAPI (`api/main.py` on port 8000)
- **SPA**: Vanilla JS + HTML (`static/index.html`)
- **Core logic**: `app/` (database, models, quiz logic, seed data)

## Important Conventions

- **Line length**: 88 chars (ruff default)
- **Coverage target**: 65% (defined in pyproject.toml)
- **Security scanning**: bandit + pip-audit (run in CI, not blocking)
- **No Dependabot**: Removed — project is stable; manually update deps if needed
- **Git workflow**: Rebase PRs onto main rather than closing/recreating

## Testing Notes

- Tests use fixtures from `tests/conftest.py` for database setup
- Some tests require PostgreSQL; mock or skip if no DB available
- Coverage includes `app/` and `api/` only (not `tests/`)

## Common Issues

- **Database connection errors**: Set `DATABASE_URL` before running tests or CLI
- **Coverage failure**: CI fails if coverage drops below 65%
- **Import errors**: Ensure all deps installed (`pip install -r requirements-dev.txt`)
