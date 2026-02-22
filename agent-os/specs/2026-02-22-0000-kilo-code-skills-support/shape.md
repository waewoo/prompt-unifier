# Skills Support for KiloCode — Shaping Notes

## Scope

Add end-to-end management of KiloCode "skills" as a third content type alongside prompts and
rules. Skills are portable AI agent guidance packages deployed as `{name}/SKILL.md` files.

What we built:
- `SkillFrontmatter` / `SkillFile` Pydantic models with name/description/mode validation
- Skill deployment in `KiloCodeToolHandler` (YAML frontmatter preserved, not stripped)
- `"skipped"` status in `ContinueToolHandler` (Continue does not support skills)
- Unified `parse_file` in `ContentFileParser` routing on `"skills"` in path parts
- Scan, validate, and deploy flow via existing CLI commands

## Decisions

- **Frontmatter preserved on deploy**: unlike prompts (converted to pure markdown for workflows),
  skills keep their `---` YAML frontmatter in the deployed `SKILL.md`. This is what KiloCode
  expects per its docs.
- **Mode routing**: `mode: code` → `.kilocode/skills-code/`; no mode → `.kilocode/skills/`.
  This mirrors the `.kilocode/skills-{mode}/` convention shown in KiloCode docs.
- **Continue = skipped, not error**: ContinueToolHandler returns `status="skipped"` with a
  descriptive message instead of crashing or silently ignoring. This surfaces the limitation
  clearly in verification reports.
- **Unified `parse_file`**: rather than keeping `parse_skill_file` as a completely separate
  implementation, `_determine_content_type` now routes based on `"skills"` in the file path,
  letting the unified `parse_file` handle all three types. `parse_skill_file` becomes a thin
  wrapper for backward compatibility.
- **No frontmatter for skill body**: unlike `PromptFile` / `RuleFile` which strip frontmatter
  and return body as `content`, `SkillFile.content` is the raw body after the `---` separator.
  The deploy step re-serializes frontmatter from the model fields.
- **`batch_validator` shared `_build_summary`**: extracted helper shared between
  `validate_directory` (prompts/rules) and `validate_skill_directory` to avoid duplication.

## Context

- **Visuals:** None
- **References:** KiloCode docs at https://kilo.ai/docs/customize/skills; existing
  `KiloCodeToolHandler` for prompts/rules as the primary reference implementation
- **Product alignment:** Extends the core value proposition (unified prompt management across
  tools) to cover KiloCode's third content type

## Standards Applied

- `python/python-code-quality` — type hints, Pydantic models, no globals
- `python/python-project-structure` — models in `models/`, logic in handlers/
- TDD — `test_skill.py` and `test_kilo_code_skill_deployment.py` written before implementation
