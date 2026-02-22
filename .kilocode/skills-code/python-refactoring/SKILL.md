---
name: python-refactoring
description: Guides safe Python refactoring using incremental steps, keeping tests
  green throughout the process.
mode: code
license: MIT
---
# Python Refactoring Skill

## When to Use

Apply this skill when:
- The user asks to refactor, clean up, or simplify existing Python code
- The user says "this function is too long", "this is hard to read", or "this is duplicated"
- Code shows clear smells: deep nesting, magic numbers, copy-pasted blocks, god classes
- The user asks to improve code structure without changing behaviour

Do NOT apply when the user wants to add a new feature (refactor and feature work must be separate commits).

## Golden Rule

> Never refactor and add features at the same time. One commit per logical refactoring step.

## Process

```
1. Make sure existing tests pass before starting
2. Apply ONE refactoring pattern at a time
3. Run tests after each step
4. Commit when tests are green
5. Repeat
```

## Common Refactoring Patterns

### Extract Function
Move a block of code into a named function when:
- The block is used more than once
- The block can be named to express intent

```python
# Before
total = sum(item.price * item.qty for item in cart if not item.is_free)
tax = total * 0.2

# After
def cart_subtotal(cart):
    return sum(item.price * item.qty for item in cart if not item.is_free)

total = cart_subtotal(cart)
tax = total * 0.2
```

### Replace Magic Numbers with Constants
```python
# Before
if retries > 3:
    raise TimeoutError()

# After
MAX_RETRIES = 3
if retries > MAX_RETRIES:
    raise TimeoutError()
```

### Simplify Conditionals
```python
# Before
if condition:
    return True
else:
    return False

# After
return condition
```

### Replace Nested Conditions with Guard Clauses
```python
# Before
def process(data):
    if data is not None:
        if data.is_valid():
            result = data.compute()
            return result

# After
def process(data):
    if data is None:
        return None
    if not data.is_valid():
        return None
    return data.compute()
```

### Replace Loop with Comprehension
```python
# Before
results = []
for item in items:
    if item.active:
        results.append(item.value)

# After
results = [item.value for item in items if item.active]
```

### Extract Class / Split God Class
When a class has more than one reason to change, split it:
- Identify cohesive groups of attributes and methods
- Extract each group into its own class
- Use composition to keep original behaviour

## Signals That Code Needs Refactoring

- Function longer than 30 lines
- More than 3 levels of nesting
- Same logic copy-pasted in 2+ places
- Class with more than 10 methods or 5 responsibilities
- Parameter list longer than 4 arguments (use a dataclass or dict)

## What NOT to Refactor Now

- Code with no tests — write tests first
- Code that is about to be deleted
- Code you don't fully understand yet — read it first