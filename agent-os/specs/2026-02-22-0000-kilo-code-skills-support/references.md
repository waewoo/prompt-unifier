# References for Skills Support for KiloCode

## Similar Implementations

### PromptFrontmatter / PromptFile model

- **Location:** `src/prompt_unifier/models/prompt.py`
- **Relevance:** Template for `SkillFrontmatter` / `SkillFile` structure and Pydantic validation
  patterns (field validators, `model_config`, `str_strip_whitespace`)
- **Key patterns:** Field-level `@field_validator`, `max_length` enforcement, slug regex

### RuleFrontmatter / RuleFile model

- **Location:** `src/prompt_unifier/models/rule.py`
- **Relevance:** Second reference for model pattern; also shows how `content` field is handled

### ContentFileParser — `parse_file`

- **Location:** `src/prompt_unifier/core/content_parser.py`
- **Relevance:** Unified entry point extended to route `"skills"` paths; `_determine_content_type`
  pattern reused
- **Key patterns:** YAML frontmatter extraction via `---` split, type dispatch

### KiloCodeToolHandler — prompt/rule deploy

- **Location:** `src/prompt_unifier/handlers/kilo_code_handler.py`
- **Relevance:** Primary reference for skill deployment: `_deploy_prompt`, `_deploy_rule`
  patterns reused for `_deploy_skill`
- **Key patterns:** `_determine_deployment_status`, `_deployment_statuses` dict, orphan cleanup

### ContinueToolHandler

- **Location:** `src/prompt_unifier/handlers/continue_handler.py`
- **Relevance:** Added early-exit + `"skipped"` status for unsupported content type

### batch_validator — `validate_directory`

- **Location:** `src/prompt_unifier/core/batch_validator.py`
- **Relevance:** `_build_summary` extracted and shared with `validate_skill_directory`

## External References

- KiloCode Skills documentation: https://kilo.ai/docs/customize/skills
  - Defines `{name}/SKILL.md` deployed format
  - Defines `skills/` and `skills-{mode}/` directory conventions
  - Defines required frontmatter fields: `name`, `description`
