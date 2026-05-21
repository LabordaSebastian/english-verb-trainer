.PHONY: setup quiz stats test lint clean help docs-serve docs-build up stop destroy

PYTHON := .venv/bin/python
PIP    := .venv/bin/pip
MODULE := app.cli

## help: Show available commands
help:
	@echo ""
	@echo "  English Irregular Verb Trainer — Makefile"
	@echo ""
	@echo "  setup       Create venv and install dependencies"
	@echo "  up          Start app and DB with Docker Compose"
	@echo "  stop        Stop Docker Compose (keep volumes)"
	@echo "  destroy     Stop and remove containers and volumes"
	@echo "  quiz        Start the quiz locally"
	@echo "  stats       Show your progress locally"
	@echo "  test        Run pytest"
	@echo "  lint        Run ruff linter"
	@echo "  docs-serve  Serve MkDocs documentation locally"
	@echo "  docs-build  Build static documentation site"
	@echo "  clean       Remove venv and cache"
	@echo ""

## setup: Create virtual environment and install all dependencies
setup:
	python3 -m venv .venv
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -r requirements-dev.txt
	$(PIP) install pre-commit
	pre-commit install

## up: Start everything with Docker Compose
up:
	docker compose -f docker/docker-compose.yml up -d

## rebuild: Rebuild and start containers (use after Python/API changes)
rebuild:
	docker compose -f docker/docker-compose.yml up -d --build

## stop: Stop containers without removing volumes
stop:
	docker compose -f docker/docker-compose.yml down

## destroy: Stop containers and remove volumes
destroy:
	docker compose -f docker/docker-compose.yml down -v

## quiz: Launch the quiz locally
quiz:
	$(PYTHON) -m $(MODULE) quiz

## stats: Show quiz stats locally
stats:
	$(PYTHON) -m $(MODULE) stats

## test: Run pytest with verbose output
test:
	$(PYTHON) -m pytest tests/ -v

## lint: Lint with ruff
lint:
	$(PYTHON) -m ruff check .

## docs-serve: Serve documentation locally with live reload
docs-serve:
	$(PYTHON) -m mkdocs serve

## docs-build: Build static documentation site
docs-build:
	$(PYTHON) -m mkdocs build

## clean: Remove venv and Python cache
clean:
	rm -rf .venv __pycache__ .pytest_cache htmlcov coverage.xml
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
