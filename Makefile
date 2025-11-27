# Makefile for Prompt Unifier CLI
#
# This Makefile provides convenient targets for common development tasks.
# It acts as the single entry point for industrialization (BP2I standards).
#
# Targets:
# - install:         Install dependencies and setup pre-commit hooks (First setup)
# - lint:            Run all static analysis via pre-commit (Fast feedback: lint, format, security)
# - test:            Run unit tests with coverage (Slow feedback: logic verification)
# - check:           Run full validation suite (lint + test)
# - security:        Run all security scans (SAST, secrets, dependencies)
# - build:           Build distribution packages (wheel and sdist)
# - release-notes:   Generate release notes for a specific version
# - clean:           Remove build artifacts and caches
#
# Usage: make <target>

.PHONY: install update-deps test test-ci test-ci-shell test-ci-clean lint typecheck format check clean clean-ci run release changelog ci-lint help security security-sast security-secrets security-deps build release-notes

# Install dependencies via Poetry and setup pre-commit hooks
install:
	poetry install
	poetry run pre-commit install

# Update all dependencies to latest versions in pyproject.toml and poetry.lock
update-deps:
	@echo "Updating all dependencies to latest versions in pyproject.toml and poetry.lock..."
	@for pkg in $$(poetry export --without-hashes --only main -f requirements.txt | cut -d'=' -f1 | sed '/^$$/d' | sort -u); do \
		echo "Updating $$pkg..."; \
		poetry add $$pkg@latest; \
	done

# Run prompt-unifier CLI (use: make run ARGS="--version")
run:
	@poetry run prompt-unifier $(ARGS)

# Run pytest test suite with coverage reporting
test:
	poetry run pytest --cov=src/prompt_unifier --cov-report=term-missing --cov-report=html --cov-report=xml --junitxml=report.xml
	@# Clean test artifacts from storage
	@rm -f ~/.prompt-unifier/storage/prompts/test-prompt.md 2>/dev/null || true
	@rm -f ~/.prompt-unifier/storage/rules/test-rule.md 2>/dev/null || true
	@rm -f ~/.prompt-unifier/storage/prompts/main-prompt.md 2>/dev/null || true
	@rm -f ~/.prompt-unifier/storage/rules/main-rule.md 2>/dev/null || true

# Run tests in GitLab CI environment locally (with Docker)
test-ci:
	@echo "Running tests in GitLab CI environment (Docker)..."
	@docker volume create prompt-unifier-venv 2>/dev/null || true
	@docker volume create prompt-unifier-pip-cache 2>/dev/null || true
	@gitlab-ci-local test \
		--volume prompt-unifier-venv:/builds/$$(basename $$(pwd))/.venv \
		--volume prompt-unifier-pip-cache:/builds/$$(basename $$(pwd))/.cache/pip

# Run tests locally with shell executor (faster, less accurate)
test-ci-shell:
	@echo "Running tests with shell executor (faster)..."
	@gitlab-ci-local test --shell-executor

# Run specific CI job (use: make test-ci-job JOB=lint)
test-ci-job:
	@if [ -z "$(JOB)" ]; then \
		echo "Error: JOB is required (e.g., make test-ci-job JOB=lint)"; \
		exit 1; \
	fi
	@echo "Running GitLab CI job: $(JOB)..."
	@gitlab-ci-local $(JOB)

# List all available GitLab CI jobs
test-ci-list:
	@echo "Available GitLab CI jobs:"
	@gitlab-ci-local --list

# Clean GitLab CI local cache and volumes
clean-ci:
	@echo "Cleaning GitLab CI local volumes..."
	@docker volume rm prompt-unifier-venv 2>/dev/null || true
	@docker volume rm prompt-unifier-pip-cache 2>/dev/null || true
	@echo "GitLab CI cache cleaned."

# Run all static analysis checks via pre-commit (Linting, Formatting, Security, Types)
lint:
	poetry run pre-commit run --all-files

