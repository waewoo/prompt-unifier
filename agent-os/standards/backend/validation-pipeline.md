# Validation Pipeline

`PromptValidator` and `RuleValidator` run a 5-step pipeline that **collects all issues** before
returning — never short-circuits on first error, so users see every problem in one run.

## Pipeline Steps (in order)

```
1. EncodingValidator   → must be UTF-8; HARD GATE (returns early if fails)
2. SeparatorValidator  → --- delimiters present and non-empty
3. YAMLParser          → valid YAML syntax, flat structure only
4. Prohibited fields   → check raw dict before Pydantic (e.g. "tools" field)
5. Pydantic schema     → PromptFrontmatter / RuleFrontmatter validation
   └─ Warning detection → missing optional fields (version, author), empty tags
```

Only step 1 (encoding) short-circuits — if the file can't be read as UTF-8, remaining steps
are skipped. All other steps continue and append to `all_errors` / `all_warnings`.

## Adding a New Validation Step

Add after step 5 (Pydantic), before warning detection. Pattern:

```python
# In validator.py validate_file():
new_issues = self._validate_my_rule(yaml_dict)
all_errors.extend([i for i in new_issues if i.severity == ValidationSeverity.ERROR])
all_warnings.extend([i for i in new_issues if i.severity == ValidationSeverity.WARNING])
```

## ValidationIssue Fields

```python
ValidationIssue(
    line=None,                          # int or None (Pydantic errors have no line)
    severity=ValidationSeverity.ERROR,  # or WARNING
    code=ErrorCode.MISSING_REQUIRED_FIELD.value,
    message="Human-readable description",
    excerpt=None,                       # optional: "5 | bad line content"
    suggestion="Actionable fix hint",
)
```

## Result

`ValidationResult.status` is `"passed"` if `all_errors` is empty (warnings are OK).
