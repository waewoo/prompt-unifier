# Prompt Manager CLI

A Python CLI tool for managing AI prompt templates and coding rules with YAML frontmatter, enabling version control, validation, and deployment workflows for both prompts and organizational standards.

## Installation

### Prerequisites
- Python 3.12+ (Python 3.11+ supported for compatibility)
- Poetry
- Git (for repository synchronization features)

### Install Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Clone and Install

```bash
git clone <repo-url>
cd prompt-manager
poetry install
```

### Install CLI Globally (after build)

```bash
pipx install .
```

## Quick Start

```bash
# Display help
poetry run prompt-manager --help

# Initialize project with Git integration
poetry run prompt-manager init

# Sync prompts from central repository
poetry run prompt-manager sync --repo https://github.com/example/prompts.git

# Check sync status
poetry run prompt-manager status
```

## File Types: Prompts and Rules

The prompt-manager supports two types of content files using standard YAML frontmatter format (Jekyll/Hugo style):

### Prompts
AI prompt templates for use with language models. Prompts are stored in the `prompts/` directory.

**Example prompt file:**
```markdown
---
title: code-review
description: Review code for bugs and improvements
version: 1.0.0
tags: [python, review]
---

# Code Review Prompt

You are an expert code reviewer...
```

### Rules
Coding standards, best practices, and organizational guidelines. Rules are stored in the `rules/` directory and require a `category` field.

**Example rule file:**
```markdown
---
title: Python Coding Standards
description: Python coding standards and best practices
category: coding-standards
tags: [python, pep8]
version: 1.0.0
applies_to: ["*.py", "*.pyi"]
---

# Python Style Guide

## Naming Conventions
- Use snake_case for functions and variables
- Use PascalCase for classes...
```

**Rule Categories:**
- `coding-standards` - Code style and formatting rules
- `architecture` - System design and architecture patterns
- `security` - Security best practices and guidelines
- `testing` - Testing strategies and requirements
- `documentation` - Documentation standards
- `performance` - Performance optimization guidelines
- `deployment` - Deployment and CI/CD practices
- `git` - Git workflow and commit conventions

**Type Detection:**
Files are automatically detected as prompts or rules based on their location:
- Files in `prompts/` directory → Prompts
- Files in `rules/` directory → Rules

**Special Fields:**
- `category` (required for rules): Categorizes the rule for organization
- `applies_to` (optional): List of glob patterns (must be quoted: `["*.py"]`)

Both prompts and rules use the same format: YAML frontmatter delimited by `---` markers, followed by markdown content.

## Commands Reference

### Global Options

```bash
prompt-manager --help      # Show help and exit
prompt-manager --version   # Show version and exit
```

### validate

Validate prompt and rule files in a directory for syntax errors and required fields.

```bash
prompt-manager validate [DIRECTORY] [OPTIONS]
```

**Arguments:**
- `DIRECTORY` (optional): Path to directory containing .md files to validate. If not provided, validates files in the synchronized storage location (requires `init` to have been run).

**Options:**
- `--type` / `-t`: Content type to validate: `all` (default), `prompts`, or `rules`
- `--json`: Output results in JSON format
- `--verbose` / `-v`: Show detailed validation progress
- `--help`: Show command help

**Examples:**
```bash
# Validate everything (prompts + rules) in synchronized storage
prompt-manager validate

# Validate only prompts
prompt-manager validate --type prompts

# Validate only rules
prompt-manager validate --type rules

# Validate specific directory
prompt-manager validate ./prompts

# Validate with JSON output
prompt-manager validate ./prompts --json

# Validate synchronized storage with verbose output
prompt-manager validate --verbose
```

### init

Initialize prompt-manager configuration in the current directory.

```bash
prompt-manager init [OPTIONS]
```

**Options:**
- `--storage-path TEXT`: Custom storage location (default: `~/.prompt-manager/storage`)
- `--help`: Show command help

**Examples:**
```bash
# Initialize with default storage
prompt-manager init

# Initialize with custom storage location
prompt-manager init --storage-path /custom/storage
```

### sync

Synchronize prompts and rules from a Git repository.

```bash
prompt-manager sync [OPTIONS]
```

**Options:**
- `--repo TEXT`: Git repository URL to sync from
- `--storage-path TEXT`: Override storage location for this sync
- `--help`: Show command help

**Examples:**
```bash
# First sync with repository URL
prompt-manager sync --repo git@github.com:team/prompts.git

# Subsequent syncs (uses URL from config)
prompt-manager sync

# Sync with custom storage location
prompt-manager sync --storage-path /custom/storage
```

### status

Display current synchronization status and check for remote updates.

```bash
prompt-manager status
```

**Options:**
- `--help`: Show command help

**Examples:**
```bash
# Check sync status
prompt-manager status
```

