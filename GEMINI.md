# Project Overview

This project is a Python CLI tool named `prompt-manager`. Its purpose is to manage AI prompt templates and coding rules. It uses YAML frontmatter for defining prompts and rules, and supports version control, validation, and deployment workflows.

The main technologies used are Python, Poetry for dependency management, Typer for the CLI, Pydantic for data validation, PyYAML for YAML parsing, and GitPython for Git integration.

The project is structured with the main source code in the `src/prompt_manager` directory and tests in the `tests` directory.

# Building and Running

The following commands are used for building, running, and testing the project.

## Installation

To install the project and its dependencies, run:

```bash
make install
```

## Running the CLI

To run the CLI, use the following command:

```bash
poetry run prompt-manager <command>
```

For example, to see the help message, run:

```bash
poetry run prompt-manager --help
```

## Running Tests

To run the test suite, use the following command:

```bash
make test
```

## Linting and Formatting

To check the code for linting errors, run:

```bash
make lint
```

To format the code, run:

```bash
make format
```

## Type Checking

To run the static type checker, run:

```bash
make typecheck
```

## All Checks

To run all checks (linting, type checking, and tests), run:

```bash
make check
```

# Development Conventions

The project follows standard Python development conventions.

- **Dependency Management:** The project uses Poetry to manage dependencies. Dependencies are listed in the `pyproject.toml` file.
- **Testing:** The project uses pytest for testing. Tests are located in the `tests` directory.
- **Linting:** The project uses Ruff for linting. The linting rules are defined in the `pyproject.toml` file.
- **Formatting:** The project uses Ruff for code formatting.
- **Type Checking:** The project uses mypy for static type checking. The mypy configuration is in the `pyproject.toml` file.
- **Pre-commit Hooks:** The project uses pre-commit hooks to run checks before committing code. The hooks are configured in the `.pre-commit-config.yaml` file.
- **Security:** The project uses `detect-secrets` and `bandit` for security scanning.


# Agent OS Configuration

This project uses Agent OS v2.x for spec-driven development.
Started initial work with Claude, now continuing with Gemini CLI.

## Product Context

@agent-os/product/overview.md
@agent-os/product/roadmap.md
@agent-os/product/tech-stack.md