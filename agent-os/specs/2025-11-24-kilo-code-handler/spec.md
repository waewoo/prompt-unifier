# Specification: Kilo Code Tool Handler

## Goal
Implement a complete tool handler for Kilo Code that deploys prompts and rules as pure Markdown files (without YAML frontmatter) to a flat directory structure, following the established ToolHandler protocol with full feature parity to the Continue handler.

## User Stories
- As a developer using Kilo Code, I want my prompts and rules deployed as pure Markdown files so they work natively with Kilo Code's expected format
- As a prompt library maintainer, I want directory-based file naming (`[directory]-[filename].md`) so I can organize source prompts in subdirectories while maintaining a flat deployment structure for maximum compatibility

## Specific Requirements

**Handler Implementation and Protocol Compliance**
- Implement `KiloCodeToolHandler` class conforming to the ToolHandler Protocol with all 7 required methods
- Define handler name as "kilocode" (lowercase, no hyphen)
- Set `KILO_CODE_DIR` constant to ".kilocode"
- Use `Path.cwd()` as default base_path for project-local installations
- Implement required attributes: `prompts_dir` and `rules_dir`
- Follow Continue handler's structure as reference implementation
- Ensure type hints on all method signatures
- Use Pydantic models for validation (PromptFrontmatter, RuleFrontmatter)

**Directory Structure and Deployment Targets**
- Create `.kilocode/` base directory at the configured base path
- Create two flat subdirectories: `workflows/` for prompts and `rules/` for rules
- Deploy prompts to `.kilocode/workflows/` (all invokable via slash-command `/`)
- Deploy rules to `.kilocode/rules/` (all passive, always active)
- Enforce flat structure with no nested subdirectories in output directories
- Auto-create directories if they don't exist with Rich console feedback
- Validate directory accessibility and write permissions

**File Naming with Directory Prefixes**
- Apply `[directory]-[filename].md` pattern to all deployed files
- Extract parent directory name from source file path relative to prompts/ or rules/
- Normalize directory names to kebab-case for prefixes
- For files without subdirectory: use default prefix `misc-` (e.g., `misc-explain.md`)
- For multi-level paths (e.g., `prompts/dev/commands/explain.md`): use closest directory to file (`commands-explain.md`)
- Preserve original filename after prefix (e.g., `commands-explain.md`, `standards-code-style.md`)
- Ensure file name uniqueness after applying prefix pattern
- Add `.md` extension if missing from source filename

**Content Transformation from YAML to Pure Markdown**
- Extract YAML frontmatter fields: `name`, `description`, and optional metadata
- Convert `name` field to Markdown H1 heading: `# Title`
- Convert `description` field to intro paragraphs immediately after title
- Format optional metadata as Markdown text line: `**Field:** value | **Field:** value`
- Include metadata fields if present: `category`, `tags`, `version`, `author`, `language`, `applies_to`
- Remove all YAML delimiters (`---` blocks) from output
- Preserve body content intact after YAML separator (`>>>` or after `---`)
- Maintain code blocks, formatting, examples from original content
- Output pure Markdown only with no YAML blocks

**Backup and Rollback Functionality**
- Create `.bak` backup files before overwriting existing files (following Continue pattern)
- Store backups with `.md.bak` extension in same directory
- Implement `rollback()` method to restore all backup files recursively
- Remove empty directories after restoration
- Handle missing backup files gracefully with warnings
- Use Rich console output for backup and rollback feedback

**Verification and Validation**
- Implement `verify_deployment_with_details()` method returning VerificationResult dataclass
- Validate all deployed files start with `# Title` (Markdown H1)
- Verify no YAML frontmatter blocks remain in output files
- Check UTF-8 encoding without BOM
- Validate file name uniqueness after prefix application
- Confirm flat structure maintenance (no subdirs in workflows/ or rules/)
- Use VerificationResult with fields: file_name, content_type, status, details
- Implement `aggregate_verification_results()` for summary statistics
- Implement `display_verification_report()` with Rich table formatting

**Deployment Status Tracking**
- Implement `get_deployment_status()` method with content hash comparison
- Return status strings: "synced", "outdated", "missing", "error"
- Use SHA-256 hashing to compare source and deployed content
- Track relative_path for subdirectory structure preservation in source
- Support source_filename parameter for custom naming

**Orphaned File Cleanup**
- Implement `clean_orphaned_files()` method accepting deployed filenames set
- Remove `.bak` backup files recursively using `BAK_GLOB_PATTERN`
- Remove orphaned `.md` files ONLY in root directories (not subdirectories)
- Preserve `.md` files in subdirectories for tag filter compatibility
- Return count of removed files
- Use Rich console output for cleanup feedback

## Visual Design
No visual assets provided for this specification.

## Existing Code to Leverage

**ContinueToolHandler - Primary Reference**
- Copy overall class structure with `__init__`, base_path, and directory setup
- Reuse `_backup_file()` method for backup creation logic
- Adapt `deploy()` method signature and deployment flow
- Copy `rollback()` implementation for backup restoration
- Reuse `_remove_empty_directories()` helper method
- Follow `clean_orphaned_files()` pattern for orphaned file cleanup with root-only `.md` removal
- Adapt `verify_deployment_with_details()` for Markdown validation instead of YAML
- Reuse `aggregate_verification_results()` and `display_verification_report()` methods
- Copy `get_deployment_status()` with content hash comparison logic
- Follow Rich console output patterns for user feedback

**ToolHandler Protocol**
- Implement all 7 required methods from protocol: `deploy()`, `get_status()`, `get_name()`, `rollback()`, `clean_orphaned_files()`, `get_deployment_status()`
- Declare `prompts_dir` and `rules_dir` attributes as Path objects
- Match method signatures exactly including optional parameters
- Use type hints matching protocol definitions

**VerificationResult Dataclass**
- Reuse existing dataclass definition from Continue handler
- Fields: file_name (str), content_type (str), status (str), details (str)
- Status values: "passed", "failed", "warning"

**Test Patterns from test_continue_handler.py**
- Follow pytest fixture patterns for handler instantiation
- Use tmp_path fixture for isolated test directories
- Create mock PromptFrontmatter and RuleFrontmatter fixtures
- Test each Protocol method with dedicated test cases
- Use parametrized tests for edge cases
- Mock file operations with unittest.mock where appropriate
- Achieve >95% test coverage following TDD pattern

**Constants and Registry Integration**
- Add `KILO_CODE_DIR = ".kilocode"` to `src/prompt_unifier/constants.py`
- Register handler in `src/prompt_unifier/handlers/registry.py`
- Update CLI commands.py to support "kilocode" as target handler option
- Follow existing pattern for handler instantiation in deploy command

## Out of Scope
- Modifying the ToolHandler Protocol interface or adding new required methods
- Changing the ToolHandlerRegistry implementation or registration pattern
- Implementing other tool handlers (Windsurf, Cursor, Aider) in this spec
- Creating a plugin system for dynamic handler loading at runtime
- Adding internationalization or localization support
- Building a GUI or web interface for handler configuration
- Supporting nested subdirectories in output (flat structure is required)
- Custom placeholder variable syntax transformation between tools
- Automatic migration of existing Kilo Code files to new format
- Integration with Kilo Code's native CLI or API (if any exists)