## Git Integration Commands

The prompt-manager CLI provides Git integration commands to sync prompts and rules from a central repository to your application project. This enables teams to maintain a single source of truth for prompts and coding standards while allowing individual projects to stay synchronized.

### Initialize Project

The `init` command sets up your project for prompt synchronization by creating the necessary directory structure and configuration files.

```bash
prompt-manager init
```

**What it creates:**
- `.prompt-manager/` - Configuration directory (tracked in version control)
- `.prompt-manager/config.yaml` - Stores repository URL, sync metadata, and storage path
- `~/.prompt-manager/storage/prompts/` - Centralized directory where synced prompts are stored
- `~/.prompt-manager/storage/rules/` - Centralized directory for prompt rules
- `~/.prompt-manager/storage/.gitignore` - Template file (in storage directory)

**Centralized Storage:** By default, prompts and rules are stored in `~/.prompt-manager/storage` to enable sharing across multiple projects. This means the `.prompt-manager/` directory in your project contains only configuration, not the actual prompts.

**Custom Storage Location:** Use `--storage-path` to specify a custom location:
```bash
prompt-manager init --storage-path /custom/path/storage
```

**Example:**
```bash
cd my-app-project
prompt-manager init
```

**Output:**
```
✓ Initialization complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Created: /path/to/my-app-project/.prompt-manager
Created: /path/to/my-app-project/.prompt-manager/config.yaml
Storage: /home/user/.prompt-manager/storage
Created: /home/user/.prompt-manager/storage/prompts
Created: /home/user/.prompt-manager/storage/rules

Next steps:
  1. Run 'prompt-manager sync --repo <git-url>' to sync prompts
  2. Run 'prompt-manager status' to check sync status
```

**Error Scenarios:**
- Running `init` twice in the same directory will fail with an error message
- Permission errors will display a clear message about directory permissions

### Sync Prompts and Rules

The `sync` command synchronizes prompts and rules from a Git repository to your local project. It clones the repository to a temporary location, extracts the `prompts/` and `rules/` directories, and copies them to your centralized storage.

```bash
# First sync - specify repository URL
prompt-manager sync --repo https://github.com/example/prompts.git

# Subsequent syncs - reads URL from config
prompt-manager sync

# Override repository URL
prompt-manager sync --repo https://github.com/other/prompts.git

# Override storage location for this sync
prompt-manager sync --storage-path /custom/path/storage
```

**How it works:**
1. Validates that `init` has been run (checks for `.prompt-manager/config.yaml`)
2. Uses `--repo` flag if provided, otherwise reads URL from config
3. Determines storage path (--storage-path flag, config, or default)
4. Clones repository to temporary directory
5. Validates that repository contains a `prompts/` directory (required)
6. Copies `prompts/` directory to centralized storage (overwrites local files)
7. Copies `rules/` directory if present in repository (optional)
8. Updates config with sync timestamp and commit hash
9. Cleans up temporary directory

**Conflict Resolution:**
The sync command always takes remote changes and overwrites local files. This is intentional - the central repository is the source of truth. If you need custom prompts, maintain them in the central repository.

**Example:**
```bash
# First sync
prompt-manager sync --repo https://github.com/example/prompts.git
```

**Output:**
```
Syncing prompts and rules...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Repository: https://github.com/example/prompts.git
Storage: /home/user/.prompt-manager/storage

Cloning repository...
Extracting prompts and rules...

✓ Sync complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Repository: https://github.com/example/prompts.git
Commit: abc1234
Synced to: /home/user/.prompt-manager/storage
```

**Authentication for Private Repositories:**

If your repository is private, you need to authenticate. You have **3 authentication options**:

**Option 1: SSH Key (Recommended)**
```bash
# Set up SSH keys with your Git provider first
# Then use SSH URL format:
prompt-manager sync --repo git@gitlab.com:username/repo.git
prompt-manager sync --repo git@github.com:username/repo.git
```

**Option 2: Git Credential Helper**
```bash
# Configure Git to store credentials persistently
git config --global credential.helper store

# Or use cache for temporary storage (credentials expire after 15 minutes)
git config --global credential.helper cache

# Git will prompt for username/password on first clone
prompt-manager sync --repo https://github.com/username/private-repo.git
```

**Option 3: Personal Access Token in URL**
```bash
# Create a personal access token from your Git provider
# Then include it in the URL:
prompt-manager sync --repo https://username:TOKEN@github.com/username/repo.git
prompt-manager sync --repo https://username:TOKEN@gitlab.com/username/repo.git

# ⚠️ Warning: Token is visible in command history and process list
```

**Creating Access Tokens:**
- **GitLab**: Settings → Access Tokens → Add new token (scopes: `read_repository`)
- **GitHub**: Settings → Developer settings → Personal access tokens → Generate new token (scopes: `repo`)

