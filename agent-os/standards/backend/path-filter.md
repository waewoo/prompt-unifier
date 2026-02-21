# PathFilter

`PathFilter.apply_filters()` filters file paths using glob patterns with **allowlist semantics**: include runs first, then exclude punches holes.

## Filtering Logic (order matters)

1. **Include** — if `include_patterns` provided, keep only files matching at least one pattern
2. **Exclude** — remove any files matching an exclude pattern

No include patterns → all files pass step 1. No exclude patterns → nothing is removed in step 2.

## Pattern Matching

Patterns use `pathlib.Path.match()` on the **relative path string** (not absolute):

```python
# Correct — relative path strings
PathFilter.apply_filters(
    ["prompts/python/a.md", "prompts/js/b.md"],
    include_patterns=["**/python/**"],
    exclude_patterns=["**/temp/**"],
)

# Wrong — absolute paths won't match correctly with Path.match()
```

## Usage

```python
from prompt_unifier.utils.path_filter import PathFilter

filtered = PathFilter.apply_filters(
    file_paths,                       # list[str] of relative paths
    include_patterns=["**/python/**"],
    exclude_patterns=["**/temp/**"],
)
```

- Both parameters are optional (pass `None` to skip that step)
- A file must match **any one** include pattern (OR logic)
- A file is excluded if it matches **any one** exclude pattern (OR logic)
