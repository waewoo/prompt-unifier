# Product Roadmap

1. [x] Core CLI Framework & Project Structure — Set up Python project with Poetry, configure Typer/Click CLI framework with basic commands (init, validate, deploy, list, sync), implement Rich for terminal output, and establish project structure with proper packaging. `S`

2. [x] Prompt Format Specification & Validation Engine — Define and document the standardized prompt format (YAML frontmatter + >>> separator), implement Pydantic models for prompt structure, create validation logic to parse and verify prompt files, and provide detailed error messages for format violations. `M`

3. [x] Git Integration & Repository Management — Implement init command to create centralized prompt repository with .gitignore and structure, add sync command to pull prompts from Git remote, handle Git operations (clone, pull, status), and implement error handling for Git conflicts or network issues. `M`

3.5. [x] Centralized Storage Architecture — Refactor Git integration to use centralized storage directory (~/.prompt-manager/storage by default) instead of storing prompts/rules in project directory. Add storage_path field to config.yaml, support --storage-path flag in init and sync commands for custom storage locations, and ensure .prompt-manager/config.yaml remains local to each project while prompts/rules are stored centrally and shared across projects. `S`

3.6. [x] Rules Directory Synchronization — Add automatic synchronization of rules/ directory alongside prompts/ during sync operations. The rules/ directory is optional and allows teams to share coding standards, best practices, and guidelines. Update GitService to extract both prompts/ (required) and rules/ (optional), maintain backward compatibility, and update all documentation. `S`

3.7. [x] Security & Secrets Detection — Implement pre-commit hooks to prevent committing secrets (API keys, tokens, passwords) using tools like detect-secrets or gitleaks. Add AppSec security checks (dependency scanning, SAST, vulnerability detection) via pre-commit hooks and GitLab CI pipeline. Configure security scanning for Python dependencies (safety, pip-audit), add SAST with bandit or semgrep, implement secrets baseline for legitimate test fixtures, and create security policy documentation. Ensure all security checks run locally (pre-commit) and in CI/CD with appropriate failure thresholds. `M`

4. [x] Rules/Context Files Support — Extend system to support rules/context files alongside prompts using standard YAML frontmatter format (---  delimiters), create separate `rules/` directory structure parallel to `prompts/`, implement path-based type detection (files in rules/ are rules), reuse existing validation engine for rules files, and update validate command with --type flag to filter by content type (all/prompts/rules). `S`

5. [x] Strategy Pattern Architecture for Tool Handlers — Design and implement Python Protocol for ToolHandler interface, create abstract base handler with common deployment logic, establish handler registration system for extensibility, and document how to add new tool handlers. `S`

6. [x] Tool Handler Implementation: Continue — Build ToolHandler implementations for Continue (deploy to .continue/ directory), including file operations, path resolution, backup mechanisms, and deployment verification. Implemented ContinueToolHandler with comprehensive test coverage (97%), YAML frontmatter conversion, automatic backup/rollback, and full CLI integration. `M`

7. [x] Configurable Handler Base Paths — Add support for customizing tool handler base paths via config.yaml and CLI options. Allow users to specify custom deployment locations for each handler (e.g., deploy Continue to custom path instead of default ~/.continue/). Implement both config-based persistent configuration (handlers.continue.base_path in config.yaml) and CLI override option (--base-path flag). Support multiple configuration approaches: per-handler config in config.yaml, CLI override for one-time deployments, and maintain backward compatibility with default paths. Apply pattern to all existing and future handlers for consistency. Changed default base path from Path.home() to Path.cwd() for project-local tool installations. `S`

8. [~] Deploy Command with Multi-Tool Support — Implement deploy command that orchestrates deployment across all configured tools, supports selective deployment (--tool flag), provides progress indicators and deployment summaries, handles rollback on failures, and validates successful deployment. **PARTIALLY IMPLEMENTED:** Core deploy command working with Continue handler, supports --tags and --handlers flags, includes backup/rollback, Rich console output. **NEW:** Added recursive file discovery (glob("**/*.md")) for prompts and rules in subdirectories, subdirectory structure preservation during deployment, and duplicate title detection across all files. Remaining: Add other tool handlers (Windsurf, Cursor, Aider) to complete multi-tool support. `L`

9. [ ] List & Status Commands with Rich UI — Create list command showing all available prompts with metadata (name, description, tools, last modified), implement status command displaying deployment state per tool, add filtering/sorting options, and format output using Rich tables and syntax highlighting. `S`

10. [ ] Configuration Management System — Implement user configuration file (~/.prompt-manager/config.yaml) to store repository paths, enabled tools, deployment preferences, and validation rules. Support init-time configuration, runtime overrides via CLI flags, and config validation. `S`

11. [ ] Error Handling, Logging & User Feedback — Implement comprehensive error handling with user-friendly messages, add logging system for debugging (optional --verbose flag), create helpful suggestions for common errors, and ensure graceful degradation when tools are not installed. `S`

12. [ ] Documentation & Onboarding — Write comprehensive README with quickstart guide, create detailed CLI help text for all commands, document prompt format specification, provide examples of valid prompts, and create contributing guide for adding new tool handlers. `M`

13. [ ] Tool Handler Implementation: Kilo Code — Complete remaining tool handlers for Kilo Code following the established pattern, with full deployment logic, configuration file handling, and validation that prompts are correctly placed in each tool's expected location. `M`

14. [ ] Tool Handler Implementation: Windsurf, Cursor, Aider — Complete remaining tool handlers for Windsurf, Aider, Cursor following the established pattern, with full deployment logic, configuration file handling, and validation that prompts are correctly placed in each tool's expected location. `M`

> Notes
> - Order items by technical dependencies and product architecture
> - Each item should represent an end-to-end (frontend + backend) functional and testable feature
> - Items 1-4 establish foundation (CLI framework, validation engine, Git integration, rules support)
> - Items 5-7 build extensible tool handler system
> - Items 8-10 complete core user-facing features
> - Items 11-13 ensure production quality and usability
