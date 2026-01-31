# Tasks: CI/CD - MegaLinter Integration

This task list tracks the implementation of MegaLinter into the GitLab CI/CD pipeline.

## Phase 1: Configuration

- [ ] **T1: Create `.mega-linter.yml`**
    - Initialize the configuration file at the project root.
    - Set `APPLY_FIXES: none` (we want to lint, not auto-commit in CI).
    - Set `VALIDATE_ALL_CODEBASE: true` (or `false` for incremental, but `true` is better for quality).
- [ ] **T2: Configure Exclusions**
    - Add `.venv`, `site`, `htmlcov`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `dist`, `build` to `EXCLUDED_DIRECTORIES`.
- [ ] **T3: Refine Linter Selection**
    - Enable: `PYTHON_RUFF`, `PYTHON_MYPY`, `PYTHON_BANDIT`, `MARKDOWN_MARKDOWNLINT`, `YAML_YAMLLINT`, `BASH_SHELLCHECK`, `DOCKERFILE_HADOLINT`.
    - Disable redundant/noisy linters if any.
- [ ] **T4: Sync with existing configs**
    - Ensure `PYTHON_RUFF_CONFIG_FILE: pyproject.toml` and `PYTHON_MYPY_CONFIG_FILE: pyproject.toml`.

## Phase 2: GitLab CI Integration

- [ ] **T5: Add `megalinter` job to `.gitlab-ci.yml`**
    - Place it in the `quality` stage.
    - Use image `oxsecurity/megalinter-python:v8`.
    - Configure `rules` to match project standards (MRs, main branch).
- [ ] **T6: Configure Artifacts**
    - Upload `megalinter-reports` directory as an artifact.
    - Set expiry to 1 week.

## Phase 3: Verification & Cleanup

- [ ] **T7: Local Validation**
    - Attempt to run a simplified version locally if possible or use `make ci-validate`.
- [ ] **T8: CI Run & Baseline**
    - Trigger the pipeline.
    - Analyze results.
    - Adjust `.mega-linter.yml` to silence false positives or fix code issues.
- [ ] **T9: Documentation Update**
    - Mention MegaLinter in `DEVELOPMENT.md` or `CONTRIBUTING.md` if necessary.
