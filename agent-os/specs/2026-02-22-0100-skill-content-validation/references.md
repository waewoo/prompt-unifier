# References for Skill Content Validation

## Similar Implementations

### SCARFFValidator

- **Location:** `src/prompt_unifier/core/scaff_validator.py`
- **Relevance:** Primary pattern reference for `generate_issues()` method, `ValidationIssue`
  construction, and the `ACTION_VERBS` constant to import
- **Key patterns:** `generate_issues()` returning `list[ValidationIssue]`, private `_check_*`
  methods for each concern, graceful exception handling

### BatchValidator — `validate_directory()`

- **Location:** `src/prompt_unifier/core/batch_validator.py`
- **Relevance:** Shows how SCAFF is integrated after schema validation passes; same pattern
  applied to `validate_skill_directory()` for `SkillContentValidator`
- **Key patterns:** `if result.status == "passed":` guard, `try/except` around content
  validation, `result.warnings.extend(issues)`

### ValidationResult / ValidationIssue / WarningCode

- **Location:** `src/prompt_unifier/models/validation.py`
- **Relevance:** `WarningCode` enum extended with 4 new `SKILL_*` entries; `ValidationIssue`
  used unchanged for all skill warnings

### SkillFrontmatter

- **Location:** `src/prompt_unifier/models/skill.py`
- **Relevance:** `compatibility: str | None` is the execution conditions field; passed to
  `SkillContentValidator.generate_issues()` as `frontmatter` argument

## External References

- agentskills specification: https://github.com/agentskills/agentskills/tree/main/skills-ref
  - `compatibility` field: documents execution conditions (environment requirements, system
    packages, OS, network access)
  - `allowed-tools` field: space-delimited list of pre-approved tools (experimental, out of scope)
