# Creating Effective Prompts (SCAFF Method)

Prompt Unifier encourages the use of structured, high-quality prompts. To help you achieve this, we
recommend the **SCAFF** methodology.

## The SCAFF Framework

SCAFF stands for **S**pecific, **C**ontextual, **A**ctionable, **F**ormatted, and **F**ocused.

| Component      | Description                        | Example                                      |
| :------------- | :--------------------------------- | :------------------------------------------- |
| **Specific**   | Define the exact role and goal.    | "Act as a Senior Python Backend Developer."  |
| **Contextual** | Provide necessary background info. | "Using FastAPI and Pydantic v2."             |
| **Actionable** | State clear commands or requests.  | "Generate a Pydantic model for UserProfile." |
| **Formatted**  | Specify the desired output format. | "Output only the Python code block."         |
| **Focused**    | Limit scope to one main task.      | "Do not include database migrations."        |

### Example SCAFF Prompt

Here is how a full SCAFF-compliant prompt looks in a Prompt Unifier file:

```markdown
---
name: "FastAPI Model Generator"
description: "Generates Pydantic v2 models for FastAPI"
tags: ["python", "fastapi", "scaff"]
tools: ["kilo", "continue"]
---

# Role
You are a Senior Python Developer specializing in FastAPI.

# Context
We are building a microservice using FastAPI and Pydantic v2.
We follow strict typing enforcement.

# Task
Generate a Pydantic model for the following data structure description provided by the user.

# Rules
- Use `pydantic.BaseModel`.
- Use `Field` for all attributes with descriptions.
- Ensure all types are strictly annotated.
- Do not include `Config` class unless necessary.

# Output Format
Provide only the Python code block. No conversational filler.
```

## Creating Rules

Rules are shared instructions that apply across multiple prompts or coding sessions (e.g., coding
standards, architectural guidelines).

In Prompt Unifier, rules live in the `rules/` directory of your repository.

### Rule Structure

Rules use the same YAML frontmatter but are typically simpler in body content.

```markdown
---
name: "Python Coding Standards"
description: "Company-wide Python style guide"
tags: ["python", "standards"]
tools: ["kilo", "continue"]
---

1. Follow PEP 8.
2. Use Black for formatting.
3. Use snake_case for variables and functions.
4. Always include type hints for function arguments and return values.
5. Docstrings must follow Google style.
```

## Creating Skills

Skills are a [Kilo Code](tools/kilo-code.md)-exclusive content type. They are portable AI agent
guidance packages that provide specialised behaviour for specific tasks or modes.

### Where to Store Skills

Author skill files in the `skills/` directory of your storage repository:

```
storage/
└── skills/
    ├── k8s-debug.md
    ├── python-tdd.md
    └── git-conventional-commits.md
```

### Skill Frontmatter Fields

| Field           | Required | Description                                                                                 |
| :-------------- | :------: | :------------------------------------------------------------------------------------------ |
| `name`          |    ✅    | Slug identifier (lowercase, hyphens, max 64 chars). Must match the deployed directory name. |
| `description`   |    ✅    | Short description of the skill (max 1024 chars).                                            |
| `mode`          |    ❌    | Kilo Code mode (`code`, `architect`, …). Determines the target directory.                   |
| `license`       |    ❌    | License identifier (e.g. `MIT`).                                                            |
| `compatibility` |    ❌    | Compatibility notes.                                                                        |
| `metadata`      |    ❌    | Arbitrary key-value pairs for additional metadata.                                          |

### Example Skill File

```markdown
---
name: k8s-debug
description: Debug Kubernetes deployments and pod issues step by step
mode: code
license: MIT
---
You are a Kubernetes expert embedded in the developer's IDE.

## Your Responsibilities

- Diagnose failing pods, crashlooping containers and misconfigured services
- Read kubectl output and explain the root cause in plain language
- Propose minimal, targeted fixes

## Workflow

1. Ask for `kubectl describe pod <name>` and recent logs
2. Identify the failure pattern (OOMKilled, ImagePullBackOff, CrashLoopBackOff, …)
3. Suggest the fix with the exact kubectl/YAML patch to apply
```

### Name Constraints

The `name` field must:

- Be lowercase alphanumeric with hyphens only (`^[a-z0-9][a-z0-9-]*[a-z0-9]$`)
- Be at most 64 characters
- Match the name of the deployed directory (Kilo Code requirement)

### Validating and Deploying Skills

```bash
# Validate skill files only
prompt-unifier validate --type skills

# Validate all content types (prompts, rules, skills)
prompt-unifier validate --type all

# Deploy skills (kilocode handler only)
prompt-unifier deploy --handlers kilocode
```

!!! warning "Skills are Kilo Code only" Continue does not support skills. Running `deploy` without
`--handlers kilocode` will show skills as `SKIPPED` in the verification report — this is expected
behaviour.

______________________________________________________________________

## Leveraging `prompt-unifier-data`

The best way to learn is by example. Our official data repository contains dozens of SCAFF-compliant
prompts and industry-standard rules.

!!! tip "Explore the Catalog" Clone or browse
**[prompt-unifier-data](https://gitlab.com/waewoo/prompt-unifier-data)** to see real-world examples
of:

```
- **Prompts**: `prompts/python/unit-test-generator.md`, `prompts/devops/dockerfile-optimizer.md`
- **Rules**: `rules/python/security-best-practices.md`, `rules/git/commit-message-convention.md`

You can even fork this repository to start your own collection!
```
