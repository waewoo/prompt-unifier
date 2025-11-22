# Spec Requirements: Windows Test Compatibility Fixes

## Initial Description
Fix 48 pre-existing test failures on Windows related to path separators (`\` vs `/`), Unicode encoding (cp1252 vs UTF-8), symlink permissions, and file locking issues. Tests pass on Linux but fail on Windows. Normalize path comparisons using `Path.as_posix()`, force UTF-8 encoding in all file operations, skip symlink tests on Windows, and fix backup/rollback file locking issues. This will ensure `make check` passes on both Windows and Linux.

## Requirements Discussion

### First Round Questions

**Q1:** I assume we should fix all 48 failing tests in a single effort rather than prioritizing certain categories (path separators, encoding, symlinks, file locking). Is that correct, or should we tackle them in phases?
**Answer:** Correct - proceed with all tests together in a single effort.

**Q2:** For symlink tests, I'm thinking we should use `pytest.mark.skipif` with `platform.system() == "Windows"` to conditionally skip them. Should we instead try to find Windows-compatible alternatives for symlink functionality?
**Answer:** Use `pytest.mark.skipif` with `platform.system() == "Windows"` to skip symlink tests.

**Q3:** I assume path normalization should use `Path.as_posix()` for comparisons while preserving native format for actual file operations. Is that correct?
**Answer:** Yes - use `Path.as_posix()` for comparisons while preserving native format for operations.

**Q4:** For UTF-8 encoding fixes, should we add explicit `encoding="utf-8"` parameters to all `open()` calls, or should we set `PYTHONUTF8=1` environment variable in the test configuration?
**Answer:** Add explicit `encoding="utf-8"` parameters to all `open()` calls, keep it purely code-based (no env vars).

**Q5:** For file locking issues in backup/rollback operations, I assume we should use context managers more strictly to ensure file handles are closed before attempting file operations. Is that the approach, or should we implement retry logic with backoff?
**Answer:** Use context managers more strictly to ensure handles are closed before file operations.

**Q6:** Should we also update CI/CD to run tests on Windows (e.g., via GitHub Actions matrix or similar), or focus solely on fixing the tests themselves?
**Answer:** Yes, if possible to run on Windows on GitLab.com SaaS solution.

**Q7:** Are there any tests that we should consider refactoring beyond what's strictly needed for cross-platform compatibility?
**Answer:** Refactor tests significantly beyond what's needed for cross-platform compatibility (user wants more extensive cleanup).

**Q8:** Is there anything that should explicitly be excluded from this effort (e.g., performance optimizations, adding new test coverage)?
**Answer:** Performance optimizations are out of scope.

### Existing Code to Reference
[Based on user's request to check codebase for existing patterns]

**Similar Features Identified:**
- Feature: Platform-specific test skipping - Path: `/root/travail/prompt-unifier/tests/handlers/test_continue_handler_base_path.py`
  - Uses `@pytest.mark.skipif(os.name == "nt", reason="Permission handling different on Windows")`
  - This is the established pattern for Windows-specific test skipping
- Feature: UTF-8 encoding in config manager - Path: `/root/travail/prompt-unifier/src/prompt_unifier/config/manager.py`
  - Consistently uses `encoding="utf-8"` with all `open()` calls
  - Pattern to replicate across all file operations
- Feature: UTF-8 encoding in tests - Path: `/root/travail/prompt-unifier/tests/config/test_manager.py`
  - Multiple examples of `with open(config_path, encoding="utf-8")` pattern
  - Context managers properly used with encoding parameter
- Feature: UTF-8 encoding in validators - Path: `/root/travail/prompt-unifier/tests/core/test_validator.py`
  - Uses `test_file.write_text(content, encoding="utf-8")` pattern
  - Path.write_text() with encoding is preferred pattern
- Feature: Symlink tests - Path: `/root/travail/prompt-unifier/tests/core/test_encoding.py`
  - Contains `test_encoding_with_symlink` test
  - Needs Windows skipif marker added

### Follow-up Questions
None required - user provided comprehensive answers and codebase patterns are well-established.

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
Not applicable - this is a test infrastructure fix with no UI components.

## Requirements Summary

### Functional Requirements
- Fix all 27 failing tests to pass on both Windows and Linux
- Normalize path comparisons using `Path.as_posix()` throughout test suite
- Add explicit `encoding="utf-8"` to all `open()` calls missing it
- Skip symlink-dependent tests on Windows using `pytest.mark.skipif`
- Fix file locking issues by ensuring context managers properly close handles
- Refactor tests for improved quality and maintainability (beyond strict compatibility fixes)
- Configure GitLab CI/CD to run tests on Windows (if supported by SaaS)

### Reusability Opportunities
- **Platform skipif pattern**: Existing pattern in `test_continue_handler_base_path.py` uses `os.name == "nt"` - can also use `platform.system() == "Windows"` for consistency
- **UTF-8 encoding pattern**: Multiple established patterns in `config/manager.py` and `tests/config/test_manager.py` to follow
- **Path.write_text() pattern**: Used in `tests/core/test_validator.py` with encoding parameter
- **Context manager pattern**: Established in config manager for file operations

### Scope Boundaries
**In Scope:**
- Fixing all 48 failing Windows tests
- Path normalization for cross-platform compatibility
- UTF-8 encoding standardization
- Symlink test skipping on Windows
- File handle/locking fixes
- Test refactoring and cleanup
- GitLab CI/CD Windows configuration (if feasible)

**Out of Scope:**
- Performance optimizations
- Adding new test coverage beyond what's needed for compatibility
- Changing core application behavior (tests only)

### Technical Considerations
- Use `platform.system() == "Windows"` or `os.name == "nt"` for platform detection (both patterns exist in codebase)
- Prefer `Path.as_posix()` for path string comparisons only, not for actual file operations
- Use `Path.write_text(content, encoding="utf-8")` and `Path.read_text(encoding="utf-8")` as preferred patterns
- Ensure all context managers properly close file handles before subsequent operations
- GitLab.com SaaS Windows runners availability needs verification
- Test refactoring should improve maintainability while maintaining test coverage
