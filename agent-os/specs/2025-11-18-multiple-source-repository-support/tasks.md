# Task Breakdown: Multiple Source Repository Support

## Overview
Total Tasks: 4 task groups with 29 sub-tasks

## Task List

### Configuration & Data Models Layer

#### Task Group 1: Repository Configuration Models and Metadata
**Dependencies:** None

- [x] 1.0 Complete configuration and data models layer
  - [x] 1.1 Write 2-8 focused tests for RepositoryConfig and GitConfig changes
    - Limit to 2-8 highly focused tests maximum
    - Test only critical model behaviors: RepositoryConfig validation, GitConfig repos list validation, metadata structure
    - Skip exhaustive coverage of all edge cases
  - [x] 1.2 Create RepositoryConfig Pydantic model
    - Fields: url (str, required), branch (str | None, optional), auth_config (dict[str, str] | None, optional), include_patterns (list[str] | None, optional), exclude_patterns (list[str] | None, optional)
    - Validations: URL format validation, branch name validation, auth_config structure validation
    - Location: src/prompt_unifier/models/git_config.py
  - [x] 1.3 Update GitConfig model for multi-repository support
    - Replace: repo_url: str | None with repos: list[RepositoryConfig] | None
    - Add: repo_metadata: list[dict] | None field for per-repo sync tracking
    - Maintain: existing deploy_tags, target_handlers, handlers, storage_path, last_sync_timestamp fields
    - Remove backward compatibility for old single-repo format
  - [x] 1.4 Create RepoMetadata utility class
    - Methods: create_metadata(url, branch, commit, timestamp), save_to_file(storage_path), load_from_file(storage_path)
    - Structure: {"files": {"path/to/file.md": {"source_url": "...", "branch": "...", "commit": "...", "timestamp": "..."}}, "repositories": [...]}
    - Location: src/prompt_unifier/utils/repo_metadata.py
  - [x] 1.5 Update ConfigManager for multi-repo configuration
    - Update: load_config() to handle repos list structure
    - Update: save_config() to serialize repos list properly
    - Add: update_multi_repo_sync_info(config_path, repo_metadata_list) method
    - Remove: old update_sync_info() method or adapt for multi-repo
    - Reuse pattern from: existing YAML handling in src/prompt_unifier/config/manager.py
  - [x] 1.6 Ensure configuration layer tests pass
    - Run ONLY the 2-8 tests written in 1.1
    - Verify RepositoryConfig validates correctly
    - Verify GitConfig handles repos list properly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 1.1 pass
- RepositoryConfig model validates all required and optional fields correctly
- GitConfig model supports repos list structure
- RepoMetadata utility can create, save, and load metadata JSON
- ConfigManager handles multi-repo YAML configuration

---

### Git Service Layer

#### Task Group 2: Multi-Repository Git Operations
**Dependencies:** Task Group 1

- [x] 2.0 Complete Git service layer enhancements
  - [x] 2.1 Write 2-8 focused tests for GitService multi-repo operations
    - Limit to 2-8 highly focused tests maximum
    - Test only critical operations: clone with branch parameter, multi-repo validation, authentication handling, selective file filtering
    - Skip exhaustive testing of all authentication scenarios
  - [x] 2.2 Extend GitService.clone_to_temp() for branch and auth support
    - Add: optional branch parameter to method signature
    - Add: optional auth_config parameter for per-repo authentication
    - Implement: branch checkout after clone if branch specified
    - Implement: auth handling for ssh_key, token, credential_helper methods
    - Reuse pattern from: existing clone_to_temp() in src/prompt_unifier/git/service.py
  - [x] 2.3 Create PathFilter utility for selective file syncing
    - Methods: apply_filters(file_paths, include_patterns, exclude_patterns)
    - Implement: glob-style pattern matching using pathlib.Path.match()
    - Logic: apply include patterns first (if specified), then exclude patterns
    - Location: src/prompt_unifier/utils/path_filter.py
  - [x] 2.4 Add multi-repository validation method
    - Create: validate_repositories(repos: list[RepositoryConfig]) method in GitService
    - Checks: URL format valid, repository accessible via git ls-remote, prompts/ directory exists
    - Behavior: fail fast on first validation error, provide clear error message per repository
    - Execute: sequentially to provide clear feedback
  - [x] 2.5 Create multi-repository sync orchestration method
    - Create: sync_multiple_repos(repos, storage_path, clear_storage=True) method in GitService
    - Steps: validate all repos, clear storage if specified, iterate repos in order, clone each, extract prompts/rules, apply filters, merge to storage, track conflicts
    - Implement: last-wins merge strategy with conflict tracking
    - Display: progress for each repository using Rich console formatting
    - Generate: .repo-metadata.json with complete file-to-repo mapping
  - [x] 2.6 Implement conflict detection and feedback
    - Track: file path collisions across repositories during merge
    - Display: "Prompt 'X' from repo A overridden by repo B" messages for conflicts
    - Store: all conflicts in metadata for audit trail
  - [x] 2.7 Ensure Git service layer tests pass
    - Run ONLY the 2-8 tests written in 2.1
    - Verify branch checkout works correctly
    - Verify multi-repo validation fails fast on errors
    - Verify selective filtering applies patterns correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 2.1 pass
