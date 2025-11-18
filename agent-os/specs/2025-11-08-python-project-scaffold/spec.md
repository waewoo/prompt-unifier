# Specification: Python Project Scaffold

## Goal
Establish a complete, production-ready Python project structure for the Prompt Unifier CLI with Poetry dependency management, TDD testing infrastructure, linting/type checking, and CI/CD automation following modern best practices.

## User Stories
- As a developer, I want a well-organized project structure with clear separation of concerns so that I can quickly locate and modify code
- As a team member, I want automated quality checks via Makefile and pre-commit hooks so that code quality is enforced consistently before commits

## Specific Requirements

**Project Directory Structure**
- Create `src/prompt_unifier/` as the main package with `__init__.py`
- Create `src/prompt_unifier/cli/` subdirectory for Typer-based CLI command implementations
- Create `src/prompt_unifier/core/` subdirectory for core business logic (validation, deployment orchestration)
- Create `src/prompt_unifier/handlers/` subdirectory for ToolHandler implementations following Strategy Pattern
- Create `src/prompt_unifier/models/` subdirectory for Pydantic data models
- Create `src/prompt_unifier/utils/` subdirectory for shared utility functions
- Create `tests/` directory at project root mirroring the src/ structure for TDD
- Create `docs/` directory for project documentation

**Poetry Configuration (pyproject.toml)**
- Set Python version requirement to >=3.12
- Include core dependencies: typer, rich, pydantic, pyyaml, gitpython
- Include dev dependencies: pytest, pytest-cov, pytest-mock, ruff, mypy, pre-commit
- Configure Ruff with PEP 8 compliance, import sorting, and code complexity limits
- Configure mypy in strict mode with no implicit Any types
- Define pytest configuration with minimum 95% coverage requirement
- Set project metadata: name, version, description, authors, license

**Makefile Development Targets**
- `make install` - Install all dependencies via Poetry
- `make test` - Run pytest test suite with coverage reporting
- `make lint` - Run Ruff linter checks
- `make typecheck` - Run mypy static type checker
- `make check` - Run all quality checks sequentially (lint, typecheck, test)
- `make clean` - Remove build artifacts, caches, and temporary files
- `make format` - Auto-format code with Ruff
- `make watch-test` - Auto-rerun tests on file changes for TDD workflow

**Pre-commit Hooks Configuration**
- Configure Ruff for automatic linting and formatting on commit
- Configure mypy for type checking on commit
- Explicitly exclude pytest from hooks for performance (tests run in CI/CD only)
- Set hook execution to fail fast on first error

**GitLab CI/CD Pipeline**
- Create configuration file `.gitlab-ci.yml`
- Configure for Linux runner (using python:3.12 Docker image)
- Install dependencies via Poetry in CI environment
- Run `make lint`, `make typecheck`, and `make test` sequentially
- Upload coverage reports as artifacts
- Ensure local dev environment matches CI environment exactly (same Python version, same tool versions)

**Python .gitignore**
- Ignore virtual environments (venv/, .venv/, env/)
- Ignore Python bytecode and caches (__pycache__/, *.pyc, .pytest_cache/)
- Ignore build artifacts (dist/, build/, *.egg-info/)
- Ignore IDE files (.vscode/, .idea/, *.swp)
- Ignore coverage reports (.coverage, htmlcov/)
- Ignore OS-specific files (.DS_Store, Thumbs.db)

**README.md Template**
- Include project title and one-sentence description aligned with product mission
- Add installation instructions using Poetry and pipx
- Provide quick start example showing basic CLI usage
- Include development setup instructions (install, test, lint)
- Link to product documentation in agent-os/product/

**Empty __init__.py Files**
- Create `src/prompt_unifier/__init__.py` with package version
- Create `src/prompt_unifier/cli/__init__.py`
- Create `src/prompt_unifier/core/__init__.py`
- Create `src/prompt_unifier/handlers/__init__.py`
- Create `src/prompt_unifier/models/__init__.py`
- Create `src/prompt_unifier/utils/__init__.py`

## Visual Design
No visual assets provided for this scaffold specification.

## Existing Code to Leverage
No existing Python code patterns found in the codebase. This is a greenfield project initialization.

## Out of Scope
- Docker configuration and containerization (add later if needed)
- MkDocs documentation site generation (add later if needed)
- Alembic database migrations (add when database features are implemented)
- Multi-OS CI/CD testing on macOS and Windows (expand after initial stability on Linux)
- Multi-version Python testing for 3.13+ (expand after initial stability on 3.12)
- pytest execution in pre-commit hooks (keep in CI/CD only for performance)
- Actual implementation code for CLI commands, handlers, or business logic
- SQLAlchemy and Alembic dependencies (add later when database features are needed)
- Release automation via `make release` target (implement after initial development)
- watch-test implementation (implement after core testing is stable)
