# Kilo Code

[Kilo Code](https://kilo.code) requires a specific format for its rules and workflows. Prompt
Unifier handles the necessary conversions automatically and supports all three Kilo Code content
types: **workflows**, **rules**, and **skills**.

## Configuration

By default, Prompt Unifier deploys to:

- **Rules**: `.kilocode/rules/`
- **Workflows**: `.kilocode/workflows/` (mapped from prompts)
- **Skills**: `.kilocode/skills/` or `.kilocode/skills-{mode}/` (mapped from skills)

## Content Types

### Workflows (from Prompts)

Prompt files in `storage/prompts/` are deployed as Kilo Code workflows. Prompt Unifier:

1. **Strips** the YAML frontmatter block.
1. **Ensures** the file starts with a Markdown header (h1/h2).
1. **Flattens** the directory structure into prefixed filenames.

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

### Rules

Rule files in `storage/rules/` are deployed as Kilo Code rules with the same flattening and
frontmatter-stripping as workflows.

- Source: `rules/python/standards.md`
- Deployed: `.kilocode/rules/python-standards.md`

### Skills

Skills are portable AI agent guidance packages specific to Kilo Code. Unlike workflows and rules,
**skills preserve their YAML frontmatter** in the deployed file, as required by Kilo Code.

See [Creating Skills](../creating-prompts.md#creating-skills) for authoring details.

#### Deployment Structure

Skills are deployed as `{name}/SKILL.md` inside a mode-specific directory:

| Source `mode` field | Target directory                             |
| :------------------ | :------------------------------------------- |
| _(not set)_         | `.kilocode/skills/{name}/SKILL.md`           |
| `code`              | `.kilocode/skills-code/{name}/SKILL.md`      |
| `architect`         | `.kilocode/skills-architect/{name}/SKILL.md` |

**Source (`storage/skills/k8s-debug.md`):**

```markdown
---
name: k8s-debug
description: Debug Kubernetes deployments and pod issues
mode: code
---
You are a Kubernetes expert. Help the user diagnose...
```

**Deployed (`.kilocode/skills-code/k8s-debug/SKILL.md`):**

```markdown
---
name: k8s-debug
description: Debug Kubernetes deployments and pod issues
mode: code
---
You are a Kubernetes expert. Help the user diagnose...
```

!!! info "Continue does not support skills" Skills are a Kilo Code-exclusive feature. When deploying
to Continue, skill files are automatically **skipped** (shown as `SKIPPED` in the verification
report).

## Flattened Structure

Kilo Code uses a flat directory for rules and workflows. Prompt Unifier converts the nested source
structure into prefixed filenames to ensure uniqueness.

- Source: `prompts/backend/api.md` → Deployed: `.kilocode/workflows/backend-api.md`
- Source: `rules/python/standards.md` → Deployed: `.kilocode/rules/python-standards.md`
- Source: `skills/k8s-debug.md` → Deployed: `.kilocode/skills-code/k8s-debug/SKILL.md`
