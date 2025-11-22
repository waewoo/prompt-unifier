# Task Breakdown: Windows Test Compatibility Fixes

## Overview
Total Tasks: 7 task groups with 42 sub-tasks

## Task List

### Core Compatibility Fixes

#### Task Group 1: Path Normalization
**Dependencies:** None
**Effort:** `M` (1 week)

- [x] 1.0 Complete path separator normalization across test suite
  - [x] 1.1 Write 4-6 focused tests for path normalization utilities
    - Test `Path.as_posix()` conversion on Windows-style paths
    - Test native path format preservation for file operations
    - Test path comparison assertions with normalized paths
    - Test edge cases (UNC paths, drive letters, relative paths)
  - [x] 1.2 Audit all test files for path string comparisons
    - Search for `assert.*str(path)` patterns
    - Search for path string equality checks
    - Document all files requiring changes
  - [x] 1.3 Create path normalization helper function
    - Add to `tests/conftest.py` or create `tests/utils/path_helpers.py`
    - Function: `normalize_path_for_comparison(path) -> str`
    - Uses `Path(path).as_posix()` internally
  - [x] 1.4 Update path assertions in test files
    - Apply `Path.as_posix()` to all path comparisons
    - Preserve native format for actual file system operations
    - Target files in `tests/core/`, `tests/cli/`, `tests/handlers/`
  - [x] 1.5 Ensure path normalization tests pass
    - Run ONLY the 4-6 tests written in 1.1
    - Verify on both Windows and Linux path formats
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 4-6 tests written in 1.1 pass
- All path comparisons use normalized format
- File operations still use native paths
- No hardcoded path separators in assertions

---

#### Task Group 2: UTF-8 Encoding Standardization
**Dependencies:** None
**Effort:** `M` (1 week)

- [x] 2.0 Complete UTF-8 encoding standardization
  - [x] 2.1 Write 4-6 focused tests for encoding fixes
    - Test `open()` with explicit encoding parameter
    - Test `Path.write_text()` with encoding parameter
    - Test `Path.read_text()` with encoding parameter
    - Test files with non-ASCII characters (emojis, special chars)
  - [x] 2.2 Audit test files for encoding issues
    - Search for `open(` without `encoding=` parameter
    - Search for `write_text(` without `encoding=` parameter
    - Search for `read_text(` without `encoding=` parameter
    - Document all instances requiring changes
  - [x] 2.3 Update `open()` calls in test files
    - Add `encoding="utf-8"` to all `open()` calls
    - Follow pattern from `/root/travail/prompt-unifier/src/prompt_unifier/config/manager.py`
    - Target: `tests/config/`, `tests/core/`, `tests/handlers/`
  - [x] 2.4 Update Path method calls in test files
    - Use `Path.write_text(content, encoding="utf-8")` pattern
    - Use `Path.read_text(encoding="utf-8")` pattern
    - Follow pattern from `/root/travail/prompt-unifier/tests/core/test_validator.py`
  - [x] 2.5 Update source code file operations (if needed)
    - Audit `src/prompt_unifier/` for missing encoding parameters
    - Add `encoding="utf-8"` where missing
    - Ensure consistency with existing patterns
  - [x] 2.6 Ensure UTF-8 encoding tests pass
    - Run ONLY the 4-6 tests written in 2.1
    - Verify non-ASCII content is handled correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 4-6 tests written in 2.1 pass
- All `open()` calls have explicit `encoding="utf-8"`
- All `Path.write_text()` and `Path.read_text()` have encoding parameter
- No cp1252 encoding errors on Windows

---

#### Task Group 3: Symlink Test Handling
**Dependencies:** None
**Effort:** `S` (2-3 days)