- clone_to_temp() supports branch and authentication parameters
- PathFilter correctly applies include/exclude glob patterns
- Multi-repo validation fails fast with clear error messages
- Sync orchestration processes repos in order with last-wins strategy
- Conflicts are detected and reported to user
- .repo-metadata.json is generated with accurate mappings

---

### CLI Layer

#### Task Group 3: Multi-Repository CLI Commands
**Dependencies:** Task Group 2

- [x] 3.0 Complete CLI layer for multi-repository support
  - [x] 3.1 Write 2-8 focused tests for CLI multi-repo functionality
    - Limit to 2-8 highly focused tests maximum
    - Test only critical CLI behaviors: multiple --repo flags, --branch pairing, error handling, progress display
    - Skip exhaustive testing of all CLI argument combinations
  - [x] 3.2 Extend sync command to accept multiple --repo flags
    - Update: --repo parameter to support multiple=True in typer.Option
    - Update: --branch parameter to support multiple=True for paired repo/branch specification
    - Logic: when CLI provides --repo flags, use those instead of config.yaml repos list
    - Process: flags in pairs for --repo URL --branch BRANCH syntax
    - Location: src/prompt_unifier/cli/commands.py:385
  - [x] 3.3 Implement CLI argument processing for multi-repo
    - Parse: multiple --repo flags into list of repository configs
    - Validate: ensure --branch flags align with --repo flags if both provided
    - Priority: CLI flags > config.yaml repos > error if none
    - Build: list[RepositoryConfig] from CLI arguments
  - [x] 3.4 Update sync command progress display
    - Display: each repository being synced with Rich console formatting
    - Show: repository URL, branch (if specified), and progress indicator
    - Show: commit hash for each successfully synced repository
    - Display: conflict feedback during sync process
    - Reuse pattern from: existing Rich console usage in CLI commands
  - [x] 3.5 Enhance error handling for multi-repo scenarios
    - Handle: validation failures with clear per-repository error messages
    - Handle: authentication failures with helpful troubleshooting info
    - Handle: network failures with retry suggestions
    - Exit: gracefully without partial sync on any repository failure
  - [x] 3.6 Update sync command completion message
    - Display: summary showing all successfully synced repositories
    - Show: repository URL, branch, and commit hash for each source
    - Show: total number of files synced and number of conflicts detected
    - Display: path to .repo-metadata.json for audit trail
  - [x] 3.7 Ensure CLI layer tests pass
    - Run ONLY the 2-8 tests written in 3.1
    - Verify multiple --repo flags are parsed correctly
    - Verify error messages are clear and helpful
    - Verify progress display shows all repositories
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 3.1 pass
- sync command accepts and processes multiple --repo flags
- CLI arguments override config.yaml repos when provided
- Progress display shows each repository with Rich formatting
- Error handling provides clear, actionable messages
- Completion message summarizes all synced repositories

---

### Testing & Integration

#### Task Group 4: Test Review & End-to-End Integration
**Dependencies:** Task Groups 1-3

