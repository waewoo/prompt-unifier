# Development Guide

This document provides technical details for developers working on the `prompt-unifier` codebase. For guidelines on submitting changes, see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Table of Contents

- [Development Setup](#development-setup)
- [Core Workflow](#core-workflow)
- [Testing](#testing)
- [Code Style and Quality](#code-style-and-quality)
- [CI/CD Pipeline](#cicd-pipeline)
- [Release Process](#release-process)
- [Project Structure](#project-structure)
- [Architecture](#architecture)

---

## Development Setup

### Prerequisites

| Requirement | Version | Check Installation      |
|-------------|---------|-------------------------|
| **Python**  | 3.11+   | `python --version`      |
| **Poetry**  | 1.7+    | `poetry --version`      |
| **Git**     | 2.x+    | `git --version`         |

### 1. Clone the Repository

```bash
git clone https://gitlab.com/waewoo/prompt-unifier.git
cd prompt-unifier
```

### 2. Install Dependencies

This project uses [Poetry](https://python-poetry.org/) for dependency management. The `Makefile` provides a convenient way to install everything.

```bash
# This runs `poetry install`
make install
```

### 3. Install Pre-commit Hooks

Pre-commit hooks automatically run linters and formatters before each commit to enforce code quality.

```bash
poetry run pre-commit install
```

---

## Core Workflow

All common tasks are managed through the `Makefile`.

### Main Commands

- `make check`: Run all quality checks (lint, types, tests). **Run this before every commit.**
- `make format`: Auto-format code with Ruff.
- `make lint`: Check for code style issues with Ruff.
- `make typecheck`: Run static type analysis with mypy.
- `make test`: Run the full test suite and generate a coverage report.

---

## Testing

We use `pytest` for testing.

### Running Tests

```bash
# Run all tests and generate a coverage report
make test

# Run tests in a specific file
poetry run pytest tests/cli/test_commands.py

# Run tests in a specific directory
poetry run pytest tests/handlers/

# Run tests with verbose output
poetry run pytest -v
```

### Test Coverage

A minimum of **95% test coverage** is required. After running `make test`, you can view a detailed HTML report by opening `htmlcov/index.html` in your browser.

```bash
# For macOS users
open htmlcov/index.html

# For Linux users
xdg-open htmlcov/index.html
```

---

## Code Style and Quality

Code quality is enforced automatically by pre-commit hooks and the CI pipeline.

- **Linting & Formatting**: We use [Ruff](https://github.com/astral-sh/ruff) for fast linting and formatting. Configuration is in `pyproject.toml`.
- **Type Checking**: We use [mypy](http://mypy-lang.org/) in `strict` mode for static type analysis.

You can run these checks manually at any time:
```bash
make lint
make typecheck
make format
```

---

## CI/CD Pipeline

The project uses GitLab CI for continuous integration. The pipeline is defined in `.gitlab-ci.yml`.

### Local CI Testing

You can run the CI pipeline locally using `gitlab-ci-local`, which is helpful for debugging pipeline issues without making commits.

**Prerequisites:**
- Node.js and npm
- `npm install -g gitlab-ci-local`

**Makefile Commands:**
- `make test-ci`: Run the full test suite in a Docker environment mirroring the CI setup.
- `make test-ci-job JOB=<name>`: Run a specific job from the pipeline (e.g., `make test-ci-job JOB=lint`).
- `make test-ci-list`: List all available jobs in the pipeline.

### Pipeline Stages

The pipeline typically includes these stages:
1.  **lint**: Checks code style.
2.  **typecheck**: Runs static type analysis.
3.  **test**: Executes the pytest suite and checks coverage.
4.  **security**: Runs security scans for vulnerabilities and secrets.

---

## Release Process

Releases are managed using `commitizen` and are automated via the `Makefile`.

To create a new release:
1.  Ensure you are on the `main` branch and all changes are committed.
2.  Run the `make release` command with the type of version bump.

```bash
# Create a patch release (e.g., 0.4.0 -> 0.4.1)
make release VERSION_BUMP=patch

# Create a minor release (e.g., 0.4.1 -> 0.5.0)
make release VERSION_BUMP=minor
```

This command will:
1.  Run all quality checks (`make check`).
2.  Bump the version number in `pyproject.toml` and `src/prompt_unifier/__init__.py`.
3.  Commit the version bump.
4.  Create a new Git tag.
5.  Push the commit and tag to the `main` branch.

---

## Project Structure

```
prompt-unifier/
├── src/prompt_unifier/   # Main source code
│   ├── cli/              # CLI commands (Typer)
│   ├── config/           # Configuration management
│   ├── core/             # Core logic (validation, parsing)
│   ├── git/              # Git integration services
│   ├── handlers/         # Handlers for AI tools (Continue, etc.)
│   ├── models/           # Pydantic data models
│   └── output/           # Output formatters (Rich, JSON)
├── tests/                # Test suite
│   ├── cli/
│   ├── core/
│   ├── integration/      # End-to-end tests
│   └── fixtures/         # Test data and fixtures
├── .github/              # GitHub-specific files (e.g., issue templates)
├── .gitlab-ci.yml        # GitLab CI/CD pipeline configuration
├── Makefile              # Makefile with development commands
├── pyproject.toml        # Project metadata and dependencies
└── README.md             # User-facing documentation
```

---

## Architecture

The data flows from your Git repositories to a central storage location on your machine, and then is deployed to the AI tools in your project.

```text
┌──────────────────────────┐      ┌───────────────────────────┐      ┌───────────────────────────┐
│                          │      │                           │      │                           │
│   Git Repository 1       ├─┐    │                           │      │    AI Assistant           │
│  (Global Prompts)        │ │    │                           │      │    (e.g., Continue)       │
│                          │ │    │                           │      │                           │
└──────────────────────────┘ │    │                           │      └───────────────────────────┘
                             │    │                           │                 ▲
                             ├────►   Centralized Storage     ├─────────────────┘
                             │    │ (~/.prompt-unifier/storage)│      (deploy)
┌──────────────────────────┐ │    │                           │
│                          │ │    │                           │
│   Git Repository 2       ├─┘    │                           │
│   (Team Prompts)         │(sync)│                           │
│                          │      │                           │
└──────────────────────────┘      └───────────────────────────┘
```
