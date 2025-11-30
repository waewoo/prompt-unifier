# ==============================================================================
# PROMPT UNIFIER CLI - DEVELOPMENT MAKEFILE
# ==============================================================================
# This Makefile acts as the single entry point for development and industrialization.
#
# Usage:
#   make <target> [VARIABLES...]
# ==============================================================================

ifeq ($(OS),Windows_NT)
    SHELL := C:/PROGRA~1/Git/bin/bash.exe
    POETRY_EXE := poetry
    ifneq (,$(shell python -c "import poetry" 2> /dev/null && echo found))
        POETRY_EXE := python -m poetry
    endif
    CHECK_POETRY_CMD := $(POETRY_EXE) --version > /dev/null 2>&1
else
    SHELL := /bin/bash
    POETRY_EXE := poetry
    CHECK_POETRY_CMD := command -v poetry >/dev/null 2>&1
endif

.DEFAULT_GOAL := help

# ==============================================================================
# VARIABLES & CONFIGURATION
# ==============================================================================

ifneq (,$(wildcard .env))
	include .env
	export
endif


PYTHON_VERSION   ?= 3.12
POETRY_CMD       := $(POETRY_EXE) run
PROJECT_SRC      := src/prompt_unifier
PROJECT_TESTS    := tests

CI_REGISTRY      := registry.gitlab.com
CI_IMAGE_NAME    ?= $(CI_REGISTRY)/waewoo/prompt-unifier/ci-base:latest
CI_VOL_VENV      := prompt-unifier-venv
CI_VOL_CACHE     := prompt-unifier-pip-cache
PORT             ?= 8000

ifeq ($(OS),Windows_NT)
    CI_EXTRA_ARGS := --variable "CI_USER_ID=1000"
else
    CI_EXTRA_ARGS :=
endif

# ==============================================================================
# 0. CHECKS & PREREQUISITES (INTERNAL)
# ==============================================================================

_ensure-poetry:
	@$(CHECK_POETRY_CMD) || { echo "[ERROR] Poetry is not installed."; exit 1; }

_ensure-docker:
	@command -v docker >/dev/null 2>&1 || { echo "[ERROR] Docker is not installed."; exit 1; }
	@docker info >/dev/null 2>&1 || { echo "[ERROR] Docker daemon is not running."; exit 1; }

_ensure-gcl:
	@if ! command -v gitlab-ci-local > /dev/null 2>&1; then \
		echo "gitlab-ci-local not found."; \
		if command -v npm > /dev/null 2>&1; then \
			echo "Installing gitlab-ci-local via npm..."; \
			npm install -g gitlab-ci-local || (echo "Install failed." && exit 1); \
		else \
			echo "[ERROR]npm required to install gitlab-ci-local."; exit 1; \
		fi; \
	fi

_ensure-git:
	@command -v git >/dev/null 2>&1 || { echo "[ERROR] Git is not installed."; exit 1; }

_ensure-rsync:
ifeq ($(OS),Windows_NT)
	@command -v rsync >/dev/null 2>&1 || { echo "[ERROR] rsync is not installed. Required for gitlab-ci-local."; echo "   [Windows] Install via Scoop: 'scoop install rsync' or Check Git Bash path."; exit 1; }
else
	@command -v rsync >/dev/null 2>&1 || { echo "[ERROR] rsync is not installed. Required for gitlab-ci-local."; echo "   [Linux] Install via 'sudo apt install rsync' (or equivalent)."; exit 1; }
endif

_ensure-npx:
	@if echo "$(SKIP)" | grep -q "validate-gitlab-ci"; then \
		echo "⚠️  [Check] Skipping npx check (validate-gitlab-ci disabled in SKIP)."; \
	else \
		command -v npx >/dev/null 2>&1 || { echo "[ERROR] npx is not installed. Required for linting (validate-gitlab-ci)."; exit 1; } \
	fi


