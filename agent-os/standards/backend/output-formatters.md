# Output Formatters

The `output/` package contains formatter classes for validation results. Each formatter handles one output mode.

## Formatters

| Class | File | Returns | Used when |
|---|---|---|---|
| `JSONFormatter` | `output/json_formatter.py` | `str` | `--json` flag; caller uses `typer.echo(json_str)` to stdout |
| `RichFormatter` | `output/rich_formatter.py` | `None` (prints directly) | Default human output; owns its own `Console()` |
| `RichTableFormatter` | `output/rich_table_formatter.py` | `None` (prints directly) | Tabular output for `status` command |

## Why the Asymmetry

`JSONFormatter` returns a string because JSON must reach stdout via `typer.echo()` (per cli-dual-output standard). `RichFormatter` prints internally because Rich Console already manages its own output stream.

## Input

Both accept `ValidationSummary` from `models/validation.py`:

```python
if json_output:
    formatter = JSONFormatter()
    typer.echo(formatter.format_summary(summary, directory))
else:
    formatter = RichFormatter()
    formatter.format_summary(summary, directory)
```

## Escape Rule

`RichFormatter` always calls `rich.markup.escape()` on user-supplied strings (messages, suggestions, excerpts) before printing — never trust arbitrary file content as Rich markup.
