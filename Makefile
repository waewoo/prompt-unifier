# ==============================================================================
# PROMPT UNIFIER CLI - DEVELOPMENT MAKEFILE
# ==============================================================================
# This Makefile acts as the single entry point for development and industrialization.
#
# Usage:
#   make <target> [VARIABLES...]
# ==============================================================================


.DEFAULT_GOAL := help
SHELL := /bin/bash

# ==============================================================================
# VARIABLES & CONFIGURATION
# ==============================================================================

ifneq (,$(wildcard .env))
    include .env
    export
endif


PYTHON_VERSION   ?= 3.12
POETRY_CMD       := poetry run
PROJECT_SRC      := src/prompt_unifier
PROJECT_TESTS    := tests

CI_REGISTRY      := registry.gitlab.com
CI_IMAGE_NAME    ?= $(CI_REGISTRY)/waewoo/prompt-unifier/ci-base:latest
CI_VOL_VENV      := prompt-unifier-venv
CI_VOL_CACHE     := prompt-unifier-pip-cache
PORT             ?= 8000

# ==============================================================================
# 0. CHECKS & PREREQUISITES (INTERNAL)
# ==============================================================================

_ensure-poetry:
	@command -v poetry >/dev/null 2>&1 || { echo "❌ Error: Poetry is not installed."; exit 1; }

_ensure-docker:
	@command -v docker >/dev/null 2>&1 || { echo "❌ Error: Docker is not installed."; exit 1; }
	@docker info >/dev/null 2>&1 || { echo "❌ Error: Docker daemon is not running."; exit 1; }

_ensure-gcl:
	@if ! command -v gitlab-ci-local > /dev/null 2>&1; then \
		echo "⚠️  gitlab-ci-local not found."; \
		if command -v npm > /dev/null 2>&1; then \
			echo "🔧 Installing gitlab-ci-local via npm..."; \
			npm install -g gitlab-ci-local || (echo "❌ Install failed. Try with sudo." && exit 1); \
		else \
			echo "❌ Error: npm required to install gitlab-ci-local."; exit 1; \
		fi; \
	fi

_ensure-git:
	@command -v git >/dev/null 2>&1 || { echo "❌ Error: Git is not installed."; exit 1; }

_ci-volumes: _ensure-docker
	@docker volume create $(CI_VOL_VENV) > /dev/null 2>&1 || true
	@docker volume create $(CI_VOL_CACHE) > /dev/null 2>&1 || true

# ==============================================================================
# 1. ENVIRONMENT (SETUP & CLEAN)
# ==============================================================================

env-install: _ensure-poetry ## [Env] Install dependencies and git hooks (First setup)
	@echo "🔧 Installing dependencies..."
	poetry install
	$(POETRY_CMD) pre-commit install

env-update: _ensure-poetry ## [Env] Update all dependencies (within constraints)
	@echo "🔄 Updating dependencies (refreshing lock file)..."
	poetry update
	@echo "✅ Dependencies updated."

env-clean: ## [Env] Cleanup temporary files and caches
	@echo "🧹 Cleaning project..."
	@rm -rf dist build htmlcov .coverage .pytest_cache .mypy_cache .ruff_cache *.egg-info .gitlab-ci-local bandit-report.json gl-code-quality* pip-audit-report.json report.xml coverage.xml
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "✅ Clean complete."

# ==============================================================================
# 2. APPLICATION (LOCAL LOOP)
# ==============================================================================

app-run: _ensure-poetry ## [App] Run the CLI (Usage: make app-run ARGS="--version")
	$(POETRY_CMD) prompt-unifier $(ARGS)

app-lint: _ensure-poetry ## [App] Run static analysis (Lint, Format, Types)
	@echo "🔍 Running Lint..."
	$(POETRY_CMD) pre-commit run --all-files

app-test: _ensure-poetry ## [App] Run unit tests with coverage
	@echo "🧪 Running Tests..."
	$(POETRY_CMD) pytest --cov=$(PROJECT_SRC) --cov-report=term-missing --cov-report=html --cov-report=xml --junitxml=report.xml --tb=short
	@echo "📊 Coverage report generated (HTML: htmlcov/, XML: coverage.xml)."

