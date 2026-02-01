# AI Assistant Instructions

**READ THIS FIRST - MANDATORY FOR ALL AI ASSISTANTS**

You are working on the `prompt-unifier` project. You MUST follow this protocol for ALL feature
development, regardless of which AI assistant you are (Claude, Gemini, etc.).

______________________________________________________________________

## Mandatory Feature Addition Protocol

Execute this checklist **IN ORDER** when developer asks to add a feature:

### ✓ STEP 1: Roadmap Update (REQUIRED)

- [ ] Ask: "Is this feature in `agent-os/product/roadmap.md`?"
- [ ] If NO: "I will add it to the roadmap now."
- [ ] Add entry with:
  - Feature name
  - Description (1-2 sentences)
  - Priority (High/Medium/Low)
  - Status (Planned)
  - Target milestone
  - Dependencies (if any)
- [ ] Show entry for approval before proceeding

### ✓ STEP 2: Agent OS Workflow (REQUIRED)

- [ ] Ask: "Do you have a spec in `agent-os/specs/`?"
- [ ] If NO, guide through phases:
  - **Vague idea** → `agent-os/commands/shape-spec/shape-spec.md run this`
  - **Clear requirements** → `agent-os/commands/write-spec/write-spec.md run this`
- [ ] If YES, confirm phase:
  - **Need tasks** → `agent-os/commands/create-tasks/create-tasks.md run this`
  - **Ready to implement** → `agent-os/commands/implement-tasks/implement-tasks.md run this`

### ✓ STEP 3: Implementation

- [ ] Only proceed after STEP 1 & 2 complete
- [ ] Follow standards in `agent-os/standards/`
- [ ] Apply TDD: write failing test first, implement, refactor
- [ ] Reference plan files if complex feature

### ✓ STEP 4: Post-Implementation

- [ ] Update roadmap status (Planned → In Progress → Completed)
- [ ] Verify spec is current
- [ ] Run `make app-check-all` before committing
- [ ] Stage changes with clear commit message

**CRITICAL: Never skip roadmap update. Never implement without spec.**

______________________________________________________________________

## Quick Start Guide

### First Time Setup

```bash
make env-install              # Install all dependencies and git hooks
```

### Common Daily Commands

```bash
# Development workflow
make app-run ARGS="--help"    # Explore CLI commands
make app-test                 # Run tests (do this often!)
make app-lint                 # Check code quality
make app-check-all            # Full validation before commit

# Security checks
make sec-all                  # Run all security scans

# CI simulation
make ci-pipeline              # Test full CI pipeline locally
make ci-list                  # See available CI jobs
```

### Before Every Commit

```bash
make app-check-all            # Lint + Test + All checks
```

### When Adding a Feature

1. Check/update `agent-os/product/roadmap.md`
1. Follow Agent OS workflow (see below)
1. Run `make app-check-all` before committing

______________________________________________________________________

## Project Overview

`prompt-unifier` is a Python CLI tool for managing AI prompt templates and coding rules using YAML
frontmatter, with version control, validation, and deployment support.

### Tech Stack

**Core:**

- Python 3.13+
- Poetry (dependency management)
- Typer (CLI framework)

**Libraries:**

- Pydantic (validation)
- PyYAML (YAML parsing)
- GitPython (Git integration)

**Dev Tools:**

- pytest (testing)
- Ruff (linting + formatting)
- mypy (type checking)
- pre-commit (hooks)

### Project Structure

```
prompt-unifier/
├── src/prompt_unifier/        # Main source
│   ├── cli/                   # CLI commands
│   ├── models/                # Pydantic models
│   ├── services/              # Business logic
│   └── utils/                 # Utilities
├── tests/                     # Tests (mirrors src/)
├── agent-os/                  # Agent OS config
│   ├── product/               # Vision, roadmap, tech-stack
│   ├── standards/             # Coding standards
│   ├── specs/                 # Feature specs
│   └── commands/              # Agent OS workflow
├── pyproject.toml             # Dependencies & config
├── Makefile                   # Build commands
└── AGENTS.md                  # This file
```

______________________________________________________________________

## Development Methodology: Agent OS

**Spec-driven development system** (Agent OS v2.x) with 3-layer context.