**Error Scenarios:**
- **Init not run:** "Configuration not found. Run 'prompt-manager init' first."
- **No repository URL:** "No repository URL configured. Use --repo flag to specify a repository."
- **Invalid repository URL:** "Failed to clone repository. Check URL and network connection."
- **Authentication failed:** Clear error message with all 3 authentication options explained
- **Missing prompts/ directory:** "Repository does not contain a prompts/ directory."
- **Network errors:** Automatically retries 3 times with exponential backoff before failing

### Check Status

The `status` command displays information about the current sync state, including the repository URL, last sync time, and whether updates are available.

```bash
prompt-manager status
```

**What it shows:**
- Storage path (where prompts are stored)
- Repository URL currently configured
- Last sync timestamp (human-readable format)
- Last synced commit hash
- Update availability (checks remote for new commits)
- Number of commits behind (if updates available)

**Example:**
```bash
prompt-manager status
```

**Output (up to date):**
```
Prompt Manager Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Storage: /home/user/.prompt-manager/storage
Repository: https://github.com/example/prompts.git
Last sync:  2 hours ago
Commit:     abc1234

✓ Up to date
```

**Output (updates available):**
```
Prompt Manager Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Storage: /home/user/.prompt-manager/storage
Repository: https://github.com/example/prompts.git
Last sync:  3 days ago
Commit:     abc1234

⚠ Updates available (5 commits behind)
Run 'prompt-manager sync' to update
```

**Network Errors:**
If the status command cannot reach the remote repository (network issues), it will still display cached information from the last successful sync. The update check will show an error, but the command exits successfully (status is informational only).

## Configuration File Format

The `.prompt-manager/config.yaml` file stores synchronization metadata:

```yaml
repo_url: https://github.com/example/prompts.git
last_sync_timestamp: 2024-11-11T14:30:00+00:00
last_sync_commit: abc1234
storage_path: /home/user/.prompt-manager/storage
```

**Fields:**
- `repo_url` (string | null): Git repository URL to sync from
- `last_sync_timestamp` (string | null): ISO 8601 timestamp of last sync
- `last_sync_commit` (string | null): Short SHA hash of last synced commit
- `storage_path` (string | null): Path to centralized storage directory (defaults to ~/.prompt-manager/storage)

**Note:** This file is managed automatically by the CLI commands. Manual editing is not recommended unless recovering from corruption.

## Validation

The `validate` command checks prompts and rules for syntax errors, required fields, and adherence to standards.

```bash
# Validate files in a directory
poetry run prompt-manager validate /path/to/directory

# Validate with JSON output
poetry run prompt-manager validate /path/to/directory --json
```

**What gets validated:**

For all files:
- UTF-8 encoding
- YAML frontmatter syntax
- Required `>>>` separator
- Non-empty content

For prompts:
- Required fields: `name`, `description`
- Optional fields: `version`, `tags`, `author`
- Semantic versioning format (if specified)
- No prohibited fields (e.g., `tools`)

For rules:
- Required fields: `name`, `description`, `type: rule`, `category`
- Optional fields: `version`, `tags`, `author`, `applies_to`
- Valid category (warns if non-standard)
- Kebab-case name format (e.g., `python-style-guide`)
- Semantic versioning format (if specified)

**Example validation output:**
```
Validating directory: /tmp/test-rules
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ python-style.md (rule)
✓ code-review.md (prompt)
✗ invalid-rule.md (rule)
  Error: Field 'category' is required for rules

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary: 2 passed, 1 failed
```

## Common Workflows

### Team Setup

**Initial setup for a new team member:**
```bash
# Clone application project
git clone https://github.com/team/application.git
cd application

# The .prompt-manager/ directory is already in the repo
# Just sync prompts from the configured repository
prompt-manager sync
```

**Setting up a new application project:**
```bash
# Create or navigate to your application project
cd my-new-app

# Initialize Git integration
prompt-manager init

# Sync prompts from central repository
prompt-manager sync --repo https://github.com/team/central-prompts.git

# Commit the configuration (prompts/rules are in centralized storage, not in project)
git add .prompt-manager/
git commit -m "Initialize prompt-manager with central repository"
git push
```

### Regular Updates

**Check for updates daily:**
```bash
# Check if new prompts are available
prompt-manager status

# Sync latest changes
prompt-manager sync
```

**Automated sync in CI/CD:**
```bash
# In your CI/CD pipeline (e.g., GitHub Actions, GitLab CI)
prompt-manager sync
```

### Switching Repositories

**Change to a different central repository:**
```bash
# Override with new repository URL
prompt-manager sync --repo https://github.com/team/new-prompts.git

# Subsequent syncs will use the new URL
prompt-manager sync
```

