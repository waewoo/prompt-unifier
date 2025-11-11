# Task Breakdown: Git Integration & Repository Management

## Overview
Total Task Groups: 5 (Configuration Management, Git Operations, CLI Commands, Integration & Error Handling, Test Coverage Review)

This feature implements three new CLI commands (init, sync, status) to enable read-only synchronization of prompts from a central Git repository to application projects. The implementation follows TDD methodology with comprehensive test coverage (target >85%).

## Task List

### Configuration Management Layer

#### Task Group 1: Configuration Models and Manager
**Dependencies:** None
**Complexity:** Medium
**Estimated Test Count:** 6-8 focused tests

- [x] 1.0 Complete configuration management layer
  - [x] 1.1 Write 6-8 focused tests for configuration management
    - Test config file creation with required fields (repo_url, last_sync_timestamp, last_sync_commit)
    - Test config loading from valid YAML file
    - Test config validation with missing/invalid fields
    - Test config update with new sync information
    - Test handling of corrupted config file with clear error
    - Test config save with proper YAML formatting
    - Skip exhaustive edge cases (focus on critical workflows)
  - [x] 1.2 Create GitConfig Pydantic model in src/prompt_manager/models/git_config.py
    - Fields: repo_url (str | None), last_sync_timestamp (str | None), last_sync_commit (str | None)
    - Use Pydantic v2 BaseModel pattern from models/validation.py
    - Add Field() descriptors with validation
    - Add model_config with json_schema_extra for examples
    - Use ISO 8601 format for timestamp field
  - [x] 1.3 Create ConfigManager class in src/prompt_manager/config/manager.py
    - Method: load_config(config_path: Path) -> GitConfig | None
    - Method: save_config(config_path: Path, config: GitConfig) -> None
    - Method: update_sync_info(config_path: Path, repo_url: str, commit_hash: str) -> None
    - Use yaml.safe_load() and yaml.safe_dump() following YAMLParser patterns
    - Validate required fields after loading
    - Handle FileNotFoundError and yaml.YAMLError with clear messages
    - Use pathlib.Path for all file operations
  - [x] 1.4 Add __init__.py for config module
    - Export ConfigManager and GitConfig
  - [x] 1.5 Ensure configuration layer tests pass
    - Run ONLY the 6-8 tests written in 1.1
    - Verify config creation, loading, saving, and validation work correctly
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- The 6-8 tests written in 1.1 pass
- GitConfig model validates all required fields
- ConfigManager successfully creates, loads, and updates config files
- YAML formatting follows existing patterns (safe_load/safe_dump)
- Clear error messages for corrupted or missing config files

**Reference Patterns:**
- Pydantic models: src/prompt_manager/models/validation.py (ValidationIssue, ValidationResult)
- YAML handling: src/prompt_manager/core/yaml_parser.py (safe_load, safe_dump, error handling)
- Path operations: src/prompt_manager/utils/file_scanner.py (pathlib.Path patterns)

---

### Git Operations Layer

#### Task Group 2: Git Service Implementation
**Dependencies:** Task Group 1
**Complexity:** High
**Estimated Test Count:** 6-8 focused tests

