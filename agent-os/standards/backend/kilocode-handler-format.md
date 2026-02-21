# KiloCodeToolHandler Deployment Format

`KiloCodeToolHandler` converts prompts to **pure Markdown** (no YAML frontmatter) — KiloCode doesn't support YAML frontmatter in its workflow files.

## Directory Structure

```
<base_path>/.kilocode/
  workflows/   ← prompts go here (NOT prompts/)
  rules/       ← rules go here
```

`KiloCodeToolHandler()` defaults to `Path.cwd()`. Directories auto-created on instantiation.

## Output Format (prompts)

Frontmatter is stripped and converted to Markdown:

```markdown
# Title from 'title' field

Description text from 'description' field

**Tags:** python, review | **Version:** 1.0.0

<body content>
```

- `title` → H1 heading
- `description` → paragraph
- `tags`, `version`, `author`, etc. → metadata line (if present)
- Body content appended after metadata

## Key Difference from ContinueToolHandler

| | ContinueToolHandler | KiloCodeToolHandler |
|---|---|---|
| Prompts dir | `.continue/prompts/` | `.kilocode/workflows/` |
| Format | YAML frontmatter + body | Pure Markdown |
| YAML fields | Preserved (renamed) | Stripped, converted to Markdown |