- [x] 3.0 Complete symlink test handling for Windows
  - [x] 3.1 Write 2-4 focused tests for skipif behavior
    - Test that skipif marker is applied correctly on Windows
    - Test that symlink tests still run on Linux
    - Test platform detection logic
  - [x] 3.2 Identify all symlink-dependent tests
    - Primary target: `/root/travail/prompt-unifier/tests/core/test_encoding.py::test_encoding_with_symlink`
    - Search for `os.symlink`, `Path.symlink_to`, `is_symlink()` in tests
    - Document all tests requiring skip markers
  - [x] 3.3 Add pytest skipif markers to symlink tests
    - Use `@pytest.mark.skipif(platform.system() == "Windows", reason="Symlinks require elevated privileges on Windows")`
    - Import `platform` module where needed
    - Add clear, descriptive skip reasons
  - [x] 3.4 Document skipped tests
    - Add comments explaining why tests are skipped
    - Note any future alternatives if applicable
  - [x] 3.5 Ensure symlink handling tests pass
    - Run ONLY the 2-4 tests written in 3.1
    - Verify skip behavior on Windows platform detection
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-4 tests written in 3.1 pass
- Symlink tests are properly skipped on Windows
- Symlink tests still execute on Linux
- Skip reasons are clear and documented

---

#### Task Group 4: File Locking and Context Manager Fixes
**Dependencies:** None
**Effort:** `S` (2-3 days)

- [x] 4.0 Complete file locking and context manager improvements
  - [x] 4.1 Write 3-5 focused tests for file locking scenarios
    - Test file handle closure before subsequent operations
    - Test backup/rollback scenarios with proper cleanup
    - Test context manager proper exit behavior
    - Test concurrent file access patterns
  - [x] 4.2 Audit tests for file locking issues
    - Search for file operations without context managers
    - Identify backup/rollback test scenarios
    - Find tests with potential file handle leaks
    - Target: `tests/handlers/`, `tests/core/`
  - [x] 4.3 Refactor file operations to use context managers
    - Wrap all file `open()` calls in `with` statements
    - Ensure handles are closed before file move/delete operations
    - Follow pattern from `/root/travail/prompt-unifier/src/prompt_unifier/repo_metadata.py`
  - [x] 4.4 Fix backup/rollback test scenarios
    - Ensure file handles are closed before backup operations
    - Add explicit `close()` or use context managers
    - Verify cleanup in test fixtures and teardown
  - [x] 4.5 Ensure file locking tests pass
    - Run ONLY the 3-5 tests written in 4.1
    - Verify no "file in use" errors on Windows
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 3-5 tests written in 4.1 pass
- All file operations use context managers
- No file locking errors on Windows
- Proper resource cleanup in all tests

---

### CI/CD Configuration

#### Task Group 5: Windows CI/CD Setup
**Dependencies:** Task Groups 1-4
**Effort:** `M` (1 week)

- [x] 5.0 Complete Windows CI/CD configuration
  - [x] 5.1 Research GitLab.com Windows runner availability
    - Check GitLab.com SaaS runner documentation
    - Verify Windows runner availability for free/paid tiers
    - Document findings and limitations
  - [x] 5.2 Create Windows CI job configuration
    - Add Windows job to `.gitlab-ci.yml`
    - Configure appropriate Python version
    - Set up Poetry and dependencies installation
  - [x] 5.3 Configure test matrix for cross-platform validation
    - Define Linux and Windows test stages
    - Set appropriate tags for runner selection
    - Configure parallel execution if supported
  - [x] 5.4 Document alternative approaches
    - If SaaS Windows runners unavailable, document:
      - Self-hosted runner setup
      - GitHub Actions alternative
      - Local testing requirements
  - [x] 5.5 Test CI configuration
    - Push changes to trigger CI pipeline
    - Verify Windows job runs successfully
    - Document any issues and resolutions

**Acceptance Criteria:**
- GitLab.com Windows runner availability documented
- `.gitlab-ci.yml` updated with Windows job (if supported)
- Test matrix configured for cross-platform validation
- Alternative approaches documented if needed

---

### Test Cleanup

#### Task Group 6: Test Refactoring and Cleanup
**Dependencies:** Task Groups 1-4
**Effort:** `L` (2 weeks)

- [x] 6.0 Complete test refactoring and cleanup
  - [x] 6.1 Write 4-6 focused tests for refactored patterns
    - Test consistent fixture patterns
    - Test helper function behaviors
    - Test improved test organization
  - [x] 6.2 Standardize test patterns across suite
    - Apply consistent fixture usage
    - Standardize setup/teardown patterns
    - Use consistent assertion styles
  - [x] 6.3 Create shared test utilities
    - Extract common patterns to `tests/conftest.py`
    - Create reusable fixtures for file operations
    - Add helper functions for common test scenarios
  - [x] 6.4 Improve test organization and readability
    - Add docstrings to test functions
    - Group related tests logically
    - Use descriptive test names
  - [x] 6.5 Remove code duplication
    - Identify duplicate setup code
    - Extract to shared fixtures
    - Apply DRY principles
  - [x] 6.6 Verify test coverage is maintained
    - Run coverage report
    - Ensure no regression in coverage
    - Document any coverage changes
  - [x] 6.7 Ensure refactored tests pass
    - Run ONLY the 4-6 tests written in 6.1
    - Verify refactored patterns work correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 4-6 tests written in 6.1 pass
