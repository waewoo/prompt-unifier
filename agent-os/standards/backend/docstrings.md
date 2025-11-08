# Docstrings Standards

## Recommended Styles
- Google style preferred for consistency.  
- Docstrings must describe function/class purpose, parameters, return type, exceptions.

## Format (Google style example)
```bash
def add(a, b):
"""
Add two numbers.

text
Args:
    a (int): First input.
    b (int): Second input.

Returns:
    int: Sum of a and b.
"""
return a + b
```

## Best Practices
- Keep concise one-line summary at the top.  
- Expand with details when needed.  
- Update docstrings upon code modification.