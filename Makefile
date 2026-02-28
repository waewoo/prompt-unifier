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


PYTHON_VERSION   ?= 3.13
POETRY_CMD       := $(POETRY_EXE) run
PROJECT_SRC      := src/prompt_unifier
PROJECT_TESTS    := tests

CI_REGISTRY      := registry.gitlab.com
CI_IMAGE_NAME    ?= $(CI_REGISTRY)/waewoo/prompt-unifier/ci-base:latest
CI_VOL_VENV      := prompt-unifier-venv
CI_VOL_CACHE     := prompt-unifier-pip-cache
CI_PROJECT_DIR   ?= /builds/waewoo/prompt-unifier
PORT             ?= 8000

ifeq ($(OS),Windows_NT)
    CI_EXTRA_ARGS := --variable "CI_USER_ID=1000"
else
    CI_EXTRA_ARGS :=
endif

# ==============================================================================
# 0. CHECKS & PREREQUISITES (INTERNAL)
# ==============================================================================

.PHONY: _ensure-poetry
_ensure-poetry:
	@$(CHECK_POETRY_CMD) || { echo "[ERROR] Poetry is not installed."; exit 1; }

.PHONY: _ensure-docker
_ensure-docker:
	@command -v docker >/dev/null 2>&1 || { echo "[ERROR] Docker is not installed."; exit 1; }
	@docker info >/dev/null 2>&1 || { echo "[ERROR] Docker not running OR permission denied (try sudo usermod -aG docker $$USER)."; exit 1; }

.PHONY: _ensure-gcl
_ensure-gcl:
	@if ! command -v gitlab-ci-local > /dev/null 2>&1; then \
		echo "gitlab-ci-local not found."; \
		read -p "Do you want to install it globally via npm? [y/N] " ans; \
		if [ "$$ans" = "y" ] || [ "$$ans" = "Y" ]; then \
			if command -v npm > /dev/null 2>&1; then \
				echo "Installing gitlab-ci-local via npm..."; \
				npm install -g gitlab-ci-local || (echo "Install failed." && exit 1); \
			else \
				echo "[ERROR] npm required to install gitlab-ci-local."; exit 1; \
			fi; \
		else \
			echo "[ERROR] gitlab-ci-local is required."; exit 1; \
		fi; \
	fi

.PHONY: _ensure-git
_ensure-git:
	@command -v git >/dev/null 2>&1 || { echo "[ERROR] Git is not installed."; exit 1; }

.PHONY: _ensure-rsync
_ensure-rsync:
ifeq ($(OS),Windows_NT)
	@command -v rsync >/dev/null 2>&1 || { echo "[ERROR] rsync is not installed. Required for gitlab-ci-local."; echo "   [Windows] Install via Scoop: 'scoop install rsync' or Check Git Bash path."; exit 1; }
else
	@command -v rsync >/dev/null 2>&1 || { echo "[ERROR] rsync is not installed. Required for gitlab-ci-local."; echo "   [Linux] Install via 'sudo apt install rsync' (or equivalent)."; exit 1; }
endif

.PHONY: _ensure-npx
_ensure-npx:
	@if echo "$(SKIP)" | grep -q "validate-gitlab-ci"; then \
		echo "⚠️  [Check] Skipping npx check (validate-gitlab-ci disabled in SKIP)."; \
	else \
		command -v npx >/dev/null 2>&1 || { echo "[ERROR] npx is not installed. Required for linting (validate-gitlab-ci)."; exit 1; } \
	fi


.PHONY: _ci-volumes
_ci-volumes: _ensure-docker
	@docker volume create $(CI_VOL_VENV) > /dev/null 2>&1 || true
	@docker volume create $(CI_VOL_CACHE) > /dev/null 2>&1 || true

# ==============================================================================
# 1. ENVIRONMENT (SETUP & CLEAN)
# ==============================================================================

.PHONY: env-install
env-install: _ensure-poetry ## [Env] Install dependencies and git hooks (First setup)
	@echo "🔧 Installing dependencies..."
	$(POETRY_EXE) install
	$(POETRY_CMD) pip install --upgrade pip
	$(POETRY_CMD) pre-commit install

.PHONY: env-update
env-update: _ensure-poetry ## [Env] Update all dependencies (within constraints)
	@echo "🔄 Updating dependencies (refreshing lock file)..."
	$(POETRY_EXE) update
	@echo "[SUCCESS] Dependencies updated."

.PHONY: env-clean
env-clean: ## [Env] Cleanup temporary files and caches
	@echo "🧹 Cleaning project..."
	@rm -rf dist build htmlcov .coverage .pytest_cache .mypy_cache .ruff_cache *.egg-info .gitlab-ci-local bandit-report.json gl-code-quality* pip-audit-report.json report.xml coverage.xml
	@python -c "import pathlib, shutil; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('__pycache__') if p.is_dir()]"
	@echo "[SUCCESS] Clean complete."

