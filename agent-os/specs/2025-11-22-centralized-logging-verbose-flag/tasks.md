# Task Breakdown: Centralized Logging & Verbose Flag

## Overview
Total Tasks: 4 Task Groups

## Task List

### Core Infrastructure

#### Task Group 1: Logging Module Creation
**Dependencies:** None

- [x] 1.0 Complete logging module infrastructure
  - [x] 1.1 Write 2-8 focused tests for logging module functionality
    - Test `configure_logging()` with different verbosity levels (0, 1, 2+)
    - Test log level mapping: 0=WARNING, 1=INFO, 2+=DEBUG
    - Test file handler creation with valid path
    - Test file handler error handling for invalid paths
    - Test RichHandler integration for console output
    - Test that both handlers can be active simultaneously
  - [x] 1.2 Create logging module at `src/prompt_unifier/utils/logging_config.py`
    - Import Python's built-in logging module
    - Import `rich.logging.RichHandler` for console formatting
    - Define log format constants for file and console output
    - Follow module pattern from existing utils (e.g., `path_helpers.py`)
  - [x] 1.3 Implement `configure_logging()` function
    - Accept `verbosity: int` parameter (count of -v flags)
    - Accept `log_file: Optional[str]` parameter for file output path
    - Map verbosity to levels: 0=WARNING, 1=INFO, 2+=DEBUG
    - Configure root logger with appropriate level
    - Clear existing handlers before adding new ones
  - [x] 1.4 Implement RichHandler console output
    - Use `rich.logging.RichHandler` for terminal output
    - Include timestamps in log messages
    - Apply color coding following `RichFormatter` pattern
    - Ensure Rich markup escaping for log messages
  - [x] 1.5 Implement file handler output
    - Create `logging.FileHandler` when log_file path provided
    - Use plain text format: timestamp, level, module, message
    - Handle file permission errors with user-friendly messages
    - Set file handler to same level as console handler
  - [x] 1.6 Export logging configuration in `__init__.py`
    - Add `configure_logging` to `src/prompt_unifier/utils/__init__.py` exports
    - Ensure clean import path for use throughout codebase
  - [x] 1.7 Ensure logging module tests pass
    - Run ONLY the 2-8 tests written in 1.1
    - Verify all verbosity levels configure correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 1.1 pass
- `configure_logging()` properly maps verbosity to log levels
- RichHandler displays colored output in terminal
- File handler writes plain text logs when path provided
- Module exports cleanly from utils package

---

### CLI Integration

#### Task Group 2: Global Verbose Flag Implementation
**Dependencies:** Task Group 1

- [x] 2.0 Complete CLI global flag integration
  - [x] 2.1 Write 2-8 focused tests for CLI global options
    - Test --verbose flag increments verbosity count (0, 1, 2+)
    - Test --log-file option accepts file path
    - Test -v short flag works for verbose (not version)
    - Test --version still works without -v short flag
    - Test callback invokes `configure_logging()` with correct parameters
    - Test verbose flag affects logging output level
  - [x] 2.2 Resolve -v flag conflict in `main.py`
    - Change --version to use only `--version` (remove `-v` short flag)
    - Or change --version to use `-V` (capital V) as short flag
    - Update `version_callback` and related option definition
    - Document the change for users
  - [x] 2.3 Add --verbose option to global callback
    - Add to `@app.callback()` in `main.py`
    - Use `typer.Option` with `count=True` to accumulate -v flags
    - Support `-v` (short) and `--verbose` (long) flags
    - Set `is_eager=True` to process before command execution
  - [x] 2.4 Add --log-file option to global callback
    - Add alongside --verbose in `main_callback`
    - Accept `Optional[str]` file path
    - Use `typer.Option` with appropriate help text
    - Set `is_eager=True` for early configuration
  - [x] 2.5 Call `configure_logging()` in callback
    - Import `configure_logging` from utils
    - Pass verbosity count and log_file path
    - Ensure logging is configured before any command runs
    - Handle configuration errors gracefully
  - [x] 2.6 Ensure CLI integration tests pass
    - Run ONLY the 2-8 tests written in 2.1
    - Verify global flags work across all commands
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 2.1 pass
- -v flag now controls verbosity (not version)
- --version works correctly (with -V or long flag only)
- --verbose increments verbosity level
- --log-file accepts and uses file path
- Logging configured before command execution

---

### Service Integration

#### Task Group 3: Migrate Existing Verbose Flags & Add Logging
**Dependencies:** Task Group 2

