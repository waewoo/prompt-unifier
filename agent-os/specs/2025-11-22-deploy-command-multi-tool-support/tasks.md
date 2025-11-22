# Task Breakdown: Deploy Command Multi-Tool Support

## Overview
Total Tasks: 4 Task Groups

## Task List

### Backup/Rollback Layer

#### Task Group 1: Enhanced Backup Storage and Subdirectory Rollback
**Dependencies:** None

- [x] 1.0 Complete backup and rollback layer enhancements
  - [x] 1.1 Write 2-8 focused tests for backup/rollback functionality
    - Test `_backup_file()` handles files in nested subdirectories
    - Test backup preserves relative directory structure from base directory
    - Test `rollback()` with recursive glob pattern `**/*.bak`
    - Test rollback restores files maintaining subdirectory structure
    - Test rollback removes empty directories after restoring files
    - Test rollback logs warning and continues when backup file is missing
  - [x] 1.2 Extend `_backup_file()` to handle subdirectory paths
    - Update method in `src/prompt_unifier/handlers/continue_handler.py` (lines 121-126)
    - Preserve relative directory structure from base directory in backup path
    - Maintain existing `.bak` suffix pattern
    - Ensure backup path mirrors source subdirectory structure
  - [x] 1.3 Modify `rollback()` for recursive subdirectory support
    - Change glob pattern from `*.bak` to `**/*.bak` in `continue_handler.py` (lines 336-351)
    - Restore backup files maintaining their subdirectory structure
    - Log warning and continue if backup file is missing during rollback
  - [x] 1.4 Implement empty directory cleanup after rollback
    - Remove empty directories after file restoration
    - Walk directory tree bottom-up to remove nested empty directories
    - Skip non-empty directories
  - [x] 1.5 Track deployed files with full subdirectory paths
    - Store full relative paths for all deployed files
    - Enable accurate rollback of nested file structures
  - [x] 1.6 Ensure backup/rollback layer tests pass
    - Run ONLY the 2-8 tests written in 1.1
    - Verify all backup and rollback operations work correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 1.1 pass
- Backup files preserve subdirectory structure (e.g., `prompts/subdir/file.md.bak`)
- Rollback finds all `.bak` files recursively
- Empty directories are cleaned up after rollback
- Missing backup files log warning but don't fail rollback

### Verification Layer

#### Task Group 2: Automatic Verification and Rich Report
**Dependencies:** Task Group 1

- [x] 2.0 Complete automatic verification layer
  - [x] 2.1 Write 2-8 focused tests for verification functionality
    - Test `verify_deployment()` is called after each successful file deploy
    - Test Rich table report displays file name, content type, verification status
    - Test color coding: green for passed, yellow for warnings, red for failures
    - Test warning message shown only when verification fails
    - Test aggregate summary count at end of deployment
  - [x] 2.2 Create verification report Rich table format
    - Display header with handler name and deployment context
    - Build Rich table with columns: File, Type, Status, Details
    - Use color constants from RichFormatter (SUCCESS_COLOR, WARNING_COLOR, ERROR_COLOR)
    - Follow existing validation summary display pattern from `rich_formatter.py` (lines 180-201)
  - [x] 2.3 Implement verification result aggregation
    - Collect results from all `verify_deployment()` calls
    - Track pass/fail/warning counts across all deployed files
    - Display summary row with aggregate counts at end of deployment
  - [x] 2.4 Add warning-only behavior for failed verifications
    - Show warning message when verification fails
    - Do NOT trigger automatic rollback
    - Continue with remaining deployments after warning
  - [x] 2.5 Ensure verification layer tests pass
    - Run ONLY the 2-8 tests written in 2.1
    - Verify verification reports display correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 2.1 pass
- Verification automatically runs after each successful deploy
- Rich table shows file name, type, status with proper colors
- Failed verifications show warning but don't rollback
- Summary displays aggregate pass/fail/warning counts

### CLI Layer

#### Task Group 3: Dry-Run Option and Deploy Command Integration
**Dependencies:** Task Group 2

