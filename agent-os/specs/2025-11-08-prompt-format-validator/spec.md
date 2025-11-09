# Specification: Prompt Format Specification & Validation Engine

## Goal
Implement a robust validation engine that enforces standardized prompt format (YAML frontmatter + >>> separator) using Pydantic models, provides detailed error reporting with Rich-formatted output, and enables CI/CD integration through JSON output mode.

## User Stories
- As a developer, I want to validate my prompt files locally before committing so that I catch format errors early
- As a tech lead, I want to enforce team-wide prompt standards in CI/CD pipelines so that only valid prompts are merged
- As a DevOps engineer, I want machine-readable validation output so that I can integrate prompt validation into automated workflows

## Specific Requirements

**Prompt File Format Definition**
- Files must use `.md` extension and UTF-8 encoding with strict enforcement
- Structure consists of three parts: YAML frontmatter, `>>>` separator on its own line, and prompt content
- YAML frontmatter must be flat (no nested structures) with required fields `name` and `description`
- Optional fields include `version` (semantic versioning), `tags` (list of strings), and `author` (string)
- Exactly one `>>>` separator must appear on its own line with no surrounding whitespace
- Content after `>>>` is treated as opaque text (no validation) but cannot be empty

**Pydantic Validation Model**
- Create `PromptFrontmatter` Pydantic v2 model with strict field validation
- Implement custom validators for semantic versioning format using regex pattern
- Enforce non-empty string validation for `name` and `description` using `field_validator`
- Reject prohibited fields (e.g., `tools`) using `model_validator` with `mode='after'`
- Validate flat YAML structure by detecting nested dictionaries during parsing
- Generate detailed validation error messages with field names and constraint violations

**File Discovery and Scanning**
- Accept directory path as CLI argument and scan recursively for `.md` files using `pathlib.Path.rglob()`
- Support both absolute and relative directory paths with proper resolution
- Handle file system errors gracefully (permission denied, directory not found)
- Collect all files before validation to report total count upfront
- Continue processing remaining files even when individual files fail encoding check

**Multi-File Validation Orchestration**
- Validate each file independently and collect all errors/warnings into structured results
- Implement validation pipeline: encoding check, separator detection, YAML parsing, schema validation, content check
- Continue validation after errors to provide complete feedback across all files
- Track per-file status (passed, failed) and aggregate error/warning counts
- Generate summary report with total files, passed count, failed count, error count, warning count

**Error and Warning Classification**
- ERRORS (block deployment): Invalid UTF-8, missing required fields, multiple/missing separators, separator formatting issues, empty content, invalid YAML, nested structures, invalid semver, prohibited fields
- WARNINGS (do not block): Missing optional fields (`version`, `author`), empty `tags` list
- Assign unique error codes for each validation failure type (e.g., INVALID_ENCODING, MISSING_REQUIRED_FIELD, MULTIPLE_SEPARATORS)
- Include line numbers, code excerpts (3-line context), and actionable suggestions for each error
- Differentiate severity levels in both CLI and JSON output formats

**Rich Terminal Output Format**
- Display validation header with directory path using Rich console
- Show per-file results with checkmarks (passed) or X marks (failed) using Rich symbols
- Color errors in red and warnings in yellow using Rich markup
- Include line numbers in square brackets before error messages
- Display code excerpts in indented blocks with syntax highlighting
- Generate summary table with progress bar and final status message
- Support `--verbose` flag to show detailed validation progress including skipped files

**JSON Output Format**
- Provide `--json` flag to output structured JSON instead of Rich terminal format
- Structure: top-level object with `summary` (metadata) and `results` (array of file validations)
- Each result contains: `file` (path), `status` (passed/failed), `errors` (array), `warnings` (array)
- Each error/warning includes: `line` (number or null), `severity`, `code`, `message`, `excerpt`, `suggestion`
- Ensure JSON is pretty-printed for readability and parseable by CI/CD tools
- Exit with code 0 for success (warnings allowed), 1 for validation failures

**CLI Command Interface**
- Implement `validate` command in Typer CLI accepting `directory` as required positional argument
- Add `--json` boolean flag for JSON output mode (default: False, CLI output)
- Add `--verbose` boolean flag for detailed progress logging
- Display help text with command description, argument/option details, and usage examples
- Handle invalid directory paths with user-friendly error message before scanning

## Visual Design
No visual assets provided.

## Existing Code to Leverage

**Project Structure from 2025-11-08-python-project-scaffold**
- Use existing `src/prompt_manager/models/` directory for Pydantic models
- Use existing `src/prompt_manager/core/` directory for validation business logic
- Use existing `src/prompt_manager/cli/` directory for Typer command implementation
- Use existing `src/prompt_manager/utils/` directory for file scanning and parsing utilities
- Follow established testing pattern with `tests/` directory mirroring source structure

**pyproject.toml Configuration**
- Pydantic v2 (>=2.5.0) already configured for data validation with modern API
- PyYAML (>=6.0.1) available for frontmatter parsing
- Rich (>=13.7.0) available for terminal formatting and colored output
- Typer (>=0.12.0) configured for CLI framework with automatic help generation
- pytest with coverage requirement (>85%) enforced via tool.coverage.report
- Ruff and mypy configured with strict type checking and linting rules

**Established Development Workflow**
- Follow TDD methodology by writing tests before implementation code
- Use Makefile targets: `make test` for pytest, `make lint` for Ruff, `make typecheck` for mypy
- Ensure 100% type hints on public APIs with mypy strict mode
- Use pathlib instead of os.path for cross-platform compatibility
- Implement proper error handling with explicit exception types (no bare `except:`)

## Out of Scope
- Strict mode validation (deferred to future enhancement)
- Custom validation rules via user configuration files
- Auto-fix suggestions that modify files directly
- Watch mode for continuous validation on file changes
- Integration with pre-commit hooks as Git hook (use CLI directly instead)
- Semantic validation of prompt content (only format validation)
- Bidirectional conversion from other prompt formats
- Support for file encodings other than UTF-8
- Nested directory structure preservation in output
- Validation of prompt effectiveness or quality metrics
