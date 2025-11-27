# Product Roadmap

1. [x] Core CLI Framework & Project Structure — Set up Python project with Poetry, configure Typer/Click CLI framework with basic commands (init, validate, deploy, list, sync), implement Rich for terminal output, and establish project structure with proper packaging. `S`

2. [x] Prompt Format Specification & Validation Engine — Define and document the standardized prompt format (YAML frontmatter + >>> separator), implement Pydantic models for prompt structure, create validation logic to parse and verify prompt files, and provide detailed error messages for format violations. `M`

3. [x] Git Integration & Repository Management — Implement init command to create centralized prompt repository with .gitignore and structure, add sync command to pull prompts from Git remote, handle Git operations (clone, pull, status), and implement error handling for Git conflicts or network issues. `M`

3.5. [x] Centralized Storage Architecture — Refactor Git integration to use centralized storage directory (~/.prompt-unifier/storage by default) instead of storing prompts/rules in project directory. Add storage_path field to config.yaml, support --storage-path flag in init and sync commands for custom storage locations, and ensure .prompt-unifier/config.yaml remains local to each project while prompts/rules are stored centrally and shared across projects. `S`

3.6. [x] Rules Directory Synchronization — Add automatic synchronization of rules/ directory alongside prompts/ during sync operations. The rules/ directory is optional and allows teams to share coding standards, best practices, and guidelines. Update GitService to extract both prompts/ (required) and rules/ (optional), maintain backward compatibility, and update all documentation. `S`

3.7. [x] Security & Secrets Detection — Implement pre-commit hooks to prevent committing secrets (API keys, tokens, passwords) using tools like detect-secrets or gitleaks. Add AppSec security checks (dependency scanning, SAST, vulnerability detection) via pre-commit hooks and GitLab CI pipeline. Configure security scanning for Python dependencies (safety, pip-audit), add SAST with bandit or semgrep, implement secrets baseline for legitimate test fixtures, and create security policy documentation. Ensure all security checks run locally (pre-commit) and in CI/CD with appropriate failure thresholds. `M`

4. [x] Rules/Context Files Support — Extend system to support rules/context files alongside prompts using standard YAML frontmatter format (---  delimiters), create separate `rules/` directory structure parallel to `prompts/`, implement path-based type detection (files in rules/ are rules), reuse existing validation engine for rules files, and update validate command with --type flag to filter by content type (all/prompts/rules). `S`

5. [x] Strategy Pattern Architecture for Tool Handlers — Design and implement Python Protocol for ToolHandler interface, create abstract base handler with common deployment logic, establish handler registration system for extensibility, and document how to add new tool handlers. `S`

6. [x] Tool Handler Implementation: Continue — Build ToolHandler implementations for Continue (deploy to .continue/ directory), including file operations, path resolution, backup mechanisms, and deployment verification. Implemented ContinueToolHandler with comprehensive test coverage (97%), YAML frontmatter conversion, automatic backup/rollback, and full CLI integration. `M`

7. [x] Configurable Handler Base Paths — Add support for customizing tool handler base paths via config.yaml and CLI options. Allow users to specify custom deployment locations for each handler (e.g., deploy Continue to custom path instead of default ~/.continue/). Implement both config-based persistent configuration (handlers.continue.base_path in config.yaml) and CLI override option (--base-path flag). Support multiple configuration approaches: per-handler config in config.yaml, CLI override for one-time deployments, and maintain backward compatibility with default paths. Apply pattern to all existing and future handlers for consistency. Changed default base path from Path.home() to Path.cwd() for project-local tool installations. `S`

8. [x] Deploy Command with Multi-Tool Support — Implement deploy command that orchestrates deployment across all configured tools, supports selective deployment (--tool flag), provides progress indicators and deployment summaries, handles rollback on failures, and validates successful deployment. Core deploy command working with Continue handler, supports --tags and --handlers flags, includes backup/rollback, Rich console output, recursive file discovery, subdirectory structure preservation, duplicate title detection and extensive tests for subdirectory support. `L`

9. [x] GitLab Release Automation — Implement automated Git tagging and GitLab Release creation in the CI/CD pipeline, including version bumping, changelog generation, and distribution package (sdist, wheel) publication. `High`

10. [x] Multiple Source Repository Support — Allow users to specify multiple source repositories using multiple --repo flags or a list in config.yaml. Enable prompts/rules to be synchronized from multiple Git repositories simultaneously, merge content from all sources into the centralized storage, handle conflicts when multiple repos contain files with same paths, and provide clear feedback about which content came from which repository. Support both CLI (--repo URL1 --repo URL2) and configuration-based (repos: [URL1, URL2] in config.yaml) approaches. `M`

