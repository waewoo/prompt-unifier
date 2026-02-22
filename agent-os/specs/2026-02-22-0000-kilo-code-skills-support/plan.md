# Plan: Skills Support for KiloCode

## Context

KiloCode supports a third content type called "skills" — portable AI agent guidance packages
deployed as `{name}/SKILL.md` inside `.kilocode/skills/` or `.kilocode/skills-{mode}/`.
prompt-unifier currently manages prompts (→ workflows) and rules, but not skills.

This feature adds end-to-end skills management: author skill files in a `skills/` storage
directory, validate them, and deploy them to KiloCode's directory format. **Continue does NOT
support skills — only KiloCode deploys them.**

Source: https://kilo.ai/docs/customize/skills

---

## Key Design Decisions

| Aspect | Decision |
|---|---|
| Source format | `.md` with `---` YAML frontmatter in `storage/skills/` |
| Required fields | `name` (slug ≤64 chars), `description` (≤1024 chars) |
| Optional fields | `mode`, `license`, `compatibility`, `metadata` |
| Deployed format | YAML frontmatter **preserved** (unlike workflows → pure markdown) |
| Deployed structure | `.kilocode/skills[-{mode}]/{name}/SKILL.md` |
| Mode routing | `mode: code` → `skills-code/`; no mode → `skills/` |
| Name constraint | Must match parent directory name (KiloCode requirement) |
| Continue handler | Returns `status="skipped"` — skills not supported by Continue |
| `parse_file` unification | `_determine_content_type` routes on `"skills"` in path parts → unified `parse_file` |

---

## Tasks

### [x] Task 1: Save Spec Documentation

Create `agent-os/specs/2026-02-22-0000-kilo-code-skills-support/` with plan, shape, standards,
and references files.

### [x] Task 2: `SkillFrontmatter` + `SkillFile` models

**File:** `src/prompt_unifier/models/skill.py`

Pattern: follow `src/prompt_unifier/models/prompt.py`.

```python
class SkillFrontmatter(BaseModel):
    name: str          # required; max 64; regex ^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$
    description: str   # required; max 1024 chars
    mode: str | None = None
    license: str | None = None
    compatibility: str | None = None
    metadata: dict[str, Any] | None = None
    model_config = {"extra": "forbid", "str_strip_whitespace": True}

class SkillFile(SkillFrontmatter):
    content: str       # body after frontmatter separator
```

Exported from `src/prompt_unifier/models/__init__.py`.

### [x] Task 3: Constants

**File:** `src/prompt_unifier/constants.py`

```python
KILO_CODE_SKILLS_DIR = "skills"
```

### [x] Task 4: ContentFileParser — unified `parse_file` for skills

**File:** `src/prompt_unifier/core/content_parser.py`

- `_determine_content_type`: added `"skills" in file_path.parts → "skill"` before rules check
- `parse_skill_file`: thin wrapper delegating to `parse_file` with `isinstance(SkillFile)` check
- Return type updated to `PromptFile | RuleFile | SkillFile`
- Removed unused `PromptFrontmatter`, `RuleFrontmatter` imports

### [x] Task 5: KiloCodeToolHandler — skill deployment

**File:** `src/prompt_unifier/handlers/kilo_code_handler.py`

- `_get_skill_target_dir(mode)`: returns `.kilocode/skills/` or `.kilocode/skills-{mode}/`
- `_deploy_skill(content, body)`: creates `{target}/{name}/SKILL.md` with YAML frontmatter preserved
- `_build_skill_yaml_content(content, body)`: serializes frontmatter + body
- `deploy()`: `elif content_type == "skill"` branch
- `_determine_target_file_path()`: "skill" case → `{skills_dir}/{name}/SKILL.md`
- `get_deployment_status()`: handles "skill" type
- `verify_deployment_with_details()`: verifies frontmatter preserved (startswith `---`)
- `clean_orphaned_files()`: scans `skills*/` subdirs, removes orphaned skill dirs

### [x] Task 6: ContinueToolHandler — skipped status for skills

**File:** `src/prompt_unifier/handlers/continue_handler.py`

- `deploy()`: early return for `content_type == "skill"`
- `verify_deployment_with_details()`: returns `VerificationResult(status="skipped")`
- `get_deployment_status()`: returns `"synced"` for skills

### [x] Task 7: Base handler — `"skipped"` status support

**File:** `src/prompt_unifier/handlers/base_handler.py`

- `VerificationResult.status`: added `"skipped"` as valid value
- `aggregate_verification_results`: `"skipped": 0` counter
- `_format_status_info`: grey "SKIPPED" display
- `_build_verification_table`: skipped items show empty path
- `display_verification_report`: summary includes skipped count

### [x] Task 8: CLI helpers — scan & deploy skills

**File:** `src/prompt_unifier/cli/helpers.py`

- `scan_content_files()`: scans `storage/skills/` using `parser.parse_file`
- `_deploy_single_content_item()`: "skill" branch uses `SkillFrontmatter`
- `_get_deployed_filename()`: skills return `{name}/SKILL.md`

### [x] Task 9: CLI commands — validate target for skills

**File:** `src/prompt_unifier/cli/commands.py`

- `validate` command: "skills" added to `--type` option
- `determine_validation_targets()`: "skills" routing

### [x] Task 10: Tests

- `tests/models/test_skill.py`: model validation (name, description, mode, extra fields)
- `tests/handlers/test_kilo_code_skill_deployment.py`: deploy, mode routing, frontmatter preserved, orphan cleanup
- `tests/handlers/test_continue_handler_verification_report.py`: skipped status, aggregate, display
- `tests/core/test_content_parser.py`: `parse_valid_skill` inside `skills/` path

---

## Verification

```bash
# Unit tests
make app-test

# Manual test
mkdir -p storage/skills
# Create storage/skills/k8s-debug.md with name: k8s-debug, description: ..., mode: code
make app-run ARGS="validate --type skills"
make app-run ARGS="deploy --handlers kilocode"
# Expected: .kilocode/skills-code/k8s-debug/SKILL.md with YAML frontmatter preserved
make app-check-all
```

---

## Status: COMPLETED (2026-02-22)
