# Makefile Reference

The Prompt Unifier project uses a **Makefile-driven architecture** that serves as the single entry
point for all development, testing, and CI/CD operations. This ensures consistency between local
development and continuous integration environments.

## Philosophy

```
.gitlab-ci.yml (orchestration) → Makefile (logic) → Poetry/Tools
```

**Key Benefits:**

- Single entry point for local and CI environments
- Consistent behavior across all environments
- Easy to debug and test locally before pushing
- Self-documenting with `make help`

## Quick Start

```bash
# See all available targets
make help

# First-time setup
make env-install

# Before every commit
make app-check-all
```

## Command Groups

### Environment Setup

Manage dependencies and development environment.

#### `make env-install`

Install all dependencies and configure pre-commit hooks.

```bash
make env-install
```

**What it does:**

- Runs `poetry install` to install all dependencies
- Installs pre-commit hooks automatically
- One-command setup for new contributors

**Use when:**

- First-time project setup
- After cloning the repository
- When `poetry.lock` changes

#### `make env-update`

Update all dependencies to their latest versions within constraints.

```bash
make env-update
```

**What it does:**

- Runs `poetry update` to refresh `poetry.lock`
- Updates dependencies while respecting version constraints in `pyproject.toml`

**Use when:**

- You want to get security updates
- Monthly dependency refresh
- Investigating if newer versions fix an issue

#### `make env-clean`

Remove all temporary files, caches, and build artifacts.

```bash
make env-clean
```

**What it does:**

- Removes `dist/`, `build/`, `.pytest_cache/`, `.mypy_cache/`, etc.
- Cleans up `__pycache__` directories
- Removes coverage reports and test artifacts

**Use when:**

- Build artifacts are stale
- Troubleshooting weird build issues
- Before a fresh build

______________________________________________________________________

### Application Development

Run, test, and validate your code.

#### `make app-run`

Run the CLI with custom arguments.

```bash
make app-run ARGS="--version"
make app-run ARGS="init"
make app-run ARGS="validate --scaff"
```

**What it does:**

- Executes `poetry run prompt-unifier` with provided arguments
- Runs the CLI in the Poetry virtual environment

**Use when:**

- Testing CLI commands during development
- Manual testing of new features
- Debugging command behavior

#### `make app-lint`

Run all code quality checks: linting, formatting, and type checking.

```bash
make app-lint
```

**What it does:**

- Runs `pre-commit run --all-files`
- Checks include: Ruff (linting + formatting), mypy (type checking), Bandit (security),
  detect-secrets
- Skips `validate-gitlab-ci` hook (set via `SKIP` variable when needed in CI)

**Use when:**

- Before committing code
- Fixing linting errors
- Ensuring code style compliance

#### `make app-test`

Run the full test suite with coverage reporting.

```bash
make app-test
```

**What it does:**

- Runs `pytest` with coverage tracking
- Generates coverage reports: terminal, HTML (`htmlcov/`), XML (`coverage.xml`)
- Generates JUnit XML report (`report.xml`) for CI integration

**Use when:**

- Verifying tests pass
- Checking test coverage
- Before pushing to GitLab

#### `make app-check-all`

**Run FULL validation**: linting, tests, and CI config validation.

```bash
make app-check-all
```

**What it does:**

- Runs `make app-lint`
- Runs `make ci-validate`
- Runs `make app-test`
- Ensures everything is ready for push

**Use when:**

- **Before every commit** (most important command!)
- Before opening a pull request
- Final check before pushing to GitLab

______________________________________________________________________

### CI/CD Simulation

Test the GitLab CI pipeline locally using `gitlab-ci-local`.

#### `make ci-pipeline`

Run the FULL GitLab CI pipeline locally in Docker.

```bash
make ci-pipeline
```

**Prerequisites:**

- Docker installed and running
- `gitlab-ci-local` installed: `npm install -g gitlab-ci-local`

**What it does:**

- Runs all GitLab CI jobs in Docker containers
- Uses the same image as GitLab CI (`$CI_IMAGE`)
- Creates and uses Docker volumes for caching
- Mirrors the exact CI environment

**Use when:**

