# Multi-Repository Sync Integration Test Scenarios

This document describes the end-to-end integration test scenarios for the multi-repository sync feature.

## Test Coverage Summary

**Total Tests**: 30 tests across 4 test files
- Task Group 1 (Models): 8 tests
- Task Group 2 (Git Service): 7 tests
- Task Group 3 (CLI): 8 tests
- Task Group 4 (Integration): 7 tests

## Integration Test Scenarios

### 1. Three-Repository Conflict Resolution (`TestThreeRepoConflictResolution`)

**Scenario**: Sync 3 repositories that all contain the same file path with different content.

**Test**: `test_last_wins_with_three_overlapping_repos`

**Steps**:
1. Configure 3 repositories with identical file path `prompts/example.md`
2. Each repo has different content for the file
3. Sync all repositories in order (repo1 → repo2 → repo3)

**Expected Results**:
- Final file content matches repo3 (last-wins strategy)
- Conflict warnings displayed for 2 overwrites (repo1→repo2, repo2→repo3)
- Metadata tracks file source as repo3

**Coverage**: Last-wins merge strategy with 3+ repositories

---

### 2. Branch-Specific Multi-Repo Sync (`TestBranchSpecificMultiRepoSync`)

**Scenario**: Sync multiple repositories where each is configured to use a different branch.

**Test**: `test_sync_with_different_branches_per_repo`

**Steps**:
1. Configure 3 repositories with different branches:
   - repo1: `main`
   - repo2: `develop`
   - repo3: `feature-xyz`
2. Sync all repositories

**Expected Results**:
- Each repository cloned from its specified branch
- Metadata tracks correct branch for each repository
- All branch-specific content correctly synced

**Coverage**: Per-repository branch configuration in multi-repo workflow

---

### 3. Selective Filtering Metadata Tracking (`TestSelectiveFilteringMetadataTracking`)

**Scenario**: Verify that include/exclude patterns affect metadata tracking.

**Test**: `test_metadata_only_tracks_filtered_files`

**Steps**:
1. Configure repository with include pattern `**/*.md`
2. Repository contains both `.md` and `.txt` files
3. Sync repository

**Expected Results**:
- `.md` files tracked in metadata
- `.txt` files NOT tracked in metadata
- Note: Current implementation copies all files to storage but filters metadata tracking

**Coverage**: Selective file filtering in metadata (known limitation documented)

---

### 4. Metadata Accuracy Verification (`TestMetadataAccuracyVerification`)

**Scenario**: Verify .repo-metadata.json contains accurate file-to-repository mappings.

**Test**: `test_metadata_file_contains_accurate_mappings`

**Steps**:
1. Configure 2 repositories with different files
2. Sync both repositories
3. Load .repo-metadata.json and verify contents

**Expected Results**:
- .repo-metadata.json created in storage root
- Each file correctly mapped to its source repository
- Metadata includes URL, branch, commit, timestamp for each file
- Repositories list contains all synced repos

**Coverage**: Metadata file accuracy and structure

---

### 5. Complete Storage Replacement (`TestCompleteStorageReplacement`)

**Scenario**: Verify storage directory is completely cleared before multi-repo sync.

**Test**: `test_storage_cleared_before_multi_repo_sync`

**Steps**:
1. Create storage directory with existing files and metadata
2. Sync new repository with different files
3. Verify old files removed

**Expected Results**:
- All old files removed from storage
- Only new repository's files present
- Old metadata replaced with new metadata
- No orphaned files from previous sync

**Coverage**: Complete storage replacement (non-incremental sync)

---

### 6. CLI to Storage End-to-End (`TestCLIToStorageEndToEnd`)

**Scenario**: Test complete workflow from CLI command through to storage and config updates.

**Test**: `test_cli_sync_creates_correct_metadata_structure`

**Steps**:
1. Execute CLI `sync` command with repository URLs
2. Verify GitService called with correct parameters
3. Verify config updated with repository metadata

**Expected Results**:
- GitService.sync_multiple_repos called with correct repos and storage path
- ConfigManager.update_multi_repo_sync_info called with metadata
- Metadata contains correct repository information

**Coverage**: End-to-end CLI → GitService → ConfigManager integration

---

### 7. Fail-Fast Validation (`TestFailFastValidationWithMultipleRepos`)

**Scenario**: Verify validation stops immediately when a repository fails validation.

**Test**: `test_validation_fails_on_invalid_repo_without_syncing`

**Steps**:
1. Configure 3 repositories where second repository is invalid (missing prompts/ directory)
2. Attempt multi-repo sync
3. Verify sync stops at second repository

**Expected Results**:
- Validation fails on second repository
- Third repository never validated (fail-fast)
- Error message clearly identifies failed repository (2/3)
- Storage directory not created (no partial sync)

**Coverage**: Fail-fast validation behavior in multi-repo scenario

---

## Known Limitations (Documented in Tests)

1. **Selective Filtering**: Current implementation copies ALL files from `prompts/` and `rules/` directories to storage, but only tracks filtered files in metadata. Include/exclude patterns only affect metadata tracking, not actual file copying.

   This limitation is documented in:
   - Test file header comment
   - `TestSelectiveFilteringMetadataTracking` class docstring
   - Individual test comments

## Test Execution

Run all multi-repository feature tests:
```bash
poetry run pytest tests/models/test_repository_config.py \
                 tests/git/test_multi_repo_operations.py \
                 tests/cli/test_multi_repo_sync.py \
                 tests/integration/test_multi_repo_e2e.py -v
```

Expected: 30 tests, all passing

## Critical Workflows Covered

1. ✅ End-to-end: CLI → GitService → metadata → storage
2. ✅ Conflict resolution with 3+ repositories
3. ✅ Branch-specific syncing across multiple repos
4. ✅ Selective filtering (metadata tracking)
5. ✅ Metadata accuracy and structure
6. ✅ Complete storage replacement
7. ✅ Fail-fast validation behavior
