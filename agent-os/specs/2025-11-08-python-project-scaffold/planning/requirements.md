# Spec Requirements: Python Project Scaffold

## Initial Description

Initialize complete Python project structure for Prompt Manager CLI, including all directories (src/, tests/, docs/, scripts/) and standard files (README.md, Makefile, pyproject.toml, .gitignore, etc.), following recommended conventions (Poetry, TDD, lint, type checking, CI/CD, etc.).

**Objective**: Have a ready-to-use skeleton for developing, testing, and deploying the CLI.

**Context**:
- Project: Prompt Manager CLI
- Working Directory: /root/travail/prompt-manager
- Product Documentation: agent-os/product/
- Initialization Date: 2025-11-08

## Requirements Discussion

### First Round Questions

**Q1:** I assume you want the standard Python project structure following modern best practices:
```
src/prompt_manager/
├── __init__.py
├── cli/          # CLI layers (Typer/Click commands)
├── core/         # Core business logic (validation, deployment orchestration)
├── handlers/     # ToolHandler implementations (Strategy Pattern)
├── models/       # Pydantic models
└── utils/        # Shared utilities
```
This promotes modularity, testability, and clarity. Is that correct?

**Answer:** CONFIRMED - Use the standard structure exactly as proposed. This promotes modularity, testability, and clarity.

**Q2:** For the CLI framework, I'm thinking Typer (modern, built on Python typing, facilitates automatic help generation, good developer experience). Should we use Typer, or would you prefer Click for finer control?

**Answer:** Typer - Modern, built on Python typing, facilitates automatic help generation, good developer experience. Click provides finer control but Typer covers most use cases and simplifies maintenance.

**Q3:** For YAML parsing, I assume PyYAML is sufficient for standard parsing of YAML frontmatters. Should we use PyYAML, or do we need ruamel.yaml for preserving comments and exact formatting?

**Answer:** PyYAML - Sufficient for standard parsing of YAML frontmatters. Minor comment loss is acceptable. Only use ruamel.yaml if preserving comments and exact formatting is critical.

**Q4:** In pyproject.toml, should we include SQLite and SQLAlchemy dependencies from the start, or add them later when database features are needed? This affects initial dependency footprint.

**Answer:** Include SQLite and SQLAlchemy dependencies early if planning to extend with local database features. Otherwise, adding them later is acceptable for minimizing initial dependencies while retaining flexibility.

**Q5:** For the Makefile, I'm planning standard targets like `make install`, `make test`, `make lint`, `make typecheck`, `make check`, `make clean`. Should we add any additional targets like `make format`, `make watch-test`, or `make release`?

**Answer:**
- Standard: `make install`, `make test`, `make lint`, `make typecheck`, `make check`, `make clean`
- Additional targets to add:
  - `make format` (code formatting)
  - `make watch-test` (automatically rerun tests during development)
  - `make release` (tagging, changelog updates, build, publish)

**Q6:** For pre-commit hooks, should we include pytest to run tests before each commit, or keep pytest only in CI/CD for performance reasons?

**Answer:** Keep pytest only in CI/CD for performance reasons. Do NOT include pytest in pre-commit hooks as it may slow down commits.

**Q7:** For the CI/CD pipeline, should we test on multiple OS (Linux, macOS, Windows) and Python versions (3.12, 3.13) from the start, or start simple with Linux + 3.12 and expand later?

**Answer:** Start simple with Linux + Python 3.12. After stability, expand to macOS, Windows, and Python 3.13 in parallel.

**Q8:** Are there any features we should explicitly exclude from the initial scaffold (e.g., Docker, MkDocs, Alembic migrations)? This helps set clear scope boundaries.

**Answer:** Do NOT include: Docker, MkDocs, or Alembic migrations initially. Add those later when specifically needed.

### Existing Code to Reference

**Similar Features Identified:**
User mentioned: "Reuse CLI, Makefile, and CI/CD patterns already established."

The user references existing patterns in the codebase but did not provide specific file paths. The spec-writer should look for existing:
- CLI command structure and patterns
- Makefile targets and conventions
- CI/CD workflow configurations

### Follow-up Questions

No follow-up questions were needed. The user's answers were comprehensive and covered all technical decisions required for the project scaffold.

## Visual Assets

### Files Provided:
No visual files found.

### Visual Insights:
No visual assets provided. This is expected for a project scaffold specification as the focus is on file structure and configuration rather than UI/UX design.

## Requirements Summary

### Functional Requirements

**Project Structure:**
- Create `src/prompt_manager/` package with modular subdirectories:
  - `cli/` - Typer-based CLI command implementations
  - `core/` - Core business logic (validation, deployment orchestration)
  - `handlers/` - ToolHandler implementations following Strategy Pattern
  - `models/` - Pydantic data models
  - `utils/` - Shared utility functions
