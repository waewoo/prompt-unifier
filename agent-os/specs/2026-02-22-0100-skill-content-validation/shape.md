# Skill Content Validation — Shaping Notes

## Scope

Add content quality validation for skill files. Currently, `validate_skill_directory()` only
checks YAML frontmatter schema. This adds 4 content-level warnings:

- `SKILL_NO_COMPATIBILITY`: execution conditions not specified
- `SKILL_CONTENT_TOO_SHORT`: body under 50 words
- `SKILL_NOT_ACTIONABLE`: no action verbs or numbered steps
- `SKILL_POORLY_STRUCTURED`: no markdown headers or lists

## Decisions

- **New `SkillContentValidator`** in `core/skill_validator.py` — keeps skill logic separate from
  SCAFF (which is prompt-specific with mandatory sections)
- **Reuse `ACTION_VERBS`** from `scaff_validator.py` — import the constant to avoid duplication
- **No numerical score for skills** — warnings only (unlike SCAFF's 0-100 score for prompts)
- **`compatibility` = execution conditions** — per agentskills spec; warn if absent
- **Integration in `batch_validator.validate_skill_directory()`** — mirrors how SCAFF is applied
  in `validate_directory()` (run after schema passes, handle exceptions gracefully)

## Context

- **Visuals:** None
- **References:** agentskills spec (https://github.com/agentskills/agentskills/tree/main/skills-ref),
  existing `SCARFFValidator` and `BatchValidator` as primary references
- **Product alignment:** Roadmap item #26

## Standards Applied

- `python/python-code-quality` — type hints, Pydantic models, no globals
- `python/python-project-structure` — core logic in `core/`, tests in `tests/core/`
- TDD — `test_skill_validator.py` written before implementation
