# Code Quality Toolchain

## Ruff (Linter + Formatter)

Line length: **100**. Selected rule sets:

`E`, `W` (pycodestyle) · `F` (pyflakes) · `I` (isort) · `N` (pep8-naming) · `UP` (pyupgrade) · `B` (bugbear) · `C4` (comprehensions) · `C90` (mccabe) · `SIM` (simplify) · `ARG` (unused args) · `ISC` (implicit str concat) · `PL` (pylint) · `RUF` · `S` (bandit)

Ignored: `PLR0913` (too many args), `PLR2004` (magic value comparison), `ISC001` (formatter conflict)

**Cognitive complexity max: 15** (aligned with SonarQube) — this is why `cli/helpers.py` exists.

Test files relax: `S101` (assert OK), `ARG001/002/005` (unused fixture args OK), `PLR0913/PLR0915/PLR2004/RUF012` (relaxed for test verbosity).

## mypy

`strict = true` applied to `src/` only. `tests/` excluded entirely. Run via pre-commit on `src/` files only.

## Pre-commit Hooks (all local via Poetry)

`fail_fast: true` — stops on first failure.

| Hook | Files | Notes |
|---|---|---|
| `trailing-whitespace` | text | Excludes `agent-os/` |
| `end-of-file-fixer` | text | Excludes `agent-os/` |
| `check-json` | JSON | All files |
| `check-added-large-files` | text | Max 15 MB; excludes `agent-os/` |
| `mdformat` | Markdown | `--wrap=100`; excludes `agent-os/`, CHANGELOG, CLI docs |
| `ruff-check` | Python | `--fix --no-cache` |
| `ruff-format` | Python | `--no-cache` |
| `mypy` | Python | `src/` only; whole-project run |
| `validate-gitlab-ci` | `.gitlab-ci.yml` | `npx gitlab-ci-local --preview` |
| `bandit` | Python | `src/` only |
| `detect-secrets` | all | Excludes `tests/fixtures/`, `.secrets.baseline`, `poetry.lock` |
| `pip-audit` | — | `always_run: true` |

## agent-os/ Auto-formatting Exclusion

`agent-os/` is excluded from `trailing-whitespace`, `end-of-file-fixer`, `check-added-large-files`, and `mdformat`. Standards files are hand-crafted — auto-formatting alters intended prose style and list formatting.