11. [x] List & Status Commands with Rich UI — Create list command showing all available prompts with metadata (name, description, tools, last modified), implement status command displaying deployment state per tool, add filtering/sorting options, and format output using Rich tables and syntax highlighting. Implemented `RichTableFormatter` for formatted output, `list` command with tag filtering and sorting, `status` command with deployment status tracking using SHA-256 content hashing. All feature-specific tests passing (12/12). **Note**: Some pre-existing tests fail on Windows due to path separator and encoding issues (48 failures), but feature is fully functional and cross-platform compatible. `S`

11.5. [x] Windows Test Compatibility Fixes — Fix 48 pre-existing test failures on Windows related to path separators (`\` vs `/`), Unicode encoding (cp1252 vs UTF-8), symlink permissions, and file locking issues. Tests pass on Linux but fail on Windows. Normalize path comparisons using `Path.as_posix()`, force UTF-8 encoding in all file operations, skip symlink tests on Windows, and fix backup/rollback file locking issues. This will ensure `make check` passes on both Windows and Linux. `S`

12. [x] Configuration Management System — Implement user configuration file (~/.prompt-unifier/config.yaml) to store repository paths, enabled tools, deployment preferences, and validation rules. Support init-time configuration, runtime overrides via CLI flags, and config validation.

13. [x] Error Handling, Logging & User Feedback — `S`
    - [x] Implement comprehensive error handling with user-friendly messages and graceful degradation.
    - [x] Add a centralized logging system and a global --verbose flag for debugging.

14. [x] Documentation & Onboarding — `M`
    - [x] Create comprehensive user-facing documentation (README, CLI help, examples).
    - [x] Write a guide for adding new tool handlers.

15. [x] Tool Handler Implementation: Kilo Code — Complete tool handler for Kilo Code following the established pattern, with full deployment logic, configuration file handling, and validation that prompts are correctly placed in the tool's expected location. `M`

16. [ ] Tool Handler Implementation: Windsurf — Complete tool handler for Windsurf following the established pattern, with full deployment logic, configuration file handling, and validation that prompts are correctly placed in the tool's expected location. `M`

17. [ ] Tool Handler Implementation: Cursor — Complete tool handler for Cursor following the established pattern, with full deployment logic, configuration file handling, and validation that prompts are correctly placed in the tool's expected location. `M`

18. [ ] Tool Handler Implementation: Aider — Complete tool handler for Aider following the established pattern, with full deployment logic, configuration file handling, and validation that prompts are correctly placed in the tool's expected location. `M`

19. [ ] Import/Migration from Existing Tools — Implement import command to migrate existing prompts from AI tools (Continue, Cursor, Windsurf, Aider, Kilo Code) into the unified format. Auto-detect tool configurations, convert to YAML frontmatter format, preserve metadata where possible, and handle duplicates. Critical for user adoption by eliminating manual migration effort. `M`

20. [ ] Diff/Preview Before Deployment — Add diff command to visualize changes between centralized storage and currently deployed files before running deploy. Show added, modified, and deleted files with color-coded diff output. Support --tool flag for tool-specific diffs and integrate with deploy command via --preview flag. `S`

21. [ ] Variables/Placeholders in Prompts — Support template variables (e.g., `{{project_name}}`, `{{language}}`, `{{author}}`) in prompt content that are resolved at deployment time. Variables can be defined in config.yaml (global), per-project config (local), or via CLI flags. Enable prompt reuse across projects with context-specific values. `M`

22. [ ] Semantic Validation of Prompts — Extend validation beyond YAML format to include semantic checks: excessive prompt length warnings, estimated token count, detection of problematic patterns (e.g., conflicting instructions, deprecated syntax), and best practice suggestions. Provide actionable feedback with severity levels (error, warning, info). `M`

23. [x] SCAFF Method Validation — Implement validation to ensure prompts follow the SCAFF methodology (Specific, Contextual, Actionable, Formatted, Focused). Add SCAFF compliance checker that analyzes prompt structure and content, detects missing SCAFF components, provides suggestions for improvement, and reports SCAFF compliance score. Support --scaff flag in validate command to enable SCAFF-specific validation. Integrate with semantic validation to provide comprehensive prompt quality assessment. `M`

> Notes
> - Order items by technical dependencies and product architecture
> - Each item should represent an end-to-end (frontend + backend) functional and testable feature
> - Items 1-4 establish foundation (CLI framework, validation engine, Git integration, rules support)
> - Items 5-7 build extensible tool handler system
> - Items 8-10 complete core user-facing features
> - Items 11-14 ensure production quality and usability
> - Items 15-18 expand the tool ecosystem