- Debugging CI pipeline failures
- Testing CI config changes before push
- Verifying pipeline passes locally

#### `make ci-job`

Run a specific GitLab CI job locally.

```bash
make ci-job JOB=app-lint
make ci-job JOB=app-test
make ci-job JOB=sec-all
```

**What it does:**

- Runs a single job from `.gitlab-ci.yml`
- Faster than running the full pipeline
- Uses Docker and volumes like `ci-pipeline`

**Use when:**

- Debugging a specific failing job
- Testing a specific stage quickly
- Iterating on CI job configuration

#### `make ci-validate`

Validate `.gitlab-ci.yml` syntax without running jobs.

```bash
make ci-validate
```

**What it does:**

- Runs `gitlab-ci-local --preview`
- Checks YAML syntax and job definitions
- Ensures no configuration errors

**Use when:**

- After modifying `.gitlab-ci.yml`
- Before committing CI changes
- Part of `make app-check-all`

#### `make ci-list`

List all available GitLab CI jobs.

```bash
make ci-list
```

**What it does:**

- Shows all jobs defined in `.gitlab-ci.yml`
- Useful reference for `make ci-job`

#### `make ci-clean`

Clean CI-related Docker volumes and cache.

```bash
make ci-clean
```

**What it does:**

- Removes Docker volumes (`prompt-unifier-venv`, `prompt-unifier-pip-cache`)
- Removes `.gitlab-ci-local/` directory
- Forces fresh CI environment on next run

**Use when:**

- CI cache is corrupted
- Testing fresh CI setup
- Freeing up disk space

#### `make ci-image-build`

Build the custom CI Docker image.

```bash
make ci-image-build
```

**What it does:**

- Builds Docker image from `Dockerfile.ci`
- Tags as `$CI_IMAGE_NAME`
- Includes Poetry, pre-commit, security tools

**Use when:**

- Updating `Dockerfile.ci`
- Need custom CI image locally
- Before pushing image to registry

#### `make ci-image-push`

Push the custom CI image to GitLab Container Registry.

```bash
make ci-image-push
```

**What it does:**

- Builds the image (via `make ci-image-build`)
- Pushes to `registry.gitlab.com/waewoo/prompt-unifier/ci-base:latest`

**Use when:**

- CI image has been updated
- Sharing image across team
- After significant dependency changes

______________________________________________________________________

### Security Scanning

Run security and vulnerability checks.

#### `make sec-all`

Run ALL security scans: code, secrets, and dependencies.

```bash
make sec-all
```

**What it does:**

- Runs `make sec-code` (Bandit)
- Runs `make sec-secrets` (detect-secrets)
- Runs `make sec-deps` (pip-audit)

**Use when:**

- Before releasing
- Part of CI pipeline
- Monthly security review

#### `make sec-code`

SAST scan with Bandit.

```bash
make sec-code
```

**What it does:**

- Runs `bandit -r src/prompt_unifier`
- Checks for common security issues in Python code

#### `make sec-secrets`

Scan for accidentally committed secrets.

```bash
make sec-secrets
```

**What it does:**

- Runs `detect-secrets scan`
- Uses `.secrets.baseline` for known false positives

#### `make sec-deps`

Check for dependency vulnerabilities.

```bash
make sec-deps
```

**What it does:**

- Runs `pip-audit` on installed dependencies
- Uses `|| true` to not fail on vulnerabilities (warning only)

______________________________________________________________________

### Package & Release

Build and publish packages.

#### `make pkg-build`

Build Python wheel and sdist packages.

```bash
make pkg-build
```

**What it does:**

- Runs `poetry build`
- Creates `dist/` directory with `.whl` and `.tar.gz`

**Use when:**

- Testing package build
- Before publishing to PyPI
- Part of release process

#### `make pkg-publish`

Create a release and push to GitLab (manual local release).

```bash
make pkg-publish VERSION_BUMP=patch
make pkg-publish VERSION_BUMP=minor
make pkg-publish VERSION_BUMP=major
```

**What it does:**

- Runs `make app-check-all` first
- Bumps version in `pyproject.toml`
- Creates git commit and tag
- Pushes commit and tag to GitLab

