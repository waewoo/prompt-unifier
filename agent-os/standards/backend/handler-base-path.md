# Handler Base Path Resolution

Base paths for deployment handlers follow a strict precedence chain.

## Precedence Order

1. **CLI `--base-path` flag** (highest priority)
2. **`config.handlers[handler_name].base_path`** (from `config.yaml`)
3. **`None`** — handler defaults to `Path.cwd()`

```python
# Resolved in cli/helpers.py:resolve_handler_base_path()
resolved = resolve_handler_base_path("continue", cli_base_path, config)
handler = ContinueToolHandler(base_path=resolved)  # None = use CWD default
```

## Env Var Support in Config

`base_path` in `config.yaml` supports env var expansion via `expand_env_vars()`:

```yaml
handlers:
  continue:
    base_path: "$PWD/.continue"
  cursor:
    base_path: "${HOME}/.cursor"
```

Supported syntaxes: `$VAR`, `${VAR}`, `%VAR%` (Windows), `~`

- **Unknown variable → `ValueError` + exit code 1** (fail fast — silently wrong path is worse than a clear error)
- `$HOME` and `$PWD` are always available even if not in `os.environ`
