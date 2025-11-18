# Tech Stack

## Overview
Prompt Unifier is a CLI-only Python application with no web interface, no centralized server, and no cloud database. All operations are local, Git-centric, and developer-focused.

## Language & Runtime

### Python 3.12+
- **Rationale**: Modern Python with improved performance, enhanced type system, better error messages, and long-term support
- **Key Features Used**: Type hints, Protocol classes, pattern matching (if needed), improved asyncio performance
- **Minimum Version**: 3.12 (for latest typing features and performance improvements)

## Frontend

**N/A - CLI Only**

This is a pure command-line interface tool with no graphical user interface, no web dashboard, and no browser-based components.

## Backend (CLI Application)

### Core Framework

**Poetry**
- **Purpose**: Dependency management, virtual environment handling, packaging, and publishing
- **Rationale**: Modern Python packaging with lock files for reproducible builds, better dependency resolution than pip, integrated build system

**Typer / Click**
- **Purpose**: CLI framework for building command-line interfaces
- **Rationale**: Type-based CLI generation (Typer) or explicit decorator approach (Click), automatic help generation, argument/option parsing, command grouping
- **Decision**: Choose Typer for type-safety or Click for explicit control

### Terminal UI

**Rich**
- **Purpose**: Advanced terminal formatting, progress bars, tables, syntax highlighting, and beautiful output
- **Rationale**: Professional CLI user experience, live progress updates during deployment, formatted tables for list/status commands, colored error messages
- **Features**: Progress indicators, markdown rendering, tree views, syntax highlighting, responsive tables

### Validation & Data Models

**Pydantic**
- **Purpose**: Data validation, settings management, and type-safe data models
- **Rationale**: Parse and validate YAML frontmatter, enforce prompt format specification, automatic error messages, JSON schema generation
- **Features**: Field validation, custom validators, serialization/deserialization, type coercion

**PyYAML / ruamel.yaml**
- **Purpose**: YAML parsing for frontmatter extraction
- **Rationale**: Parse YAML frontmatter from prompt files, maintain comments and formatting (ruamel.yaml), standards-compliant parsing
- **Decision**: Use PyYAML for simplicity or ruamel.yaml for comment preservation

### Testing

**pytest**
- **Purpose**: Test framework following TDD methodology
- **Rationale**: Comprehensive test discovery, fixture system, parametrized testing, plugin ecosystem
- **Coverage Target**: >95% code coverage

**pytest-cov**
- **Purpose**: Coverage reporting integrated with pytest
- **Rationale**: Track test coverage, enforce coverage requirements in CI/CD, identify untested code paths

**pytest-mock**
- **Purpose**: Mocking and patching for unit tests
- **Rationale**: Mock file system operations, Git commands, and external tool interactions during testing

### Code Quality

**Ruff**
- **Purpose**: Fast Python linter and formatter (replaces Flake8, Black, isort)
- **Rationale**: 10-100x faster than existing tools, combines multiple tools in one, automatic fixes, compatible with Black
- **Rules**: Enforce PEP 8, import sorting, code complexity limits, security checks

**mypy**
- **Purpose**: Static type checker
- **Rationale**: Catch type errors before runtime, enforce type hints across codebase, improve IDE autocomplete, serve as documentation
- **Configuration**: Strict mode enabled, no implicit Any, check untyped definitions

**pre-commit**
- **Purpose**: Git hooks for automatic code quality checks
- **Rationale**: Run Ruff, mypy, and tests before commits, ensure code quality gates, prevent broken commits

## Database

### No Centralized Database

**Rationale**: Git serves as the source of truth for prompts, no need for centralized storage, keeps tool lightweight and offline-capable

### SQLite (Future Extension Only)

**Purpose**: Local metadata storage if needed for caching, deployment history, or tool-specific state
- **Use Case**: Track deployment timestamps, cache validation results, store user preferences
- **Location**: ~/.prompt-unifier/data.db (user-local, not shared)
- **Migration**: Alembic for schema versioning if needed

**SQLAlchemy + Alembic** (if SQLite is used)
- **Purpose**: ORM for database operations, schema migrations
- **Rationale**: Type-safe database queries, automatic migrations, cross-platform compatibility

## Infrastructure & Deployment

### Deployment Model: Local Only

**No Server Component**
- Application runs entirely on user's local machine
- No centralized deployment, no API server, no cloud hosting
- Each user installs via pip/pipx

### Installation Methods

**pip / pipx**
- **Purpose**: Python package installation
- **Rationale**: Standard Python distribution, pipx for isolated CLI tool installation
- **Command**: `pipx install prompt-unifier` (recommended) or `pip install prompt-unifier`

