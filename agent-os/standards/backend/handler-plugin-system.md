# Handler Plugin System

Three-layer architecture for adding new deployment targets (e.g. Cursor, Windsurf).

## Layers

1. `ToolHandler` (Protocol) — defines the interface; `@runtime_checkable` so `isinstance()` works
   without subclassing. External handlers can conform without importing project internals.
2. `BaseToolHandler(ToolHandler, ABC)` — provides shared file management (orphan cleanup,
   verification reporting, hash comparison). **Always extend this**, not the Protocol directly.
3. `ToolHandlerRegistry` — central registry keyed by handler name. Validates protocol conformance
   on `register()`.

## Adding a New Handler

```python
from prompt_unifier.handlers.base_handler import BaseToolHandler

class CursorToolHandler(BaseToolHandler):
    def __init__(self, base_path: Path) -> None:
        super().__init__()
        self.name = "cursor"
        self.base_path = base_path
        self.tool_dir_constant = ".cursor"
        self.prompts_dir = base_path / self.tool_dir_constant / "prompts"
        self.rules_dir = base_path / self.tool_dir_constant / "rules"

    def deploy(self, content, content_type, body="", source_filename=None, relative_path=None):
        ...

    def get_deployment_status(self, ...):
        ...
```

## Rules

- Handler name must be unique in the registry (`ValueError` if duplicate)
- `validate_tool_installation()` is inherited — call it before registering optional handlers
- SCAFF validation is **disabled automatically** for `rules/` directories in all handlers
- `rollback()` is a no-op stub (backup functionality removed) — don't rely on it
