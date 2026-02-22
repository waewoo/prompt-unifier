# Supported AI Tools

Prompt Unifier supports deployment to various AI coding assistants. Each tool has its own
configuration requirements and capabilities.

## Feature Matrix

| Feature                 |   [Continue](continue.md)   |  [Kilo Code](kilo-code.md)   |
| :---------------------- | :-------------------------: | :--------------------------: |
| **Prompts → Workflows** |             ✅              |              ✅              |
| **Rules**               |             ✅              |              ✅              |
| **Skills**              |        ❌ (skipped)         |              ✅              |
| **Format (prompts)**    | Markdown + YAML Frontmatter |        Pure Markdown         |
| **Format (skills)**     |             N/A             |  YAML Frontmatter preserved  |
| **Structure**           |     Nested Directories      |       Flat (Prefixed)        |
| **Metadata**            |          Preserved          | Removed (for prompts/rules)  |
| **Prompts path**        |    `.continue/prompts/`     |    `.kilocode/workflows/`    |
| **Rules path**          |     `.continue/rules/`      |      `.kilocode/rules/`      |
| **Skills path**         |             N/A             | `.kilocode/skills[-{mode}]/` |

## Selecting a Handler

You can specify which handler(s) to use during deployment:

```bash
# Deploy to all configured handlers (default)
prompt-unifier deploy

# Deploy only to Continue
prompt-unifier deploy --handlers continue

# Deploy only to Kilo Code (required for skills)
prompt-unifier deploy --handlers kilocode

# Deploy to multiple tools
prompt-unifier deploy --handlers continue,kilocode
```

!!! note "Skills require Kilo Code" Skills are only deployed by the `kilocode` handler. If you run
`deploy` with `--handlers     continue`, skill files will be listed as `SKIPPED` in the verification
report.
