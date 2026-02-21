# Config Manager

`ConfigManager` manages `.prompt-unifier/config.yaml` (created by `prompt-unifier init`).

## Rules

- `load_config()` **never raises** — returns `None` on any error (file missing, bad YAML, invalid schema)
- `None` always means uninitialised → tell user to run `prompt-unifier init`
- `save_config()` uses `sort_keys=False` to preserve field order; `default_flow_style=False` for human-readable block style

## Usage Pattern

```python
config_manager = ConfigManager()
config = config_manager.load_config(config_path)

if config is None:
    typer.echo("Error: Configuration not found. Run 'prompt-unifier init' first.", err=True)
    raise typer.Exit(code=1)
```

## Config File Location

```
<cwd>/.prompt-unifier/config.yaml
```

Always resolved relative to the current working directory, not the user's home directory.

## YAML Serialization

- Uses `yaml.safe_load` / `yaml.safe_dump` (never `yaml.load` — security)
- Serializes via `config.model_dump()` (Pydantic v2)
- Timestamps stored as ISO 8601 with UTC: `datetime.now(UTC).isoformat()`
