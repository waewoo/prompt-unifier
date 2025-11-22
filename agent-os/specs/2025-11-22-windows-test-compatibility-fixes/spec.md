# Specification: Windows Test Compatibility Fixes

## Goal
Fix 48 failing tests on Windows related to path separators, UTF-8 encoding, symlink permissions, and file locking to ensure `make check` passes on both Windows and Linux platforms.

## User Stories
- As a developer on Windows, I want all tests to pass so that I can confidently develop and test features locally
- As a CI maintainer, I want cross-platform test compatibility so that the pipeline catches issues regardless of the runner's OS
- As a contributor, I want consistent test behavior across platforms so that my PRs don't fail unexpectedly due to OS differences

## Specific Requirements

**Path Separator Normalization**
- Use `Path.as_posix()` for all path string comparisons in tests
- Preserve native path format for actual file system operations
- Apply normalization consistently across all test assertions involving paths
- Target assertions that compare path strings (e.g., `assert str(path) == "expected/path"`)

**UTF-8 Encoding Standardization**
- Add explicit `encoding="utf-8"` parameter to all `open()` calls
- Use `Path.write_text(content, encoding="utf-8")` and `Path.read_text(encoding="utf-8")` patterns
- No environment variable configuration (pure code-based approach)
- Address Windows default cp1252 encoding issues

**Symlink Test Handling**
- Add `@pytest.mark.skipif(platform.system() == "Windows", reason="Symlinks require elevated privileges on Windows")` to symlink-dependent tests
- Target test at `/root/travail/prompt-unifier/tests/core/test_encoding.py::test_encoding_with_symlink`
- Document skip reasons clearly for future reference

**File Locking and Context Manager Improvements**
- Ensure all file handles are properly closed before subsequent file operations
- Use context managers (`with` statements) for all file operations
- Address backup/rollback scenarios where file locks prevent operations
- Ensure proper resource cleanup in test fixtures and teardown

**Windows CI/CD Configuration**
- Investigate GitLab.com SaaS Windows runner availability
- Configure `.gitlab-ci.yml` with Windows job if supported
- Set up appropriate test matrix for cross-platform validation
- Document alternative approaches if SaaS Windows runners unavailable

**Test Refactoring and Cleanup**
- Refactor tests beyond strict compatibility fixes for improved maintainability
- Apply consistent patterns across the test suite
- Improve test organization and readability
- Maintain or improve existing test coverage

## Visual Design
No visual assets provided - this is a test infrastructure fix with no UI components.

## Existing Code to Leverage

**Platform skipif pattern in test_continue_handler_base_path.py**
- Uses `@pytest.mark.skipif(os.name == "nt", reason="...")` pattern
- Established pattern for Windows-specific test skipping
- Alternative: `platform.system() == "Windows"` for consistency

**UTF-8 encoding in config/manager.py**
- Uses `with open(config_path, encoding="utf-8") as f:` pattern consistently
- Demonstrates proper context manager usage with encoding
- Pattern to replicate across all file operations in tests and source

**Path methods in continue_handler.py**
- Uses `Path.write_text(content, encoding="utf-8")` pattern
- Uses `Path.read_text(encoding="utf-8")` pattern
- Preferred over raw `open()` calls for file I/O

**test_encoding.py symlink test**
- Contains `test_encoding_with_symlink` that needs Windows skip marker
- Shows current symlink testing approach to preserve on Linux

**Context manager patterns in repo_metadata.py**
- Demonstrates proper file handle management with `with open(...)`
- Pattern for ensuring file handles are closed before operations

## Out of Scope
- Performance optimizations of tests or source code
- Adding new test coverage beyond what is needed for compatibility fixes
- Changing core application behavior (test-only changes)
- Migrating to alternative test frameworks
- Windows-specific feature implementations
- Changing Python version requirements
- Modifying CI/CD for non-Windows platforms
- Implementing Windows-compatible symlink alternatives
- Automated encoding detection or conversion
- Changes to production file I/O patterns (focus on tests)
