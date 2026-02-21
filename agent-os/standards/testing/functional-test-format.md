# Functional Test File Format (.test.yaml)

Schema for AI-driven prompt tests. Complements the naming convention in `functional-test-files.md`.

## Structure

```yaml
provider: gpt-4o          # optional — overrides global config for this file
iterations: 1             # optional, default: 1

scenarios:
  - description: "Brief description of what is being tested"
    input: |
      Multi-line user input
      sent to the AI as the user message
    expect:
      - type: contains
        value: "expected phrase"
        case_sensitive: false      # optional, default: true
        error: "Custom failure message"   # optional
      - type: not-contains
        value: "forbidden phrase"
      - type: regex
        value: "^\\d{4}-\\d{2}-\\d{2}$"
      - type: max-length
        value: 500                 # integer — max characters in response
```

## Assertion Types

| Type | `value` type | What it checks |
|---|---|---|
| `contains` | string | Response contains this text |
| `not-contains` | string | Response does not contain this text |
| `regex` | string | Response matches this regex pattern |
| `max-length` | integer | Response length ≤ N characters |

## Provider Priority

1. Per-file `provider:` field (top of .test.yaml)
2. Global `ai_provider` in config.yaml
3. `DEFAULT_LLM_MODEL` env var
4. Default: `gpt-4o-mini`

No per-scenario provider override — `provider` applies to all scenarios in the file.