app-lint-sonar: _ensure-docker app-test ## [App] Run SonarScanner locally (requires .env with SONAR_* vars)
	@echo "🔍 Running SonarScanner..."
	@if [ ! -f .env ]; then \
		echo "❌ Error: .env file not found. Create it with SONAR_HOST_URL and SONAR_TOKEN"; \
		exit 1; \
	fi
	@if [ ! -f coverage.xml ]; then \
		echo "⚠️  coverage.xml not found. Running tests first..."; \
		$(MAKE) app-test; \
	fi
	@docker run --rm \
		--user $(shell id -u):$(shell id -g) \
		--env-file .env \
		-v "$(PWD):/usr/src" \
		-w /usr/src \
		sonarsource/sonar-scanner-cli:latest \
		sonar-scanner
	@echo "✅ SonarScanner complete."

app-check-all: app-lint ci-validate app-test ## [App] Run FULL validation (Lint + Test + CI Check)
	@echo "✅ All local checks passed!"

# ==============================================================================
# 3. CI SIMULATION & IMAGES
# ==============================================================================

ci-pipeline: _ensure-docker _ensure-gcl _ci-volumes ## [CI] Run FULL pipeline in Docker (Recommended)
	@echo "🚀 Running Pipeline (Docker)..."
	gitlab-ci-local \
		--variable "CI_IMAGE=$(CI_IMAGE_NAME)" \
		--variable "SONAR_HOST_URL=$(SONAR_HOST_URL)" \
		--variable "SONAR_TOKEN=$(SONAR_TOKEN)" \
		--volume $(CI_VOL_VENV):/builds/waewoo/prompt-unifier/.venv \
		--volume $(CI_VOL_CACHE):/builds/waewoo/prompt-unifier/.cache/pip

ci-job: _ensure-docker _ensure-gcl _ci-volumes ## [CI] Run specific job (Usage: make ci-job JOB=lint)
	@if [ -z "$(JOB)" ]; then echo "❌ Error: JOB required"; exit 1; fi
	@echo "🔄 Running Job: $(JOB)..."
	gitlab-ci-local $(JOB) \
		--variable "CI_IMAGE=$(CI_IMAGE_NAME)" \
		--variable "SONAR_HOST_URL=$(SONAR_HOST_URL)" \
		--variable "SONAR_TOKEN=$(SONAR_TOKEN)" \
		--volume $(CI_VOL_VENV):/builds/waewoo/prompt-unifier/.venv \
		--volume $(CI_VOL_CACHE):/builds/waewoo/prompt-unifier/.cache/pip

ci-list: _ensure-gcl ## [CI] List all available jobs
	gitlab-ci-local --list

ci-clean: _ensure-docker ## [CI] Clean CI volumes and cache
	@docker volume rm $(CI_VOL_VENV) $(CI_VOL_CACHE) 2>/dev/null || true
	@rm -rf .gitlab-ci-local/
	@echo "✅ CI Cleaned."

ci-validate: _ensure-gcl ## [CI] Validate .gitlab-ci.yml syntax
	gitlab-ci-local --preview > /dev/null
	@echo "✅ CI Config valid."

ci-image-login: _ensure-docker ## [CI] Login to Registry
	@docker login $(CI_REGISTRY) -u $(USER)

ci-image-build: _ensure-docker ## [CI] Build CI Base Image
	@docker build -t $(CI_IMAGE_NAME) -f Dockerfile.ci .

ci-image-push: ci-image-build ## [CI] Push CI Base Image
	@docker push $(CI_IMAGE_NAME)

# ==============================================================================
# 4. SECURITY (SECOPS)
# ==============================================================================

sec-all: _ensure-poetry sec-code sec-secrets sec-deps ## [Sec] Run ALL security scans
	@echo "🛡️ Security check complete."