- [x] 3.0 Complete CLI layer enhancements
  - [x] 3.1 Write 2-8 focused tests for CLI functionality
    - Test `--dry-run` flag is recognized by deploy command
    - Test dry-run preview shows Rich table with source path, target path, handler name
    - Test dry-run logs warning when target directories don't exist
    - Test dry-run skips backup, deploy, and verification operations
    - Test deploy command calls verification after successful deploys
    - Test existing --clean and --tags filtering behavior unchanged
  - [x] 3.2 Add `--dry-run` boolean flag to deploy command
    - Add flag to deploy function in `src/prompt_unifier/cli/commands.py` (lines 634-902)
    - Follow existing Typer flag patterns in the codebase
    - Include helpful description for CLI help text
  - [x] 3.3 Implement dry-run preview logic
    - Build Rich-formatted table showing: source path, target path, handler name
    - Log warning if target directories don't exist
    - Do NOT perform validation checks during dry-run
    - Skip backup, deploy, and verification operations entirely
  - [x] 3.4 Integrate verification calls in deploy flow
    - Call `verify_deployment()` after each successful file deploy in handler loop (lines 812-889)
    - Pass deployed file paths for accurate verification
    - Reuse relative path calculation pattern (lines 824-837)
  - [x] 3.5 Ensure deploy command integration works with dry-run check
    - Check dry-run flag early in deploy flow before file operations
    - Exit cleanly after displaying dry-run preview
    - Maintain existing --clean and --tags filtering behavior
  - [x] 3.6 Ensure CLI layer tests pass
    - Run ONLY the 2-8 tests written in 3.1
    - Verify dry-run and verification integration work correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 3.1 pass
- `--dry-run` flag shows preview without executing operations
- Preview table displays source, target, handler information
- Verification runs automatically after successful deploys
- Existing deploy functionality unchanged (--clean, --tags)

### Testing

#### Task Group 4: Test Review & Gap Analysis
**Dependencies:** Task Groups 1-3

- [x] 4.0 Review existing tests and fill critical gaps only
  - [x] 4.1 Review tests from Task Groups 1-3
    - Review the 2-8 tests written for backup/rollback (Task 1.1)
    - Review the 2-8 tests written for verification (Task 2.1)
    - Review the 2-8 tests written for CLI (Task 3.1)
    - Total existing tests: approximately 6-24 tests
  - [x] 4.2 Analyze test coverage gaps for THIS feature only
    - Identify critical user workflows that lack test coverage
    - Focus ONLY on gaps related to deploy command improvements
    - Do NOT assess entire application test coverage
    - Prioritize integration tests: dry-run -> deploy -> verify -> rollback workflow
  - [x] 4.3 Write up to 10 additional strategic tests maximum
    - Add maximum of 10 new tests to fill identified critical gaps
    - Focus on end-to-end workflow: full deploy with verification
    - Test integration between dry-run, backup, deploy, verify components
    - Consider edge cases: nested directories, missing files, multiple handlers
    - Do NOT write comprehensive coverage for all scenarios
  - [x] 4.4 Run feature-specific tests only
    - Run ONLY tests related to deploy command improvements (tests from 1.1, 2.1, 3.1, and 4.3)
    - Expected total: approximately 16-34 tests maximum
    - Do NOT run the entire application test suite
    - Verify critical workflows pass

**Acceptance Criteria:**
- All feature-specific tests pass (approximately 16-34 tests total)
- Critical user workflows for deploy improvements are covered
- No more than 10 additional tests added when filling in testing gaps
- Testing focused exclusively on this spec's feature requirements

## Execution Order

Recommended implementation sequence:

1. **Backup/Rollback Layer (Task Group 1)** - Foundation for subdirectory support
   - Must be completed first as other features depend on proper backup/restore
   - Establishes subdirectory tracking pattern used throughout

2. **Verification Layer (Task Group 2)** - Automatic verification with Rich reports
   - Depends on backup layer for understanding deployed file tracking
   - Establishes Rich table patterns reused by dry-run preview

3. **CLI Layer (Task Group 3)** - Dry-run and deploy command integration
   - Depends on verification layer for calling verify_deployment()
   - Integrates all components into cohesive deploy flow

4. **Test Review & Gap Analysis (Task Group 4)** - Final verification
   - Reviews all tests and fills integration gaps
   - Ensures end-to-end workflow is properly tested

## Technical Notes

### Key Files to Modify
- `src/prompt_unifier/handlers/continue_handler.py` - Backup/rollback/verify methods
- `src/prompt_unifier/cli/commands.py` - Deploy command (lines 634-902)
- `src/prompt_unifier/output/rich_formatter.py` - Reference for Rich patterns

### Code Patterns to Follow
- Color constants: `ERROR_COLOR`, `WARNING_COLOR`, `SUCCESS_COLOR` from RichFormatter
- Rich table pattern: Model after `_display_summary_table()` in rich_formatter.py
- Console output: Follow existing patterns in continue_handler.py
- Relative path calculation: Reuse pattern from deploy command (lines 824-837)

### Testing Approach
- Use pytest with TDD approach (write tests first)
- Mock file system operations where appropriate
- Follow existing test patterns in `tests/` directory