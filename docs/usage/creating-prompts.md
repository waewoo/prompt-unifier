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
