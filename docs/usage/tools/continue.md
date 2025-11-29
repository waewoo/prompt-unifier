# Continue

[Continue](https://continue.dev/) is an open-source AI code assistant. Prompt Unifier provides full
support for Continue's prompt format.

## Configuration

By default, Prompt Unifier deploys to the standard Continue configuration directory in your project
root:

- **Prompts**: `.continue/prompts/`
- **Rules**: `.continue/rules/` (if supported by your version)

## Features

### YAML Frontmatter Preservation

Continue natively supports YAML frontmatter for metadata. Prompt Unifier preserves this exactly as
is.

**Source (`storage/prompts/my-prompt.md`):**

```markdown
---
title: Refactor Code
description: Refactor selection for better readability
version: 1.0
---
Refactor the following code...
```

**Deployed (`.continue/prompts/my-prompt.md`):**

```markdown
---
title: Refactor Code
description: Refactor selection for better readability
version: 1.0
---
Refactor the following code...
```

### Directory Structure

Continue supports nested directories. If you organize your prompts in folders (e.g.,
`prompts/python/testing.md`), they will be deployed with the same structure
(`.continue/prompts/python/testing.md`).
