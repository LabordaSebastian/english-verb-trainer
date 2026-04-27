.PHONY: setup quiz stats test clean destroy help

PYTHON := .venv/bin/python
PIP    := .venv/bin/pip

## help: Show available commands
help:
	@echo ""
	@echo "  English Irregular Verb Trainer — Makefile"
	@echo ""
	@echo "  make setup    Full setup (Docker, Terraform, venv, seed)"
	@echo "  make quiz     Start the quiz"
	@echo "  make stats    Show your progress"
	@echo "  make test     Run pytest"
	@echo "  make lint     Run ruff linter"
	@echo "  make clean    Remove venv and cache"
	@echo "  make destroy  Stop & destroy Postgres container (Terraform)"
	@echo ""

## setup: Full one-shot setup (same as python start.py)
setup:
	python start.py --seed

## quiz: Launch the quiz (setup must have been run first)
quiz:
	$(PYTHON) main.py quiz

## stats: Show quiz stats
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

## destroy: Destroy the Postgres Terraform container
destroy:
	cd terraform && terraform destroy -auto-approve
