# Task Breakdown: Recursive File Discovery for Deploy Command

## Overview
Total Tasks: 3 task groups

## Task List

### CLI Layer Modifications

#### Task Group 1: Update File Discovery & Add Duplicate Title Check
**Dependencies:** None

- [x] 1.0 Complete CLI layer modifications
  - [x] 1.1 Write 2-8 focused tests for recursive file discovery in `deploy` command
    - Test that files in subdirectories are found.
    - Test that files at the root are still found.
  - [x] 1.2 Modify `src/prompt_manager/cli/commands.py` to use `glob("**/*.md")`
    - Update `prompts_dir.glob("*.md")` to `prompts_dir.glob("**/*.md")`.
    - Update `rules_dir.glob("*.md")` to `rules_dir.glob("**/*.md")`.
  - [x] 1.3 Implement duplicate title conflict detection in `deploy` command
    - Before deploying, iterate through `content_files` to check for duplicate `title` values from YAML frontmatter.
    - If duplicates are found, raise `typer.Exit(code=1)` with an informative error message listing conflicting files.
  - [x] 1.4 Ensure CLI layer tests pass
    - Run ONLY the 2-8 tests written in 1.1.

**Acceptance Criteria:**
- The 2-8 tests written in 1.1 pass.
- The `deploy` command successfully discovers `.md` files in subdirectories.
- The `deploy` command fails with an error message if duplicate titles are detected.

### Handler Protocol & Implementation

#### Task Group 2: Update ToolHandler Protocol and Implementations
**Dependencies:** Task Group 1

- [x] 2.0 Complete Handler Protocol & Implementations
  - [x] 2.1 Write 2-8 focused tests for `ToolHandler.deploy` with relative paths
    - Test that `ContinueToolHandler` correctly creates subdirectory structure.
    - Test with nested files.
  - [x] 2.2 Update `ToolHandler.deploy` method signature in `handlers/protocol.py`
    - Add a parameter (e.g., `relative_path: Path | None = None`) to the `deploy` method.
  - [x] 2.3 Update `ContinueToolHandler.deploy` implementation in `handlers/continue_handler.py`
    - Modify the method to accept and use the `relative_path` parameter.
    - Ensure the deployment logic reproduces the subdirectory structure in the target `.continue/` directory.
  - [x] 2.4 Ensure Handler layer tests pass
    - Run ONLY the 2-8 tests written in 2.1.

**Acceptance Criteria:**
- The 2-8 tests written in 2.1 pass.
- The `ToolHandler.deploy` protocol is updated.
- `ContinueToolHandler` correctly deploys files, preserving their relative subdirectory structure.

### Testing

#### Task Group 3: Review & Gap Analysis
**Dependencies:** Task Groups 1-2

- [x] 3.0 Review existing tests and fill critical gaps only
  - [x] 3.1 Review tests from Task Groups 1-2
    - Review the 2-8 tests written for CLI modifications (Task 1.1).
    - Review the 2-8 tests written for Handler updates (Task 2.1).
  - [x] 3.2 Analyze test coverage gaps for THIS feature only
    - Identify critical user workflows that lack test coverage (e.g., edge cases for path handling, complex subdirectory structures).
  - [x] 3.3 Write up to 10 additional strategic tests maximum
    - Focus on integration points and end-to-end workflows for the entire feature.
  - [x] 3.4 Run feature-specific tests only
    - Run ONLY tests related to this spec's feature (tests from 1.1, 2.1, and 3.3).

**Acceptance Criteria:**
- All feature-specific tests pass.
- Critical user workflows for this feature are covered.
- No more than 10 additional tests added when filling in testing gaps.

## Execution Order

Recommended implementation sequence:
1. CLI Layer Modifications (Task Group 1) - COMPLETED
2. Handler Protocol & Implementation (Task Group 2) - COMPLETED
3. Testing (Task Group 3) - COMPLETED