**Gitlab Releases**
- **Purpose**: Versioned releases with changelog
- **Rationale**: Track versions, provide release notes, enable Gitlab Actions automation

### Version Control

**Git**
- **Purpose**: Source code versioning, prompt storage, team collaboration
- **Rationale**: Industry standard, built-in branching/merging, distributed architecture, excellent for code review
- **Repository**: User's prompt repository (separate from tool source code)

**GitPython**
- **Purpose**: Python library for Git operations
- **Rationale**: Programmatic Git access, clone/pull/status operations, avoid shell command injection

## Development Tools

### IDE / Editor Support

**VS Code / PyCharm / Vim**
- Type hints enable excellent autocomplete and inline documentation
- Linting integration with Ruff
- Test runner integration with pytest

### CI/CD

**GitLab Actions**
- **Purpose**: Automated testing, linting, type checking, and release automation
- **Pipeline**: Run pytest, Ruff, mypy on every commit and PR
- **Principle**: Local development environment MUST match CI environment exactly (same Python version, same tool versions, same checks)

**Makefile / just**
- **Purpose**: Task runner for common development commands
- **Commands**: `make test`, `make lint`, `make typecheck`, `make install`
- **Rationale**: Ensure consistency between local and CI environments

### Documentation

**Markdown**
- **Purpose**: README, contributing guide, prompt format specification
- **Rationale**: GitHub-native rendering, simple formatting, widely understood

**Docstrings (Google/NumPy style)**
- **Purpose**: Inline code documentation
- **Rationale**: Auto-generate API docs, improve IDE tooltips, serve as developer reference

**MkDocs / Sphinx** (Optional)
- **Purpose**: Generate documentation website if needed
- **Rationale**: Searchable docs, versioned documentation, API reference generation

## Architectural Patterns

### Strategy Pattern (via Python Protocols)

**ToolHandler Protocol**
- **Purpose**: Define interface for AI tool integrations (Continue, Cursor, Windsurf, Aider, Kilo Code)
- **Benefits**: Extensibility without core code changes, dependency inversion, testability via mocks, clear contracts
- **Implementation**: Python 3.12 Protocol class with deploy(), validate_deployment(), get_tool_info() methods

### Layered Architecture

**CLI Layer** (Typer/Click commands)
- User interaction, argument parsing, output formatting
- Delegates to Core layer

**Core Layer** (Business logic)
- Prompt validation, deployment orchestration, Git operations
- Tool-agnostic business rules

**Handler Layer** (Tool integrations)
- Tool-specific deployment logic via ToolHandler implementations
- File system operations, path resolution

**Model Layer** (Data structures)
- Pydantic models for prompts, configuration, validation results
- Type-safe data transfer objects

### Dependency Injection

**Purpose**: Inject ToolHandler instances, Git clients, file system abstractions
**Benefits**: Testability (mock dependencies), flexibility (swap implementations), clear dependencies

## Security & Best Practices

### Security Considerations

**No Secrets in Prompts**
- Validate that prompts don't contain API keys or credentials
- Git pre-commit hooks to detect common secret patterns

**File System Safety**
- Validate all file paths to prevent directory traversal
- Use pathlib for cross-platform path handling
- Sandboxed operations within configured directories

**Git Operations**
- Validate repository URLs (no arbitrary command injection)
- Use GitPython library instead of shell commands where possible

### Best Practices

**Type Safety**
- 100% type hints on public APIs
- mypy strict mode enforced
- No `Any` types except where absolutely necessary

**Test-Driven Development**
- Write tests before implementation
- Red-Green-Refactor cycle
- High coverage (>95%) requirement

**Error Handling**
- Explicit exception types, not bare `except:`
- User-friendly error messages via Rich
- Logging for debugging (--verbose flag)

**Cross-Platform Compatibility**
- Test on Linux, macOS, Windows
- Use pathlib instead of os.path
- Handle different line endings and file systems

## Summary Table

| Category | Technology | Purpose |
|----------|-----------|---------|
| Language | Python 3.12+ | Core runtime |
| Package Manager | Poetry | Dependency management |
| CLI Framework | Typer/Click | Command-line interface |
| Terminal UI | Rich | Beautiful CLI output |
| Validation | Pydantic | Data models and validation |
| Testing | pytest | Test framework (TDD) |
| Linting | Ruff | Fast linting and formatting |
| Type Checking | mypy | Static type analysis |
| Git Integration | GitPython | Programmatic Git operations |
| Database | SQLite (optional) | Local metadata storage |
| ORM | SQLAlchemy (optional) | Database operations |
| Deployment | pip/pipx | Local installation |
| CI/CD | Gitlab Actions | Automated testing & releases |
| Architecture | Strategy Pattern | Extensible tool handlers |