- [ ] 2.0 Complete Git operations layer
  - [ ] 2.1 Write 6-8 focused tests for Git operations
    - Test successful repository clone to temporary directory
    - Test extraction of prompts/ directory from cloned repo
    - Test retrieval of latest commit hash from repository
    - Test checking for remote updates (new commits available)
    - Test handling of invalid repository URL with clear error
    - Test cleanup of temporary directory after operations
    - Test authentication error handling with helpful message
    - Skip network retry logic testing (integration test covers this)
  - [ ] 2.2 Create GitService class in src/prompt_manager/git/service.py
    - Use GitPython library (already in dependencies: gitpython ^3.1.40)
    - Method: clone_to_temp(repo_url: str) -> tuple[Path, git.Repo]
    - Method: get_latest_commit(repo: git.Repo) -> str (return short SHA)
    - Method: extract_prompts_dir(repo_path: Path, target_path: Path) -> None
    - Method: check_remote_updates(repo_url: str, last_commit: str) -> tuple[bool, int]
    - Use tempfile.TemporaryDirectory() as context manager for temp clone
    - Validate that cloned repo contains prompts/ directory
    - Use shutil.copytree with dirs_exist_ok=True for directory copying
    - Handle git.exc.GitCommandError for clone failures
    - Return tuple (has_updates: bool, commits_behind: int) from check_remote_updates
  - [ ] 2.3 Implement network retry logic with exponential backoff
    - Create retry decorator or helper function
    - 3 retry attempts for network operations (clone, fetch)
    - Exponential backoff: 1s, 2s, 4s delays between retries
    - Log retry attempts for user visibility
    - Fail with clear error message after 3 attempts
  - [ ] 2.4 Add __init__.py for git module
    - Export GitService
  - [ ] 2.5 Ensure Git operations layer tests pass
    - Run ONLY the 6-8 tests written in 2.1
    - Use pytest-mock for mocking GitPython operations
    - Verify clone, extract, and commit retrieval work correctly
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- The 6-8 tests written in 2.1 pass
- GitService successfully clones repos to temporary directories
- Prompts directory extracted and copied to target location
- Temporary directories cleaned up after operations
- Clear error messages for Git failures (invalid URL, auth, network)
- Retry logic implemented with exponential backoff (3 attempts)

**Reference Patterns:**
- File operations: src/prompt_manager/utils/file_scanner.py (pathlib.Path, directory validation)
- Error handling: src/prompt_manager/core/yaml_parser.py (try-except with clear messages)
- Context managers: Python tempfile.TemporaryDirectory() for cleanup

**GitPython Usage Examples:**
```python
import git
from pathlib import Path

# Clone repository
repo = git.Repo.clone_from(repo_url, temp_dir)

# Get latest commit hash (short)
commit_hash = repo.head.commit.hexsha[:7]

# Fetch remote updates
origin = repo.remote(name='origin')
origin.fetch()

# Check commits behind
commits_behind = len(list(repo.iter_commits(f'{local_commit}..origin/main')))
```

---

### CLI Commands Layer

#### Task Group 3: Init, Sync, and Status Commands
**Dependencies:** Task Groups 1 and 2
**Complexity:** High
**Estimated Test Count:** 8 focused tests

- [ ] 3.0 Complete CLI commands implementation
  - [ ] 3.1 Write 8 focused tests for CLI commands
    - Test init command creates .prompt-manager/ directory and config.yaml
    - Test init command creates prompts/ directory structure (rules/, custom/, shared/)
    - Test init command creates .gitignore if it doesn't exist (without ignoring .prompt-manager/)
    - Test init command fails if .prompt-manager/ already exists
    - Test sync command fails if init not run first (missing config.yaml)
    - Test sync command with --repo flag stores URL and syncs prompts
    - Test sync command without --repo flag reads URL from config
    - Test status command displays repo URL, last sync time, and update availability
    - Skip exhaustive testing of all edge cases
  - [ ] 3.2 Implement init command in src/prompt_manager/cli/commands.py
    - Function signature: def init() -> None
    - Create .prompt-manager/ directory in current working directory (Path.cwd())
    - Use Path.mkdir(parents=True, exist_ok=False) to prevent re-initialization
    - Create config.yaml with empty placeholders: repo_url: null, last_sync_timestamp: null, last_sync_commit: null
    - Create prompts/ directory with subdirectories: rules/, custom/, shared/
    - Create .gitignore template if not exists (do NOT ignore .prompt-manager/)
    - Use Rich Console for success output with green checkmark
    - Exit with code 0 on success, code 1 on failure (raise typer.Exit(code=1))
    - Follow pattern from cli/commands.py validate command
  - [ ] 3.3 Implement sync command in src/prompt_manager/cli/commands.py
    - Function signature: def sync(repo: str | None = typer.Option(None, "--repo")) -> None
    - Validate .prompt-manager/config.yaml exists (error if not: "Run 'prompt-manager init' first")
    - If --repo provided: use repo URL from flag
    - If --repo not provided: read repo URL from config.yaml
    - Error if repo URL is None: "No repository URL configured. Use --repo flag."
    - Use GitService to clone repository to temporary directory
    - Extract prompts/ directory and copy to current directory
    - Update config.yaml with current timestamp (ISO 8601) and latest commit hash
    - Display Rich formatted output: repo URL, files synced, timestamp
    - Handle all Git errors with clear messages and exit code 1
    - Clean up temporary directory on success or error
  - [ ] 3.4 Implement status command in src/prompt_manager/cli/commands.py
    - Function signature: def status() -> None
    - Validate .prompt-manager/config.yaml exists (error if not: "Run 'prompt-manager init' first")
    - Load config.yaml and display: repo URL, last sync timestamp (human-readable), last commit hash (short)
    - Use GitService.check_remote_updates() to check for new commits
    - Display "Updates available" or "Up to date" with green/yellow color
    - Show commits behind count if updates available
    - Use Rich Console with symbols (checkmark for up-to-date, warning for updates)
    - Exit with code 0 always (status is informational)
  - [ ] 3.5 Register commands in src/prompt_manager/cli/main.py
    - Add @app.command(name="init", help="...") decorator for init
    - Add @app.command(name="sync", help="...") decorator for sync
    - Add @app.command(name="status", help="...") decorator for status
    - Follow pattern from existing validate command registration
  - [ ] 3.6 Ensure CLI commands tests pass
    - Run ONLY the 8 tests written in 3.1
    - Use tmp_path fixture for temporary directories
    - Use pytest-mock to mock GitService operations
    - Verify command behaviors and exit codes
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- The 8 tests written in 3.1 pass
- init command creates required directory structure and files
- init command prevents re-initialization with clear error
- sync command validates init was run first
- sync command accepts --repo flag or reads from config
- sync command updates config with sync metadata
- status command displays repo info and update availability
- All commands use Rich Console for formatted output
- Exit codes follow specification (0 for success, 1 for errors)