- [x] 3.0 Complete service integration with logging
  - [x] 3.1 Write 2-8 focused tests for service logging integration
    - Test `validate` command uses global logging level
    - Test `list_content` command uses global logging level
    - Test INFO messages appear with -v flag
    - Test DEBUG messages appear with -vv flag
    - Test services log contextual information (file paths, counts)
    - Test backward compatibility of command behavior
  - [x] 3.2 Migrate `validate` command to global logging
    - Remove local `--verbose/-v` option from command signature (line 69)
    - Replace verbose boolean checks with `logging.info()` and `logging.debug()` calls
    - Import `logging` module and get logger with `logging.getLogger(__name__)`
    - Maintain same information output, just via logging system
  - [x] 3.3 Migrate `list_content` command to global logging
    - Remove local `--verbose/-v` option from command signature (line 147)
    - Replace verbose boolean checks with `logging.info()` and `logging.debug()` calls
    - Import `logging` module and get logger with `logging.getLogger(__name__)`
    - Maintain same information output, just via logging system
  - [x] 3.4 Add logging to key services
    - Add `logger = logging.getLogger(__name__)` to `GitService`
    - Add `logger = logging.getLogger(__name__)` to `ValidationService`
    - Add `logger = logging.getLogger(__name__)` to command handlers
    - Log at appropriate levels: DEBUG for tracing, INFO for progress, WARNING for issues
  - [x] 3.5 Add contextual logging to operations
    - Log file paths being processed
    - Log counts (files synced, validated, deployed)
    - Log durations for operations where relevant
    - Log git operations (commits, status checks)
  - [x] 3.6 Ensure service integration tests pass
    - Run ONLY the 2-8 tests written in 3.1
    - Verify commands work without local verbose flags
    - Verify logging output appears at correct levels
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 3.1 pass
- `validate` and `list_content` commands use global logging
- Local --verbose flags removed from migrated commands
- Services log contextual information at appropriate levels
- Backward compatibility maintained for command behavior

---

### Testing

#### Task Group 4: Test Review & Gap Analysis
**Dependencies:** Task Groups 1-3

- [x] 4.0 Review existing tests and fill critical gaps only
  - [x] 4.1 Review tests from Task Groups 1-3
    - Review the 2-8 tests written for logging module (Task 1.1)
    - Review the 2-8 tests written for CLI integration (Task 2.1)
    - Review the 2-8 tests written for service integration (Task 3.1)
    - Total existing tests: approximately 6-24 tests
  - [x] 4.2 Analyze test coverage gaps for THIS feature only
    - Identify critical user workflows that lack test coverage
    - Focus ONLY on gaps related to logging and verbose flag requirements
    - Do NOT assess entire application test coverage
    - Prioritize end-to-end workflows: CLI -> logging -> output
  - [x] 4.3 Write up to 10 additional strategic tests maximum
    - Add maximum of 10 new tests to fill identified critical gaps
    - Focus on integration: CLI flag -> logging config -> service output
    - Test end-to-end: command with -v flag shows INFO logs
    - Test end-to-end: command with -vv flag shows DEBUG logs
    - Test end-to-end: --log-file creates file with correct content
    - Test error scenarios: invalid log file path handling
    - Do NOT write comprehensive coverage for all scenarios
    - Skip edge cases unless business-critical
  - [x] 4.4 Run feature-specific tests only
    - Run ONLY tests related to this spec's feature (tests from 1.1, 2.1, 3.1, and 4.3)
    - Expected total: approximately 16-34 tests maximum
    - Do NOT run the entire application test suite
    - Verify critical workflows pass

**Acceptance Criteria:**
- All feature-specific tests pass (approximately 16-34 tests total)
- Critical user workflows for logging feature are covered
- No more than 10 additional tests added when filling in testing gaps
- Testing focused exclusively on this spec's feature requirements

---

## Execution Order

Recommended implementation sequence:

1. **Core Infrastructure (Task Group 1)** - Create the logging module foundation
   - Build `configure_logging()` function
   - Set up RichHandler and file handler
   - Export from utils module

2. **CLI Integration (Task Group 2)** - Add global flags to CLI
   - Resolve -v flag conflict
   - Add --verbose and --log-file to global callback
   - Wire up `configure_logging()` call

3. **Service Integration (Task Group 3)** - Migrate and enhance logging
   - Remove local --verbose flags from commands
   - Add logging to services
   - Include contextual information in logs

4. **Test Review & Gap Analysis (Task Group 4)** - Verify complete implementation
   - Review all tests from previous groups
   - Fill critical workflow gaps
   - Run feature-specific test suite
