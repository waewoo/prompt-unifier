# Kilo Code

[Kilo Code](https://kilo.code) requires a specific format for its rules and workflows. Prompt
Unifier handles the necessary conversions automatically.

## Configuration

By default, Prompt Unifier deploys to:

- **Rules**: `.kilocode/rules/`
- **Workflows**: `.kilocode/workflows/` (Mapped from prompts)

## Features

### Pure Markdown Conversion

Kilo Code does not support YAML frontmatter in the same way as Continue. Prompt Unifier:

1. **Strips** the YAML frontmatter block.
1. **Ensures** the file starts with a Markdown header (h1/h2).

**Source (`storage/prompts/backend/api.md`):**

```markdown
---
title: API Generator
description: Create a FastAPI endpoint
---
# API Generator
...
```

**Deployed (`.kilocode/workflows/backend-api.md`):**

```markdown
# API Generator
...
```

### Flattened Structure

Kilo Code often prefers a flat structure or specific naming conventions. Prompt Unifier "flattens"
your nested directory structure into filenames to ensure uniqueness and clarity.

- Source: `prompts/backend/api.md`
- Deployed: `.kilocode/workflows/backend-api.md`