**Reference Patterns:**
- CLI structure: src/prompt_manager/cli/commands.py (validate command)
- CLI registration: src/prompt_manager/cli/main.py (@app.command decorator)
- Rich output: src/prompt_manager/output/rich_formatter.py (Console, colors, symbols)
- Error handling: typer.echo(message, err=True) and raise typer.Exit(code=1)

**Rich Console Output Examples:**
```python
from rich.console import Console

console = Console()
console.print("[green]✓[/green] Initialization complete")
console.print("━" * 80)
console.print(f"Repository: {repo_url}")
console.print(f"Last sync: {timestamp}")
console.print("[yellow]⚠ Updates available[/yellow] (3 commits behind)")
```

---

### Integration & Error Handling

#### Task Group 4: End-to-End Workflows and Error Cases
**Dependencies:** Task Groups 1, 2, and 3
**Complexity:** Medium
**Estimated Test Count:** 6-8 focused tests

- [ ] 4.0 Complete integration and error handling
  - [ ] 4.1 Write 6-8 focused integration tests
    - Test complete workflow: init -> sync -> status (end-to-end)
    - Test sync overwrites local changes (auto-resolve to remote)
    - Test sync handles missing prompts/ directory in remote repo
    - Test sync with authentication error shows helpful message
    - Test sync with network failure retries and fails gracefully
    - Test status with no remote access shows cached information
    - Test multiple sync operations (subsequent syncs after first)
    - Skip exhaustive error permutations
  - [ ] 4.2 Enhance error messages across all modules
    - Git clone failure: "Failed to clone repository. Check URL and network connection."
    - Authentication error: "Authentication failed. Ensure Git credentials are configured."
    - Missing prompts/ in repo: "Repository does not contain a prompts/ directory."
    - Network failure: "Network error. Retrying... (attempt X/3)"
    - Missing config: "Configuration not found. Run 'prompt-manager init' first."
    - Permission error: "Permission denied. Check directory permissions."
    - Review all error messages for clarity and actionability
  - [ ] 4.3 Implement human-readable timestamp formatting
    - Create utility function in src/prompt_manager/utils/formatting.py
    - Function: format_timestamp(iso_timestamp: str) -> str
    - Convert ISO 8601 to relative time: "2 hours ago", "3 days ago"
    - Fallback to absolute format if relative not applicable: "2024-11-11 14:30:00"
    - Use Python datetime and timedelta for calculations
  - [ ] 4.4 Add comprehensive docstrings and type hints
    - Ensure all public methods have docstrings following existing patterns
    - Add type hints for all function signatures (strict mypy compliance)
    - Document all exceptions that can be raised
    - Add usage examples in docstrings where helpful
  - [ ] 4.5 Ensure integration tests pass
    - Run ONLY the 6-8 tests written in 4.1
    - Verify end-to-end workflows complete successfully
    - Verify error cases handled gracefully with clear messages
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- The 6-8 tests written in 4.1 pass
- Complete workflow (init -> sync -> status) works end-to-end
- Sync auto-resolves conflicts by taking remote changes
- All error cases display helpful, actionable messages
- Retry logic works for network failures (3 attempts)
- Human-readable timestamps display correctly
- All code passes mypy strict type checking
- Docstrings follow existing patterns from codebase

