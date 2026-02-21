# Content File Format (.md)

All prompt and rule files use standard YAML frontmatter format:

```
---
title: My Prompt
description: What this prompt does
---

Markdown body content goes here.
```

## Rules

- File must start with `---` on line 1
- Closing `---` is required
- Body content after closing `---` must not be empty
- YAML must be **flat** — no nested dicts; lists of strings are allowed
- Must be UTF-8 encoded

## YAML Gotchas

**Version must be quoted** — unquoted `1.0.0` parses as a float chain and fails:

```yaml
version: "1.0.0"   # ✅
version: 1.0.0     # ❌ YAML parse error
```

**Glob patterns in `applies_to` must be quoted** — `*` is a YAML alias character:

```yaml
applies_to: ["*.py", "src/**/*.ts"]   # ✅
applies_to: [*.py]                     # ❌ "while scanning an alias" error
```

## File Locations

- Prompts: `<storage>/prompts/**/*.md`
- Rules: `<storage>/rules/**/*.md`
- Subdirectory structure is preserved during deployment