# Run mypy static type checker (kept for individual running if needed)
typecheck:
	poetry run mypy src/

# Auto-format code with Ruff (via pre-commit hook directly or standalone)
format:
	poetry run ruff format src/ tests/

# Check GitLab CI configuration syntax
ci-lint:
	@echo "Checking GitLab CI configuration syntax..."
	@gitlab-ci-local --preview > /dev/null

# Run all quality checks in sequence (lint + test)
check: lint test ci-lint

# ============================================================================
# SECURITY SCANS
# ============================================================================

# Run all security scans
security: security-sast security-secrets security-deps

# Run Bandit SAST scan (matches pre-commit config)
security-sast:
	@echo "🔎 Running Bandit SAST scan..."
	@poetry run bandit -r src/ -f json -o bandit-report.json
	@poetry run bandit -r src/ -f screen

# Run Detect-Secrets scan (matches pre-commit config)
security-secrets:
	@echo "🔑 Running Detect-Secrets scan..."
	@poetry run detect-secrets scan --baseline .secrets.baseline

# Run dependency vulnerability scans (used in CI)
security-deps:
	@echo "📦 Running dependency vulnerability scans..."
	@echo "   - Pip-audit scan:"
	@poetry run pip-audit --format json --output pip-audit-report.json || true
	@poetry run pip-audit

# ============================================================================
# BUILD & RELEASE
# ============================================================================

# Build distribution packages
build:
	@echo "📦 Building distribution packages..."
	@poetry build

# Generate release notes for a specific version (used in CI)
# Usage: make release-notes VERSION=1.2.3
release-notes:
	@if [ -z "$(VERSION)" ]; then \
		echo "Error: VERSION is required"; \
		exit 1; \
	fi
	@poetry run cz changelog --dry-run "$(VERSION)" > RELEASE_NOTES.md 2>/dev/null || { \
		echo "## Release v$(VERSION)" > RELEASE_NOTES.md; \
		echo "" >> RELEASE_NOTES.md; \
		echo "See [CHANGELOG.md](./CHANGELOG.md) for full details." >> RELEASE_NOTES.md; \
	}

# Generate changelog
changelog:
	@echo "Generating changelog..."
	@poetry run cz changelog --incremental > CHANGELOG.md
	@echo "Changelog generated in CHANGELOG.md"

# Create a new release
# Usage: make release VERSION_BUMP=patch
release: check
	@if [ -z "$(VERSION_BUMP)" ]; then \
		echo "Error: VERSION_BUMP is required (e.g., patch, minor, major)"; \
		exit 1; \
	fi
	@echo "Bumping version with poetry version $(VERSION_BUMP)..."
	@NEW_VERSION=$$(poetry version $(VERSION_BUMP) --short) && \
	echo "New version: v$${NEW_VERSION}" && \
	git add pyproject.toml && \
	git commit -m "chore(release): Bump version to v$${NEW_VERSION}" && \
	git tag v$${NEW_VERSION} && \
	echo "Pushing commit and tag to main branch..." && \
	git push origin main && \
	git push origin v$${NEW_VERSION} && \
	echo "Release v$${NEW_VERSION} created and pushed."

# Remove build artifacts, caches, and temporary files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*.pyd" -delete 2>/dev/null || true

# Help target to display available commands
help:
	@echo "Available targets:"
	@echo "  make install          - Install dependencies and setup pre-commit hooks"
	@echo "  make lint             - Run all static analysis (lint, format, security) via pre-commit"
	@echo "  make test             - Run unit tests via pytest"
	@echo "  make check            - Run full validation suite (lint + test)"
	@echo "  make security         - Run all security scans (SAST, secrets, dependencies)"
	@echo "  make build            - Build distribution packages"
	@echo "  make clean            - Remove build artifacts and caches"
	@echo "  make update-deps      - Update all dependencies"
	@echo "  make format           - Auto-format code"
	@echo "  make changelog        - Generate changelog"
	@echo "  make release VERSION_BUMP=<type> - Create and push a new release"
