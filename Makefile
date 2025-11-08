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

.PHONY: install test lint typecheck format check clean

# Install dependencies via Poetry
install:
	poetry install

# Run pytest test suite with coverage reporting
test:
	poetry run pytest --cov=src/prompt_manager --cov-report=term-missing --cov-report=html

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
