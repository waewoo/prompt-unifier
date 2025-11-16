---
name: Python Coding Standards
description: Comprehensive coding standards for Python development following PEP 8
  and industry best practices
globs:
- '*.py'
alwaysApply: false
category: standards
version: 1.0.0
tags:
- python
- standards
- pep8
- style-guide
- type-hints
author: prompt-manager
language: python
---
# Python Coding Standards

## Overview

This document defines the coding standards for Python development. All Python code must adhere to these guidelines to ensure consistency, readability, and maintainability across the codebase.

## PEP 8 Style Guide

### Line Length
- **Maximum line length**: 88 characters (Black formatter standard)
- **Docstrings/comments**: 72 characters
- Break long lines using parentheses, not backslashes

```python
# Good
result = some_function(
    parameter_one,
    parameter_two,
    parameter_three,
)

# Avoid
result = some_function(parameter_one, parameter_two, \
                      parameter_three)
```

### Naming Conventions

**Variables and Functions**: `snake_case`
```python
user_count = 0
def calculate_total_price():
    pass
```

**Classes**: `PascalCase`
```python
class UserManager:
    pass

class HTTPResponseHandler:
    pass
```

**Constants**: `UPPER_SNAKE_CASE`
```python
MAX_CONNECTIONS = 100
API_BASE_URL = "https://api.example.com"
```

**Private members**: Prefix with single underscore `_`
```python
class MyClass:
    def __init__(self):
        self._internal_state = {}

    def _helper_method(self):
        pass
```

**Name mangling**: Prefix with double underscore `__` (use sparingly)
```python
class MyClass:
    def __init__(self):
        self.__private_attr = "truly private"
```

### Imports

**Order**: Standard library, third-party, local application
```python
# Standard library
import os
import sys
from datetime import datetime
from pathlib import Path

# Third-party packages
import requests
import pytest
from pydantic import BaseModel

# Local application
from myapp.core import database
from myapp.models import User
```

**Formatting**:
- Absolute imports preferred over relative
- One import per line (except `from x import a, b`)
- Avoid wildcard imports (`from module import *`)

```python
# Good
from typing import List, Dict
import os
import sys

# Avoid
from typing import *
import os, sys
```

### Whitespace

**Function/class spacing**:
- Two blank lines between top-level functions and classes
- One blank line between methods in a class

**Operators**: Space around binary operators
```python
# Good
result = value1 + value2
is_valid = x == 5 and y > 10

# Avoid
result=value1+value2
```

**Commas**: Space after, not before
```python
# Good
my_list = [1, 2, 3]
my_dict = {"key": "value", "other": 123}

# Avoid
my_list = [1,2,3]
my_list = [1 , 2 , 3]
```

## Type Hints

### Required Usage
- **All function signatures** must have type hints
- **All public API functions** must have return type annotations
- **Class attributes** should be annotated

```python
from typing import Optional, List, Dict

def process_users(
    users: List[Dict[str, str]],
    filter_active: bool = True
) -> List[str]:
    """Process user list and return active usernames."""
    return [u["name"] for u in users if not filter_active or u.get("active")]

class UserService:
    _cache: Dict[int, User]

    def __init__(self) -> None:
        self._cache = {}

    def get_user(self, user_id: int) -> Optional[User]:
        """Retrieve user by ID, returns None if not found."""
        return self._cache.get(user_id)
```

### Modern Type Hints (Python 3.10+)
Use `|` for unions instead of `Optional` or `Union` when possible:

```python
# Good (Python 3.10+)
def get_user(user_id: int) -> User | None:
    pass

# Acceptable (older Python versions)
from typing import Optional
def get_user(user_id: int) -> Optional[User]:
    pass
```

Use built-in generics (Python 3.9+):
```python
# Good (Python 3.9+)
def process_items(items: list[str]) -> dict[str, int]:
    pass

# Old style (Python < 3.9)
from typing import List, Dict
def process_items(items: List[str]) -> Dict[str, int]:
    pass
```

## Docstrings

### Required For
- All public modules
- All public classes
- All public functions/methods
- All complex private functions

### Format: Google Style

