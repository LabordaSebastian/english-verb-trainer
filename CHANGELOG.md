# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Security scanning (Bandit, pip-audit, Trivy) via CI/CD workflows
- Dependabot configuration for automated dependency updates
- `.dockerignore` for smaller, more secure Docker builds
- Non-root user in Docker container
- CHANGELOG.md and issue templates
- Concurrency control for CI/CD workflows

### Changed

- Split `requirements.txt` into `requirements-prod.txt` and `requirements-dev.txt`
- Pinned production dependency versions for reproducible builds
- Replaced hardcoded database credentials with environment variables
- Updated `mkdocs.yml` with `site_url` set directly (removed sed injection)
- Removed default `DATABASE_URL` — now required to be set explicitly
- Switched `docs.yml` to trigger on all pushes to main (not just docs changes)

### Fixed

- Lint issues: import ordering, type annotations (`Optional[str]` → `str | None`)
- Naming convention in tests (`Session` → `session_factory`)
- Removed unsupported `indent-width` field from ruff config
- Duplicate migration logic between `main.py` and `api/main.py`

### Security

- Removed hardcoded database password from `app/database.py`
- Removed default `DATABASE_URL` from `Dockerfile` (must be set via env var)
- Added non-root user to Docker runtime
- Integrated security scanning in CI/CD pipeline
