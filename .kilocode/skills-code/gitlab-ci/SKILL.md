---
name: gitlab-ci
description: Creates and reviews GitLab CI/CD pipelines following best practices for
  speed, reliability, and security.
mode: code
license: MIT
---
# GitLab CI Skill

## When to Use

Apply this skill when:
- The user asks to create or write a `.gitlab-ci.yml` pipeline
- The user asks to add, fix, or optimise a CI/CD job
- The user asks to review a pipeline for best practices or security issues
- The user asks "why is my pipeline slow?" or "how do I add caching?"

Do NOT apply when the user is asking about GitHub Actions, Jenkins, or other CI systems.

## Pipeline Structure

```yaml
# .gitlab-ci.yml

stages:
  - lint
  - test
  - build
  - deploy

variables:
  PYTHON_VERSION: "3.13"
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

default:
  image: python:${PYTHON_VERSION}-slim
  interruptible: true           # cancel outdated pipelines on new push
  before_script:
    - pip install --upgrade pip
```

## Caching

```yaml
.python_cache: &python_cache
  cache:
    key:
      files:
        - poetry.lock
    paths:
      - .cache/pip
      - .venv/
    policy: pull-push
```

## Job Templates with Anchors

```yaml
.base_job: &base_job
  <<: *python_cache
  before_script:
    - pip install poetry
    - poetry install --no-interaction

lint:
  <<: *base_job
  stage: lint
  script:
    - poetry run ruff check .
    - poetry run mypy src/

test:
  <<: *base_job
  stage: test
  script:
    - poetry run pytest --cov=src --cov-report=xml
  coverage: '/TOTAL.*\s(\d+\%)/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
    expire_in: 1 week
```

## Rules — Control When Jobs Run

```yaml
deploy_production:
  stage: deploy
  script:
    - ./deploy.sh
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual        # require explicit trigger on main
    - if: $CI_COMMIT_TAG  # auto-deploy on tags
      when: on_success
    - when: never         # skip on all other branches
```

## Environments and Secrets

```yaml
deploy_staging:
  stage: deploy
  environment:
    name: staging
    url: https://staging.example.com
  script:
    - echo "Deploying to staging"
  variables:
    APP_ENV: staging
```

**Never** hardcode secrets in `.gitlab-ci.yml`. Use:
- `Settings → CI/CD → Variables` (masked + protected)
- HashiCorp Vault integration
- OIDC/IRSA for cloud providers

## Docker Build with Kaniko (rootless)

```yaml
build_image:
  stage: build
  image:
    name: gcr.io/kaniko-project/executor:v1.23.0-debug
    entrypoint: [""]
  script:
    - /kaniko/executor
      --context "${CI_PROJECT_DIR}"
      --dockerfile "${CI_PROJECT_DIR}/Dockerfile"
      --destination "${CI_REGISTRY_IMAGE}:${CI_COMMIT_SHA}"
      --destination "${CI_REGISTRY_IMAGE}:latest"
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

## Needs — Parallel Fan-in/Fan-out

```yaml
test_unit:
  stage: test
  script: pytest tests/unit/

test_integration:
  stage: test
  script: pytest tests/integration/

build:
  stage: build
  needs: [test_unit, test_integration]   # runs as soon as both tests pass
  script: make pkg-build
```

## Include for DRY Pipelines

```yaml
include:
  - project: 'org/ci-templates'
    ref: main
    file: '/templates/python.gitlab-ci.yml'
```

## Checklist

- [ ] `stages` defined in logical order
- [ ] Caching configured for dependencies
- [ ] `rules:` used instead of `only:/except:` (deprecated)
- [ ] No secrets in YAML — use CI/CD Variables
- [ ] `artifacts` expire to avoid storage bloat
- [ ] `interruptible: true` on non-deploy jobs
- [ ] `needs:` used to parallelise independent jobs
- [ ] Pipeline validated with `gitlab-ci-local` before pushing