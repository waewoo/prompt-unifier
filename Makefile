# Makefile for Prompt Unifier CLI
#
# This Makefile provides convenient targets for common development tasks:
# - install: Install dependencies via Poetry
# - update-deps: Update all dependencies to latest version in pyproject.toml and poetry.lock
# - test: Run pytest test suite with coverage
# - test-ci: Run tests in GitLab CI environment locally
# - test-ci-shell: Run tests locally with shell executor (faster)
# - lint: Run Ruff linter checks
# - typecheck: Run mypy static type checker
# - format: Auto-format code with Ruff
# - check: Run all quality checks (lint, typecheck, test)
# - clean: Remove build artifacts and caches
# - clean-ci: Clean GitLab CI local volumes
#
# Usage: make <target>

.PHONY: install update-deps test test-ci test-ci-shell test-ci-clean lint typecheck format check clean clean-ci run release changelog ci-lint

# Install dependencies via Poetry
install:
	poetry install

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
	poetry run pytest --cov=src/prompt_unifier --cov-report=term-missing --cov-report=html
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

# Run Ruff linter checks
lint:
	poetry run ruff check src/ tests/

# Run mypy static type checker
typecheck:
	poetry run mypy src/

# Auto-format code with Ruff
format:
	poetry run ruff format src/ tests/

# Check GitLab CI configuration syntax
ci-lint:
	@echo "Checking GitLab CI configuration syntax..."
	@gitlab-ci-local --preview > /dev/null

# Run all quality checks in sequence
check: lint typecheck test ci-lint

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

# Help target to display available commands
help:
	@echo "Available targets:"
	@echo "  make install          - Install dependencies via Poetry"
	@echo "  make update-deps      - Update all dependencies to latest version in pyproject.toml and poetry.lock"
	@echo "  make test             - Run tests locally with Poetry"
	@echo "  make test-ci          - Run tests in GitLab CI environment (Docker, with cache)"
	@echo "  make test-ci-shell    - Run tests with shell executor (faster, less accurate)"
	@echo "  make test-ci-job JOB=<name> - Run specific GitLab CI job"
	@echo "  make test-ci-list     - List all available GitLab CI jobs"
	@echo "  make clean-ci         - Clean GitLab CI local cache and volumes"
	@echo "  make lint             - Run Ruff linter checks"
	@echo "  make typecheck        - Run mypy static type checker"
	@echo "  make format           - Auto-format code with Ruff"
	@echo "  make check            - Run all quality checks (lint, typecheck, test)"
	@echo "  make clean            - Remove build artifacts and caches"
	@echo "  make changelog        - Generate changelog"
	@echo "  make release VERSION_BUMP=<type> - Create and push a new release (patch/minor/major)"
	@echo "  make run ARGS='<args>' - Run prompt-unifier CLI with arguments"
