# Plan: Skill Content Validation

## Context

`prompt-unifier` validates skill frontmatter (name, description, mode) but applies no content
quality checks. The agentskills spec defines `compatibility` as the field for execution conditions.

This feature adds `SkillContentValidator` with 4 checks, integrates it into `BatchValidator`, and
adds corresponding `WarningCode` entries.

---

## Tasks

### [x] Task 1: Roadmap + Spec documentation

- Add item #26 to `agent-os/product/roadmap.md`
- Create `agent-os/specs/2026-02-22-0100-skill-content-validation/` with plan, shape, standards,
  references

### [ ] Task 2: New WarningCode entries

**File:** `src/prompt_unifier/models/validation.py`

```python
SKILL_NO_COMPATIBILITY = "SKILL_NO_COMPATIBILITY"
SKILL_CONTENT_TOO_SHORT = "SKILL_CONTENT_TOO_SHORT"
SKILL_NOT_ACTIONABLE = "SKILL_NOT_ACTIONABLE"
SKILL_POORLY_STRUCTURED = "SKILL_POORLY_STRUCTURED"
```

### [ ] Task 3: Tests (TDD — write first)

**File:** `tests/core/test_skill_validator.py`

10 test cases covering all 4 checks and the happy path.

### [ ] Task 4: SkillContentValidator

**File:** `src/prompt_unifier/core/skill_validator.py`

Public method: `generate_issues(frontmatter: SkillFrontmatter, content: str) -> list[ValidationIssue]`

4 private checks:
- `_check_compatibility(frontmatter)` → `SKILL_NO_COMPATIBILITY` if `compatibility is None`
- `_check_content_length(content)` → `SKILL_CONTENT_TOO_SHORT` if < 50 words
- `_check_actionable(content)` → `SKILL_NOT_ACTIONABLE` if no action verbs and no numbered list
- `_check_structure(content)` → `SKILL_POORLY_STRUCTURED` if no headers and no lists

### [ ] Task 5: Integrate into BatchValidator

**File:** `src/prompt_unifier/core/batch_validator.py`

In `validate_skill_directory()`: after schema passes, run `SkillContentValidator.generate_issues()`
and extend `result.warnings`.

---

## Status: IN PROGRESS
