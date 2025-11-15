# Project Brief

## Core Requirements
Prompt Manager is a CLI tool for centralizing, validating, and deploying AI prompts and coding rules across multiple tools (Continue, Cursor, Windsurf, Aider, Kilo Code). Key requirements:
- Git-based synchronization from central repositories (read-only).
- Standardized format: YAML frontmatter + >>> separator for prompts and rules.
- Validation engine with Pydantic models, error reporting (Rich/JSON).
- Extensible deployment via Strategy Pattern handlers.
- Centralized local storage (~/.prompt-manager/storage) shared across projects.
- CLI commands: init, sync, status, validate, list, deploy.
- Offline-capable, type-safe (mypy strict), TDD (>95% coverage).

## Goals
- Solve fragmented prompt management: scattered storage, no versioning/validation, manual sync, team collaboration barriers.
- Enable reproducible, standardized AI assistance workflows.
- Support team standardization of coding practices via rules.
- Ensure extensibility for new AI tools without core changes.

## Scope Boundaries
- CLI-only, no GUI/web/server.
- Local execution, no cloud dependencies.
- Read-only Git sync (no push/merge).
- Format validation only (no semantic content analysis).
- No built-in prompt editing (use external editors).

## Success Metrics
- Commands execute <2s for typical use (50 files).
- Zero format errors in team repositories after adoption.
- >90% user satisfaction for ease of setup/sync.
- Easy addition of new handlers (1-2 files, no core changes).

This brief shapes all memory bank files and serves as the source of truth for project scope. Update as requirements evolve.