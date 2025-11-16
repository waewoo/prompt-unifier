# Changelog

## 2025-11-16

### Recursive File Discovery for Deploy Command
- Implement recursive file discovery for prompts and rules in the `deploy` command, preserving subdirectory structure in target handlers, and ensuring no duplicate prompt/rule titles.

## 2025-11-15

### Tool Handler Implementation: Continue
- Implement a `ContinueToolHandler` that allows users to deploy prompts and rules from `prompt-manager` to the "Continue" AI assistant. This handler will be responsible for converting and copying files to the appropriate directories, as well as handling backups and deployment verification.

### Strategy Pattern Architecture for Tool Handlers
- Implement a flexible and extensible system that allows for the addition of new AI tool handlers with minimal changes to the core application, while ensuring robust error handling and the ability to enable/disable these handlers.

### Configurable Handler Base Paths
- Enable flexible deployment locations for AI coding assistant handlers through per-handler base path configuration via config.yaml and CLI options, replacing the current hardcoded Path.home() default with Path.cwd() to support project-local tool installations.

## 2025-11-12

### Security & Secrets Detection
- Implement comprehensive security scanning to prevent accidental commits of secrets (API keys, tokens, passwords) and detect security vulnerabilities in code and dependencies through automated pre-commit hooks and CI/CD pipeline integration.

### Rules/Context Files Support
- Extend the Prompt Manager CLI to fully support rules/context files alongside prompts, using the same YAML frontmatter + >>> separator format, with complete validation, listing, and filtering capabilities to provide a unified experience for managing both prompts and coding rules.

## 2025-11-11

### Git Integration & Repository Management
- Enable application projects to sync prompts and rules from a central Git repository by implementing init, sync, and status commands that manage a local .prompt-manager/ configuration directory with read-only synchronization.

## 2025-11-08

### Prompt Format Specification & Validation Engine
- Implement a robust validation engine that enforces standardized prompt format (YAML frontmatter + >>> separator) using Pydantic models, provides detailed error reporting with Rich-formatted output, and enables CI/CD integration through JSON output mode.

### Python Project Scaffold
- Establish a complete, production-ready Python project structure for the Prompt Manager CLI with Poetry dependency management, TDD testing infrastructure, linting/type checking, and CI/CD automation following modern best practices.