# ==============================================================================
# 2. QUALITY
# ==============================================================================

.PHONY: app-run
app-run: _ensure-poetry ## [App] Run the CLI (Usage: make app-run ARGS="--version")
	$(POETRY_CMD) prompt-unifier $(if $(ARGS),$(ARGS),--help)

.PHONY: app-lint
app-lint: _ensure-poetry _ensure-npx ## [App] Run static analysis (Quality & CI only)
	@echo "🔍 Running Lint (Quality + CI)..."
	SKIP="bandit,detect-secrets,pip-audit$$(if [ -n "$(SKIP)" ]; then echo ",$(SKIP)"; fi)" $(POETRY_CMD) pre-commit run --all-files

.PHONY: app-test
app-test: _ensure-poetry ## [App] Run unit tests with coverage
	@echo "🧪 Running Tests..."
	$(POETRY_CMD) pytest --cov=$(PROJECT_SRC) --cov-report=term-missing --cov-report=html --cov-report=xml --junitxml=report.xml --tb=short
	@echo "📊 Coverage report generated (HTML: htmlcov/, XML: coverage.xml)."

.PHONY: app-lint-sonar
app-lint-sonar: _ensure-docker ## Sonar + Issues listées
	@./scripts/run_sonar.sh

.PHONY: app-check-all
app-check-all: app-lint app-test ## [App] Run FULL validation (Lint + Test + CI Check)
	@echo "[SUCCESS] All local checks passed!"

# ==============================================================================
# 3. CI SIMULATION & IMAGES
# ==============================================================================

.PHONY: ci-pipeline
ci-pipeline: _ensure-docker _ensure-gcl _ensure-rsync _ci-volumes _ensure-npx ## [CI] Run FULL pipeline in Docker (Recommended)
	@echo "🚀 Running Pipeline (Docker)..."
	gitlab-ci-local \
		$(CI_EXTRA_ARGS) \
		--variable "CI_IMAGE=$(CI_IMAGE_NAME)" \
		--variable "SONAR_HOST_URL=$(SONAR_HOST_URL)" \
		--variable "SONAR_TOKEN=$(SONAR_TOKEN)" \
		--volume $(CI_VOL_VENV):$(CI_PROJECT_DIR)/.venv \
		--volume $(CI_VOL_CACHE):$(CI_PROJECT_DIR)/.cache/pip

.PHONY: ci-job
ci-job: _ensure-docker _ensure-gcl _ci-volumes _ensure-npx ## [CI] Run specific job (Usage: make ci-job JOB=lint)
	@if [ -z "$(JOB)" ]; then echo "[ERROR] JOB required"; exit 1; fi
	@echo "🔄 Running Job: $(JOB)..."
	gitlab-ci-local $(JOB) \
		$(CI_EXTRA_ARGS) \
		--variable "CI_IMAGE=$(CI_IMAGE_NAME)" \
		--variable "SONAR_HOST_URL=$(SONAR_HOST_URL)" \
		--variable "SONAR_TOKEN=$(SONAR_TOKEN)" \
		--volume $(CI_VOL_VENV):$(CI_PROJECT_DIR)/.venv \
		--volume $(CI_VOL_CACHE):$(CI_PROJECT_DIR)/.cache/pip

.PHONY: ci-list
ci-list: _ensure-gcl _ensure-npx ## [CI] List all available jobs
	gitlab-ci-local $(CI_EXTRA_ARGS) --list

.PHONY: ci-clean
ci-clean: _ensure-docker ## [CI] Clean CI volumes and cache
	@docker volume rm $(CI_VOL_VENV) $(CI_VOL_CACHE) 2>/dev/null || true
	@rm -rf .gitlab-ci-local/
	@echo "[SUCCESS] CI Cleaned."

.PHONY: ci-validate
ci-validate: _ensure-gcl _ensure-npx ## [CI] Validate .gitlab-ci.yml syntax
	gitlab-ci-local --preview > /dev/null
	@echo "[SUCCESS] CI Config valid."

.PHONY: ci-image-login
ci-image-login: _ensure-docker ## [CI] Login to Registry
	@docker login $(CI_REGISTRY) -u $(USER)

.PHONY: ci-image-build
ci-image-build: _ensure-docker ## [CI] Build CI Base Image
	@docker build -t $(CI_IMAGE_NAME) -f Dockerfile.ci .

.PHONY: ci-image-push
ci-image-push: ci-image-build ## [CI] Push CI Base Image
	@docker push $(CI_IMAGE_NAME)

# ==============================================================================
# 4. SECURITY (SECOPS)
# ==============================================================================

.PHONY: sec-all
sec-all: _ensure-poetry sec-code sec-secrets sec-deps ## [Sec] Run ALL security scans
	@echo "🛡️ Security check complete."

