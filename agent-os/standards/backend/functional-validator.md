# FunctionalValidator

`FunctionalValidator` executes `.test.yaml` scenarios against AI prompt output.

## Assertion Dispatch

Assertion types are dispatched via a dict of `Callable`s — add new types by adding an entry:

```python
validators: dict[str, Callable] = {
    "contains": self._validate_contains,
    "not-contains": self._validate_not_contains,
    "regex": self._validate_regex,
    "max-length": self._validate_max_length,
}
```

- **Unknown type → `False` (FAIL)** + warning logged — so typos in `.test.yaml` fail visibly
- `contains` / `not-contains` both support `case_sensitive` flag (default: True)
- `regex` uses `re.search()` (matches anywhere in output, not full match)
- `max-length` value is compared to `len(output)` in characters

## Custom Error Messages

Set `error:` in the assertion to override the default failure message:

```yaml
  expect:
    - type: contains
      value: "```python"
      error: "Response must include a Python code block"
```

## AI Execution Error Handling

`AIExecutionError` during `validate_with_ai()` creates a FAIL result (not re-raised):
- `status: FAIL`
- `failed_count` = number of assertions in the scenario
- `actual_excerpt` = first 100 chars of the exception message

## Provider Priority

`validate_with_ai(provider=...)` → test_file.provider → executor default