**Reference Patterns:**
- Integration tests: tests/integration/test_end_to_end.py
- Error messages: src/prompt_manager/cli/commands.py (typer.echo with err=True)
- Type hints: All modules use strict typing (mypy strict mode)
- Docstrings: src/prompt_manager/core/yaml_parser.py (comprehensive examples)

---

### Testing & Documentation

#### Task Group 5: Test Coverage Review and Documentation
**Dependencies:** Task Groups 1-4
**Complexity:** Low
**Estimated Test Count:** Maximum 10 additional tests

- [ ] 5.0 Review existing tests and fill critical gaps only
  - [ ] 5.1 Review tests from Task Groups 1-4
    - Review 6-8 tests from configuration layer (Task 1.1)
    - Review 6-8 tests from Git operations layer (Task 2.1)
    - Review 8 tests from CLI commands layer (Task 3.1)
    - Review 6-8 tests from integration layer (Task 4.1)
    - Total existing tests: approximately 26-32 tests
  - [ ] 5.2 Analyze test coverage gaps for THIS feature only
    - Run pytest with coverage: pytest --cov=src/prompt_manager/config --cov=src/prompt_manager/git --cov-report=term-missing
    - Identify critical user workflows lacking test coverage
    - Focus ONLY on gaps related to Git integration feature
    - Do NOT assess entire application test coverage
    - Prioritize CLI command workflows and error handling paths
  - [ ] 5.3 Write up to 10 additional strategic tests maximum
    - Add tests ONLY for critical gaps identified in 5.2
    - Focus on edge cases for CLI commands (e.g., concurrent sync attempts)
    - Test .gitignore creation logic (ensure .prompt-manager/ not ignored)
    - Test directory structure validation (missing subdirectories)
    - Test config.yaml corruption recovery paths
    - Do NOT write comprehensive coverage for all scenarios
    - Skip performance tests, stress tests, and accessibility tests
  - [ ] 5.4 Run feature-specific tests only
    - Run ONLY tests related to Git integration feature
    - Expected total: approximately 36-42 tests maximum
    - Command: pytest tests/config/ tests/git/ tests/cli/test_git_commands.py tests/integration/test_git_integration.py
    - Verify all critical workflows pass
    - Ensure coverage is >85% for new modules (config/, git/)
    - Do NOT run entire application test suite
  - [ ] 5.5 Update README.md with new commands documentation
    - Add section: "Git Integration Commands"
    - Document init command with usage examples
    - Document sync command with --repo flag examples
    - Document status command with example output
    - Include common error scenarios and solutions
    - Add configuration file format documentation (config.yaml structure)
  - [ ] 5.6 Verify code quality checks pass
    - Run ruff linting: ruff check src/prompt_manager/config src/prompt_manager/git
    - Run ruff formatting: ruff format src/prompt_manager/config src/prompt_manager/git
    - Run mypy type checking: mypy src/prompt_manager/config src/prompt_manager/git
    - Fix any linting, formatting, or type errors
    - Ensure strict mypy compliance (no type: ignore comments)

**Acceptance Criteria:**
- All feature-specific tests pass (approximately 36-42 tests total)
- Test coverage for new modules (config/, git/) exceeds 85%
- No more than 10 additional tests added when filling coverage gaps
- Testing focused exclusively on Git integration feature requirements
- README.md includes comprehensive command documentation
- All code passes ruff linting and formatting checks
- All code passes mypy strict type checking
- No type: ignore comments used