## Security

This project uses automated security scanning to detect and prevent security issues before they reach production.

### Security Scanning Tools

The project implements multiple layers of security:

- **Secrets Detection** - Prevents committing API keys, tokens, and passwords
- **SAST (Static Application Security Testing)** - Identifies code security vulnerabilities
- **Dependency Scanning** - Detects vulnerable packages and CVEs

### For Developers

Security checks run automatically at two levels:

**1. Pre-commit Hooks (Local)**
- Runs before each `git commit`
- Blocks commits containing secrets or security issues
- Fast feedback loop (~10-30 seconds)

**2. CI/CD Pipeline (GitLab)**
- Runs on every merge request
- Comprehensive security scan of entire codebase
- Generates security reports as artifacts

### Getting Started with Security Tools

Install pre-commit hooks after cloning:

```bash
# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install

# Test hooks (optional)
poetry run pre-commit run --all-files
```

### What Gets Checked?

**Local (Pre-commit):**
- API keys, tokens, passwords (detect-secrets)
- Python security vulnerabilities (bandit)
- Code formatting and type safety (ruff, mypy)

**CI/CD (GitLab):**
- All pre-commit checks
- Dependency vulnerabilities (safety, pip-audit)
- CVE database scanning
- Security report generation

### Handling Security Findings

**If a secret is detected:**
```bash
# Use environment variables instead
import os
api_key = os.getenv("API_KEY")  # Good

# Don't hardcode secrets
api_key = "sk-1234..."  # Bad - will be blocked
```

**If a security vulnerability is found:**
- Review the finding in the commit output or CI logs
- Follow the remediation guidance provided
- See [docs/security.md](docs/security.md) for detailed fixes

### Best Practices

**Credential Management:**
- Use SSH keys for Git authentication (recommended)
- Store secrets in environment variables
- Never commit `.env` files with real credentials

**Example: SSH vs Token**
```bash
# ✅ Recommended: SSH authentication
prompt-manager sync --repo git@gitlab.com:username/repo.git

# ❌ Avoid: Token in URL (security risk)
prompt-manager sync --repo https://user:TOKEN@gitlab.com/user/repo.git
```

### Documentation

- **[SECURITY.md](SECURITY.md)** - Security policy and vulnerability reporting
- **[docs/security.md](docs/security.md)** - Developer security guide
- **[docs/ci-security.md](docs/ci-security.md)** - CI/CD security pipeline documentation

### Reporting Security Issues

**Do not** open public issues for security vulnerabilities.

Instead, email security issues to: [your-security-email@example.com]

See [SECURITY.md](SECURITY.md) for our responsible disclosure policy.

## Troubleshooting

### "Configuration not found" Error

**Problem:** Running `sync` or `status` before `init`

**Solution:**
```bash
prompt-manager init
```

### Authentication Failures

**Problem:** "Authentication failed. Ensure Git credentials are configured."

**Solutions:**
1. **SSH authentication:** Ensure your SSH key is added to your Git hosting service
2. **HTTPS authentication:** Configure Git credentials or use a personal access token
3. **Test Git access:** Try cloning the repository manually with `git clone`

### Network Errors

**Problem:** "Check URL and network connection."

**Solutions:**
1. Verify internet connectivity
2. Check that the repository URL is correct
3. The command automatically retries 3 times - if it still fails, check your network
4. Use `prompt-manager status` to see cached information while offline

### Repository Doesn't Contain prompts/ Directory

**Problem:** "Repository does not contain a prompts/ directory."

**Solution:** Ensure your central repository has a `prompts/` directory at the root level. The sync command requires this specific structure.

**Note:** The `rules/` directory is optional. If your repository contains a `rules/` directory, it will be synced automatically. If not, only the `prompts/` directory will be synced.

### Permission Errors

**Problem:** "Permission denied. Check directory permissions."

**Solutions:**
1. Ensure you have write permissions in the current directory
2. Check that `.prompt-manager/`, `prompts/`, and `rules/` directories are writable
3. Run with appropriate user permissions (avoid `sudo` unless necessary)

## Development

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
```

### Running Git Integration Tests

```bash
# Run all Git integration tests
poetry run pytest tests/config/ tests/git/ tests/cli/test_git_commands.py tests/integration/test_git_integration.py tests/utils/test_formatting.py

# Run tests with coverage
poetry run pytest tests/config/ tests/git/ tests/cli/test_git_commands.py tests/integration/test_git_integration.py tests/utils/test_formatting.py --cov=src/prompt_manager/config --cov=src/prompt_manager/git --cov-report=term-missing
```

## Documentation

See `agent-os/product/` for full product documentation.

## Contributing

Pull requests welcome. Please ensure `make check` passes before submitting.

## License

MIT
