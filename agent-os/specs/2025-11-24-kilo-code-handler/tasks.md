# Task Breakdown: Kilo Code Tool Handler

## Overview
Total Tasks: 6 Task Groups
Total Estimated Time: 2 weeks (M effort)

## Task List

### Core Handler Implementation

#### Task Group 1: Handler Class and Protocol Compliance
**Dependencies:** None

- [x] 1.0 Complete core handler implementation
  - [x] 1.1 Write 2-8 focused tests for KiloCodeToolHandler class
    - Limit to 2-8 highly focused tests maximum
    - Test only critical behaviors: initialization, directory creation, Protocol compliance
    - Skip exhaustive coverage of all edge cases
    - Tests: handler instantiation, base_path handling, directory attribute types, Protocol method existence
  - [x] 1.2 Create `src/prompt_unifier/handlers/kilo_code_handler.py`
    - Implement `KiloCodeToolHandler` class conforming to ToolHandler Protocol
    - Define handler name as "kilocode" (lowercase, no hyphen)
    - Use `Path.cwd()` as default base_path for project-local installations
    - Declare required attributes: `prompts_dir` (Path to `.kilocode/workflows/`) and `rules_dir` (Path to `.kilocode/rules/`)
    - Reference structure: `src/prompt_unifier/handlers/continue_handler.py`
  - [x] 1.3 Implement `__init__()` method
    - Accept `base_path: Optional[Path] = None` parameter (defaults to `Path.cwd()`)
    - Initialize `prompts_dir = base_path / KILO_CODE_DIR / "workflows"`
    - Initialize `rules_dir = base_path / KILO_CODE_DIR / "rules"`
    - Store base_path for use in other methods
    - Follow Continue handler's initialization pattern
  - [x] 1.4 Implement `get_name()` method
    - Return string: "kilocode"
    - Match ToolHandler Protocol signature
  - [x] 1.5 Implement `get_status()` method
    - Check if `.kilocode/workflows/` and `.kilocode/rules/` directories exist
    - Return appropriate status message with Rich formatting
    - Follow Continue handler's status check pattern
  - [x] 1.6 Add type hints to all method signatures
    - Use Protocol-matching signatures exactly
    - Include Optional, Path, List types as needed
    - Ensure mypy compliance
  - [x] 1.7 Ensure core handler tests pass
    - Run ONLY the 2-8 tests written in 1.1
    - Verify handler instantiation works correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 1.1 pass
- Handler class implements ToolHandler Protocol
- Handler returns correct name "kilocode"
- Handler initializes with correct directory paths
- All methods have proper type hints

---

### Content Transformation Logic

#### Task Group 2: YAML to Pure Markdown Conversion
**Dependencies:** Task Group 1

- [x] 2.0 Complete content transformation logic
  - [x] 2.1 Write 2-8 focused tests for content transformation
    - Limit to 2-8 highly focused tests maximum
    - Test only critical transformations: YAML extraction, H1 title generation, metadata formatting, body preservation
    - Skip exhaustive testing of all metadata field combinations
    - Tests: basic transformation, metadata inclusion, no-metadata case, body content preservation
  - [x] 2.2 Implement `_extract_yaml_frontmatter()` helper method
    - Parse YAML block between `---` delimiters
    - Extract fields: `name`, `description`, optional metadata (`category`, `tags`, `version`, `author`, `language`, `applies_to`)
    - Return dict with extracted fields
    - Handle missing or malformed YAML gracefully
  - [x] 2.3 Implement `_convert_to_pure_markdown()` helper method
    - Convert `name` field to Markdown H1: `# Title`
    - Add `description` as paragraphs after title (with blank line)
    - Format optional metadata as: `**Field:** value | **Field:** value`
    - Include metadata line only if metadata fields are present
    - Remove all YAML delimiters (`---` blocks)
    - Preserve body content after YAML separator (`>>>` or after `---`)
    - Maintain code blocks, formatting, examples from original
    - Return pure Markdown string with no YAML blocks
  - [x] 2.4 Implement `_generate_directory_prefix()` helper method
    - Extract parent directory name from source file path
    - Get directory relative to `prompts/` or `rules/` base
    - For multi-level paths (e.g., `dev/commands/explain.md`), use closest directory to file (`commands`)
    - Normalize directory name to kebab-case
    - Return default prefix `misc-` for root files (no subdirectory)
    - Ensure prefix compatibility with flat structure
  - [x] 2.5 Implement `_apply_file_naming_pattern()` helper method
    - Apply `[directory]-[filename].md` pattern
    - Use directory prefix from `_generate_directory_prefix()`
    - Preserve original filename after prefix
    - Add `.md` extension if missing
    - Validate filename uniqueness in target directory
    - Examples: `commands-explain.md`, `standards-code-style.md`, `misc-explain.md`
  - [x] 2.6 Ensure content transformation tests pass
    - Run ONLY the 2-8 tests written in 2.1
    - Verify YAML to Markdown conversion works correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 2.1 pass