- [x] 4.0 Review existing tests and fill critical gaps only
  - [x] 4.1 Review tests from Task Groups 1-3
    - Review the 2-8 tests written for configuration layer (Task 1.1)
    - Review the 2-8 tests written for Git service layer (Task 2.1)
    - Review the 2-8 tests written for CLI layer (Task 3.1)
    - Total existing tests: approximately 6-24 tests
  - [x] 4.2 Analyze test coverage gaps for THIS feature only
    - Identify critical multi-repo workflows that lack test coverage
    - Focus ONLY on gaps related to multi-repository sync requirements
    - Do NOT assess entire application test coverage
    - Prioritize end-to-end workflows: config → validate → sync → verify results
    - Check for gaps in: fail-fast validation, last-wins merge, conflict detection, metadata generation
  - [x] 4.3 Write up to 10 additional strategic tests maximum
    - Add maximum of 10 new integration tests to fill identified critical gaps
    - Focus on end-to-end workflows: full multi-repo sync with conflicts, authentication across repos, selective filtering across repos
    - Test critical scenarios: validation failure on second repo, conflicting files from 3+ repos, branch-specific syncing
    - Test metadata accuracy: verify .repo-metadata.json correctly maps files to source repos
    - Do NOT write comprehensive coverage for all edge cases
    - Skip performance tests and stress testing unless business-critical
  - [x] 4.4 Create end-to-end integration test scenarios
    - Scenario 1: Sync 3 repos with overlapping files, verify last-wins behavior and conflict reporting
    - Scenario 2: Sync with per-repo branch configuration, verify correct branches checked out
    - Scenario 3: Sync with selective file patterns, verify only matching files included
    - Scenario 4: Fail-fast validation with one invalid repo in list of 3
    - Use: real Git repositories or mocked Git operations for test reliability
  - [x] 4.5 Verify metadata and storage correctness
    - Test: .repo-metadata.json contains accurate file-to-repo mappings
    - Test: storage directory completely replaced on sync (not incremental)
    - Test: repository metadata list in config updated correctly
    - Verify: last_sync_timestamp updated after successful multi-repo sync
  - [x] 4.6 Test CLI integration with real-world scenarios
    - Test: CLI --repo flags override config.yaml repos
    - Test: Multiple --repo and --branch flags processed correctly
    - Test: Progress display and completion messages show all repos
    - Test: Error handling provides clear messages for common failures
  - [x] 4.7 Run feature-specific tests only
    - Run ONLY tests related to multi-repository sync feature (tests from 1.1, 2.1, 3.1, and 4.3)
    - Expected total: approximately 16-34 tests maximum
    - Do NOT run the entire application test suite
    - Verify critical multi-repo workflows pass
  - [x] 4.8 Document integration test scenarios and results
    - Document: test scenarios covered in feature-specific tests
    - Document: any known limitations or edge cases not covered
    - Create: simple testing checklist for manual verification if needed
    - Location: tests/integration/test_multi_repo_sync.py or similar

**Acceptance Criteria:**
- All feature-specific tests pass (approximately 16-34 tests total)
- Critical multi-repo workflows are covered by integration tests
- No more than 10 additional tests added when filling in testing gaps
- Testing focused exclusively on multi-repository sync requirements
- End-to-end scenarios verify: validation, sync, merge, conflict detection, metadata generation
- .repo-metadata.json accuracy verified
- CLI integration tested with real-world scenarios

---

## Execution Order

Recommended implementation sequence:
1. Configuration & Data Models Layer (Task Group 1) - Foundation for multi-repo support
2. Git Service Layer (Task Group 2) - Core multi-repo sync operations
3. CLI Layer (Task Group 3) - User-facing multi-repo commands
4. Test Review & End-to-End Integration (Task Group 4) - Comprehensive validation

## Technical Notes

**Key Design Decisions:**
- Last-wins merge strategy: repositories processed in order, later repos override earlier ones
- Fail-fast validation: all repos validated before any sync begins
- Complete storage replacement: entire storage cleared and repopulated on multi-repo sync
- Per-repository configuration: each repo can have different branch, auth, and file filters
- Metadata tracking: .repo-metadata.json maps every file to its source repository

**Critical Dependencies:**
- Task Group 2 depends on RepositoryConfig and GitConfig models from Task Group 1
- Task Group 3 depends on sync_multiple_repos() orchestration from Task Group 2
- Task Group 4 requires all layers complete for end-to-end testing

**Reusable Components:**
- GitService.clone_to_temp() extended with branch/auth parameters (used by all sync operations)
- PathFilter utility (used by selective file syncing in sync orchestration)
- RepoMetadata utility (used by sync orchestration and CLI for tracking)
- ConfigManager multi-repo methods (used by CLI and sync operations)
