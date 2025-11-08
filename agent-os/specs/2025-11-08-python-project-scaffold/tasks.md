# Task Breakdown: Python Project Scaffold

## Overview
Total Tasks: 6 task groups with 29 sub-tasks

This tasks list creates a complete, production-ready Python project structure for the Prompt Manager CLI with Poetry dependency management, TDD testing infrastructure, linting/type checking, and CI/CD automation.

## Task List

### Task Group 1: Foundation - Project Structure
**Dependencies:** None

- [x] 1.0 Create complete project directory structure
  - [x] 1.1 Create src/prompt_manager/ package directory
  - [x] 1.2 Create src/prompt_manager/cli/ subdirectory for Typer CLI commands
  - [x] 1.3 Create src/prompt_manager/core/ subdirectory for core business logic
  - [x] 1.4 Create src/prompt_manager/handlers/ subdirectory for ToolHandler implementations
  - [x] 1.5 Create src/prompt_manager/models/ subdirectory for Pydantic models
  - [x] 1.6 Create src/prompt_manager/utils/ subdirectory for shared utilities
  - [x] 1.7 Create tests/ directory at project root for TDD test suite
  - [x] 1.8 Create docs/ directory for project documentation
  - [x] 1.9 Verify all directories exist with correct paths

**Acceptance Criteria:**
- All 8 directories exist: src/prompt_manager/ (with 5 subdirectories), tests/, docs/
- Directory structure mirrors spec requirements exactly
- All paths are accessible and correctly nested

### Task Group 2: Python Package Configuration
**Dependencies:** Task Group 1

- [x] 2.0 Configure Python package structure
  - [x] 2.1 Create src/prompt_manager/__init__.py with package version (0.1.0)
  - [x] 2.2 Create src/prompt_manager/cli/__init__.py (empty)
  - [x] 2.3 Create src/prompt_manager/core/__init__.py (empty)
  - [x] 2.4 Create src/prompt_manager/handlers/__init__.py (empty)
  - [x] 2.5 Create src/prompt_manager/models/__init__.py (empty)
  - [x] 2.6 Create src/prompt_manager/utils/__init__.py (empty)
  - [x] 2.7 Verify package can be imported successfully

**Acceptance Criteria:**
- All 6 __init__.py files created
- Main __init__.py contains version: __version__ = "0.1.0"
- Python recognizes src/prompt_manager as a valid package
- No import errors when attempting: `python -c "import prompt_manager"`

### Task Group 3: Dependency Management and Configuration
**Dependencies:** Task Group 2

- [x] 3.0 Configure Poetry and project dependencies
  - [x] 3.1 Create pyproject.toml with project metadata
    - name: "prompt-manager"
    - version: "0.1.0"
    - description: "CLI tool for managing AI prompt templates with YAML frontmatter"
    - authors: ["Your Name <your.email@example.com>"]
    - license: "MIT"
    - Python requirement: ">=3.12"
  - [x] 3.2 Add core dependencies to pyproject.toml
    - typer (CLI framework)
    - rich (terminal UI)
    - pydantic (data validation)
    - pyyaml (YAML parsing)
    - gitpython (Git operations)
  - [x] 3.3 Add development dependencies to pyproject.toml
    - pytest (testing framework)
    - pytest-cov (coverage reporting)
    - pytest-mock (mocking utilities)
    - ruff (linter and formatter)
    - mypy (static type checker)
    - pre-commit (Git hooks manager)
  - [x] 3.4 Configure Ruff settings in pyproject.toml
    - PEP 8 compliance
    - Import sorting enabled
    - Max line length: 100
    - Target Python version: py312
  - [x] 3.5 Configure mypy settings in pyproject.toml
    - Strict mode enabled
    - Disallow untyped defs
    - No implicit optional
    - Warn on redundant casts
  - [x] 3.6 Configure pytest settings in pyproject.toml
    - Test paths: tests/
    - Minimum coverage: 85%
    - Coverage report format: term-missing
    - Coverage fail under: 85
  - [x] 3.7 Create .gitignore for Python projects
    - Virtual environments: venv/, .venv/, env/, .env/
    - Python bytecode: __pycache__/, *.pyc, *.pyo, *.pyd
    - Testing artifacts: .pytest_cache/, .coverage, htmlcov/, .tox/
    - Build artifacts: dist/, build/, *.egg-info/, *.egg
    - IDE files: .vscode/, .idea/, *.swp, *.swo, *~
    - OS files: .DS_Store, Thumbs.db, desktop.ini
  - [x] 3.8 Verify pyproject.toml is valid TOML syntax
  - [x] 3.9 Run `poetry install` to verify dependency resolution

