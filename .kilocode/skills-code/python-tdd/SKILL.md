---
name: python-tdd
description: Enforces Test-Driven Development workflow for Python projects using pytest,
  guiding the red-green-refactor cycle and test best practices.
mode: code
license: MIT
---
# Python TDD Skill

## When to Use

Apply this skill when:
- The user asks to implement a new function, class, or feature in Python
- The user asks to add tests to existing code
- The user asks "how should I test this?"
- A bug fix is requested — write a regression test first

Do NOT apply when the user explicitly asks to skip tests or when the code is a one-off script with no logic to test.

## The Cycle

```
1. RED   → Write a failing test that describes the desired behaviour
2. GREEN → Write the minimal code to make the test pass
3. REFACTOR → Clean up code and tests while keeping tests green
```

Never write implementation code before a failing test exists.

## Test Structure (Arrange-Act-Assert)

```python
def test_<unit>_<scenario>_<expected>():
    # Arrange
    input_data = ...

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result == expected_value
```

## Pytest Conventions

- Mirror source structure: `src/module/foo.py` → `tests/module/test_foo.py`
- Use fixtures for shared setup, not `setUp` methods
- Parametrize to avoid duplicated test logic:
  ```python
  @pytest.mark.parametrize("value,expected", [
      (1, True),
      (0, False),
  ])
  def test_is_positive(value, expected):
      assert is_positive(value) == expected
  ```
- Mock external dependencies (filesystem, HTTP, DB) with `pytest-mock` or `unittest.mock`
- Never let tests depend on each other or on execution order

## What to Test

- **Happy path**: normal inputs produce correct outputs
- **Edge cases**: empty inputs, boundary values, None
- **Error cases**: invalid inputs raise the right exceptions
- **Side effects**: functions that write files, call APIs, etc.

## What NOT to Test

- Third-party library internals
- Pure configuration (no logic)
- Trivial getters/setters with no logic

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run a specific test
pytest tests/module/test_foo.py::test_specific_case

# Run tests matching a keyword
pytest -k "dag"
```

## Minimum Coverage

Aim for >80% coverage on new code. Focus on meaningful coverage, not vanity metrics.