_ci-volumes: _ensure-docker
	@docker volume create $(CI_VOL_VENV) > /dev/null 2>&1 || true
	@docker volume create $(CI_VOL_CACHE) > /dev/null 2>&1 || true

# ==============================================================================
# 1. ENVIRONMENT (SETUP & CLEAN)
# ==============================================================================

env-install: _ensure-poetry ## [Env] Install dependencies and git hooks (First setup)
	@echo "🔧 Installing dependencies..."
	$(POETRY_EXE) install
	$(POETRY_CMD) pre-commit install

env-update: _ensure-poetry ## [Env] Update all dependencies (within constraints)
	@echo "🔄 Updating dependencies (refreshing lock file)..."
	$(POETRY_EXE) update
	@echo "[SUCCESS] Dependencies updated."

env-clean: ## [Env] Cleanup temporary files and caches
	@echo "🧹 Cleaning project..."
	@rm -rf dist build htmlcov .coverage .pytest_cache .mypy_cache .ruff_cache *.egg-info .gitlab-ci-local bandit-report.json gl-code-quality* pip-audit-report.json report.xml coverage.xml
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "[SUCCESS] Clean complete."

# ==============================================================================
# 2. QUALITY
# ==============================================================================

app-run: _ensure-poetry ## [App] Run the CLI (Usage: make app-run ARGS="--version")
	$(POETRY_CMD) prompt-unifier $(ARGS)

app-lint: _ensure-poetry _ensure-npx ## [App] Run static analysis (Quality & CI only)
	@echo "🔍 Running Lint (Quality + CI)..."
	SKIP="bandit,detect-secrets,pip-audit,$(SKIP)" $(POETRY_CMD) pre-commit run --all-files

app-test: _ensure-poetry ## [App] Run unit tests with coverage
	@echo "🧪 Running Tests..."
	$(POETRY_CMD) pytest --cov=$(PROJECT_SRC) --cov-report=term-missing --cov-report=html --cov-report=xml --junitxml=report.xml --tb=short
	@echo "📊 Coverage report generated (HTML: htmlcov/, XML: coverage.xml)."

app-lint-sonar: _ensure-docker app-test ## [App] Run SonarScanner locally (requires .env with SONAR_* vars)
	@echo "🔍 Running SonarScanner..."
	@if [ ! -f .env ]; then \
		echo "[ERROR] .env file not found. Create it with SONAR_HOST_URL and SONAR_TOKEN"; \
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
	@echo "[SUCCESS] SonarScanner complete."

app-check-all: app-lint app-test ## [App] Run FULL validation (Lint + Test + CI Check)
	@echo "[SUCCESS] All local checks passed!"

# ==============================================================================
# 3. CI SIMULATION & IMAGES
# ==============================================================================

ci-pipeline: _ensure-docker _ensure-gcl _ensure-rsync _ci-volumes _ensure-npx ## [CI] Run FULL pipeline in Docker (Recommended)
	@echo "🚀 Running Pipeline (Docker)..."
	gitlab-ci-local \
		$(CI_EXTRA_ARGS) \
		--variable "CI_IMAGE=$(CI_IMAGE_NAME)" \
		--variable "SONAR_HOST_URL=$(SONAR_HOST_URL)" \
		--variable "SONAR_TOKEN=$(SONAR_TOKEN)" \
		--volume $(CI_VOL_VENV):/builds/waewoo/prompt-unifier/.venv \
		--volume $(CI_VOL_CACHE):/builds/waewoo/prompt-unifier/.cache/pip

ci-job: _ensure-docker _ensure-gcl _ci-volumes _ensure-npx ## [CI] Run specific job (Usage: make ci-job JOB=lint)
	@if [ -z "$(JOB)" ]; then echo "[ERROR] JOB required"; exit 1; fi
	@echo "🔄 Running Job: $(JOB)..."
	gitlab-ci-local $(JOB) \
		$(CI_EXTRA_ARGS) \
		--variable "CI_IMAGE=$(CI_IMAGE_NAME)" \
		--variable "SONAR_HOST_URL=$(SONAR_HOST_URL)" \
		--variable "SONAR_TOKEN=$(SONAR_TOKEN)" \
		--volume $(CI_VOL_VENV):/builds/waewoo/prompt-unifier/.venv \
		--volume $(CI_VOL_CACHE):/builds/waewoo/prompt-unifier/.cache/pip