- YAML frontmatter correctly extracted
- Pure Markdown output with H1 title and description
- Metadata formatted as Markdown text (when present)
- No YAML blocks in output
- Body content preserved intact
- Directory-prefixed file naming works correctly

---

### File Operations and Deployment

#### Task Group 3: Deploy, Backup, and Rollback
**Dependencies:** Task Groups 1, 2

- [x] 3.0 Complete file operations and deployment
  - [x] 3.1 Write 2-8 focused tests for deployment operations
    - Limit to 2-8 highly focused tests maximum
    - Test only critical operations: deploy, backup creation, rollback, directory creation
    - Skip exhaustive testing of all file operation edge cases
    - Tests: deploy creates files, backup before overwrite, rollback restores, empty dir cleanup
  - [x] 3.2 Implement `deploy()` method signature
    - Parameters: `content: str`, `content_type: str`, `relative_path: str = ""`, `source_filename: Optional[str] = None`
    - Return deployed file path as Path
    - Match ToolHandler Protocol signature exactly
  - [x] 3.3 Implement deployment logic in `deploy()` method
    - Determine target directory: `workflows/` for prompts, `rules/` for rules
    - Auto-create directories if they don't exist with Rich console feedback
    - Transform content using `_convert_to_pure_markdown()`
    - Apply file naming pattern using `_apply_file_naming_pattern()`
    - Backup existing file if present (call `_backup_file()`)
    - Write pure Markdown content to target file
    - Validate write permissions and handle errors
    - Return deployed file path
  - [x] 3.4 Implement `_backup_file()` helper method
    - Create `.md.bak` backup of existing file before overwrite
    - Store backup in same directory as original
    - Follow Continue handler's backup pattern
    - Use Rich console output for backup feedback
  - [x] 3.5 Implement `rollback()` method
    - Find all `.md.bak` files recursively in `.kilocode/` directory
    - Restore each backup file to original `.md` file
    - Remove backup files after restoration
    - Call `_remove_empty_directories()` after restoration
    - Handle missing backup files gracefully with warnings
    - Use Rich console output for rollback feedback
    - Follow Continue handler's rollback implementation
  - [x] 3.6 Implement `_remove_empty_directories()` helper method
    - Remove empty directories recursively
    - Preserve directories that contain files
    - Reuse Continue handler's implementation
  - [x] 3.7 Ensure file operations tests pass
    - Run ONLY the 2-8 tests written in 3.1
    - Verify deploy, backup, and rollback work correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 3.1 pass
- `deploy()` method creates files in correct directories
- Backup files created before overwriting
- `rollback()` method restores all backups
- Empty directories cleaned up after rollback
- Rich console feedback provided

---

### Verification and Status Tracking

#### Task Group 4: Deployment Verification and Status
**Dependencies:** Task Groups 1, 2, 3