.PHONY: sec-code
sec-code: ## [Sec] SAST Scan (Bandit)
	$(POETRY_CMD) pre-commit run bandit --all-files

.PHONY: sec-secrets
sec-secrets: ## [Sec] Secret Detection
ifeq ($(OS),Windows_NT)
	@echo "🛑 [Windows] Skipping detect-secrets to prevent file path format corruption."
	@echo "   Run this check on Linux or inside Docker (make ci-job JOB=sec-secrets)."
else
	$(POETRY_CMD) pre-commit run detect-secrets --all-files
endif

.PHONY: sec-deps
sec-deps: ## [Sec] Dependency Vulnerabilities
	$(POETRY_CMD) pre-commit run pip-audit --all-files

# ==============================================================================
# 5. RELEASE & DISTRIBUTION
# ==============================================================================

.PHONY: pkg-build
pkg-build: _ensure-poetry ## [Rel] Build Wheel/Sdist packages
	@echo "📦 Building..."
	@$(POETRY_EXE) build

.PHONY: pkg-changelog
pkg-changelog: _ensure-git _ensure-poetry ## [Rel] Generate Changelog
	$(POETRY_CMD) cz changelog --incremental > CHANGELOG.md

.PHONY: pkg-notes
pkg-notes: _ensure-git _ensure-poetry ## [Rel] Generate Release Notes (Usage: make pkg-notes VERSION=x.y.z)
	@if [ -z "$(VERSION)" ]; then echo "[ERROR] VERSION is required"; exit 1; fi
	@echo "📝 Generating notes for v$(VERSION)..."
	$(POETRY_CMD) cz changelog "$(VERSION)" --dry-run > RELEASE_NOTES.md

.PHONY: pkg-publish
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

.PHONY: pkg-prepare-release
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
.PHONY: pkg-publish-package
pkg-publish-package: _ensure-poetry ## [Rel] Upload to PyPI (Require PYPI_USER & PYPI_PASSWORD)
	@echo "📦 Uploading to PyPI..."
	@$(POETRY_EXE) publish --username $(PYPI_USER) --password $(PYPI_PASSWORD)

# ==============================================================================
# 7. AI CODE REVIEW
# ==============================================================================

# Internal helper for pr-agent commands
.PHONY: _pr-agent-cmd
_pr-agent-cmd:
	@./scripts/run_pr_agent.sh "$(CMD)" "$(MR_URL)" "$(PYTHON_VERSION)"

.PHONY: pr-review
pr-review: ## [PR-Agent] Review IA d'une MR (usage: make pr-review MR_URL=...)
	@$(MAKE) _pr-agent-cmd CMD=review MR_URL="$(MR_URL)"

.PHONY: pr-improve
pr-improve: ## [PR-Agent] Suggestions d'amélioration pour une MR (usage: make pr-improve MR_URL=...)
	@$(MAKE) _pr-agent-cmd CMD=improve MR_URL="$(MR_URL)"

.PHONY: pr-describe
pr-describe: ## [PR-Agent] Génère une description pour une MR (usage: make pr-describe MR_URL=...)
	@$(MAKE) _pr-agent-cmd CMD=describe MR_URL="$(MR_URL)"

.PHONY: check-config
check-config: ## [Review] Vérifie la configuration
	@echo "🔍 Vérification configuration..."
	@if [ ! -f .pr_agent.toml ]; then echo "❌ .pr_agent.toml manquant"; exit 1; fi
	@if [ ! -f .env ]; then echo "❌ .env manquant"; exit 1; fi
	@command -v uv >/dev/null 2>&1 || { echo "❌ uv n'est pas installé. (curl -LsSf https://astral.sh/uv/install.sh | sh)"; exit 1; }
	@echo "✅ Fichiers de config OK"
	@echo ""
	@echo "Modèle configuré:"
	@grep "^model = " .pr_agent.toml || echo "❌ Model non trouvé dans .pr_agent.toml"

# ==============================================================================
# 6. DOCUMENTATION
# ==============================================================================

.PHONY: docs-install
docs-install: _ensure-poetry ## [Doc] Install docs requirements
	$(POETRY_EXE) install --with docs

.PHONY: docs-live
docs-live: docs-install ## [Doc] Serve docs locally (Live reload)
	$(POETRY_CMD) mkdocs serve -a localhost:$(PORT)

.PHONY: docs-build
docs-build: docs-install ## [Doc] Build static site
	$(POETRY_CMD) mkdocs build

# ==============================================================================
# HELP
# ==============================================================================

.PHONY: help
help: ## Show this help message
	@echo "📚 Prompt Unifier CLI - Available Targets"
	@echo "----------------------------------------------------------------"
	@cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'
	@echo "----------------------------------------------------------------"
