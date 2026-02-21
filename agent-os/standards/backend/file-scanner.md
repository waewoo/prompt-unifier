# FileScanner

`FileScanner` discovers `.md` files for validation and deployment.

## Key Behaviors

- **Excludes `README.md`** (case-insensitive) everywhere — by design, README.md is never a prompt or rule
- Returns **sorted, absolute paths** — always deterministic, no ordering assumptions needed
- Accepts both a **single `.md` file** and a **directory** as input

## Rules

```python
scanner = FileScanner()
files = scanner.scan_directory(path)  # path = Path object
```

- `path` is a `.md` file → returns `[path]` (single-file validation)
- `path` is a directory → returns all `.md` files found recursively via `rglob`
- `path` is a non-`.md` file → raises `FileNotFoundError`
- `path` does not exist → raises `FileNotFoundError`
- Empty directory → returns `[]` (no error)

## Exclusion Rule

`README.md` (any case: `readme.md`, `Readme.md`) is silently skipped in all scan results.
Never name a prompt or rule file `README.md`.
