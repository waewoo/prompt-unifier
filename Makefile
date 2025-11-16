# Makefile for Prompt Manager CLI
#
# This Makefile provides convenient targets for common development tasks:
# - install: Install dependencies via Poetry
# - test: Run pytest test suite with coverage
# - lint: Run Ruff linter checks
# - typecheck: Run mypy static type checker
# - format: Auto-format code with Ruff
# - check: Run all quality checks (lint, typecheck, test)
# - clean: Remove build artifacts and caches
#
# Usage: make <target>

.PHONY: install test lint typecheck format check clean run release changelog

# Install dependencies via Poetry
install:
	poetry install

# Run prompt-manager CLI (use: make run ARGS="--version")
run:
	@poetry run prompt-manager $(ARGS)

# Run pytest test suite with coverage reporting
test:
	poetry run pytest --cov=src/prompt_manager --cov-report=term-missing --cov-report=html
	@# Clean test artifacts from storage
	@rm -f ~/.prompt-manager/storage/prompts/test-prompt.md 2>/dev/null || true
	@rm -f ~/.prompt-manager/storage/rules/test-rule.md 2>/dev/null || true
	@rm -f ~/.prompt-manager/storage/prompts/main-prompt.md 2>/dev/null || true
	@rm -f ~/.prompt-manager/storage/rules/main-rule.md 2>/dev/null || true

# Run Ruff linter checks
lint:
	poetry run ruff check src/ tests/

# Run mypy static type checker
typecheck:
	poetry run mypy src/

# Auto-format code with Ruff
format:
	poetry run ruff format src/ tests/

# Run all quality checks in sequence
check: lint typecheck test

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
	@NEW_VERSION=$$(poetry version $(VERSION_BUMP) --short)
	@echo "New version: v$${NEW_VERSION}"
	@git add pyproject.toml
	@git commit -m "chore(release): Bump version to v$${NEW_VERSION}"
	@git tag v$${NEW_VERSION}
	@echo "Pushing commit and tag to main branch..."
	@git push origin main
	@git push origin v$${NEW_VERSION}
	@echo "Release v$${NEW_VERSION} created and pushed."
