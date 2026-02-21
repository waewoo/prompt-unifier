# CLI Option Constants

Typer option objects **must** be declared as module-level constants, not inline function defaults.

## Why

Python evaluates default argument values at import time. `typer.Option(...)` objects used inline
as function defaults cause runtime errors or unexpected behavior.

## Pattern

```python
# ✅ Correct — module-level constants
DEFAULT_DRY_RUN = False
DEFAULT_DRY_RUN_OPTION = typer.Option(False, "--dry-run", help="Preview without executing")

def deploy(dry_run: bool = DEFAULT_DRY_RUN_OPTION) -> None:
    ...

# ❌ Wrong — inline typer.Option as default
def deploy(dry_run: bool = typer.Option(False, "--dry-run")) -> None:
    ...
```

## Naming Convention

- Raw default value: `DEFAULT_<OPTION_NAME>` (e.g. `DEFAULT_DRY_RUN = False`)
- Typer option object: `DEFAULT_<OPTION_NAME>_OPTION` (e.g. `DEFAULT_DRY_RUN_OPTION`)
- `typer.Argument` objects: suffix `_ARG` (e.g. `DEFAULT_VALIDATE_DIRECTORY_ARG`)
