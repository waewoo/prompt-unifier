# Specification: Automated Code Review

**Feature:** Automated Code Review Integration
**Date:** 2026-01-31
**Status:** In Progress

## 1. Overview

Integrate `pr-agent` into `prompt-unifier` to provide AI-powered code reviews. The goal is an ULTRA-SIMPLE configuration that supports both local usage and GitLab CI/CD pipelines.

## 2. Goals

- **Simplicity:** Minimal configuration complexity.
- **Flexibility:** Easy to switch LLM providers (Gemini, Claude, OpenAI, etc.).
- **Security:** Secrets managed via `.env` (local) and CI variables (GitLab), never versioned.
- **Consistency:** Same configuration file (`.pr_agent.toml`) used for both local and CI environments.

## 3. Architecture

- **Configuration:** `.pr_agent.toml` (versioned) stores non-sensitive settings (LLM model, PR agent options).
- **Secrets:** `.env` (non-versioned, ignored) stores API keys.
- **Local Execution:** `Makefile` commands (`make review`, `make install-review`) wrap `pr-agent` CLI.
- **CI Execution:** `.gitlab-ci.yml` job runs `pr-agent` on Merge Requests.

## 4. Implementation Details

### 4.1. Configuration (`.pr_agent.toml`)
- **Section `[config]`**: Defines the model (default: `gemini/gemini-3-flash-preview`).
- **Section `[gitlab]`**: GitLab URL.
- **Section `[pr_reviewer]`**: Review settings (no strict requirements by default).
- **Section `[pr_description]`**: options for PR description generation.
- **Section `[pr_code_suggestions]`**: Defaults to 5 suggestions.

### 4.2. Secrets (`.env` & `.env.example`)
- `.env.example` provides a template.
- Keys: `GITLAB_TOKEN`, `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, etc.
- `.env` must be added to `.gitignore`.

### 4.3. Makefile Interface
- `make install-review`: Installs `pr-agent`.
- `make review MR_URL=...`: Runs review on a specific MR using local `.env`.
- `make check-config`: Validates presence of config files and tokens.

### 4.4. CI/CD (`.gitlab-ci.yml`)
- New stage: `code-review`.
- Job `pr-agent-review`:
  - Runs on merge requests.
  - Installs `pr-agent`.
  - Injects CI variables into environment.
  - Executes review.

### 4.5. Documentation
- Update `README.md` with setup instructions, usage examples, and configuration guide for different LLMs.

## 5. Security Considerations
- API Keys MUST never be committed.
- `.env` must be in `.gitignore`.
- CI variables must be Masked and Protected where possible.
