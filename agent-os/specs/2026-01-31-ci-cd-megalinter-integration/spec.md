---
title: CI/CD - MegaLinter Integration
date: 2026-01-31
status: draft
author: Gemini
version: 1.0.0
---

# CI/CD - MegaLinter Integration

## 1. Overview

Integrate [MegaLinter](https://megalinter.io/latest/) into the GitLab CI/CD pipeline. MegaLinter acts as a "Linter of Linters," analyzing the codebase for consistency, errors, and security issues across various file types (Python, YAML, Markdown, Bash, Dockerfile, etc.). This ensures a high standard of code quality and unified reporting.

## 2. Goals

-   **Comprehensive Linting**: Cover all file types in the repository, not just Python.
-   **Clean Integration**: Seamless addition to `.gitlab-ci.yml` without breaking existing workflows.
-   **Configuration Control**: Use `.mega-linter.yml` to define rules, enabling/disabling specific linters to match project standards.
-   **Reporting**: Generate accessible reports (HTML/Console) in CI artifacts.
-   **Performance**: Optimize to avoid excessive pipeline duration (using the specific "python" or "cupcake" flavor if appropriate, or properly configuring the generic one).

## 3. Implementation Details

### 3.1. Configuration File (`.mega-linter.yml`)

Create a configuration file at the project root to:
-   **Enable** specific linters relevant to the project:
    -   **Python**: `PYTHON_RUFF`, `PYTHON_MYPY`, `PYTHON_BANDIT` (ensure config matches `pyproject.toml`).
    -   **Markdown**: `MARKDOWN_MARKDOWNLINT`.
    -   **YAML**: `YAML_YAMLLINT`.
    -   **Bash**: `BASH_SHELLCHECK`.
    -   **Dockerfile**: `DOCKERFILE_HADOLINT`.
    -   **Secrets**: `REPOSITORY_GITLEAKS` (check overlap with existing secret scan).
-   **Disable** redundant or noisy linters (e.g., `PYTHON_PYLINT` if strictly using Ruff, or others that conflict).
-   **Ignore Files**: Configure `EXCLUDED_DIRECTORIES` (e.g., `.venv`, `site`, `coverage`, `.pytest_cache`).

### 3.2. GitLab CI Integration (`.gitlab-ci.yml`)

Add a `megalinter` job in the `quality` stage.
-   Use the official MegaLinter Docker image (likely `megalinter-python:v8` or `megalinter:v8` to keep it lighter if possible, or `v8` standard).
-   Preserve the existing `app-lint` job for now (which runs `make app-lint` / Ruff locally) as a fast "smoke test", or mark it as a dependency. MegaLinter will be the comprehensive gate.
-   Configure artifacts to expose the MegaLinter reports.

### 3.3. Interaction with Existing Tools

-   **Ruff/MyPy**: The project uses Poetry. MegaLinter needs to respect the `pyproject.toml` configuration. We need to ensure MegaLinter picks up these configs.
-   **Pre-commit**: The project has pre-commit hooks. MegaLinter basically runs these and more.

## 4. Verification

1.  **Pipeline Run**: Trigger a pipeline and verify the `megalinter` job runs.
2.  **Report Analysis**: Check the generated artifacts.
3.  **Failure Test**: Introduce a linting error (bad YAML or Python syntax) and verify the job fails.
4.  **False Positives**: Verify that valid code (according to project standards) passes.

## 5. Tasks

- [ ] Create `.mega-linter.yml` configuration file.
- [ ] Configure `pyproject.toml` integration for Python linters within MegaLinter variables if needed.
- [ ] Update `.gitlab-ci.yml` to include the MegaLinter job.
- [ ] Run initial pipeline to baseline current linting status.
- [ ] Fix immediate issues or adjust configuration to pass 'cleanly'.
