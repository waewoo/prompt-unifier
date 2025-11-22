# Specification: Deploy Command Multi-Tool Support

## Goal
Complete the deploy command by adding --dry-run preview, automatic verification with Rich reports, and extended rollback/backup support for subdirectories to prepare for future multi-handler support.

## User Stories
- As a developer, I want to preview deployments with --dry-run so that I can verify what will be deployed before executing
- As a developer, I want automatic verification after deployment so that I can confirm files were deployed correctly
- As a developer, I want rollback to handle subdirectories so that I can safely restore previous state of nested file structures

## Specific Requirements

**--dry-run Option**
- Add `--dry-run` boolean flag to deploy command in CLI
- Preview deployment without executing any file operations
- Use Rich-formatted table showing: source path, target path, handler name
- Log warning and continue if target directories don't exist
- Do NOT perform validation checks during dry-run
- Skip backup, deploy, and verification operations entirely

**Automatic Verification After Deploy**
- Call `verify_deployment()` after each successful file deploy
- Display detailed Rich table report showing: file name, content type, verification status
- Use color coding: green for passed, yellow for warnings, red for failures
- Show warning message only when verification fails (no automatic rollback)
- Aggregate results and display summary count at end of deployment

**Extended Rollback for Subdirectories**
- Modify `rollback()` to use recursive glob pattern `**/*.bak` instead of `*.bak`
- Track all deployed files with their full subdirectory paths
- Restore backup files maintaining subdirectory structure
- Remove empty directories after restoring files
- Log warning and continue if backup file is missing during rollback

**Enhanced Backup Storage**
- Maintain subdirectory structure in backup locations (e.g., `prompts/subdir/file.md.bak`)
- Update `_backup_file()` to handle files in nested directories
- Ensure backup path preserves relative directory structure from base directory

**Verification Report Format**
- Display header with handler name and deployment context
- Show Rich table with columns: File, Type, Status, Details
- Use consistent color constants from RichFormatter (SUCCESS_COLOR, WARNING_COLOR, ERROR_COLOR)
- Display summary row with pass/fail/warning counts
- Follow existing validation summary display pattern

**Deploy Command Integration**
- Integrate dry-run check early in deploy flow before file operations
- Call verification after successful deploy in the handler loop
- Pass deployed file paths to verification for accurate checking
- Maintain existing --clean and --tags filtering behavior

## Existing Code to Leverage

**ContinueToolHandler (`src/prompt_unifier/handlers/continue_handler.py`)**
- `_backup_file()` method (lines 121-126): Extend to handle subdirectory paths while preserving logic
- `rollback()` method (lines 336-351): Change glob pattern from `*.bak` to `**/*.bak` and add empty dir cleanup
- `verify_deployment()` method (lines 303-334): Already exists, call automatically and format output as Rich table
- Console patterns: Reuse existing console print statements with color formatting

**RichFormatter (`src/prompt_unifier/output/rich_formatter.py`)**
- Color constants (lines 40-44): ERROR_COLOR, WARNING_COLOR, SUCCESS_COLOR for consistent styling
- `_display_summary_table()` method (lines 180-201): Model verification report after this pattern
- Console print patterns: Follow existing indentation and formatting conventions

**Deploy Command (`src/prompt_unifier/cli/commands.py`)**
- Deploy function (lines 634-902): Add dry-run flag and verification calls
- Handler loop pattern (lines 812-889): Insert verification after successful deploys
- Relative path calculation (lines 824-837): Reuse for tracking deployed file paths

**ToolHandlerRegistry pattern**
- Existing handler iteration pattern for multi-handler support readiness
- Handler name retrieval with `get_name()` method

## Out of Scope
- Implementing other tool handlers (Windsurf, Cursor, Aider) - roadmap steps 15-16
- Automatic rollback on verification failure
- Validation checks during dry-run
- Changes to existing handler protocol interface
- New handler types beyond ContinueToolHandler
- Interactive confirmation prompts
- Progress bars or spinners for long operations
- Persistent deployment history or logging
- Configuration options for verification behavior
- Partial rollback (rollback specific files only)
