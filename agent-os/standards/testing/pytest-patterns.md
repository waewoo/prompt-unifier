# Pytest Patterns

## Patch at Import Site (not definition site)

Always patch the name in the module that **uses** it:

```python
# commands.py does: from prompt_unifier.config.manager import ConfigManager
# So patch HERE:
with patch("prompt_unifier.cli.commands.ConfigManager") as mock:
    ...

# NOT here (definition site — won't work):
# patch("prompt_unifier.config.manager.ConfigManager")
```

Python's `mock.patch` replaces the name in the target module's namespace, not the original definition.

## CLI Testing with CliRunner

```python
from typer.testing import CliRunner
from prompt_unifier.cli.main import app

runner = CliRunner()

def test_something():
    with runner.isolated_filesystem():  # sets CWD to temp dir
        result = runner.invoke(app, ["validate", "--type", "prompts"])
        assert result.exit_code == 0
        assert "passed" in result.output
```

- `runner.isolated_filesystem()` — use when the command reads CWD (e.g. config lookup)
- `tmp_path` pytest fixture — use for unit tests that create files directly
- `result.output` captures both stdout and stderr (mixed)
- Check `result.exit_code` not just output content

## Test Fixtures Directory

`tests/fixtures/` contains real `.md` files:

```
tests/fixtures/
  valid_prompts/prompts/    — minimal_valid.md, full_valid.md, with_warnings.md
  invalid_prompts/          — missing_name.md, no_separator.md, ...
  rules/                    — valid rule files
  prompts/                  — additional prompt fixtures
```

`tests/conftest.py` provides fixtures returning `Path` objects to these files. For format/validation tests, prefer real fixture files over inline string content — they're easier to maintain and more realistic.