Learn more: [buildermethods.com/agent-os](https://buildermethods.com/agent-os)

### Context Layers

1. **Standards** (`agent-os/standards/`): Coding practices, conventions
1. **Product** (`agent-os/product/`): Mission, roadmap, tech decisions
1. **Specs** (`agent-os/specs/`): Feature specifications

### Agent OS Workflow

#### Phase 0: Plan Product (Run Once)

Define product strategy, roadmap, tech stack.

```
agent-os/commands/plan-product/plan-product.md run this
```

**When:** Project start or Agent OS installation

#### Feature Development Cycle (Phases 1-5)

##### Phase 1: Shape Spec (Optional)

Clarify vague requirements into well-scoped features.

```
agent-os/commands/shape-spec/shape-spec.md run this
```

Skip if requirements already clear.

##### Phase 2: Write Spec (Required)

Create detailed specification with implementation details.

```
agent-os/commands/write-spec/write-spec.md run this
```

Output: Spec file in `agent-os/specs/[feature-name]/`

##### Phase 3: Create Tasks (Required)

Break spec into prioritized, actionable checklist.

```
agent-os/commands/create-tasks/create-tasks.md run this
```

##### Phase 4: Implement Tasks (Simple)

Direct implementation for straightforward features.

```
agent-os/commands/implement-tasks/implement-tasks.md run this
```

##### Phase 5: Orchestrate Tasks (Complex)

Advanced orchestration with subagents for complex features.

```
agent-os/commands/orchestrate-tasks/orchestrate-tasks.md run this
```

**Note:** Choose ONE: implement-tasks OR orchestrate-tasks (not both).

______________________________________________________________________

## Building and Running

### Installation

```bash
make env-install              # Install dependencies and git hooks (first setup)
```

### Development Commands

```bash
# CLI usage
make app-run                  # Run CLI (use ARGS="--version" to pass arguments)
make app-run ARGS="--help"    # Show CLI help
make app-run ARGS="<command>" # Run specific command

# Quality checks
make app-lint                 # Run linting (Ruff, validate-gitlab-ci)
make app-test                 # Run tests with coverage
make app-check-all            # Run ALL checks (lint + test)

# Environment management
make env-update               # Update all dependencies
make env-clean                # Clean temporary files and caches
```

### GitLab CI Local Testing

The project uses `gitlab-ci-local` for local CI pipeline simulation. All dependencies are
auto-installed via make targets.

```bash
make ci-pipeline              # Run FULL CI pipeline locally (Docker)
make ci-job JOB=<name>        # Run specific GitLab CI job
make ci-list                  # List all available jobs
make ci-validate              # Validate .gitlab-ci.yml syntax
make ci-clean                 # Clean CI volumes and cache
```

### Security Checks

```bash
make sec-all                  # Run ALL security scans
make sec-code                 # SAST scan (Bandit)
make sec-secrets              # Secret detection
make sec-deps                 # Dependency vulnerabilities (pip-audit)
```

### Release & Distribution

```bash
make pkg-build                           # Build wheel/sdist packages
make pkg-changelog                       # Generate changelog
make pkg-notes VERSION=x.y.z             # Generate release notes
make pkg-publish VERSION_BUMP=patch      # Create release & push (patch/minor/major)
```

### Documentation

```bash
make docs-install             # Install documentation dependencies
make docs-live                # Serve docs locally with live reload (default port: 8000)
make docs-live PORT=9000      # Serve docs on custom port
make docs-build               # Build static documentation site
```

______________________________________________________________________

## Code Style

### Python Standards

- Follow PEP 8
- Max line length: 100 chars
- Type hints on all function signatures
- Google-style docstrings for public APIs

### Naming Conventions

- `snake_case` for functions, variables, modules
- `PascalCase` for classes
- `UPPER_CASE` for constants
- Descriptive names (no abbreviations unless obvious)

### Architecture

- Prefer composition over inheritance
- Keep functions focused (single responsibility)
- Dependency injection over globals
- Domain models in `models/`, logic in `services/`

______________________________________________________________________

## Testing Instructions

### TDD Workflow (MANDATORY)

1. Write failing test first (in `tests/`)
1. Implement minimal code to pass test
1. Refactor while keeping tests green
1. Tests mirror source structure: `tests/test_X.py` for `src/X.py`

### Testing Practices

- Use pytest fixtures for setup/teardown
- Mock external dependencies (Git, filesystem, etc.)
- Test edge cases and error conditions
- Aim for >80% coverage on new code

### Running Tests

```bash
make app-test                      # All tests with coverage report (recommended)
poetry run pytest                  # All tests (direct command)
poetry run pytest tests/test_X.py  # Single file
poetry run pytest -k "test_name"   # Specific test by name
```

______________________________________________________________________

## Workflow Guidelines

### Starting a Feature

1. Check roadmap (`agent-os/product/roadmap.md`)
1. If not there, add it (see Protocol above)
1. Follow Agent OS workflow (shape → write → tasks → implement)
1. Use plan mode for complex features

### During Development

- Commit frequently with conventional commits
- Run `make app-check-all` before pushing
- Update specs when requirements change
- Document important decisions

### For Complex Features

- Create `plan.md` file with Spec, Plan, Tasks, Context sections
- Use planning mode: separate planning from implementation
- Keep checklist of tasks, mark as completed
- Clear context after completing major phases

### Repository Etiquette

- Branch naming: `feature/`, `fix/`, `refactor/`, `docs/`
- Squash commits before merging to main
- No direct commits to main
- Pull latest before starting work
- **No AI attribution**: Never add AI attribution in commits (no "Co-Authored-By: Claude" or
  similar) or in code comments

______________________________________________________________________

## Agent OS Product Context

**Mission:** `agent-os/product/mission.md`

**Roadmap:** `agent-os/product/roadmap.md`

- **YOU MUST update this when adding features**
- Track status: Planned → In Progress → Completed

**Tech Stack:** `agent-os/product/tech-stack.md`

**Standards:** `agent-os/standards/`

- Auto-loaded by Agent OS commands
- Reference before implementation

**Specs:** `agent-os/specs/`

- Each feature has dedicated directory
- Contains requirements, design, tasks

______________________________________________________________________

## Common Pitfalls

### DON'T

- Skip roadmap updates (MANDATORY)
- Implement features without specs
- Write code before tests (violates TDD)
- Commit without running `make app-check-all`
- Use `require()` syntax (use ES modules)
- Mutate function arguments
- Ignore type errors from mypy

### DO

- Update documentation when you find repeated issues
- Use checklists for complex migrations
- Clear context after major phases
- Destructure imports when possible
- Keep functions pure when possible
- Document non-obvious design decisions

______________________________________________________________________

## Quick Reference

| Developer Says   | Your Response                                              |
| ---------------- | ---------------------------------------------------------- |
| "Add feature X"  | Execute Protocol → Check roadmap → Guide Agent OS workflow |
| "I have an idea" | `shape-spec` command                                       |
| "Implement Y"    | "Spec ready? In roadmap?"                                  |
| "Fix bug Z"      | Assess severity → Add to roadmap if significant            |
| "Refactor"       | Check standards, update docs                               |

______________________________________________________________________

## Assistant-Specific Notes

### For Claude Code Users

- Use `/memory` commands to manage context
- Use `/clear` after 1-3 messages to prevent bloat
- Turn off auto-compact in `/config` (prevents stale context)

### For Gemini Users

- Use memory refresh commands when available
- Follow the same Protocol steps as Claude
- Orchestration commands may have limited support

### For All Assistants

- **Always verify spec exists before coding**
- **Roadmap update is non-negotiable**
- **TDD is mandatory**
- **Run `make app-check-all` before committing**

______________________________________________________________________

**REMEMBER: Roadmap update is non-negotiable. Always verify spec exists before coding.**

______________________________________________________________________

## Getting Help

### Makefile Reference

```bash
make help                     # Show all available make targets with descriptions
```

### Available Make Targets by Category

**Environment:**

- `make env-install` — Install dependencies and git hooks
- `make env-update` — Update all dependencies
- `make env-clean` — Clean temporary files and caches

**Application:**

- `make app-run` — Run CLI (use ARGS="...")
- `make app-lint` — Run linting
- `make app-test` — Run tests with coverage
- `make app-check-all` — Run ALL checks

**CI Simulation:**

- `make ci-pipeline` — Run full CI pipeline locally
- `make ci-job` — Run specific job (use JOB=...)
- `make ci-list` — List all available jobs
- `make ci-validate` — Validate CI config
- `make ci-clean` — Clean CI cache

**Security:**

- `make sec-all` — Run ALL security scans
- `make sec-code` — SAST scan (Bandit)
- `make sec-secrets` — Secret detection
- `make sec-deps` — Dependency vulnerabilities

**Release:**

- `make pkg-build` — Build packages
- `make pkg-changelog` — Generate changelog
- `make pkg-publish` — Create release (use VERSION_BUMP=...)

**Documentation:**

- `make docs-install` — Install doc dependencies
- `make docs-live` — Serve docs locally
- `make docs-build` — Build static docs

______________________________________________________________________

## Additional Context

For Tessl-managed rules, see: `.tessl/RULES.md`

# Agent Rules <!-- tessl-managed -->

@.tessl/RULES.md follow the [instructions](.tessl/RULES.md)
