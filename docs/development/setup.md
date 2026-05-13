# Local Development Setup

Guide to set up the project for local development.

## Prerequisites

### System Requirements

- **OS**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 20.04+)
- **Disk Space**: ~2 GB
- **RAM**: ~4 GB minimum

### Required Tools

| Tool | Version | Purpose | Install |
|------|---------|---------|---------|
| **Python** | 3.10+ | Application runtime | [python.org](https://www.python.org/downloads/) |
| **Git** | 2.0+ | Version control | [git-scm.com](https://git-scm.com/) |
| **Docker Desktop** | 4.0+ | Container runtime | [docker.com](https://www.docker.com/products/docker-desktop/) |
| **Make** (Linux/Mac) | 4.0+ | Task automation | Usually pre-installed |

### Optional (Recommended)

- **VS Code** — Code editor with Python extension
- **Git GUI** — GitHub Desktop or SourceTree
- **Postman** — API testing (alternative: curl)

---

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/LabordaSebastian/english-verb-trainer.git
cd english-verb-trainer
```

### 2. Create Python Virtual Environment

**Linux/Mac**:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt)**:
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

### 3. Install Dependencies

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements-dev.txt
```

> `requirements.txt` is a convenience alias that points to `requirements-dev.txt`.
> Production deployments should use `requirements-prod.txt` (pinned versions).

### 4. Install Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

This automatically runs linting/type-checking before each commit.

### 5. Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env with your PostgreSQL password
```

> **Important:** `DATABASE_URL` is **required** — the application will not start without it. The `.env` file is automatically loaded by docker-compose and python-dotenv.

### 6. Start PostgreSQL (Docker)

```bash
docker compose up -d db
```

Wait for PostgreSQL to be ready:

```bash
docker compose logs db | grep "database system is ready"
```

### 7. Initialize Database

```bash
python main.py seed
```

This creates tables and loads 100 irregular verbs.

### 8. Verify Setup

```bash
# Test CLI
python main.py quiz --rounds 3

# Test API (separate terminal, keep postgres running)
pip install httpx
python -c "
import httpx
resp = httpx.get('http://localhost:8000/health')
print(resp.json())
"
```

✅ If you see quiz questions or health check response, setup is complete!

---

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ -v --cov=app --cov-report=html

# Open coverage report
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Linting & Type Checking

```bash
# Format code
ruff format .

# Check for lint issues
ruff check .

# Type check
mypy app/ api/
```

### Running the API Server

```bash
# Terminal 1: Start PostgreSQL
docker compose up -d db

# Terminal 2: Run server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 in browser.

### Running the CLI

```bash
python main.py quiz
python main.py stats
python main.py seed
```

### Using Makefile (Linux/Mac)

```bash
make help              # See all commands
make setup             # Create venv + install all dependencies
make up                # Start docker-compose
make stop              # Stop containers (keep volumes)
make destroy           # Stop containers and remove volumes
make test              # Run tests
make lint              # Run ruff linter
make quiz              # Start CLI quiz
make docs-serve        # Serve MkDocs locally with live reload
make docs-build        # Build static documentation site
make clean             # Remove venv and cache
```

---

## Project Structure (Development)

```
.
├── main.py                 # CLI entry point
├── app/                    # Core logic
│   ├── database.py
│   ├── models.py
│   ├── quiz.py
│   └── seed.py
├── api/                    # REST API
│   ├── main.py
│   └── schemas.py
├── tests/                  # Test suite
│   ├── test_api.py
│   ├── test_cli.py
│   ├── test_quiz.py
│   ├── test_seed.py
│   └── conftest.py
├── static/                 # Frontend
│   └── index.html
├── docs/                   # Documentation
├── .env                        # Environment (git ignored)
├── requirements.txt            # Dev deps (alias → requirements-dev.txt)
├── requirements-dev.txt        # Dev + testing + docs dependencies
├── requirements-prod.txt       # Pinned production dependencies
├── pyproject.toml              # Configuration
├── Dockerfile                  # Container image (non-root user)
├── .dockerignore               # Build exclusions
├── docker-compose.yml          # Multi-container setup
├── Makefile                    # Convenience tasks
└── .github/
    ├── workflows/              # CI/CD pipeline definitions
    └── dependabot.yml          # Automatic dependency updates
```

---

## Code Style & Quality

### Pre-commit Hooks

Automatically run before each commit:

```bash
git add .
git commit -m "feat: add new feature"
# Hooks run automatically:
# 1. ruff format
# 2. ruff check
# 3. mypy
# 4. trailing-whitespace
```

If hooks fail, fix issues and commit again.

### Manual Checks

```bash
# Format code
ruff format app/ api/ tests/

# Check for issues
ruff check app/ api/ tests/ --fix

# Type checking
mypy app/ api/
```

### Testing

Always run tests before pushing:

```bash
pytest tests/ -v --cov=app
```

Minimum coverage: 70%

---

## IDE Setup

### VS Code

**Extensions to install**:
- Python
- Pylance
- Ruff
- mypy
- Even Better TOML
- Docker

**.vscode/settings.json**:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "charliermarsh.ruff"
  },
  "ruff.path": [".venv/bin/ruff"],
  "mypy-type-checker.path": [".venv/bin/mypy"]
}
```

### PyCharm

1. **Interpreter**: File → Settings → Project → Python Interpreter
   - Select `.venv` folder
2. **Linting**: Settings → Tools → Python Integrated Tools
   - Ruff: Enable
3. **Type Checker**: Settings → Tools → Python Integrated Tools
   - mypy: Enable

---

## Common Tasks

### Add a New Dependency

```bash
# Add to the appropriate requirements file:
pip install package_name
pip freeze | grep package_name >> requirements-prod.txt
# Or for dev-only tools:
pip freeze | grep package_name >> requirements-dev.txt

# Then commit
git add requirements-*.txt
git commit -m "chore(deps): add package_name"
```

### Create a New Test

```bash
# Create test in tests/test_*.py
pytest tests/test_new_feature.py -v
```

### Run Specific Test

```bash
pytest tests/test_quiz.py::TestVerbCheckAnswer::test_correct_lowercase -v
```

### Debug a Test

```bash
pytest tests/test_quiz.py -v --pdb
# Drops into debugger on failure
```

### Generate Coverage Report

```bash
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

---

## Troubleshooting

### "Command not found: python3"

**Problem**: Python not in PATH

**Solution**:
```bash
# Find Python
which python
which python3

# Use full path or add to PATH
/usr/bin/python3 -m venv .venv
```

### "ModuleNotFoundError: No module named 'app'"

**Problem**: Virtual environment not activated

**Solution**:
```bash
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### "Cannot connect to PostgreSQL"

**Problem**: Database not running

**Solution**:
```bash
docker ps  # Check if container is running
docker compose up -d db
docker compose logs db
```

### "Port 5432 already in use"

**Problem**: PostgreSQL port conflict

**Solution**:
```bash
# Use different port in docker-compose.yml
# Or kill existing process
sudo lsof -ti:5432 | xargs kill -9
```

### "Permission denied: entrypoint.sh"

**Problem**: entrypoint.sh not executable (Windows)

**Solution**:
```bash
chmod +x entrypoint.sh
# Or edit in docker-compose.yml to use: ["sh", "entrypoint.sh"]
```

### Pre-commit hook fails

**Problem**: Code doesn't meet quality standards

**Solution**:
```bash
# Let ruff auto-fix
ruff check . --fix

# Fix mypy errors manually
mypy app/

# Try commit again
git add .
git commit -m "message"
```

---

## Performance Tips

### Speed Up Tests

```bash
# Run only fast tests (skip slow ones)
pytest tests/ -v -m "not slow"

# Run tests in parallel (requires pytest-xdist)
pytest tests/ -v -n auto
```

### Faster Development Loop

```bash
# Run API with auto-reload
uvicorn api.main:app --reload

# Edit code → auto-reloads

# Run tests on save (requires pytest-watch)
ptw tests/
```

### Database Performance

```bash
# Keep database running between sessions
docker compose up -d db

# Don't recreate tables on each run
# (tables persist across sessions)
```

---

## Next Steps

- [Read the Architecture Guide](../architecture/overview.md)
- [Explore the Codebase](../structure.md)
- [Check API Endpoints](../api/endpoints.md)
- [Write Your First Test](testing.md)

---

## Getting Help

- **Questions?** Create an issue on GitHub
- **Bug?** Report with reproduction steps
- **Ideas?** Open a discussion
- **Want to contribute?** Read [Contributing Guide](contributing.md)