sec-code: ## [Sec] SAST Scan (Bandit)
	$(POETRY_CMD) bandit -r $(PROJECT_SRC) -f screen

sec-secrets: ## [Sec] Secret Detection
	$(POETRY_CMD) detect-secrets scan --baseline .secrets.baseline

sec-deps: ## [Sec] Dependency Vulnerabilities
	$(POETRY_CMD) pip-audit || true

# ==============================================================================
# 5. RELEASE & DISTRIBUTION
# ==============================================================================

pkg-build: _ensure-poetry ## [Rel] Build Wheel/Sdist packages
	@echo "📦 Building..."
	@poetry build

pkg-changelog: _ensure-git _ensure-poetry ## [Rel] Generate Changelog
	$(POETRY_CMD) cz changelog --incremental > CHANGELOG.md

pkg-notes: _ensure-git _ensure-poetry ## [Rel] Generate Release Notes (Usage: make pkg-notes VERSION=x.y.z)
	@if [ -z "$(VERSION)" ]; then echo "❌ Error: VERSION is required"; exit 1; fi
	@echo "📝 Generating notes for v$(VERSION)..."
	$(POETRY_CMD) cz changelog "$(VERSION)" --dry-run > RELEASE_NOTES.md

pkg-publish: app-check-all _ensure-git ## [Rel] Create Release & Push (Usage: make pkg-publish VERSION_BUMP=patch)
	@test -n "$(VERSION_BUMP)" || (echo "❌ VERSION_BUMP required"; exit 1)
	@echo "🚀 Publishing $(VERSION_BUMP)..."
	@NEW_VER=$$(poetry version $(VERSION_BUMP) --short) && \
	echo "📌 Version: $$NEW_VER" && \
	git add pyproject.toml && \
	git commit -m "chore(release): Bump version to v$$NEW_VER" && \
	git tag v$$NEW_VER && \
	git push origin main && \
	git push origin v$$NEW_VER

pkg-ci-bump: _ensure-git _ensure-poetry ## [Rel] CI Auto-bump (Require CI vars)
	@echo "🤖 Configuring Git for CI..."
	@git config --global credential.helper store
	@echo "https://oauth2:$(CI_PUSH_TOKEN)@$(CI_SERVER_HOST)" > ~/.git-credentials
	@git config user.email "$(GITLAB_USER_EMAIL)"
	@git config user.name "$(GITLAB_USER_NAME)"
	@echo "🚀 Bumping version (Commitizen)..."
	$(POETRY_CMD) cz bump --changelog --yes
	@echo "📤 Pushing changes..."
	@git push origin HEAD:main && git push origin --tags

# Cible pour le Robot (CI Only) - Remplace le script 'publish-pypi' de la CI
pkg-upload: _ensure-poetry ## [Rel] Upload to PyPI (Require PYPI_USER & PYPI_PASSWORD)
	@echo "📦 Uploading to PyPI..."
	@poetry publish --username $(PYPI_USER) --password $(PYPI_PASSWORD)

# ==============================================================================
# 6. DOCUMENTATION
# ==============================================================================

docs-install: _ensure-poetry ## [Doc] Install docs requirements
	poetry install --with docs

docs-live: docs-install ## [Doc] Serve docs locally (Live reload)
	$(POETRY_CMD) mkdocs serve -a localhost:$(PORT)

docs-build: docs-install ## [Doc] Build static site
	$(POETRY_CMD) mkdocs build

# ==============================================================================
# HELP
# ==============================================================================

help: ## Show this help message
	@echo "📚 Prompt Unifier CLI - Available Targets"
	@echo "----------------------------------------------------------------"
	@cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'
	@echo "----------------------------------------------------------------"

.PHONY: env-install env-update env-clean app-run app-lint app-test app-check-all ci-pipeline ci-pipeline-fast ci-job ci-list ci-clean ci-validate ci-image-login ci-image-build ci-image-push sec-all sec-code sec-secrets sec-deps pkg-build pkg-changelog pkg-notes pkg-publish docs-install docs-live docs-build help
