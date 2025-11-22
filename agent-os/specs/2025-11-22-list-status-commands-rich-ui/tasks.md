# Task Breakdown: List & Status Commands with Rich UI

## Overview
Total Tasks: 14

## Task List

### Core & Handlers

#### Task Group 1: Protocol & Handler Implementation
**Dependencies:** None

- [x] 1.0 Complete Core & Handler updates
  - [x] 1.1 Write 2-8 focused tests for Handler Status Logic
    - Test `ContinueToolHandler.get_deployment_status` with synced, outdated, and missing files
    - Test `ContinueToolHandler` content hashing/comparison logic
  - [x] 1.2 Update `ToolHandler` Protocol
    - Add `get_deployment_status(self, content_name, content_type, source_content) -> str` method signature
  - [x] 1.3 Implement `get_deployment_status` in `ContinueToolHandler`
    - Implement content hashing (SHA-256) for comparison
    - Handle "synced", "outdated", "missing" states
    - Reuse/adapt `verify_deployment_with_details` where helpful
  - [x] 1.4 Ensure Core tests pass
    - Run ONLY the tests written in 1.1
    - Verify handler status logic works correctly

**Acceptance Criteria:**
- `ToolHandler` protocol includes `get_deployment_status`
- `ContinueToolHandler` correctly identifies synced, outdated, and missing files
- Tests in 1.1 pass

### CLI & UI

#### Task Group 2: Rich Formatting & List Command
**Dependencies:** Task Group 1 (for stable models/protocol, though mostly independent)

- [ ] 2.0 Complete List Command
  - [ ] 2.1 Write 2-8 focused tests for List Command
    - Test filtering by `--tool` and `--tag`
    - Test sorting by name and date
    - Test `--verbose` flag output generation (mocking Rich console)
  - [ ] 2.2 Create `RichTableFormatter` class
    - Method to generate main prompts table
    - Support for colored status columns (Green/Yellow/Red)
    - Method to render syntax-highlighted preview for `--verbose`
  - [ ] 2.3 Implement `list` command in `commands.py`
    - Gather all prompts/rules using `ContentFileParser`
    - Apply filtering and sorting logic
    - Use `RichTableFormatter` for output
  - [ ] 2.4 Ensure List Command tests pass
    - Run ONLY the tests written in 2.1
    - Verify filtering, sorting, and output generation

**Acceptance Criteria:**
- `list` command displays all prompts/rules in a Rich table
- Filtering by tool and tag works
- Sorting works
- `--verbose` shows content preview
- Tests in 2.1 pass

#### Task Group 3: Status Command
**Dependencies:** Task Group 1 (requires handler status logic)

- [ ] 3.0 Complete Status Command
  - [ ] 3.1 Write 2-8 focused tests for Status Command
    - Test aggregation of status across multiple tools
    - Test grouping by tool in output
    - Test handling of partial deployments
  - [ ] 3.2 Implement `status` command in `commands.py`
    - Iterate through configured handlers
    - For each handler, check status of all known prompts/rules
    - Aggregate results
  - [ ] 3.3 Update `RichTableFormatter` for Status
    - Add method to render status reports (grouped by tool)
    - Visual indicators for Sync/Outdated/Missing
  - [ ] 3.4 Ensure Status Command tests pass
    - Run ONLY the tests written in 3.1
    - Verify status aggregation and reporting

**Acceptance Criteria:**
- `status` command shows deployment state per tool
- Correctly reports Synced/Outdated/Missing states
- Output is grouped by tool and formatted with Rich
- Tests in 3.1 pass

### Testing

#### Task Group 4: Test Review & Gap Analysis
**Dependencies:** Task Groups 1-3

- [ ] 4.0 Review existing tests and fill critical gaps only
  - [ ] 4.1 Review tests from Task Groups 1-3
    - Review tests from 1.1 (Handler Logic)
    - Review tests from 2.1 (List Command)
    - Review tests from 3.1 (Status Command)
  - [ ] 4.2 Analyze test coverage gaps for THIS feature only
    - Check for edge cases in status comparison (e.g., whitespace differences, if relevant)
    - Check for empty states (no prompts, no tools)
  - [ ] 4.3 Write up to 10 additional strategic tests maximum
    - Add integration test: `deploy` -> modify source -> `status` (verify "outdated")
    - Add integration test: `deploy` -> `list` (verify metadata)
  - [ ] 4.4 Run feature-specific tests only
    - Run tests from 1.1, 2.1, 3.1, and 4.3
    - Verify end-to-end flows

**Acceptance Criteria:**
- All feature-specific tests pass
- Critical flows (Deploy -> Status Check -> List) are covered
- No more than 10 additional tests added

## Execution Order

Recommended implementation sequence:
1. Protocol & Handler Implementation (Task Group 1)
2. Rich Formatting & List Command (Task Group 2)
3. Status Command (Task Group 3)
4. Test Review & Gap Analysis (Task Group 4)