**Testing Commands:**
```bash
# Run feature-specific tests with coverage
pytest tests/config/ tests/git/ tests/cli/test_git_commands.py tests/integration/test_git_integration.py --cov=src/prompt_manager/config --cov=src/prompt_manager/git --cov-report=term-missing

# Run code quality checks
ruff check src/prompt_manager/config src/prompt_manager/git
ruff format --check src/prompt_manager/config src/prompt_manager/git
mypy src/prompt_manager/config src/prompt_manager/git
```

**Reference Patterns:**
- Test structure: tests/core/test_yaml_parser.py (pytest fixtures, test classes)
- Coverage configuration: pyproject.toml ([tool.coverage.run] and [tool.coverage.report])
- Documentation: README.md (existing command documentation sections)

---

## Execution Order

Recommended implementation sequence:
1. **Configuration Management Layer** (Task Group 1) - Foundation for storing sync metadata
2. **Git Operations Layer** (Task Group 2) - Core Git functionality for clone/sync operations
3. **CLI Commands Layer** (Task Group 3) - User-facing commands that orchestrate config and Git operations
4. **Integration & Error Handling** (Task Group 4) - End-to-end workflows and comprehensive error handling
5. **Testing & Documentation** (Task Group 5) - Coverage review, gap filling, and documentation

## Dependencies Graph

```
Task Group 1 (Config)
    ↓
Task Group 2 (Git Operations) ← depends on Task Group 1
    ↓
Task Group 3 (CLI Commands) ← depends on Task Groups 1 & 2
    ↓
Task Group 4 (Integration) ← depends on Task Groups 1, 2 & 3
    ↓
Task Group 5 (Testing Review) ← depends on Task Groups 1-4
```

## Key Technical Decisions

1. **TDD Approach**: Each task group starts with writing 6-8 focused tests before implementation
2. **Test Isolation**: Each task group runs only its own tests during development (not entire suite)
3. **Configuration Management**: Use Pydantic for config validation, PyYAML for file I/O
4. **Git Operations**: Use GitPython library with tempfile for safe temporary directory management
5. **CLI Pattern**: Follow existing Typer + Rich pattern from validate command
6. **Error Handling**: Clear, actionable error messages with proper exit codes (0 or 1)
7. **Auto-Resolve Conflicts**: Always overwrite local changes with remote (no interactive prompts)
8. **Read-Only Sync**: No push commands or bidirectional sync (central repo is source of truth)
9. **Type Safety**: Strict mypy compliance with comprehensive type hints
10. **Test Coverage**: Target >85% coverage for new modules with 36-42 focused tests total

## Implementation Notes

**Critical Constraints:**
- .prompt-manager/ directory must be tracked in version control (NOT gitignored)
- Each application project has its own .prompt-manager/ configuration
- Sync is unidirectional: central repo → application project only
- Init must be run before sync (no automatic initialization)
- Repository URL can be overridden with --repo flag even after initial sync

**Code Quality Standards:**
- Python >=3.11 compatibility
- Mypy strict mode (no type: ignore comments)
- Ruff linting and formatting compliance
- Pytest with >85% coverage requirement
- Comprehensive docstrings with usage examples
- Proper exception handling with clear messages

**Testing Strategy:**
- Write 6-8 focused tests per task group during development
- Run only relevant tests during development (not entire suite)
- Maximum 10 additional tests for gap filling in final review
- Total expected tests: 36-42 focused tests
- Use pytest-mock for mocking external dependencies (GitPython, file I/O)
- Use tmp_path fixture for temporary directory testing

**New Files to Create:**
```
src/prompt_manager/models/git_config.py
src/prompt_manager/config/__init__.py
src/prompt_manager/config/manager.py
src/prompt_manager/git/__init__.py
src/prompt_manager/git/service.py
src/prompt_manager/utils/formatting.py (for timestamp formatting)

tests/models/test_git_config.py
tests/config/__init__.py
tests/config/test_manager.py
tests/git/__init__.py
tests/git/test_service.py
tests/cli/test_git_commands.py
tests/integration/test_git_integration.py
tests/utils/test_formatting.py
```

**Files to Modify:**
```
src/prompt_manager/cli/commands.py (add init, sync, status functions)
src/prompt_manager/cli/main.py (register new commands)
README.md (add Git integration documentation)
```
