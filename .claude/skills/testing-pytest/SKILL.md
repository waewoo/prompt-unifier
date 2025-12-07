---
name: Testing Pytest
description: Write and organize Python tests using pytest framework with fixtures, parametrization, mocking, and pytest conventions for isolated, deterministic, and maintainable test suites. Use this skill when writing Python test files, when creating pytest fixtures, when using pytest-mock for mocking, when parametrizing tests, when organizing tests in tests/ directory, when using pytest markers, when configuring pytest.ini or pyproject.toml, or when running pytest commands. Apply when writing test functions with test_ prefix, when using @pytest.fixture decorators, when using assert statements, when mocking with mocker fixture, or when running pytest with specific options.
---

# Testing Pytest

This Skill provides Claude Code with specific guidance on how to adhere to coding standards as they relate to how it should handle testing pytest.

## When to use this skill

- When writing Python test files (test_*.py or *_test.py)
- When creating pytest fixtures using @pytest.fixture decorator
- When using pytest-mock (mocker fixture) for mocking external dependencies
- When parametrizing tests with @pytest.mark.parametrize
- When organizing test files in the `tests/` directory mirroring source structure
- When using pytest markers (@pytest.mark.skip, @pytest.mark.slow, etc.)
- When configuring pytest settings in `pytest.ini` or `pyproject.toml`
- When running pytest commands (pytest, pytest -v, pytest --cov, etc.)
- When writing test functions with `test_` prefix naming convention
- When using assert statements for test expectations
- When mocking functions, methods, or objects with the mocker fixture
- When creating conftest.py files for shared fixtures
- When running specific test files, modules, or test functions

## Instructions

For details, refer to the information provided in this file:
[testing pytest](../../../agent-os/standards/testing/pytest.md)
