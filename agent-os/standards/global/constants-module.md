# Constants Module

All magic strings live in `src/prompt_unifier/constants.py`. No inline string literals elsewhere.

## What Goes in constants.py

- Config/directory paths (`CONFIG_DIR = ".prompt-unifier"`, `CONFIG_FILE = "config.yaml"`)
- Tool handler directory names (`CONTINUE_DIR = ".continue"`, `KILO_CODE_DIR = ".kilocode"`)
- Glob patterns (`MD_GLOB_PATTERN = "**/*.md"`)
- Shared error messages (`ERROR_CONFIG_NOT_FOUND = "Error: ..."`)
- Any string used in more than one place

## What Stays Local

- Single-use display strings (Rich markup, one-off console messages)
- Test data strings in test files

## Import Pattern

```python
from prompt_unifier.constants import CONFIG_DIR, CONFIG_FILE, ERROR_CONFIG_NOT_FOUND
```

Never reference `.prompt-unifier`, `config.yaml`, `.continue`, or `.kilocode` as raw strings
outside of `constants.py`.
