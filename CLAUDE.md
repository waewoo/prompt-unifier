# Instructions for Claude Code

**YOU MUST follow this protocol for ALL feature development.**

## Mandatory Feature Addition Protocol

Execute this checklist IN ORDER when developer asks to add a feature:

### ✓ STEP 1: Roadmap Update (REQUIRED)
- Ask: "Is this feature in `@agent-os/product/roadmap.md`?"
- If NO: "I will add it to the roadmap now."
- Add entry with: Feature name, Description, Priority (High/Medium/Low), Status (Planned), Target milestone, Dependencies
- Show entry for approval before proceeding

### ✓ STEP 2: Agent OS Workflow (REQUIRED)
- Ask: "Do you have a spec in `@agent-os/specs/`?"
- If NO, guide through phases:
  - Vague idea → `@agent-os/commands/shape-spec/shape-spec.md run this`
  - Clear requirements → `@agent-os/commands/write-spec/write-spec.md run this`
- If YES, confirm phase:
  - Need tasks → `@agent-os/commands/create-tasks/create-tasks.md run this`
  - Ready to implement → `@agent-os/commands/implement-tasks/implement-tasks.md run this`

### ✓ STEP 3: Implementation
- Only proceed after STEP 1 & 2 complete
- Follow standards in `@agent-os/standards/`
- Apply TDD: write failing test first, implement, refactor
- Reference plan files if complex feature

### ✓ STEP 4: Post-Implementation
- Update roadmap status (Planned → In Progress → Completed)
- Verify spec is current
- Run `make check` before committing
- Stage changes with clear commit message

**IMPORTANT: Never skip roadmap update. Never implement without spec.**

---

# Project Overview

`prompt-manager` is a Python CLI tool for managing AI prompt templates and coding rules using YAML frontmatter, with version control, validation, and deployment support.

## Tech Stack

**Core:**
- Python 3.11+
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

## Project Structure

prompt-manager/
├── src/prompt_manager/ # Main source
│ ├── cli/ # CLI commands
│ ├── models/ # Pydantic models
│ ├── services/ # Business logic
│ └── utils/ # Utilities
├── tests/ # Tests (mirrors src/)
├── agent-os/ # Agent OS config
│ ├── product/ # Vision, roadmap, tech-stack
│ ├── standards/ # Coding standards
│ ├── specs/ # Feature specs
│ └── commands/ # Agent OS workflow
├── pyproject.toml # Dependencies & config
├── Makefile # Build commands
└── CLAUDE.md # This file

text

---

# Development Methodology: Agent OS

**Spec-driven development system** (Agent OS v2.x) with 3-layer context.