**Acceptance Criteria:**
- pyproject.toml contains all required sections: [tool.poetry], [tool.ruff], [tool.mypy], [tool.pytest]
- All 5 core dependencies and 6 dev dependencies specified with compatible versions
- Ruff configured with line-length=100, target-version="py312"
- mypy configured with strict=true
- pytest configured with testpaths=["tests"], coverage minimum 85%
- .gitignore contains all standard Python ignores (12+ patterns)
- `poetry install` completes successfully without errors
- poetry.lock file generated

### Task Group 4: Development Tooling - Makefile
**Dependencies:** Task Group 3

- [x] 4.0 Create Makefile with development targets
  - [x] 4.1 Add `install` target - Install dependencies via Poetry
    - Command: `poetry install`
  - [x] 4.2 Add `test` target - Run pytest with coverage
    - Command: `poetry run pytest --cov=src/prompt_manager --cov-report=term-missing --cov-report=html`
  - [x] 4.3 Add `lint` target - Run Ruff linter
    - Command: `poetry run ruff check src/ tests/`
  - [x] 4.4 Add `typecheck` target - Run mypy type checker
    - Command: `poetry run mypy src/`
  - [x] 4.5 Add `format` target - Auto-format code with Ruff
    - Command: `poetry run ruff format src/ tests/`
  - [x] 4.6 Add `check` target - Run all quality checks sequentially
    - Commands: `make lint && make typecheck && make test`
  - [x] 4.7 Add `clean` target - Remove build artifacts and caches
    - Remove: __pycache__, .pytest_cache, .coverage, htmlcov, dist, build, *.egg-info
  - [x] 4.8 Add `.PHONY` declarations for all targets
  - [x] 4.9 Verify each Makefile target executes successfully

**Note:** `make watch-test` target is explicitly out of scope per requirements. `make release` target is out of scope for initial scaffold.

**Acceptance Criteria:**
- Makefile contains 7 targets: install, test, lint, typecheck, format, check, clean
- All targets use `poetry run` prefix for tool commands
- .PHONY declarations present for all targets
- `make install` successfully installs dependencies
- `make lint` runs without errors (no code to lint yet, but command works)
- `make typecheck` runs without errors (no code to check yet, but command works)
- `make test` runs (may show 0 tests collected)
- `make format` runs successfully
- `make check` executes all three checks in sequence
- `make clean` removes temporary files and directories

### Task Group 5: Quality Automation - Pre-commit and CI/CD
**Dependencies:** Task Group 4

- [x] 5.0 Configure pre-commit hooks and CI/CD pipeline
  - [x] 5.1 Create .pre-commit-config.yaml
    - Add Ruff hook for linting (ruff check)
    - Add Ruff hook for formatting (ruff format)
    - Add mypy hook for type checking
    - Explicitly exclude pytest (performance reasons per spec)
    - Set fail_fast: true
  - [x] 5.2 Create .gitlab-ci.yml
    - Image: python:3.12
    - Stages: lint, typecheck, test
    - Before_script: Install Poetry and dependencies
    - Jobs:
      - lint: Run `poetry run ruff check src/ tests/`
      - typecheck: Run `poetry run mypy src/`
      - test: Run `poetry run pytest --cov=src/prompt_manager --cov-report=term-missing --cov-report=xml`
    - Artifacts: Upload coverage report (coverage.xml)
    - Cache: Poetry cache directory for faster builds
  - [x] 5.3 Install pre-commit hooks locally
    - Command: `poetry run pre-commit install`
  - [x] 5.4 Test pre-commit hooks on a dummy file
  - [x] 5.5 Verify CI/CD workflow syntax is valid

