# Spec Requirements: Deploy Command Multi-Tool Support

## Initial Description
Complete the Deploy Command with Multi-Tool Support (Roadmap Step 8) by adding the missing functionality:
- Add --dry-run option to preview deployments without executing them
- Call verify_deployment() automatically after each successful deploy
- Extend rollback() to handle files in subdirectories (not just root level)
- These improvements complete the deploy command before adding other tool handlers

## Requirements Discussion

### First Round Questions

**Q1:** For the --dry-run option, I assume we want to show a Rich-formatted preview that lists each file, its source path, target path, and which handler will process it. Is that correct, or should it be simpler text output?
**Answer:** Correct - Rich-formatted preview showing files, source/target paths, handler

**Q2:** For --dry-run output verbosity, should we also show validation warnings/errors during dry-run, or only what would be deployed and where?
**Answer:** Only show what would be deployed where, no validation in dry-run

**Q3:** For automatic verification after deploy, if verify_deployment() returns false for any item, should we: (a) just log a warning and continue, or (b) automatically trigger rollback?
**Answer:** Warning only, NO automatic rollback

**Q4:** For verification output, should we show a detailed report (Rich table with file name, verification status, issues found) or keep it minimal (just success/failure count)?
**Answer:** Detailed report with Rich tables showing what was checked

**Q5:** For subdirectory rollback, should we track all deployed files (including their subdirectory paths) so we can restore backups from those same subdirectory locations?
**Answer:** Yes to both - track all files with subdirectory paths AND remove empty directories after rollback

**Q6:** For subdirectory backup storage, I'm assuming we maintain the same subdirectory structure in the backup (e.g., prompts/subdir/file.md.bak stays in prompts/subdir/). Is that correct?
**Answer:** Correct - maintain same subdirectory structure in backup

**Q7:** What should happen if --dry-run detects that target directories don't exist yet? Should we: (a) show they would be created, (b) show a warning, or (c) fail the dry-run?
**Answer:** Log warning and continue

**Q8:** Is there anything you specifically do NOT want included in this implementation? Any features that should be deferred to future specs?
**Answer:** Do NOT implement other handlers (steps 15-16 of roadmap) - this spec focuses only on the deploy command improvements

### Existing Code to Reference

**Similar Features Identified:**
- Feature: Continue Handler - Path: `src/prompt_unifier/handlers/continue_handler.py`
  - Components to potentially reuse: `_backup_file()` method, `rollback()` method, `verify_deployment()` method
  - Backend logic to reference: File backup/restore pattern with `.bak` extension
- Feature: Rich Formatter - Path: `src/prompt_unifier/output/rich_formatter.py`
  - Components to potentially reuse: Console patterns, color constants, table formatting approach
  - Note: Currently uses simple text-based summary, not Rich Table - consider upgrading
- Feature: Deploy Command - Path: `src/prompt_unifier/cli/commands.py` (line 634+)
  - Backend logic to reference: Current deploy flow, handler registration, file filtering

### Follow-up Questions
No follow-up questions were needed.

## Visual Assets

### Files Provided:
No visual files found

### Visual Insights:
No visual assets provided.

## Requirements Summary

### Functional Requirements
- Add `--dry-run` flag to deploy command that previews deployment without executing
- Dry-run output shows Rich-formatted preview with files, source/target paths, and handler names
- Automatic verification after each successful file deployment
- Verification output as detailed Rich tables showing what was checked and status
- Verification failures log warnings only (no automatic rollback)
- Extended rollback to handle files in subdirectories
- Track all deployed files with full subdirectory paths for proper rollback
- Remove empty directories after rollback operations
- Maintain subdirectory structure in backup file locations
- Log warning and continue if target directories don't exist during dry-run

### Reusability Opportunities
- `_backup_file()` method in ContinueToolHandler - extend to handle subdirectory paths
- `rollback()` method in ContinueToolHandler - extend with recursive glob pattern `**/*.bak`
- `verify_deployment()` method - already exists, need to call automatically and format output
- Rich Console patterns in `rich_formatter.py` - reuse color constants and formatting approach
- Validation output patterns - model verification report after validation summary display

### Scope Boundaries
**In Scope:**
- `--dry-run` option for deploy command with Rich-formatted output
- Automatic `verify_deployment()` calls after each successful deploy
- Detailed verification report with Rich tables
- Extended `rollback()` to handle subdirectories recursively
- Track deployed files with subdirectory paths
- Remove empty directories after rollback
- Warning on missing target directories during dry-run

**Out of Scope:**
- Implementing other tool handlers (roadmap steps 15-16)
- Automatic rollback on verification failure
- Validation checks during dry-run
- Changes to existing handler protocol interface
- New handler types beyond ContinueToolHandler

### Technical Considerations
- Integration points: Deploy command in CLI, ContinueToolHandler methods, RichFormatter patterns
- Existing system constraints: Current backup uses `.bak` suffix, rollback only globs root level
- Technology preferences: Rich library for terminal output, Typer for CLI framework
- Similar code patterns to follow:
  - Rich Console output in `continue_handler.py` (lines 5, 11, 30, 126, etc.)
  - Color constants pattern in `rich_formatter.py` (ERROR_COLOR, WARNING_COLOR, SUCCESS_COLOR)
  - Validation summary display pattern in `rich_formatter.py` `_display_summary_table()`
  - File path calculation in deploy command (lines 824-837 for relative_path calculation)
