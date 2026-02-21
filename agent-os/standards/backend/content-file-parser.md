# ContentFileParser

Parses `.md` content files into typed Pydantic models.

## Usage

```python
from prompt_unifier.core.content_parser import ContentFileParser, parse_content_file

# Instance method
parser = ContentFileParser()
result = parser.parse_file(Path("prompts/my-prompt.md"))  # → PromptFile

# Convenience function
result = parse_content_file(Path("rules/my-rule.md"))     # → RuleFile
```

## Return Types

Type is determined by directory path (`rules` in `file_path.parts`):

| File location | Return type |
|---|---|
| `prompts/**/*.md` | `PromptFile` (with `.content` field) |
| `rules/**/*.md` | `RuleFile` (with `.content` field) |

## Error Handling

`parse_file()` raises `ValueError` (not Pydantic `ValidationError`) on all failures:
- `"encoding validation failed"` — not UTF-8
- `"separator validation failed"` — missing `---` delimiters
- `"invalid yaml"` — YAML parse error
- Pydantic `ValidationError` (re-raised as `ValueError`) — schema violation

## Backward Compatibility

The `type` field in frontmatter (e.g., `type: prompt`) is **silently stripped** before
Pydantic validation. Old files with this field continue to parse correctly.
Do not add `type` to new files — it is not part of the schema.
