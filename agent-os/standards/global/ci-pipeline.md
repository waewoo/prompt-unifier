# CI Pipeline

GitLab CI driven by Makefile targets. All jobs call `make <target>`, not raw commands.

## Stages & Branch Strategy

| Stage | MR | main | Tag |
|---|---|---|---|
| `setup` | auto | auto | auto |
| `quality` | auto | auto | — |
| `security` | auto | auto | — |
| `build` | auto | auto | auto |
| `release` | — | **manual gate** | auto |
| `pull-request` | manual (AI review) | — | — |

## Key Design Decisions

- **Golden image** (`ci-base:latest`): Custom image with Python 3.12, Poetry, security tools pre-installed — avoids install overhead on every job.
- **Cache**: `pull-push` only in `setup-deps` (keyed on `poetry.lock`). All other jobs: `pull` only. `.venv/` also passed as artifact (1h TTL) for reliability.
- **Anti-loop**: `workflow:` filters out `bump:` and `chore(release):` commits globally — prevents infinite release loops.
- **`interruptible: true`**: Set globally; cancels redundant pipelines on same branch.
- **`optional: true` on needs**: Build stage depends on quality/security but doesn't hard-fail if they were skipped via circuit breakers.

## Circuit Breakers (CI Variables)

Set to `"true"` to skip stages during debug:

- `SKIP_QUALITY`, `SKIP_SECURITY`, `SKIP_BUILD`, `SKIP_RELEASE`
- `SIMULATE_MAIN="true"` — forces feature branch to behave like main (tests release flow)
- `DRY_RUN="true"` — skips actual GitLab Release creation and PyPI publish

## Release Flow (main branch)

1. `pkg-prepare-release` (manual) — bumps version, updates changelog, pushes Git tag via `CI_PUSH_TOKEN`
2. Tag triggers new pipeline → `pkg-gitlab-release` + `pkg-publish-package` (auto on `v*.*.*` tags)
3. `pages` job deploys docs to GitLab Pages

## AI Code Review (pull-request stage)

`pr-review`, `pr-improve`, `pr-describe` jobs — manual, `allow_failure: true`, MR only. Run in parallel (`needs: []`). Require `GITLAB_TOKEN` + `MISTRAL_API_KEY` CI variables.

## Required CI Variables

`SONAR_TOKEN`, `SONAR_HOST_URL`, `CI_PUSH_TOKEN` (write access), `PYPI_USER`, `PYPI_PASSWORD`, `GITLAB_TOKEN`, `MISTRAL_API_KEY`

## Windows Runner

`app-test-windows` — manual, `allow_failure: true`, tagged `pc-windows`, no CI image (uses system Python). Has own pull-push cache keyed `windows-poetry-cache`.