**Acceptance Criteria:**
- .pre-commit-config.yaml contains 3 hooks: ruff (check), ruff (format), mypy
- pytest is NOT included in pre-commit hooks
- .gitlab-ci.yml exists with correct YAML syntax
- CI pipeline targets Linux + Python 3.12 only (no multi-OS or multi-version)
- CI runs lint, typecheck, and test stages
- Coverage artifacts uploaded (coverage.xml)
- `poetry run pre-commit install` completes successfully
- `poetry run pre-commit run --all-files` executes without errors

### Task Group 6: Documentation
**Dependencies:** Task Group 5

- [x] 6.0 Create project documentation
  - [x] 6.1 Create README.md with sections:
    - Project title: "Prompt Manager CLI"
    - One-sentence description: "A Python CLI tool for managing AI prompt templates with YAML frontmatter, enabling version control, validation, and deployment workflows"
    - Installation section:
      - Prerequisites: Python 3.12+, Poetry
      - Install Poetry: `curl -sSL https://install.python-poetry.org | python3 -`
      - Clone repository and install: `git clone <repo-url> && cd prompt-manager && poetry install`
      - Install CLI globally: `pipx install .` (after build)
    - Quick Start section:
      - Example: `poetry run prompt-manager --help`
      - Example: `poetry run prompt-manager validate prompts/`
    - Development section:
      - Setup: `make install`
      - Run tests: `make test`
      - Run linter: `make lint`
      - Run type checker: `make typecheck`
      - Run all checks: `make check`
      - Format code: `make format`
    - Documentation link: "See agent-os/product/ for full product documentation"
    - Contributing section: "Pull requests welcome. Please ensure `make check` passes."
    - License: MIT
  - [x] 6.2 Verify README renders correctly on GitLab (markdown syntax)
  - [x] 6.3 Add brief comment headers to key files
    - Add docstring to pyproject.toml explaining sections
    - Add comment header to Makefile explaining targets
    - Add comment header to .pre-commit-config.yaml

**Acceptance Criteria:**
- README.md contains all 8 required sections
- Installation instructions use Poetry and pipx as specified
- Quick start examples show basic CLI usage patterns
- Development section references all Makefile targets
- Documentation link points to agent-os/product/
- README markdown renders correctly (test with `gh readme` or markdown viewer)
- Key configuration files have explanatory comments

## Execution Order

Recommended implementation sequence:
1. **Foundation** (Task Group 1): Create directory structure - no dependencies
2. **Package Configuration** (Task Group 2): Add __init__.py files - requires directories
3. **Dependency Management** (Task Group 3): Set up Poetry and configuration files - requires package structure
4. **Development Tooling** (Task Group 4): Create Makefile targets - requires Poetry and dependencies
5. **Quality Automation** (Task Group 5): Configure pre-commit and CI/CD - requires Makefile and tooling
6. **Documentation** (Task Group 6): Write README and comments - requires all tooling to describe accurately

## Testing and Verification

After completing all task groups, verify the scaffold is production-ready:

1. **Clean slate test**: Delete poetry.lock and .venv/, run `make install` from scratch
2. **Quality checks**: Run `make check` and ensure all checks pass (lint, typecheck, test)
3. **Pre-commit test**: Make a trivial change and commit to verify hooks execute
4. **CI simulation**: Manually run all CI commands locally to ensure they match workflow
5. **Package import**: Run `python -c "import prompt_manager; print(prompt_manager.__version__)"` to verify package structure

Expected results:
- All Makefile targets execute without errors
- Pre-commit hooks run on commit (Ruff + mypy, NO pytest)
- CI workflow would pass if triggered (simulate locally)
- Package imports successfully and shows version 0.1.0
- Project structure matches spec exactly

## Notes

- **No actual implementation code**: This scaffold creates structure and tooling only. Business logic, CLI commands, and handlers are out of scope.
- **Out of scope items**: Docker, MkDocs, Alembic, multi-OS/multi-version CI, `make watch-test`, `make release` target
- **SQLAlchemy/SQLite**: Not included per requirements discussion (add later when database features needed)
- **Greenfield project**: No existing code patterns to leverage, creating from scratch
- **TDD-ready**: Structure supports test-driven development with pytest and coverage requirements
- **Quality gates**: Pre-commit hooks and CI/CD enforce code quality before merge
- **Local-CI parity**: Development environment matches CI environment exactly (Python 3.12, same tool versions)
- **Python version note**: Python >=3.12 specified in requirements, but >=3.11 supported for compatibility with current environment
