# Prompt Manager CLI

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/poetry-1.7%2B-blue)](https://python-poetry.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)](./coverage)

A Python CLI tool for managing AI prompt templates and coding rules with YAML frontmatter, enabling version control, validation, and deployment workflows.

---

## Table of Contents

- [Why Prompt Manager?](#why-prompt-unifier)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Core Concepts](#core-concepts)
  - [Prompts and Rules](#prompts-and-rules)
  - [Subdirectory Organization](#subdirectory-organization)
- [Commands](#commands)
  - [init](#init---initialize-configuration)
  - [sync](#sync---synchronize-from-git)
  - [status](#status---check-sync-status)
  - [validate](#validate---validate-files)
  - [deploy](#deploy---deploy-to-handlers)
- [Configuration](#configuration)
- [Handlers](#handlers)
- [Security](#security)
- [Architecture](#architecture)
- [Real-World Examples](#real-world-examples)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

---

## Why Prompt Manager?

**Problem:** Managing AI prompts across teams is chaotic:
- ❌ Prompts scattered in Slack, Notion, local files
- ❌ No version control or change tracking
- ❌ Difficult to share and standardize

**Solution:** Prompt Manager CLI provides:
- ✅ **Git-based versioning** - Track every change, roll back easily
- ✅ **Centralized storage** - Single source of truth for all prompts
- ✅ **Easy deployment** - One command to deploy to AI tools (Continue, Cursor, etc.)
- ✅ **Team collaboration** - Share prompts via Git repositories
- ✅ **Validation** - Catch errors before deployment
- ✅ **Recursive discovery** - Organize prompts in subdirectories

---

## Quick Start

Get started in 60 seconds:

```bash
# 1. Install dependencies
cd prompt-unifier
poetry install

# 2. Initialize in your project
poetry run prompt-unifier init

# 3. Sync prompts from Git repository
poetry run prompt-unifier sync --repo git@github.com:your-org/prompts.git

# 4. Deploy to Continue (AI coding assistant)
poetry run prompt-unifier deploy

# 5. Check status anytime
poetry run prompt-unifier status
```

---

## Installation

### Prerequisites

| Requirement | Version | Check Installation |
|-------------|---------|-------------------|
| **Python** | 3.11+ (3.12+ recommended) | `python --version` |
| **Poetry** | 1.7+ | `poetry --version` |
| **Git** | 2.x+ | `git --version` |

**Missing dependencies?** Follow the installation guides:
- [Install Python](https://www.python.org/downloads/)
- [Install Poetry](https://python-poetry.org/docs/#installation)
- [Install Git](https://git-scm.com/downloads)

### Install Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Clone and Install

```bash
git clone <repo-url>
cd prompt-unifier
poetry install
```

### Install CLI Globally (Optional)

```bash
pipx install .
```

---

## Core Concepts

### Prompts and Rules

The prompt-unifier supports two types of content files using **YAML frontmatter** format (Jekyll/Hugo style):

#### **Prompts**

AI prompt templates for use with language models. Stored in `prompts/` directory.

**Example:**

```markdown
---
title: code-review
description: Review code for bugs and improvements
version: 1.0.0
tags: [python, review]
---

# Code Review Prompt

You are an expert code reviewer. Analyze the provided code for:
- Potential bugs and edge cases
- Code quality and best practices
- Performance optimizations
```

**Required fields:**
- `title` - Unique identifier
- `description` - Brief description

**Optional fields:**
- `version` - Semantic version (e.g., `1.0.0`)
- `tags` - List of tags for filtering
- `author` - Author information

#### **Rules**

Coding standards, best practices, and organizational guidelines. Stored in `rules/` directory.

**Example:**

```markdown
---
title: python-style-guide
description: Python coding standards and best practices
category: coding-standards
tags: [python, pep8]
version: 1.0.0
applies_to: ["*.py", "*.pyi"]
---

# Python Style Guide

## Naming Conventions
- Use `snake_case` for functions and variables
- Use `PascalCase` for classes
- Use `UPPER_CASE` for constants
```

**Required fields:**
- `title` - Unique identifier (kebab-case recommended)
- `description` - Brief description
- `category` - One of: `coding-standards`, `architecture`, `security`, `testing`, `documentation`, `performance`, `deployment`, `git`

**Optional fields:**
- `version` - Semantic version
- `tags` - List of tags
- `applies_to` - Glob patterns (must be quoted: `["*.py"]`)

### Subdirectory Organization

**Organize prompts and rules in subdirectories for better structure:**

```
prompts/
├── backend/
│   ├── api/
│   │   └── api-design.md
│   └── database/
│       └── query-optimization.md
├── frontend/
│   └── react-component.md
└── general-coding.md

rules/
├── security/
│   ├── auth/
│   │   └── authentication.md
│   └── encryption.md
└── global-standards.md
```

**Features:**
- **Recursive Discovery** - Files in any subdirectory depth are automatically discovered
- **Structure Preservation** - Subdirectory structure is maintained during deployment
- **Duplicate Detection** - Titles must be unique across all files (prevents conflicts)

**Example:**
- `prompts/backend/api/api-design.md` → Deployed to `.continue/prompts/backend/api/api-design.md`
- Backward compatible: files at root level continue to work

---

## Commands

### init - Initialize Configuration

Initialize prompt-unifier in your project directory.

```bash
prompt-unifier init [OPTIONS]
```

**Options:**
- `--storage-path TEXT` - Custom storage location (default: `~/.prompt-unifier/storage`)

**What it creates:**
- `.prompt-unifier/` - Configuration directory (tracked in version control)
- `.prompt-unifier/config.yaml` - Project configuration
- `~/.prompt-unifier/storage/` - Centralized storage for synced prompts/rules

**Example:**

```bash
# Initialize with default storage
prompt-unifier init

# Initialize with custom storage
prompt-unifier init --storage-path /custom/storage
```

---

### sync - Synchronize from Git

Synchronize prompts and rules from a Git repository to local storage.

```bash
prompt-unifier sync [OPTIONS]
```

**Options:**
- `--repo TEXT` - Git repository URL (saved to config for future syncs)
- `--storage-path TEXT` - Override storage location

**How it works:**
1. Clones repository to temporary directory
2. Extracts `prompts/` (required) and `rules/` (optional) directories
3. Copies to centralized storage (overwrites local files)
4. Updates config with sync timestamp and commit hash

**Common Use Cases:**
- 🔄 **Daily updates**: `prompt-unifier sync` (team gets latest prompts)
- 🆕 **New team member**: Clone project → `prompt-unifier sync` → instant setup
- 🔀 **Switch projects**: Different repos per project, auto-configured

**Authentication for Private Repositories:**

**Option 1: SSH Keys (Recommended)**
```bash
prompt-unifier sync --repo git@github.com:username/repo.git
```

**Option 2: Git Credential Helper**
```bash
git config --global credential.helper store
prompt-unifier sync --repo https://github.com/username/private-repo.git
```

**Option 3: Personal Access Token**
```bash
prompt-unifier sync --repo https://username:TOKEN@github.com/username/repo.git
```

**Examples:**

```bash
# First sync with repository URL
prompt-unifier sync --repo git@github.com:team/prompts.git

# Subsequent syncs (uses URL from config)
prompt-unifier sync

# Override repository URL
prompt-unifier sync --repo git@github.com:other-team/prompts.git
```

---

### status - Check Sync Status

Display synchronization status and check for remote updates.

```bash
prompt-unifier status
```

**What it shows:**
- Storage path
- Repository URL
- Last sync timestamp (human-readable)
- Last synced commit hash
- Update availability (checks remote for new commits)

**Example output:**

```
Prompt Manager Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Storage: /home/user/.prompt-unifier/storage
Repository: https://github.com/team/prompts.git
Last sync: 2 hours ago
Last synced commit: abc1234

✓ Up to date
```

---

### validate - Validate Files

Validate prompt and rule files for syntax errors and required fields.

```bash
prompt-unifier validate [DIRECTORY] [OPTIONS]
```

**Arguments:**
- `DIRECTORY` (optional) - Path to validate. If not provided, validates synchronized storage.

**Options:**
- `--type` / `-t` - Content type: `all` (default), `prompts`, or `rules`
- `--json` - Output results in JSON format
- `--verbose` / `-v` - Show detailed validation progress

**What gets validated:**

**For all files:**
- UTF-8 encoding
- YAML frontmatter syntax
- Required separator (`---`)
- Non-empty content

**For prompts:**
- Required fields: `title`, `description`
- Semantic versioning format (if specified)

**For rules:**
- Required fields: `title`, `description`, `category`
- Valid category (warns if non-standard)
- Kebab-case title format
- Semantic versioning format (if specified)

**Examples:**

```bash
# Validate synchronized storage
prompt-unifier validate

# Validate specific directory
prompt-unifier validate ./my-prompts

# Validate only prompts
prompt-unifier validate --type prompts

# Validate with JSON output
prompt-unifier validate --json
```

---

### deploy - Deploy to Handlers

Deploy prompts and rules to AI coding assistant handlers (currently: **Continue**).

```bash
prompt-unifier deploy [NAME] [OPTIONS]
```

**Arguments:**
- `NAME` (optional) - Specific prompt/rule to deploy. If omitted, deploys all matching items.

**Options:**
- `--tags TEXT` - Comma-separated tags to filter (e.g., `python,review`)
- `--handlers TEXT` - Comma-separated handlers (currently only `continue` supported)
- `--base-path PATH` - Custom base path for deployment
- `--clean` - Remove orphaned files in destination ⚠️ **Permanent deletion**

**What it does:**
- **Recursively discovers** all prompts and rules in subdirectories using `glob("**/*.md")`
- **Detects duplicate titles** across all files before deployment
- **Preserves subdirectory structure** during deployment
  - Example: `prompts/backend/api/api-prompt.md` → `.continue/prompts/backend/api/api-prompt.md`
- Processes content for target handler (e.g., adds `invokable: true` for Continue)
- Backs up existing files
- Verifies deployment success

**Deployment Locations:**
- **Continue**: `{base_path}/.continue/prompts/` and `{base_path}/.continue/rules/`
- **Default base_path**: Current working directory
- **Custom base_path**: Configure in `config.yaml` or via `--base-path` flag

**Examples:**

```bash
# Deploy all prompts/rules to Continue
prompt-unifier deploy

# Deploy specific prompt
prompt-unifier deploy code-review

# Deploy only items tagged "python"
prompt-unifier deploy --tags python

# Deploy with multiple tags
prompt-unifier deploy --tags python,review

# Deploy to custom location
prompt-unifier deploy --base-path /custom/path

# Clean orphaned files during deployment
prompt-unifier deploy --clean
```

**Tag Filtering:**
Items are deployed if they contain **at least one** of the specified tags.

**Clean Option:**
- Removes files in destination that don't exist in source
- Removes all `.bak` backup files
- **Warning:** Deletion is permanent

---

## Configuration

The `.prompt-unifier/config.yaml` file stores project configuration:

```yaml
# Git synchronization
repo_url: https://github.com/example/prompts.git
last_sync_timestamp: 2024-11-11T14:30:00+00:00
last_sync_commit: abc1234
storage_path: /home/user/.prompt-unifier/storage

# Deployment filters (optional)
deploy_tags:
  - python
  - review

target_handlers:
  - continue

# Handler configuration (optional)
handlers:
  continue:
    base_path: $PWD/.continue
```

### Configuration Fields

**Synchronization (managed automatically):**
- `repo_url` - Git repository URL
- `last_sync_timestamp` - ISO 8601 timestamp
- `last_sync_commit` - Short SHA hash
- `storage_path` - Centralized storage path

**Deployment (user-configurable):**
- `deploy_tags` - Tags to filter items during deployment
- `target_handlers` - Handlers to deploy to (currently only `continue` supported)
- `handlers` - Per-handler configuration

### Handler Base Paths

Configure custom deployment locations:

```yaml
handlers:
  continue:
    base_path: $PWD/.continue  # Project-local
    # or
    base_path: $HOME/.continue # User-global
```

**Supported environment variables:**
- `$HOME` or `${HOME}` - User's home directory
- `$USER` or `${USER}` - Current username
- `$PWD` or `${PWD}` - Current working directory

**Precedence order:**
1. CLI `--base-path` flag (temporary override)
2. `config.yaml` handlers section (persistent)
3. Current working directory (default)

---

## Handlers

### Current Support

| Handler | Status | Deploy Location | Notes |
|---------|--------|-----------------|-------|
| **Continue** | ✅ Supported | `~/.continue/` | Full support with subdirectories |
| **Cursor** | 🚧 Coming Soon | `~/.cursor/` | Q1 2025 |
| **Windsurf** | 🚧 Coming Soon | `~/.windsurf/` | Q1 2025 |
| **Aider** | 📋 Planned | TBD | Q2 2025 |
| **Kilo Code** | 📋 Planned | TBD | Q2 2025 |

Want another handler? [Open an issue](https://github.com/your-org/prompt-unifier/issues/new?template=handler-request.md) 🚀

---

## Security

This project uses automated security scanning to detect and prevent security issues.

### Quick Security Reference

| ✅ Safe Practices | ❌ Avoid |
|------------------|----------|
| SSH keys for Git | Tokens in URLs |
| Environment variables | Hardcoded secrets |
| `.gitignore` for `.env` | Committing `.env` |
| Pre-commit hooks enabled | Bypassing with `--no-verify` |

### Security Tools

- **Secrets Detection** - Prevents committing API keys, tokens, passwords
- **SAST** - Static Application Security Testing
- **Dependency Scanning** - Detects vulnerable packages and CVEs

### For Developers

**Pre-commit Hooks (Local):**
```bash
# Install pre-commit hooks
poetry run pre-commit install

# Test hooks
poetry run pre-commit run --all-files
```

**Security Checks:**
- Runs before each `git commit`
- Blocks commits containing secrets or security issues
- Fast feedback (~10-30 seconds)

### Best Practices

**Credential Management:**
- Use SSH keys for Git authentication (recommended)
- Store secrets in environment variables
- Never commit `.env` files with real credentials

```bash
# ✅ Recommended: SSH authentication
prompt-unifier sync --repo git@github.com:username/repo.git

# ❌ Avoid: Token in URL (security risk)
prompt-unifier sync --repo https://user:TOKEN@github.com/user/repo.git
```

**Reporting Security Issues:**

Do not open public issues for security vulnerabilities. Email security issues to: [your-security-email@example.com]

See [SECURITY.md](SECURITY.md) for our responsible disclosure policy.

---

## Architecture

### Architecture Overview

```
┌─────────────────┐
│  Git Repository │
│   (prompts/)    │
└────────┬────────┘
         │ sync
         ▼
┌─────────────────┐
│ Local Storage   │
│ ~/.prompt-mgr/  │
└────────┬────────┘
         │ deploy
         ▼
┌─────────────────┐
│   AI Handlers   │
│ Continue/Cursor │
└─────────────────┘
```

### Data Flow

1. **Git Repository** - Team stores prompts in version-controlled repository
2. **Sync** - Pull latest prompts to local centralized storage
3. **Validate** - Check files for errors and inconsistencies
4. **Deploy** - Push validated prompts to AI coding assistants
5. **Use** - AI tools use deployed prompts for code assistance

---

## Real-World Examples

### Example 1: Team Onboarding

```bash
# New developer joins team
git clone git@github.com:company/backend-service.git
cd backend-service

# One-time setup
prompt-unifier init
prompt-unifier sync  # Gets company's standard prompts
prompt-unifier deploy  # Ready to use Continue with team prompts

# Done! Prompts available in Continue
```

### Example 2: Multi-Project Workflow

```bash
# Each project has its own prompt config
cd ~/projects/api-service
prompt-unifier sync  # Uses API-specific prompts

cd ~/projects/frontend-app
prompt-unifier sync  # Uses frontend-specific prompts

# Each project's `.prompt-unifier/config.yaml` stores its own repo_url
```

### Example 3: Testing New Prompts

```bash
# Create test branch in prompts repo
cd ~/prompts-repo
git checkout -b test-new-prompt
# Edit prompts/new-feature.md
git commit && git push

# In your project
prompt-unifier sync --repo git@github.com:you/prompts.git#test-new-prompt
prompt-unifier deploy
# Test the new prompt in Continue
```

### Example 4: Tag-Based Deployment

```bash
# Deploy only Python-related prompts to Continue
prompt-unifier deploy --tags python --handlers continue

# Deploy Python AND review prompts
prompt-unifier deploy --tags python,review

# Deploy everything
prompt-unifier deploy
```

### Example 5: Custom Deployment Location

```bash
# Deploy to project-specific .continue directory
prompt-unifier deploy --base-path $PWD/.continue

# Or configure permanently in config.yaml
cat >> .prompt-unifier/config.yaml << 'EOF'
handlers:
  continue:
    base_path: $PWD/.continue
EOF

# Now deploy uses project location
prompt-unifier deploy
```

---

## Development

### Setup

```bash
# Install dependencies
make install

# Run tests
make test

# Run linter
make lint

# Run type checker
make typecheck

# Run all quality checks
make check

# Format code
make format

# Generate changelog
make changelog

# Create a new release (e.g., make release VERSION_BUMP=patch)
make release VERSION_BUMP=<type>
```

### CI/CD Local Testing

To run GitLab CI/CD jobs locally, you can use `gitlab-ci-local`. This is useful for debugging your `.gitlab-ci.yml` pipeline without pushing to a remote repository.

#### Prerequisites

You need Node.js and npm installed to install `gitlab-ci-local`.

```bash
# Install Node.js and npm (example for Ubuntu/Debian)
sudo apt update
sudo apt install nodejs npm

# Install gitlab-ci-local globally
npm install -g gitlab-ci-local
```

#### Usage

```bash
# Run tests in GitLab CI environment (with Docker and cache)
make test-ci

# Run tests with shell executor (faster, less accurate)
make test-ci-shell

# Run a specific CI job (e.g., make test-ci-job JOB=lint)
make test-ci-job JOB=<name>

# List all available GitLab CI jobs
make test-ci-list

# Clean GitLab CI local cache and volumes
make clean-ci
```

### Running Tests

```bash
# All tests
make test

# Specific test suites
poetry run pytest tests/cli/
poetry run pytest tests/handlers/
poetry run pytest tests/integration/

# With coverage
poetry run pytest --cov=src/prompt_unifier --cov-report=html
```

### Quality Standards

- **Test Coverage:** ≥95% required
- **Linting:** Ruff (no errors)
- **Type Checking:** mypy (strict mode)
- **Security:** Pre-commit hooks must pass

---

## Troubleshooting

### "Configuration not found" Error

**Problem:** Running `sync` or `status` before `init`

**Solution:**
```bash
prompt-unifier init
```

### Authentication Failures

**Problem:** "Authentication failed. Ensure Git credentials are configured."

**Solutions:**
1. Ensure SSH key is added to your Git hosting service
2. Configure Git credentials: `git config --global credential.helper store`
3. Test Git access manually: `git clone <repo-url>`

### Network Errors

**Problem:** "Check URL is valid and network connection is available."

**Solutions:**
1. Verify internet connectivity
2. Check repository URL is correct
3. Command automatically retries 3 times
4. Use `prompt-unifier status` to see cached information while offline

### Repository Structure Issues

**Problem:** "Repository does not contain a prompts/ directory."

**Solution:** Ensure your repository has a `prompts/` directory at the root level. The `rules/` directory is optional.

### Permission Errors

**Problem:** "Permission denied. Check directory permissions."

**Solutions:**
1. Ensure write permissions in current directory
2. Check `.prompt-unifier/` directory is writable
3. Avoid using `sudo` unless necessary

### Environment Variable Errors

**Problem:** "Environment variable CUSTOM_VAR not found"

**Solution:**
- Use supported variables only: `$HOME`, `$USER`, `$PWD`
- Fix variable reference in `.prompt-unifier/config.yaml`

```yaml
# ❌ Incorrect - CUSTOM_VAR not supported
handlers:
  continue:
    base_path: $CUSTOM_VAR/.continue

# ✅ Correct - use supported variables
handlers:
  continue:
    base_path: $PWD/.continue
```

### Handler Deployment Issues

**Problem:** Prompts deployed to wrong location

**Solution:**
1. Check precedence: CLI `--base-path` > config > default
2. Verify `handlers` section in `.prompt-unifier/config.yaml`
3. Use `--base-path` flag to test deployment

```bash
# Debug deployment location
cat .prompt-unifier/config.yaml | grep -A2 handlers

# Deploy with explicit path to verify
prompt-unifier deploy --base-path /tmp/test-deploy

# Check deployment
ls -la /tmp/test-deploy/.continue/prompts/
```

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
export prompt_unifier_DEBUG=1
prompt-unifier sync --verbose
```

This will show:
- Detailed Git operations
- File system operations
- Handler deployment steps

---

## FAQ

<details>
<summary><b>Q: Can I use multiple Git repositories for prompts?</b></summary>

A: Yes! Each project can have its own `.prompt-unifier/config.yaml` pointing to different repositories. Switch between projects and run `prompt-unifier sync` to load project-specific prompts.
</details>

<details>
<summary><b>Q: What happens if I edit deployed prompts directly in `.continue/`?</b></summary>

A: Your changes will be overwritten on the next `deploy`. Always edit prompts in your Git repository, then sync and deploy.
</details>

<details>
<summary><b>Q: Can I use this without Git?</b></summary>

A: Not recommended, but you can manually manage files in `~/.prompt-unifier/storage/`. However, you'll lose versioning and team sync benefits.
</details>

<details>
<summary><b>Q: How do I share prompts privately within my organization?</b></summary>

A: Use a private Git repository (GitHub, GitLab, Bitbucket) with SSH authentication. Only team members with repository access can sync prompts.
</details>

<details>
<summary><b>Q: Why do I get "Duplicate titles detected"?</b></summary>

A: Each prompt and rule must have a unique `title` across the entire storage. Rename files in different subdirectories if they have the same title.
</details>

<details>
<summary><b>Q: How often should I sync?</b></summary>

A: Sync whenever you want the latest prompts. Common patterns:
- Daily at start of work
- Before starting a new feature
- After team announces prompt updates
- Manually whenever needed
</details>

<details>
<summary><b>Q: Can I deploy to multiple handlers?</b></summary>

A: Yes! Currently only Continue is supported, but Cursor and Windsurf handlers are coming in Q1 2025. You'll be able to do: `prompt-unifier deploy --handlers continue,cursor,windsurf`
</details>

<details>
<summary><b>Q: What's the difference between `--base-path` and `storage_path`?</b></summary>

A: 
- **storage_path** (`~/.prompt-unifier/storage/`) - Where synced prompts are stored locally
- **base_path** (`~/.continue/`) - Where deployed prompts are written for AI tools to use
</details>

---

## Documentation

- **[Manual Testing Guide](./TEST.md)** - Comprehensive testing procedures
- **[Contributing Guide](./CONTRIBUTING.md)** - How to contribute to this project
- **[Security Policy](./SECURITY.md)** - Security guidelines and reporting
- **[License](./LICENSE)** - MIT License
- **[Product Documentation](./docs/)** - Full technical documentation

---

## Contributing

We welcome contributions! Please read our [**Contributing Guide (CONTRIBUTING.md)**](CONTRIBUTING.md) for detailed information on how to contribute to this project.
