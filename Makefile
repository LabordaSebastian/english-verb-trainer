.PHONY: setup quiz stats test clean destroy help

PYTHON := .venv/bin/python
PIP    := .venv/bin/pip

## help: Show available commands
help:
	@echo ""
	@echo "  English Irregular Verb Trainer — Makefile"
	@echo ""
	@echo "  make up       Start app and DB with Docker Compose"
	@echo "  make down     Stop and remove containers and volumes"
	@echo "  make quiz     Start the quiz locally (requires local setup)"
	@echo "  make stats    Show your progress locally"
	@echo "  make test     Run pytest"
	@echo "  make lint     Run ruff linter"
	@echo "  make clean    Remove venv and cache"
	@echo ""

## up: Start everything with Docker Compose
up:
	docker compose up -d

## down: Stop everything and remove DB volume
down:
	docker compose down -v

## quiz: Launch the quiz locally
quiz:
	$(PYTHON) main.py quiz

## stats: Show quiz stats locally
stats:
	$(PYTHON) main.py stats

## test: Run pytest with verbose output
test:
	$(PYTHON) -m pytest tests/ -v

## lint: Lint with ruff
lint:
	$(PYTHON) -m ruff check .

## clean: Remove venv and Python cache
clean:
	rm -rf .venv __pycache__ .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