- [x] 4.0 Complete verification and status tracking
  - [x] 4.1 Write 2-8 focused tests for verification
    - Limit to 2-8 highly focused tests maximum
    - Test only critical verification: VerificationResult creation, status comparison, report generation
    - Skip exhaustive testing of all validation scenarios
    - Tests: verification with valid file, verification with invalid format, status hash comparison, aggregate results
  - [x] 4.2 Import/reuse `VerificationResult` dataclass
    - Use existing dataclass from Continue handler
    - Fields: `file_name: str`, `content_type: str`, `status: str`, `details: str`
    - Status values: "passed", "failed", "warning"
  - [x] 4.3 Implement `verify_deployment_with_details()` method
    - Accept deployed file path as parameter
    - Read deployed file content
    - Validate file starts with `# Title` (Markdown H1)
    - Verify no YAML frontmatter blocks remain (`---` delimiters)
    - Check UTF-8 encoding without BOM
    - Validate file is in flat structure (no subdirs in workflows/ or rules/)
    - Return VerificationResult with status and details
    - Status "passed" if all validations pass, "failed" otherwise
  - [x] 4.4 Implement `aggregate_verification_results()` method
    - Accept list of VerificationResult objects
    - Calculate summary statistics: total, passed, failed, warnings
    - Return aggregated results as dict
    - Reuse Continue handler's aggregation logic
  - [x] 4.5 Implement `display_verification_report()` method
    - Accept list of VerificationResult objects
    - Create Rich Table with columns: File, Type, Status, Details
    - Display aggregated statistics
    - Follow Continue handler's Rich table formatting pattern
  - [x] 4.6 Implement `get_deployment_status()` method
    - Parameters: `source_content: str`, `deployed_file_path: Path`
    - Compare content using SHA-256 hash
    - Transform source content to pure Markdown before comparison
    - Return status string: "synced", "outdated", "missing", "error"
    - Follow Continue handler's status comparison logic
  - [x] 4.7 Ensure verification tests pass
    - Run ONLY the 2-8 tests written in 4.1
    - Verify validation logic works correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 4.1 pass
- `verify_deployment_with_details()` validates pure Markdown format
- No YAML frontmatter detected in valid files
- `get_deployment_status()` accurately compares content hashes
- Verification report displays with Rich table formatting
- Aggregated results show correct statistics

---

### Orphaned File Cleanup

#### Task Group 5: Orphaned File Removal
**Dependencies:** Task Groups 1, 3

- [x] 5.0 Complete orphaned file cleanup
  - [x] 5.1 Write 2-8 focused tests for cleanup operations
    - Limit to 2-8 highly focused tests maximum
    - Test only critical cleanup: `.bak` removal, orphaned `.md` removal in root, subdirectory preservation
    - Skip exhaustive testing of all file patterns
    - Tests: removes orphaned .md files, removes .bak files, preserves subdirectory .md files, returns count
  - [x] 5.2 Implement `clean_orphaned_files()` method signature
    - Parameter: `deployed_filenames: Set[str]`
    - Return count of removed files as int
    - Match ToolHandler Protocol signature
  - [x] 5.3 Implement cleanup logic for `.bak` files
    - Find all `.bak` files recursively using `BAK_GLOB_PATTERN` (likely `**/*.bak`)
    - Remove all backup files found
    - Count removed `.bak` files
    - Use Rich console output for feedback
  - [x] 5.4 Implement cleanup logic for orphaned `.md` files
    - Find `.md` files ONLY in root directories (`workflows/` and `rules/`)
    - Do NOT remove `.md` files in subdirectories (preserve for tag filter compatibility)
    - Compare against `deployed_filenames` set
    - Remove `.md` files not in deployed set
    - Count removed orphaned `.md` files
    - Follow Continue handler's orphaned file pattern
  - [x] 5.5 Return total count of removed files
    - Sum `.bak` removal count and orphaned `.md` removal count
    - Display total in Rich console output
  - [x] 5.6 Ensure cleanup tests pass
    - Run ONLY the 2-8 tests written in 5.1
    - Verify orphaned files removed correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 5.1 pass
- All `.bak` files removed recursively
- Orphaned `.md` files removed ONLY from root directories
- `.md` files in subdirectories preserved
- Correct count of removed files returned
- Rich console feedback provided

---

### Integration and Constants

#### Task Group 6: Registry, Constants, and CLI Integration
**Dependencies:** Task Groups 1-5