- Create `tests/` directory mirroring src/ structure for TDD
- Create `docs/` directory for documentation
- Create `scripts/` directory for development and deployment automation

**Configuration Files:**
- `pyproject.toml` - Poetry configuration with:
  - Core dependencies: Typer, Rich, Pydantic, PyYAML, GitPython
  - Development dependencies: pytest, pytest-cov, pytest-mock, Ruff, mypy, pre-commit
  - Optional: SQLite and SQLAlchemy (for future extensions)
  - Python version: 3.12+
- `.gitignore` - Python-specific ignores (venv, __pycache__, .pytest_cache, etc.)
- `README.md` - Project description, installation, quick start
- `Makefile` - Development task automation
- `.pre-commit-config.yaml` - Git hooks configuration (Ruff, mypy, but NO pytest)

**Makefile Targets:**
- `make install` - Install dependencies via Poetry
- `make test` - Run pytest suite
- `make lint` - Run Ruff linter
- `make typecheck` - Run mypy type checker
- `make check` - Run all checks (lint + typecheck + test)
- `make clean` - Remove build artifacts, caches
- `make format` - Format code with Ruff
- `make watch-test` - Auto-rerun tests on file changes
- `make release` - Tag, changelog, build, publish workflow

**CI/CD Pipeline:**
- Gitlab Actions workflow (or equivalent)
- Initial: Linux only, Python 3.12
- Future expansion: macOS, Windows, Python 3.13
- Steps: install dependencies, run lint, run typecheck, run tests
- Coverage reporting with pytest-cov

**Pre-commit Hooks:**
- Ruff linting and formatting
- mypy type checking
- DO NOT include pytest (performance reasons)

**Technology Choices:**
- CLI Framework: Typer (type-safe, automatic help, modern DX)
- YAML Parsing: PyYAML (sufficient for standard parsing)
- Terminal UI: Rich (progress bars, tables, syntax highlighting)
- Validation: Pydantic (data models and validation)
- Testing: pytest with pytest-cov and pytest-mock
- Linting: Ruff (fast, comprehensive)
- Type Checking: mypy (strict mode)
- Package Manager: Poetry (modern dependency management)

### Reusability Opportunities

**Patterns to Reuse:**
- CLI command structure and patterns from existing codebase
- Makefile targets and conventions already established
- CI/CD workflow configurations from existing pipelines

User indicated these patterns exist but did not provide specific paths. Spec-writer should investigate the codebase for:
- Existing CLI implementations to model command structure after
- Current Makefile for target naming conventions
- Existing Gitlab Actions workflows or CI configurations

### Scope Boundaries

**In Scope:**
- Complete project directory structure (src/, tests/, docs/, scripts/)
- pyproject.toml with Poetry configuration and all core dependencies
- Makefile with comprehensive development targets (install, test, lint, typecheck, check, clean, format, watch-test, release)
- .gitignore for Python projects
- .pre-commit-config.yaml with Ruff and mypy (NO pytest)
- Basic README.md template
- Gitlab Actions CI/CD for Linux + Python 3.12
- All __init__.py files for proper Python package structure

**Out of Scope (Explicitly Excluded):**
- Docker configuration (add later if needed)
- MkDocs documentation site (add later if needed)
- Alembic migrations (add later if database features are implemented)
- Multi-OS CI/CD testing (expand after initial stability)
- Multi-version Python testing (expand after initial stability)
- pytest in pre-commit hooks (CI/CD only for performance)
- Actual implementation code (this is scaffold only)

### Technical Considerations

**Alignment with Product Mission:**
- Supports "CLI-first, developer-centric design" differentiator
- Enables "Quality-focused TDD development" differentiator
- Foundation for implementing Strategy Pattern architecture (ToolHandler Protocol)
- Establishes testing and quality gates from day one

**Integration with Tech Stack:**
- Python 3.12+ for modern type system and performance
- Poetry for dependency management as specified in tech stack
- Typer for CLI framework (type-safe alternative to Click)
- Rich for terminal UI as specified
- Pydantic for validation and data models
- pytest + Ruff + mypy for quality toolchain
- GitPython for future Git operations (include in dependencies)

**Development Workflow:**
- Local environment matches CI environment exactly (same Python version, same checks)
- Pre-commit hooks prevent quality issues before commit
- Makefile provides consistent commands across team
- TDD workflow supported with `make watch-test`
- Release automation via `make release`

**Future Extensibility:**
- SQLite/SQLAlchemy dependencies can be added when needed
- Structure supports Strategy Pattern for ToolHandler implementations
- Modular architecture (cli/, core/, handlers/, models/, utils/) supports clean separation of concerns
- CI/CD pipeline can expand to multi-OS and multi-version testing

**Cross-Platform Compatibility:**
- Use pathlib for path handling (not os.path)
- Poetry ensures consistent dependency resolution across platforms
- Initial focus on Linux, expand to macOS/Windows after stability
