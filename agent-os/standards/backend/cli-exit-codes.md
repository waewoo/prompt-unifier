# CLI Exit Codes

## Standard Rule

- `0` — success (warnings are acceptable, don't cause exit 1)
- `1` — validation or runtime errors

```python
if not summary.success:
    raise typer.Exit(code=1)   # errors found
# warnings: do NOT raise Exit — return normally (implicit 0)
```

## Exception: status Command

`status` always exits 0, even when errors occur. It is purely informational:

```python
# From commands.py status():
except Exception as e:
    typer.echo(f"Error: {e}", err=True)
    # Status is informational - don't exit with error code
    console.print()
```

Do not use `status` exit code to gate CI pipelines.

## Error Output

Always send error messages to **stderr**:

```python
typer.echo("Error: ...", err=True)   # ✅ errors → stderr
console.print("[red]Error: ...[/red]")  # ✅ display output → stdout
```
