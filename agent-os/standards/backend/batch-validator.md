# BatchValidator

`BatchValidator` orchestrates multi-file validation: scan → validate each → compute summary.

## Usage

```python
validator = BatchValidator()
summary = validator.validate_directory(Path("./prompts"), scaff_enabled=True)
# summary.success → True if no errors across all files
```

## Validation Order

1. `FileScanner` discovers all `.md` files
2. `PromptValidator.validate_file()` runs on each file (format validation)
3. **SCAFF runs only if format validation passed** — malformed files can't be meaningfully scored
4. SCAFF issues appended to `result.warnings` (never errors)
5. `ValidationSummary` computed: `success = total_errors == 0`

## Key Rule: SCAFF Gate

```python
if scaff_enabled and result.status == "passed":
    # SCAFF analysis only on format-clean files
    scaff_score = self.scaff_validator.validate_content(prompt_content)
```

If format fails, SCAFF is skipped entirely — no warnings added.

## Failure Resilience

Validation **continues for all files** even when individual files fail. Never short-circuit on one bad file; always report the full picture.

## Summary Success Rule

`summary.success = total_errors == 0` — warnings (including all SCAFF warnings) never set `success = False`.
