# Functional Test File Naming

Functional tests (AI-driven prompt validation) use `.test.yaml` companion files.

## Convention

```
prompts/
  my-prompt.md           # prompt file
  my-prompt.md.test.yaml # functional test file
```

Pattern: `<prompt_filename>.test.yaml` — the full filename including extension is the prefix.

## Discovery

The CLI discovers test files via `**/*.test.yaml` glob from configured storage or `cwd`.

Given a prompt file, the test file path is:
```python
test_file = prompt_file.parent / f"{prompt_file.name}.test.yaml"
```

## Rules

- A `.test.yaml` **can** exist without a companion `.md` — a warning is printed but execution continues
- Test files must live alongside the prompt file (same directory), not in a separate `tests/` folder
- Run with: `prompt-unifier validate --test` or `prompt-unifier validate <path>`
