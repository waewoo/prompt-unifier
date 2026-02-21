# CLI Dual Output Mode

Commands that return structured data support both human (Rich) and machine (JSON) output.

## Rule

Only **data-returning commands** need `--json` (e.g. `validate`, `list`).
Informational commands (`init`, `sync`, `status`) output human-readable text only.

## Pattern

```python
# 1. Separate output logic into two private functions
def _validate_with_json_output(validator, directories, scaff_enabled): ...
def _validate_with_rich_output(validator, directories, scaff_enabled): ...

# 2. Branch in the command function
def validate(..., json_output: bool = DEFAULT_VALIDATE_JSON_OPTION) -> None:
    if json_output:
        _validate_with_json_output(validator, directories, scaff)
    else:
        _validate_with_rich_output(validator, directories, scaff)
```

## JSON Output Rules

- Use `typer.echo()` (not `console.print()`) for JSON — avoids Rich markup contamination
- JSON output goes to **stdout**; errors always go to **stderr** (`typer.echo(..., err=True)`)
- Formatters live in `src/prompt_unifier/output/`: `JSONFormatter`, `RichFormatter`, `RichTableFormatter`
- Never mix Rich markup into JSON strings
