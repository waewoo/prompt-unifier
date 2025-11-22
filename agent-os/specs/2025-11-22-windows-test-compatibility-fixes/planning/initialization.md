# Spec Initialization: Windows Test Compatibility Fixes

## Raw Idea

**Feature:** Windows Test Compatibility Fixes

**Description:** Fix 48 pre-existing test failures on Windows related to path separators (`\` vs `/`), Unicode encoding (cp1252 vs UTF-8), symlink permissions, and file locking issues. Tests pass on Linux but fail on Windows. Normalize path comparisons using `Path.as_posix()`, force UTF-8 encoding in all file operations, skip symlink tests on Windows, and fix backup/rollback file locking issues. This will ensure `make check` passes on both Windows and Linux.

## Source

Selected from product roadmap item 11.5

## Date Initialized

2025-11-22
