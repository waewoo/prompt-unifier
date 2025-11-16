# Instructions for Gemini Assistant

**STOP. READ THIS FIRST.**

You are working on the `prompt-manager` project. You MUST follow this protocol for ALL feature requests.

## Mandatory Feature Addition Protocol

When the developer asks to add ANY new feature, execute this checklist IN ORDER:

### STEP 1: Roadmap Update (MANDATORY)
- [ ] Ask: "Is this feature in `@agent-os/product/roadmap.md`?"
- [ ] If NO: "I will add it to the roadmap now. Confirming..."
- [ ] Add to roadmap with:
  - Feature name
  - Description (1-2 sentences)  
  - Priority: High/Medium/Low
  - Status: Planned
  - Target milestone
  - Dependencies (if any)
- [ ] Show the roadmap entry for approval

### STEP 2: Agent OS Workflow (MANDATORY)
- [ ] Ask: "Do you have a spec for this in `@agent-os/specs/`?"
- [ ] If NO, guide through Agent OS phases:
  - **Vague idea?** → `@agent-os/commands/shape-spec/shape-spec.md run this`
  - **Clear requirements?** → `@agent-os/commands/write-spec/write-spec.md run this`
- [ ] If YES, confirm phase:
  - **Need tasks?** → `@agent-os/commands/create-tasks/create-tasks.md run this`
  - **Ready to code?** → `@agent-os/commands/implement-tasks/implement-tasks.md run this`

### STEP 3: Implementation
- [ ] Only proceed after STEP 1 & 2 complete
- [ ] Follow standards in `@agent-os/standards/`
- [ ] Apply TDD practices from project conventions

### STEP 4: Post-Implementation
- [ ] Update roadmap status (Planned → In Progress → Completed)
- [ ] Verify spec documentation is current
- [ ] Run `make check` before committing

**DO NOT skip steps. DO NOT implement without roadmap entry and spec.**

---

# Project Overview

`prompt-manager` is a Python CLI tool for managing AI prompt templates and coding rules. It uses YAML frontmatter for prompts/rules, supporting version control, validation, and deployment workflows.

## Tech Stack

- **Python**: 3.11+
- **CLI**: Typer
- **Dependencies**: Poetry
- **Validation**: Pydantic
- **YAML**: PyYAML
- **Git**: GitPython
- **Testing**: pytest
- **Linting**: Ruff
- **Type Checking**: mypy

## Project Structure

prompt-manager/
├── src/prompt_manager/ # Main source code
│ ├── cli/ # CLI commands
│ ├── models/ # Pydantic models
│ ├── services/ # Business logic
│ └── utils/ # Utilities
├── tests/ # Test suite
├── agent-os/ # Agent OS configuration
│ ├── product/ # Product con│ │ ├── mission.md
│ │ ├── roadmap.md
│ │ └── tech-stack.md
│ ├── standards/ # Development standards
│ ├── specs/ # Feature specs
│ └── commands/ # Agent OS commands
├── pyproject.toml
├── Makefile
└── GEMINI.md # This file


---

# Development Methodology: Agent OS

This project follows **Agent OS v2.x** spec-driven development methodology.

## 3-Layer Context System

- **Standards** (`@agent-os/standards/`): Coding standards and best practices
- **Product** (`@agent-os/product/`): Vision, roadmap, tech stack
- **Specs** (`@agent-os/specs/`): Feature specifications

Learn more: [buildermethods.com/agent-os](https://buildermethods.com/agent-os)

## Agent OS Workflow (6 Phases)

### Phase 0: Plan Product (Run Once)

Initialize project strategy and architecture.

@agent-os/commands/plan-product/plan-product.md run this


**When**: Project start or Agent OS installation

### Repeatable Feature Cycle (Phases 1-5)

#### Phase 1: Shape Spec (Optional)

Transform vague ideas into clear requirements.

@agent-os/commands/shape-spec/shape-spec.md run this


**Skip if**: Requirements already clear

#### Phase 2: Write Spec (Required)

Create detailed feature specification.

@agent-os/commands/write-spec/write-spec.md run this


**Output**: Spec in `@agent-os/specs/[feature-name]/`

#### Phase 3: Create Tasks (Required)

Break spec into actionable task list.

@agent-os/commands/create-tasks/create-tasks.md run this


**Output**: Prioritized, grouped tasks

#### Phase 4: Implement Tasks (Choose One)

**Simple implementation:**
@agent-os/commands/implement-tasks/implement-tasks.md run this


**OR**

**Complex orchestration (Claude Code only):**
@agent-os/commands/orchestrate-tasks/orchestrate-tasks.md run this


**Important**: Use implement-tasks OR orchestrate-tasks, not both.

---

# Building and Running

## Installation

make install


## CLI Usage

poetry run prompt-manager --help
poetry run prompt-manager <command>


## Development Commands

| Command | Purpose |
|---------|---------|
| `make test` | Run test suite |
| `make lint` | Check linting |
| `make format` | Format code |
| `make typecheck` | Run mypy |
| `make check` | All checks (lint + types + tests) |

---

# Development Conventions

## Code Style

- Follow PEP 8
- Type hints required on all functions
- Docstrings for public APIs (Google style)
- Max line length: 100 characters

## Testing Strategy (TDD)

1. Write failing test first
2. Implement minimal code to pass
3. Refactor while keeping tests green
4. Tests in `tests/` mirror `src/` structure

## Dependency Management

- Poetry for all dependencies
- Add: `poetry add <package>`
- Dev deps: `poetry add --group dev <package>`
- Lock file committed to repo

## Pre-commit Hooks

Configured in `.pre-commit-config.yaml`:
- Ruff linting and formatting
- mypy type checking
- detect-secrets security scanning
- bandit security analysis

Install hooks: `pre-commit install`

## Commit Conventions

- Use conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- Keep commits atomic and focused
- Reference issues/specs in commit messages

---

# Product Context (Agent OS)

## Mission
`@agent-os/product/mission.md`

## Roadmap
`@agent-os/product/roadmap.md`

**YOU MUST update this file when adding features (see Protocol above).**

## Tech Stack
`@agent-os/product/tech-stack.md`

## Standards
`@agent-os/standards/`

Auto-loaded by Agent OS commands.

## Specs
`@agent-os/specs/`

Each feature has its own directory with spec files.

---

# Quick Reference

## When Developer Says...

| Request | Your Response |
|---------|---------------|
| "Add a feature" | Execute Mandatory Protocol → Check roadmap → Guide through Agent OS phases |
| "I have an idea" | `@agent-os/commands/shape-spec/shape-spec.md` |
| "Implement X" | "Do we have a spec? Is it in the roadmap?" |
| "Fix bug" | Check if in roadmap, create spec if significant |
| "Refactor" | Verify against standards, update docs |

## Memory Commands

/memory refresh # Reload this file
/memory show # Display loaded con/memory list # Show all GEMINI.md files


---

**Remember**: Roadmap update is MANDATORY before any implementation. No exceptions.