# Python Code Style

## General Conventions

- Follow [PEP8](https://peps.python.org/pep-0008/) for indentation (4 spaces) and max line length (100 chars).  
- Separate imports by standard library, third-party packages, and local modules, with blank lines between groups.  
- Use snake_case for variable and function names.  
- Use PascalCase for classes and exceptions.  
- Prefix boolean variables with `is_`, `has_`, or `should_`.  
- Add spaces around operators (ex: `a = b + c`).  
- Avoid global variables; use constants in uppercase with underscores.

## Comments and Docstrings

- Write clear and meaningful comments, avoid stating obvious.  
- Use docstrings with Google or NumPy style documenting parameters, returns, and exceptions.

## Examples
```bash
def increment(value):
"""Increase value by one.

text
Args:
    value (int): Number to increment.

Returns:
    int: Incremented number.
"""
return value + 1
```
