# Pydantic Forward Reference Resolution

When two Pydantic models in different modules reference each other's types, use `model_rebuild()` to resolve the forward reference at import time.

## The Pattern

```python
# models/validation.py — uses SCARFFScore as a forward reference
if TYPE_CHECKING:
    from prompt_unifier.models.scaff import SCARFFScore

class ValidationResult(BaseModel):
    scaff_score: "SCARFFScore | None" = None  # forward ref as string

# models/scaff.py — calls rebuild after both modules can be imported
def rebuild_models() -> None:
    from prompt_unifier.models.validation import ValidationResult
    ValidationResult.model_rebuild(_types_namespace={"SCARFFScore": SCARFFScore})

rebuild_models()  # called at module import
```

## When to Apply

- Model A references Model B's type
- B is in a different module that (directly or transitively) imports A
- A uses `if TYPE_CHECKING:` to avoid the circular import
- `"ModelB | None"` as string annotation is not enough — Pydantic v2 still needs `model_rebuild()`

## Where to Put It

- Define `rebuild_models()` in the module that resolves the cycle (the one that can safely import both)
- Call it unconditionally at module level (bottom of the file)
- Pass `_types_namespace` with the concrete type to resolve
