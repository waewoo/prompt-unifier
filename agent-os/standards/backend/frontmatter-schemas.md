# Frontmatter Schemas

Two Pydantic models for prompt and rule files. **Type is determined by directory, not a field.**

## PromptFrontmatter (`models/prompt.py`)

| Field | Required | Notes |
|---|---|---|
| `title` | ✅ | Non-empty string |
| `description` | ✅ | Non-empty string |
| `version` | optional | Semver `"X.Y.Z"` — must be quoted in YAML |
| `tags` | optional | List of strings |
| `author` | optional | Warns if missing |
| `language` | optional | e.g. `"python"` |
| `applies_to` | optional | Glob patterns (quoted) |
| `invokable` | optional | Boolean |
| `tools` | ❌ prohibited | Raises error |

Extra fields are **forbidden** (`extra: "forbid"`).

## RuleFrontmatter (`models/rule.py`)

| Field | Required | Notes |
|---|---|---|
| `title` | ✅ | Non-empty string |
| `description` | ✅ | 1–200 chars |
| `category` | ✅ | One of `VALID_CATEGORIES` (warn if non-standard, not error) |
| `version` | optional | Default: `"1.0.0"` |
| `tags` | optional | Max 10 |
| `applies_to` | optional | Glob patterns (quoted) |
| `author` | optional | |

Valid categories: `coding-standards`, `architecture`, `security`, `testing`, `documentation`,
`performance`, `deployment`, `git`, `standards`, `infrastructure`.

To add a category: edit `VALID_CATEGORIES` in `src/prompt_unifier/models/rule.py`.

## Type Detection

Content type (`prompt` vs `rule`) is determined **by directory location**, not any field:

```
storage/prompts/  → PromptFrontmatter
storage/rules/    → RuleFrontmatter
```
