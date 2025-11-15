# Architecture

## System Architecture
Prompt Manager follows a layered architecture designed for separation of concerns, testability, and extensibility:

- **CLI Layer**: User interface and command parsing using Typer. Handles input validation, option processing, and output formatting.
- **Core Layer**: Business logic including validation, Git operations, and deployment orchestration. Tool-agnostic and reusable.
- **Handler Layer**: Tool-specific implementations using Strategy Pattern. Each handler (e.g., ContinueToolHandler) manages deployment to a specific AI tool.
- **Model Layer**: Pydantic-based data models for prompts, rules, configuration, and validation results. Ensures type safety and validation.
- **Utility Layer**: Cross-cutting concerns like file scanning, YAML parsing, and formatting utilities.

The system is stateless and local-only, with no database or server components. Git serves as the external source of truth for prompts and rules.

## Source Code Paths
- `src/prompt_manager/cli/`: Typer commands (main.py, commands.py)
- `src/prompt_manager/core/`: Validation engine (validator.py, yaml_parser.py, separator.py, encoding.py, batch_validator.py)
- `src/prompt_manager/handlers/`: Tool handler implementations and registry (protocol.py, registry.py, continue_handler.py)
- `src/prompt_manager/models/`: Pydantic models (prompt.py, rule.py, git_config.py, validation.py)
- `src/prompt_manager/config/`: Configuration management (manager.py)
- `src/prompt_manager/git/`: Git operations (service.py)
- `src/prompt_manager/output/`: Output formatters (rich_formatter.py, json_formatter.py)
- `src/prompt_manager/utils/`: Utilities (file_scanner.py, formatting.py, excerpt.py)
- `tests/`: Comprehensive test suite mirroring source structure

## Key Technical Decisions
- **CLI-First Approach**: Pure terminal interface optimized for developers, scriptable, and CI/CD friendly. No GUI or web components.
- **Git as Source of Truth**: Read-only sync from central Git repository. No local modifications pushed back.
- **Centralized Storage**: Prompts and rules stored in `~/.prompt-manager/storage/` for sharing across projects. Project-specific config in `.prompt-manager/config.yaml`.
- **Standardized Format**: YAML frontmatter + `>>>` separator for both prompts and rules. Ensures consistency and validation.
- **Extensible Handlers**: Strategy Pattern with Python Protocols for adding new AI tools without core changes.
- **Type Safety**: 100% type hints with mypy strict mode. No `Any` types except where unavoidable.
- **Offline Capable**: All operations local after initial sync. No cloud dependencies.
- **Error Resilience**: Continue processing after individual file errors. Detailed reporting without crashing.

## Design Patterns in Use
- **Strategy Pattern**: For tool handlers. `ToolHandler` Protocol defines interface; concrete implementations (e.g., `ContinueToolHandler`) provide tool-specific logic. Registry enables dynamic selection.
- **Dependency Injection**: Handlers and services injected via constructor parameters. Enables mocking in tests.
- **Repository Pattern**: `GitService` abstracts Git operations. Future extensions could add local file system repositories.
- **Factory Pattern**: `ToolHandlerRegistry` creates and manages handler instances.
- **Observer Pattern**: Potential for future event system (e.g., post-deployment hooks), but not implemented yet.
- **Command Pattern**: Typer commands encapsulate CLI actions with clear separation.

## Component Relationships
```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│     CLI Layer   │───▶│    Core Layer    │───▶│   Handler Layer  │
│ (Typer Commands)│    │ (Validation, Git)│    │ (Tool Strategies)│
└─────────────────┘    └──────────────────┘    └──────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   Model Layer   │◄───│   Utility Layer  │◄───│   Config Layer   │
│ (Pydantic Models)│    │ (File Ops, YAML) │    │ (ConfigManager)  │
└─────────────────┘    └──────────────────┘    └──────────────────┘
```
- CLI invokes Core services, which use Models and Utilities.
- Core orchestrates Handlers for deployment.
- Config provides settings to all layers.
- GitService in Core interacts with external Git repositories.

## Critical Implementation Paths
1. **Sync Path**: CLI → ConfigManager → GitService → extract_prompts_dir() → shutil.copytree to storage.
2. **Validation Path**: CLI → BatchValidator → PromptValidator (encoding → separator → YAML → Pydantic) → RichFormatter/JSONFormatter.
3. **Deployment Path**: CLI → ToolHandlerRegistry → select_handlers() → handler.deploy() → backup/rollback if error.
4. **List/Status Path**: CLI → ContentLoader → filter/search → display via Rich tables.

All paths emphasize error handling, logging, and user-friendly feedback. Critical paths are covered by integration tests in `tests/integration/`.