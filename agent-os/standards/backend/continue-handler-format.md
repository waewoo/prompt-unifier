# ContinueToolHandler Deployment Format

`ContinueToolHandler` transforms prompt-unifier's model fields into Continue's expected frontmatter format on deploy.

## Field Mapping

| prompt-unifier field | Continue frontmatter key | Notes |
|---|---|---|
| `title` | `name` | Required |
| `description` | `description` | Optional |
| `category` | `category` | Optional |
| `version` | `version` | Optional |
| `tags` | `tags` | Optional |
| `author` | `author` | Optional |
| `language` | `language` | Optional |
| *(always added)* | `invokable: true` | Required by Continue to show in slash command menu |

For rules:

| prompt-unifier field | Continue frontmatter key |
|---|---|
| `title` | `name` |
| `applies_to` | `globs` |

## Default Base Path

`ContinueToolHandler()` defaults to `Path.cwd()` (not `Path.home()`). Target directories:

```
<base_path>/.continue/prompts/
<base_path>/.continue/rules/
```

Directories are **auto-created on instantiation** if they don't exist.

## Output Format

Prompts deploy as `---\n<continue_frontmatter>\n---\n<body>` (standard `.prompt` file format expected by Continue).