**Functions**:
```python
def calculate_shipping_cost(
    weight: float,
    destination: str,
    express: bool = False
) -> float:
    """Calculate shipping cost based on weight and destination.

    Args:
        weight: Package weight in kilograms
        destination: Destination country code (ISO 3166-1 alpha-2)
        express: Whether to use express shipping (default: False)

    Returns:
        Total shipping cost in USD

    Raises:
        ValueError: If weight is negative or destination is invalid

    Examples:
        >>> calculate_shipping_cost(2.5, "US")
        15.75
        >>> calculate_shipping_cost(2.5, "US", express=True)
        32.50
    """
    if weight < 0:
        raise ValueError("Weight cannot be negative")
    # Implementation...
```

**Classes**:
```python
class UserRepository:
    """Repository for managing user data persistence.

    This class provides an abstraction layer over the database for user
    operations including CRUD operations and queries.

    Attributes:
        connection: Database connection instance
        cache: In-memory cache for frequently accessed users

    Examples:
        >>> repo = UserRepository(db_connection)
        >>> user = repo.get_by_id(123)
        >>> repo.save(user)
    """

    def __init__(self, connection: Connection) -> None:
        """Initialize repository with database connection.

        Args:
            connection: Active database connection
        """
        self.connection = connection
        self.cache: dict[int, User] = {}
```

**Modules**:
```python
"""User authentication and authorization module.

This module provides functionality for user authentication, password hashing,
token generation, and permission checking.

Example:
    from myapp.auth import authenticate_user

    user = authenticate_user("username", "password")
    if user:
        print(f"Welcome {user.name}")
"""
```

## Code Organization

### File Structure
```
module.py structure:
1. Module docstring
2. Imports (stdlib, third-party, local)
3. Module-level constants
4. Exception classes
5. Public classes
6. Public functions
7. Private helpers
8. if __name__ == "__main__": block (if applicable)
```

### Class Structure
```python
class MyClass:
    """Class docstring."""

    # Class variables
    class_variable: ClassVar[int] = 0

    # Instance variables (annotated)
    instance_var: str

    def __init__(self) -> None:
        """Initialize instance."""
        # Initialization

    # Public methods
    def public_method(self) -> None:
        """Public method."""
        pass

    # Private methods
    def _private_method(self) -> None:
        """Private helper method."""
        pass

    # Special methods last
    def __str__(self) -> str:
        return f"MyClass({self.instance_var})"
```

## Best Practices

### Use Context Managers
```python
# Good
with open("file.txt") as f:
    content = f.read()

# Avoid
f = open("file.txt")
content = f.read()
f.close()
```

### List Comprehensions for Simple Cases
```python
# Good
squares = [x**2 for x in range(10)]
active_users = [u for u in users if u.is_active]

# Avoid (when simple comprehension works)
squares = []
for x in range(10):
    squares.append(x**2)
```

### Use `pathlib` Over `os.path`
```python
# Good
from pathlib import Path

config_path = Path.home() / ".config" / "app.yaml"
if config_path.exists():
    content = config_path.read_text()

# Avoid
import os
config_path = os.path.join(os.path.expanduser("~"), ".config", "app.yaml")
if os.path.exists(config_path):
    with open(config_path) as f:
        content = f.read()
```

### F-strings for String Formatting
```python
# Good
name = "Alice"
age = 30
message = f"Hello, {name}. You are {age} years old."

# Avoid
message = "Hello, %s. You are %d years old." % (name, age)
message = "Hello, {}. You are {} years old.".format(name, age)
```

### Default Mutable Arguments
```python
# Good
def add_item(item: str, items: list[str] | None = None) -> list[str]:
    if items is None:
        items = []
    items.append(item)
    return items

# NEVER do this (mutable default argument bug)
def add_item(item: str, items: list[str] = []) -> list[str]:
    items.append(item)
    return items
```

## Tooling

### Required Tools
- **Black**: Code formatter (line length: 88)
- **Ruff**: Fast linter (replaces flake8, isort, etc.)
- **mypy**: Static type checker (strict mode)
- **pytest**: Testing framework

### Configuration

**pyproject.toml**:
```toml
[tool.black]
line-length = 88
target-version = ['py311']

[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "W", "UP"]
ignore = []

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.8
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

## Enforcement

- All code **must** pass `black --check`
- All code **must** pass `ruff check`
- All code **must** pass `mypy --strict`
- All public APIs **must** have docstrings
- All code **must** have type hints
- Target test coverage: **85%+**

## References

- [PEP 8](https://peps.python.org/pep-0008/)
- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)