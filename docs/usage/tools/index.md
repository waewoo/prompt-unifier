# Supported AI Tools

Prompt Unifier supports deployment to various AI coding assistants. Each tool has its own
configuration requirements and capabilities.

## Feature Matrix

| Feature             |   [Continue](continue.md)   |  [Kilo Code](kilo-code.md)  |
| :------------------ | :-------------------------: | :-------------------------: |
| **Format**          | Markdown + YAML Frontmatter |        Pure Markdown        |
| **Structure**       |     Nested Directories      |       Flat (Prefixed)       |
| **Metadata**        |          Preserved          | Removed (Converted to text) |
| **Deployment Path** |    `.continue/prompts/`     |     `.kilocode/rules/`      |

## Selecting a Handler

You can specify which handler(s) to use during deployment:

```bash
# Deploy to all configured handlers (default)
prompt-unifier deploy

# Deploy only to Continue
prompt-unifier deploy --handlers continue

# Deploy to multiple tools
prompt-unifier deploy --handlers continue,kilocode
```
