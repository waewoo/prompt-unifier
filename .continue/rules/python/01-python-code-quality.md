---
name: Python Code Quality Standards
description: Comprehensive standards for writing clean, readable, and efficient Python
  code across all projects.
globs:
- '**/*.py'
alwaysApply: false
category: standards
version: 1.0.0
tags:
- python
- standards
- quality
- pep8
- logging
- type-hints
author: prompt-manager
language: python
---
# Python Code Quality Standards

This document outlines Python-specific coding standards for all code written in Python.

## 1. Code Style and Formatting

- **PEP 8**: All Python code must adhere to the [PEP 8 style guide](https://peps.python.org/pep-0008/).
- **Formatter**: Use `ruff format` for automatic, consistent code formatting.
- **Linter**: Use `ruff check` to catch common errors and style issues.
- **`pre-commit`**: Configure `pre-commit` hooks to run `ruff format` and `ruff check` automatically before each commit to ensure all code in the repository is compliant.

## 2. Type Hinting

- **Requirement**: All Python functions, methods, and class attributes should have type hints.
- **Clarity**: Type hints improve code readability, allow for static analysis with tools like `mypy`, and reduce runtime errors.
- **Static Analysis**: Use `mypy` as a static type checker to enforce type correctness.

```python
from __future__ import annotations
from typing import TYPE_CHECKING
import pandas as pd

# Good: Fully type-hinted function
def process_user_data(df: pd.DataFrame, logical_date: str) -> int:
    """Processes a DataFrame of user data."""
    # ... logic ...
    return len(df)
```

## 3. Docstrings

- **Requirement**: All public functions, classes, and modules must have a docstring.
- **Format**: Use the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#3.8-comments-and-docstrings) for docstrings.
- **Content**:
  - A brief summary of the object's purpose.
  - `Args:` section describing each argument.
  - `Returns:` section describing the return value.
  - `Raises:` section for any exceptions that are intentionally raised.

```python
def get_active_users(db_connection, min_logins: int = 10) -> pd.DataFrame:
    """Fetches active users from the database.

    Args:
        db_connection: An active database connection object.
        min_logins: The minimum number of logins to be considered active.

    Returns:
        A pandas DataFrame containing the active users.
    """
    # Assume db_connection has a method to execute queries
    sql = "SELECT * FROM users WHERE login_count >= %s"
    return pd.read_sql(sql, db_connection, params=(min_logins,))
```

## 4. Error Handling and Logging

### Logging
- **Use the `logging` module**: Use Python's standard `logging` module. Do not use `print()` for application output.
- **Accessing the Logger**: Get the logger via `logging.getLogger(__name__)`.
- **Log Levels**: Use appropriate log levels (`INFO`, `WARNING`, `ERROR`, `CRITICAL`) to convey the importance of the message.

```python
import logging

log = logging.getLogger(__name__)

def my_python_function():
    log.info("Starting function...")
    try:
        # ... logic ...
        log.info("Function finished successfully.")
    except Exception as e:
        log.error(f"Function failed with an unexpected error: {e}")
        raise
```

### Exception Handling
- **Fail Explicitly**: If a function cannot complete its objective, it should raise an exception. Do not swallow exceptions with a bare `except: pass`.
- **Custom Exceptions**: For business logic, define custom, specific exceptions to provide clear context on what failed.

## 5. Efficiency and Performance

- **Memory Usage**: Be mindful of memory usage, especially when processing large datasets. Consider:
  - Processing data in chunks.
  - Using more memory-efficient data types.
- **Database Queries**:
  - Avoid fetching entire large tables into memory. Use `WHERE` clauses to filter data at the source.
  - Use server-side cursors for very large query results if your database connector supports it.
- **Avoid Unnecessary Imports**: Only import modules that are needed for the specific function or module.