# Validation Error/Warning Codes

All validation issues use `ErrorCode` / `WarningCode` enums from `models/validation.py`.

## ErrorCode (blocks deployment)

| Code | Meaning |
|---|---|
| `INVALID_ENCODING` | File is not valid UTF-8 |
| `NO_SEPARATOR` / `MULTIPLE_SEPARATORS` / `SEPARATOR_NOT_ALONE` / `SEPARATOR_WHITESPACE` | Separator (`---`) violations |
| `INVALID_YAML` | YAML syntax error |
| `NESTED_STRUCTURE` | Nested YAML not allowed |
| `MISSING_REQUIRED_FIELD` | `title` or `description` absent |
| `INVALID_SEMVER` | Bad version string |
| `PROHIBITED_FIELD` | Disallowed frontmatter field (e.g. `tools`) |
| `INVALID_FILE_EXTENSION` | File not `.md` |
| `FUNC_YAML_INVALID` / `FUNC_FILE_MISSING` / `FUNC_ASSERTION_FAILED` / `FUNC_AI_EXECUTION_ERROR` | Functional test failures |

## WarningCode (non-blocking)

| Code | Meaning |
|---|---|
| `MISSING_OPTIONAL_FIELD` | `version` or `author` absent |
| `EMPTY_TAGS_LIST` | Tags list is empty |
| `MISSING_AUTHOR` | Author field absent |
| `SCAFF_NOT_SPECIFIC` / `SCAFF_LACKS_CONTEXT` / `SCAFF_NOT_ACTIONABLE` / `SCAFF_POORLY_FORMATTED` / `SCAFF_UNFOCUSED` | SCAFF component failures |
| `FUNC_UNKNOWN_ASSERTION_TYPE` | Unknown assertion type in `.test.yaml` |

## ValidationIssue Rules

- `suggestion` is **required** — every issue must tell the user what to fix
- `suggestion` is always rendered in output — `None` is not accepted by the schema
- `is_valid` on `ValidationResult` checks `len(errors) == 0` — warnings never block
- `excerpt` is optional (use when showing the offending line helps)

## Adding a New Code

1. Add to `ErrorCode` or `WarningCode` in `models/validation.py`
2. Raise it via `ValidationIssue(code=ErrorCode.YOUR_CODE.value, suggestion="...")`
3. Always provide a non-empty `suggestion`
