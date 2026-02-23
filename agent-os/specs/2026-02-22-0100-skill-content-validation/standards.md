# Standards for Skill Content Validation

The following standards apply to this work.

---

## python/python-code-quality

- Type hints on all function signatures
- Pydantic models for all data structures (no raw dicts crossing boundaries)
- `model_config = {"extra": "forbid"}` to catch unexpected fields early
- No mutable default arguments; use `None` with explicit check
- Keep functions focused (single responsibility)

---

## python/python-project-structure

- Core validation logic in `core/` (`SkillContentValidator`)
- Domain models in `models/` (`WarningCode` entries in `validation.py`)
- Tests mirror source: `tests/core/test_skill_validator.py`

---

## testing-pytest (TDD)

- Write failing test first; implement minimal code to pass; refactor
- Use `tmp_path` fixture for filesystem isolation
- Mock external dependencies (Git, filesystem side effects)
- Test edge cases: empty content, boundary word count, no action verbs
- Aim for >80% coverage on new code (maintained at >95% overall)

---

## global-coding-style

- Max line length: 100 chars
- `snake_case` for functions/variables/modules, `PascalCase` for classes
- Google-style docstrings on public methods
- Ruff for formatting and linting; mypy for type checking