- [x] 6.0 Complete integration with existing system
  - [x] 6.1 Write 2-8 focused tests for integration
    - Limit to 2-8 highly focused tests maximum
    - Test only critical integration: handler registration, constant access, CLI instantiation
    - Skip exhaustive testing of all integration scenarios
    - Tests: handler registered in registry, constant defined correctly, CLI can instantiate handler
  - [x] 6.2 Add `KILO_CODE_DIR` constant
    - Add to `src/prompt_unifier/constants.py`
    - Value: `".kilocode"`
    - Follow existing constant naming conventions
  - [x] 6.3 Register handler in registry
    - Update `src/prompt_unifier/handlers/registry.py`
    - Import `KiloCodeToolHandler` class
    - Register handler with name "kilocode"
    - Follow existing registration pattern for Continue handler
  - [x] 6.4 Update CLI commands for Kilo Code support
    - Update `src/prompt_unifier/cli/commands.py`
    - Add "kilocode" as valid target handler option
    - Support handler instantiation in deploy command
    - Follow existing pattern for Continue handler
  - [x] 6.5 Update `__init__.py` exports if needed
    - Export `KiloCodeToolHandler` from `src/prompt_unifier/handlers/__init__.py`
    - Follow existing export pattern
  - [x] 6.6 Ensure integration tests pass
    - Run ONLY the 2-8 tests written in 6.1
    - Verify handler integrates correctly with system
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 6.1 pass
- `KILO_CODE_DIR` constant accessible from constants module
- Handler registered in `ToolHandlerRegistry`
- CLI commands support "kilocode" target
- Handler can be instantiated via CLI
- All exports properly configured

---

### Testing and Quality Assurance

#### Task Group 7: Test Review & Gap Analysis
**Dependencies:** Task Groups 1-6

- [x] 7.0 Review existing tests and fill critical gaps only
  - [x] 7.1 Review tests from Task Groups 1-6
    - Review the 2-8 tests written for core handler (Task 1.1)
    - Review the 2-8 tests written for content transformation (Task 2.1)
    - Review the 2-8 tests written for file operations (Task 3.1)
    - Review the 2-8 tests written for verification (Task 4.1)
    - Review the 2-8 tests written for cleanup (Task 5.1)
    - Review the 2-8 tests written for integration (Task 6.1)
    - Total existing tests: approximately 12-48 tests
  - [x] 7.2 Analyze test coverage gaps for THIS feature only
    - Identify critical workflows that lack test coverage
    - Focus ONLY on gaps related to Kilo Code handler requirements
    - Do NOT assess entire application test coverage
    - Prioritize end-to-end workflows over unit test gaps
    - Check for edge cases: malformed YAML, special characters in filenames, multi-level directories
  - [x] 7.3 Write up to 10 additional strategic tests maximum
    - Add maximum of 10 new tests to fill identified critical gaps
    - Focus on integration points and end-to-end workflows
    - Do NOT write comprehensive coverage for all scenarios
    - Priority areas: full deploy cycle, error handling, edge cases in file naming
    - Skip performance tests and accessibility tests unless business-critical
  - [x] 7.4 Run feature-specific tests only
    - Run ONLY tests related to Kilo Code handler (tests from 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, and 7.3)
    - Expected total: approximately 22-58 tests maximum
    - Do NOT run the entire application test suite
    - Verify critical workflows pass
    - Aim for >95% coverage on handler code
  - [x] 7.5 Run quality checks
    - Run `make lint` to verify Ruff linting passes
    - Run `make typecheck` to verify mypy type checking passes
    - Fix any linting or type errors found
    - Ensure code follows project conventions

**Acceptance Criteria:**
- All feature-specific tests pass (approximately 22-58 tests total)
- Critical user workflows for Kilo Code handler are covered
- No more than 10 additional tests added when filling in testing gaps
- Testing focused exclusively on this spec's feature requirements
- >95% test coverage achieved on handler code
- All linting and type checking passes

---

## Execution Order

Recommended implementation sequence:
1. Core Handler Implementation (Task Group 1)
2. Content Transformation Logic (Task Group 2)
3. File Operations and Deployment (Task Group 3)
4. Verification and Status Tracking (Task Group 4)
5. Orphaned File Cleanup (Task Group 5)
6. Integration and Constants (Task Group 6)
7. Test Review & Gap Analysis (Task Group 7)

## Notes

- **Reference Implementation**: Use `src/prompt_unifier/handlers/continue_handler.py` as primary pattern
- **Critical Difference**: Kilo Code outputs pure Markdown (no YAML frontmatter), Continue preserves YAML
- **Directory Structure**: Flat structure required with `workflows/` and `rules/` subdirectories
- **File Naming**: Apply `[directory]-[filename].md` pattern to all deployed files
- **Testing Strategy**: Write focused tests during development (2-8 per group), fill gaps at end (max 10 additional)
- **Visual Assets**: None provided, rely on Continue handler patterns