ci-list: _ensure-gcl _ensure-npx ## [CI] List all available jobs
	gitlab-ci-local $(CI_EXTRA_ARGS) --list

ci-clean: _ensure-docker ## [CI] Clean CI volumes and cache
	@docker volume rm $(CI_VOL_VENV) $(CI_VOL_CACHE) 2>/dev/null || true
	@rm -rf .gitlab-ci-local/
	@echo "[SUCCESS] CI Cleaned."

ci-validate: _ensure-gcl _ensure-npx ## [CI] Validate .gitlab-ci.yml syntax
	gitlab-ci-local --preview > /dev/null
	@echo "[SUCCESS] CI Config valid."

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
	$(POETRY_CMD) pre-commit run bandit --all-files

sec-secrets: ## [Sec] Secret Detection
ifeq ($(OS),Windows_NT)
	@echo "🛑 [Windows] Skipping detect-secrets to prevent file path format corruption."
	@echo "   Run this check on Linux or inside Docker (make ci-job JOB=sec-secrets)."
else
	$(POETRY_CMD) pre-commit run detect-secrets --all-files
endif

sec-deps: ## [Sec] Dependency Vulnerabilities
	$(POETRY_CMD) pre-commit run pip-audit --all-files

# ==============================================================================
# 5. RELEASE & DISTRIBUTION
# ==============================================================================

pkg-build: _ensure-poetry ## [Rel] Build Wheel/Sdist packages
	@echo "📦 Building..."
	@$(POETRY_EXE) build

pkg-changelog: _ensure-git _ensure-poetry ## [Rel] Generate Changelog
	$(POETRY_CMD) cz changelog --incremental > CHANGELOG.md

pkg-notes: _ensure-git _ensure-poetry ## [Rel] Generate Release Notes (Usage: make pkg-notes VERSION=x.y.z)
	@if [ -z "$(VERSION)" ]; then echo "[ERROR] VERSION is required"; exit 1; fi
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

pkg-prepare-release: _ensure-git _ensure-poetry ## [Rel] CI Auto-bump (Require CI vars)
	@echo "🤖 Configuring Git for CI..."
	@git config user.email "$(GITLAB_USER_EMAIL)"
	@git config user.name "$(GITLAB_USER_NAME)"
	@git remote set-url origin "https://gitlab-ci-token:$(CI_PUSH_TOKEN)@$(CI_SERVER_HOST)/$(CI_PROJECT_PATH).git"
	@echo "🚀 Bumping version (Commitizen)..."
	$(POETRY_CMD) cz bump --changelog --yes
	@echo "📤 Pushing changes..."
	@git push origin HEAD:main && git push origin --tags

# Cible pour le Robot (CI Only) - Remplace le script 'publish-pypi' de la CI
pkg-publish-package: _ensure-poetry ## [Rel] Upload to PyPI (Require PYPI_USER & PYPI_PASSWORD)
	@echo "📦 Uploading to PyPI..."
	@$(POETRY_EXE) publish --username $(PYPI_USER) --password $(PYPI_PASSWORD)

# ==============================================================================
# 6. DOCUMENTATION
# ==============================================================================

docs-install: _ensure-poetry ## [Doc] Install docs requirements
	$(POETRY_EXE) install --with docs

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

.PHONY: env-install env-update env-clean app-run app-lint app-test app-check-all ci-pipeline ci-pipeline-fast ci-job ci-list ci-clean ci-validate ci-image-login ci-image-build ci-image-push sec-all sec-code sec-secrets sec-deps pkg-build pkg-changelog pkg-notes pkg-publish-package docs-install docs-live docs-build help