**Use when:**

- Creating a new release from local machine
- Manual release workflow

**CI Variables Required:**

- None (uses local git credentials)

#### `make pkg-ci-bump`

Auto-bump version using commitizen (CI only).

```bash
make pkg-ci-bump
```

**What it does:**

- Analyzes commit messages (conventional commits)
- Auto-determines version bump (patch/minor/major)
- Creates commit and tag
- Pushes to GitLab

**Use when:**

- Automated CI release workflow
- Manual trigger in GitLab CI

**CI Variables Required:**

- `CI_PUSH_TOKEN`
- `GITLAB_USER_EMAIL`
- `GITLAB_USER_NAME`
- `CI_SERVER_HOST`

#### `make pkg-upload`

Upload package to PyPI (CI only).

```bash
make pkg-upload
```

**What it does:**

- Runs `poetry publish`
- Uploads to PyPI

**Use when:**

- Automated CI release on tags

**CI Variables Required:**

- `PYPI_USER`
- `PYPI_PASSWORD`

______________________________________________________________________

### Documentation

Build and serve MkDocs documentation.

#### `make docs-install`

Install documentation dependencies.

```bash
make docs-install
```

**What it does:**

- Runs `poetry install --with docs`
- Installs MkDocs and plugins

#### `make docs-live`

Serve documentation locally with live reload.

```bash
make docs-live PORT=8000
```

**What it does:**

- Runs `mkdocs serve`
- Watches for file changes
- Auto-rebuilds on save

**Use when:**

- Writing documentation
- Previewing docs changes

#### `make docs-build`

Build static documentation site.

```bash
make docs-build
```

**What it does:**

- Runs `mkdocs build`
- Generates `site/` directory

**Use when:**

- Testing docs build
- Before deploying to GitLab Pages
- Part of CI pipeline

______________________________________________________________________

## Common Workflows

### First-Time Setup

```bash
git clone https://gitlab.com/waewoo/prompt-unifier.git
cd prompt-unifier
make env-install
make app-check-all
```

### Daily Development

```bash
# Make changes
git checkout -b feature/my-feature

# Run checks frequently
make app-lint
make app-test

# Before committing
make app-check-all

# Commit and push
git add .
git commit -m "feat: add my feature"
git push origin feature/my-feature
```

### Debugging CI Failures

```bash
# Run full pipeline locally
make ci-pipeline

# OR run specific failing job
make ci-job JOB=app-test

# Clean and retry
make ci-clean
make ci-pipeline
```

### Creating a Release

```bash
# Manual release
make pkg-publish VERSION_BUMP=minor

# OR trigger CI release
# Push to main, then manually trigger pkg-ci-bump job in GitLab
```

______________________________________________________________________

## Environment Variables

The Makefile uses these environment variables:

| Variable         | Default                      | Description                 |
| ---------------- | ---------------------------- | --------------------------- |
| `PYTHON_VERSION` | `3.12`                       | Python version for CI image |
| `PROJECT_SRC`    | `src/prompt_unifier`         | Source directory            |
| `PROJECT_TESTS`  | `tests`                      | Tests directory             |
| `CI_IMAGE_NAME`  | `registry.../ci-base:latest` | Custom Docker image         |
| `CI_VOL_VENV`    | `prompt-unifier-venv`        | Docker volume for venv      |
| `CI_VOL_CACHE`   | `prompt-unifier-pip-cache`   | Docker volume for pip cache |

Override with:

```bash
make app-run PYTHON_VERSION=3.11 ARGS="--version"
```

______________________________________________________________________

## Troubleshooting

### Command not found: make

Install GNU Make for your platform:

- **Ubuntu/Debian**: `sudo apt-get install build-essential`
- **macOS**: Install Xcode Command Line Tools: `xcode-select --install`
- **Windows**: Use WSL or install via Chocolatey: `choco install make`

### Poetry command not found

Install Poetry:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### gitlab-ci-local not found

Install via npm:

```bash
npm install -g gitlab-ci-local
```

### Docker not running

Ensure Docker Desktop is running (macOS/Windows) or Docker daemon is active (Linux):

```bash
docker info
```