Learn more: [buildermethods.com/agent-os](https://buildermethods.com/agent-os)

## Context Layers

1. **Standards** (`@agent-os/standards/`): Coding practices, conventions
2. **Product** (`@agent-os/product/`): Mission, roadmap, tech decisions
3. **Specs** (`@agent-os/specs/`): Feature specifications

## Agent OS Workflow

### Phase 0: Plan Product (Run Once)
Define product strategy, roadmap, tech stack.

@agent-os/commands/plan-product/plan-product.md run this

text

When: Project start or Agent OS installation

### Feature Development Cycle (Phases 1-5)

#### Phase 1: Shape Spec (Optional)
Clarify vague requirements into well-scoped features.

@agent-os/commands/shape-spec/shape-spec.md run this

text

Skip if requirements already clear.

#### Phase 2: Write Spec (Required)
Create detailed specification with implementation details.

@agent-os/commands/write-spec/write-spec.md run this

text

Output: Spec file in `@agent-os/specs/[feature-name]/`

#### Phase 3: Create Tasks (Required)
Break spec into prioritized, actionable checklist.

@agent-os/commands/create-tasks/create-tasks.md run this

text

#### Phase 4: Implement Tasks (Simple)
Direct implementation for straightforward features.

@agent-os/commands/implement-tasks/implement-tasks.md run this

text

#### Phase 5: Orchestrate Tasks (Complex)
Advanced orchestration with subagents for complex features.

@agent-os/commands/orchestrate-tasks/orchestrate-tasks.md run this

text

**Choose ONE**: implement-tasks OR orchestrate-tasks (not both).

---

# Bash Commands

**Installation:**
make install # Install deps with Poetry

text

**Development:**
poetry run prompt-manager --help # CLI help
poetry run prompt-manager <cmd> # Run command

text

**Quality Checks:**
make test # Run pytest
make lint # Ruff linting
make format # Ruff formatting
make typecheck # mypy type checking
make check # All checks (lint + types + tests)

text

**Pre-commit:**
pre-commit install # Install hooks
pre-commit run --all-files # Run manually

text

---

# Code Style

**Python Standards:**
- Follow PEP 8
- Max line length: 100 chars
- Type hints on all function signatures
- Google-style docstrings for public APIs

**Naming:**
- `snake_case` for functions, variables, modules
- `PascalCase` for classes
- `UPPER_CASE` for constants
- Descriptive names (no abbreviations unless obvious)

**Architecture:**
- Prefer composition over inheritance
- Keep functions focused (single responsibility)
- Dependency injection over globals
- Domain models in `models/`, logic in `services/`

---

# Testing Instructions

**TDD Workflow (MANDATORY):**

1. Write failing test first (in `tests/`)
2. Implement minimal code to pass test
3. Refactor while keeping tests green
4. Tests mirror source structure: `tests/test_X.py` for `src/X.py`

**Testing Practices:**
- Use pytest fixtures for setup/teardown
- Mock external dependencies (Git, filesystem, etc.)
- Test edge cases and error conditions
- Aim for >80% coverage on new code

**Running Tests:**
make test # All tests
poetry run pytest tests/test_X.py # Single file
poetry run pytest -k "test_name" # Specific test
poetry run pytest --cov # With coverage

text

---

# Workflow Guidelines

**Starting a Feature:**
1. Check roadmap (`@agent-os/product/roadmap.md`)
2. If not there, add it (see Protocol above)
3. Follow Agent OS workflow (shape → write → tasks → implement)
4. Use `/plan` mode for complex features

**During Development:**
- Commit frequently with conventional commits
- Run `make check` before pushing
- Update specs when requirements change
- Use `#` key to add notes to CLAUDE.md

**For Complex Features:**
- Create `plan.md` file with Spec, Plan, Tasks, Context sections
- Use planning mode: separate planning Claude from implementation Claude
- Keep checklist of tasks, mark as completed
- `/clear` context after completing major phases

**Repository Etiquette:**
- Branch naming: `feature/`, `fix/`, `refactor/`, `docs/`
- Squash commits before merging to main
- No direct commits to main
- Pull latest before starting work

---

# Agent OS Product Context

**Mission:** `@agent-os/product/mission.md`

**Roadmap:** `@agent-os/product/roadmap.md`
- **YOU MUST update this when adding features**
- Track status: Planned → In Progress → Completed

**Tech Stack:** `@agent-os/product/tech-stack.md`

**Standards:** `@agent-os/standards/`
- Auto-loaded by Agent OS commands
- Reference before implementation

**Specs:** `@agent-os/specs/`
- Each feature has dedicated directory
- Contains requirements, design, tasks

---

# Custom Commands

Create reusable workflows in `~/.claude/commands/`.

**Example: `/feature [description]`**
Guides through Agent OS workflow for new feature.

**Example: `/test [module]`**
Runs tests and coverage for specific module.

---

# Common Pitfalls

**DON'T:**
- Skip roadmap updates (MANDATORY)
- Implement features without specs
- Write code before tests (violates TDD)
- Commit without running `make check`
- Use `require()` syntax (use ES modules)
- Mutate function arguments
- Ignore type errors from mypy

**DO:**
- Update CLAUDE.md when you find repeated issues
- Use checklists for complex migrations
- Clear context (`/clear`) after major phases
- Destructure imports when possible
- Keep functions pure when possible
- Document non-obvious design decisions

---

# Quick Reference

| Developer Says | Your Response |
|----------------|---------------|
| "Add feature X" | Execute Protocol → Check roadmap → Guide Agent OS workflow |
| "I have an idea" | `shape-spec` command |
| "Implement Y" | "Spec ready? In roadmap?" |
| "Fix bug Z" | Assess severity → Add to roadmap if significant |
| "Refactor" | Check standards, update docs |

---

# Memory Management

**Claude Code Commands:**
/memory # Edit CLAUDE.md
/memory refresh # Reload context
/clear # Clear conversation (keep CLAUDE.md)
/init # Initialize CLAUDE.md
#note # Quick add to CLAUDE.md

text

**Context Best Practices:**
- Use `/clear` after 1-3 messages to prevent bloat
- Keep this file under 100 lines when possible (currently extended for Agent OS)
- Use subdirectory CLAUDE.md for module-specific context
- Turn off auto-compact in `/config` (prevents stale context)

---

**REMEMBER: Roadmap update is non-negotiable. Always verify spec exists before coding.**