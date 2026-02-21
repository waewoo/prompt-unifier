# Logging Convention

Two separate output channels — never mix them:

| Channel | Purpose | Goes to |
|---|---|---|
| `logger` (Python logging) | Debug/info traces, internal state | stderr via RichHandler |
| `console` (Rich Console) | User-facing display output | stdout |

## Verbosity Levels

```
(no flag)  → WARNING  — silent unless something goes wrong
-v         → INFO     — progress messages
-vv        → DEBUG    — detailed traces
```

## Module Setup

Every module that logs must declare at module level:

```python
import logging
logger = logging.getLogger(__name__)
```

## Usage Rules

```python
# ✅ Correct
logger.debug(f"Parsed {len(files)} files")    # internal trace
logger.info("Sync complete")                   # progress
logger.warning(f"Handler {name} not found")   # recoverable issue
logger.error(f"Failed: {e}")                  # non-fatal error

console.print("[green]✓ Sync complete[/green]")  # user display
typer.echo("Error: ...", err=True)               # error to stderr

# ❌ Wrong — mixing channels
console.print(f"DEBUG: parsed {files}")  # debug info via console
logger.info("[bold]Done![/bold]")        # Rich markup in logger
```

## Why stderr for RichHandler

Log output goes to **stderr** (not stdout) so that:
- `--json` output on stdout is not polluted by log lines
- Users can pipe stdout cleanly: `prompt-unifier validate --json | jq .`
