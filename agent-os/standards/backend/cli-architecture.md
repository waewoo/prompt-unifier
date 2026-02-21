# CLI Architecture

Three-layer CLI split: `main.py` → `commands.py` → `cli/helpers.py`.

## What Goes Where

| Layer | File | Responsibility |
|---|---|---|
| CLI layer | `cli/main.py` | Typer app, option/arg declarations, type coercion (`str → Path`), calls command functions |
| Logic layer | `cli/commands.py` | Business logic, service calls, output (Rich/JSON), return values |
| Helper layer | `cli/helpers.py` | Extracted sub-functions to satisfy cognitive complexity linter limits |

## Rules

- `main.py` wrappers do **nothing** except coerce types and call the matching `commands.py` function
- All testable logic lives in `commands.py` — tests import command functions directly, never `main.py`
- Adding a new command always requires touching **both** files: declare wrapper in `main.py`, implement logic in `commands.py`
- `commands.py` delegates to `helpers.py`; helpers are never called from `main.py`
- When a function in `commands.py` exceeds cognitive complexity limits, extract sub-steps to `helpers.py`
- Private helpers use leading `_`; public helpers (shared by multiple commands) do not

## Example

```python
# main.py — thin wrapper
@app.command()
def validate(path: str = DEFAULT_PATH_ARG) -> None:
    commands.validate(path=Path(path))

# commands.py — business logic
def validate(path: Path, ...) -> None:
    files = scanner.scan_directory(path)
    ...
```
