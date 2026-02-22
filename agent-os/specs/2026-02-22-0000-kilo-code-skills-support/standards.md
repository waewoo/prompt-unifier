# Standards for Skills Support for KiloCode

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

- Domain models in `models/` (SkillFrontmatter, SkillFile)
- Parsing logic in `core/` (ContentFileParser)
- Handler logic in `handlers/` (KiloCodeToolHandler, ContinueToolHandler)
- CLI integration in `cli/` (helpers.py, commands.py)
- Tests mirror source: `tests/models/`, `tests/handlers/`, `tests/core/`

---

## testing-pytest (TDD)

- Write failing test first; implement minimal code to pass; refactor
- Use `tmp_path` fixture for filesystem isolation
- Mock external dependencies (Git, filesystem side effects)
- Test edge cases: name too long, invalid chars, extra fields rejected
- Aim for >80% coverage on new code (maintained at >95% overall)

---

## global-coding-style

- Max line length: 100 chars
- `snake_case` for functions/variables/modules, `PascalCase` for classes
- Google-style docstrings on public methods
- Ruff for formatting and linting; mypy for type checking
