---
name: python-code-review
description: Reviews Python code for quality, correctness, security, and adherence
  to PEP 8 and project conventions.
mode: code
license: MIT
---
# Python Code Review Skill

## When to Use

Apply this skill when:
- The user asks to review a Python file, function, class, or pull request diff
- The user asks "does this code look good?", "can you review this?", or "what can be improved?"
- A code change is shown and feedback or approval is requested
- The user asks to check a Python file for bugs, security issues, or style problems

Do NOT apply when the user only asks to run or explain code (not review it).

## Review Checklist

### Correctness
- [ ] Logic is correct and matches the intent described in the task/issue
- [ ] Edge cases handled: `None`, empty collections, zero, negative values
- [ ] No off-by-one errors in loops or slices
- [ ] Exception handling is specific (avoid bare `except:`)
- [ ] No silent swallowing of exceptions

### Code Quality
- [ ] Functions are focused (single responsibility)
- [ ] No duplication — DRY principle respected
- [ ] Naming is clear and descriptive (no abbreviations unless obvious)
- [ ] Max line length respected (100 chars)
- [ ] No dead code or commented-out blocks
- [ ] Complexity is manageable — refactor if cyclomatic complexity > 10

### Type Safety
- [ ] Type hints on all function signatures
- [ ] `Optional[X]` or `X | None` used correctly
- [ ] No implicit `Any` without justification

### Security
- [ ] No hardcoded secrets, tokens, or passwords
- [ ] User inputs validated before use (SQL, shell, file paths)
- [ ] No use of `eval()`, `exec()`, or `pickle` on untrusted data
- [ ] File operations use safe paths (no path traversal)

### Tests
- [ ] New code is covered by tests
- [ ] Tests cover happy path, edge cases, and error cases
- [ ] Mocks are scoped correctly and don't mask real bugs

### Dependencies
- [ ] No unnecessary new dependencies added
- [ ] Pinned versions for direct dependencies

## Comment Format

When leaving review feedback:

```
[BLOCKER] The function does not handle `None` input — will raise AttributeError in production.

[SUGGESTION] Consider extracting this logic into a helper function for readability.

[NITPICK] Variable name `d` is unclear — rename to `data` or `document`.
```

- **BLOCKER**: Must fix before merge (bug, security issue, broken test)
- **SUGGESTION**: Improvement worth discussing
- **NITPICK**: Minor style point, non-blocking