- Consistent patterns across test suite
- Improved code organization and readability
- Test coverage maintained or improved

---

### Final Verification

#### Task Group 7: Test Review and Final Verification
**Dependencies:** Task Groups 1-6
**Effort:** `S` (2-3 days)

- [x] 7.0 Review and verify all fixes
  - [x] 7.1 Review tests from Task Groups 1-6
    - Review the 4-6 tests written for path normalization (Task 1.1)
    - Review the 4-6 tests written for UTF-8 encoding (Task 2.1)
    - Review the 2-4 tests written for symlink handling (Task 3.1)
    - Review the 3-5 tests written for file locking (Task 4.1)
    - Review the 4-6 tests written for refactoring (Task 6.1)
    - Total existing tests: approximately 17-27 tests
  - [x] 7.2 Analyze test coverage gaps
    - Identify any critical workflows lacking coverage
    - Focus ONLY on Windows compatibility gaps
    - Prioritize integration tests over unit tests
  - [x] 7.3 Write up to 8 additional tests if needed
    - Fill critical gaps identified in 7.2
    - Focus on cross-platform edge cases
    - Do NOT write exhaustive coverage
  - [x] 7.4 Run full test suite on both platforms
    - Run all 48 tests on Linux
    - Run all 48 tests on Windows (local or CI)
    - Verify all tests pass
  - [x] 7.5 Run `make check` for final validation
    - Execute `make check` command
    - Verify lint, typecheck, and tests all pass
    - Document any remaining issues
  - [x] 7.6 Create verification report
    - Document all fixes applied
    - List tests modified
    - Confirm 48/48 tests passing

**Acceptance Criteria:**
- All 48 tests pass on both Windows and Linux
- `make check` passes completely
- No more than 8 additional tests added
- Verification report completed

---

## Execution Order

Recommended implementation sequence:

1. **Task Groups 1-4 (Parallel)** - Core compatibility fixes can be done in parallel:
   - Path Normalization (Task Group 1)
   - UTF-8 Encoding (Task Group 2)
   - Symlink Handling (Task Group 3)
   - File Locking (Task Group 4)

2. **Task Group 5: Windows CI/CD Setup** - Configure after core fixes are in place

3. **Task Group 6: Test Refactoring** - Clean up and standardize after compatibility fixes

4. **Task Group 7: Final Verification** - Run complete verification after all other tasks

---

## Files Likely to Be Modified

### Test Files
- `tests/core/test_encoding.py` - Symlink skip markers, encoding fixes
- `tests/core/test_validator.py` - Path normalization, encoding fixes
- `tests/config/test_manager.py` - Encoding fixes, context managers
- `tests/handlers/test_continue_handler_base_path.py` - Reference for patterns
- `tests/handlers/*.py` - Various compatibility fixes
- `tests/cli/*.py` - Path normalization fixes
- `tests/conftest.py` - Shared fixtures and utilities

### Configuration Files
- `.gitlab-ci.yml` - Windows CI job configuration

### Utility Files (may be created)
- `tests/utils/path_helpers.py` - Path normalization utilities (optional)

---

## Effort Summary

| Task Group | Description | Effort | Est. Time |
|------------|-------------|--------|-----------|
| 1 | Path Normalization | M | 1 week |
| 2 | UTF-8 Encoding | M | 1 week |
| 3 | Symlink Handling | S | 2-3 days |
| 4 | File Locking | S | 2-3 days |
| 5 | Windows CI/CD | M | 1 week |
| 6 | Test Refactoring | L | 2 weeks |
| 7 | Final Verification | S | 2-3 days |

**Total Estimated Effort:** 6-7 weeks (with Task Groups 1-4 parallelized: 4-5 weeks)
