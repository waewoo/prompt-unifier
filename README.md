# Prompt Manager CLI

A Python CLI tool for managing AI prompt templates with YAML frontmatter, enabling version control, validation, and deployment workflows.

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

## Git Integration Commands

The prompt-manager CLI provides Git integration commands to sync prompts from a central repository to your application project. This enables teams to maintain a single source of truth for prompts while allowing individual projects to stay synchronized.

### Initialize Project

The `init` command sets up your project for prompt synchronization by creating the necessary directory structure and configuration files.

```bash
prompt-manager init
```

**What it creates:**
- `.prompt-manager/` - Configuration directory (tracked in version control)
- `.prompt-manager/config.yaml` - Stores repository URL and sync metadata
- `prompts/` - Directory where synced prompts will be stored
- `rules/` - Directory for prompt rules
- `.gitignore` - Template file (if it doesn't exist)

**Important:** The `.prompt-manager/` directory is tracked in version control so that team members share the same configuration.

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
Created: /path/to/my-app-project/prompts
Created: /path/to/my-app-project/rules

Next steps:
  1. Run 'prompt-manager sync --repo <git-url>' to sync prompts
  2. Run 'prompt-manager status' to check sync status
```

**Error Scenarios:**
- Running `init` twice in the same directory will fail with an error message
- Permission errors will display a clear message about directory permissions

### Sync Prompts

The `sync` command synchronizes prompts from a Git repository to your local project. It clones the repository to a temporary location, extracts the `prompts/` directory, and copies it to your project.

```bash
# First sync - specify repository URL
prompt-manager sync --repo https://github.com/example/prompts.git

# Subsequent syncs - reads URL from config
prompt-manager sync

# Override repository URL
prompt-manager sync --repo https://github.com/other/prompts.git
```

**How it works:**
1. Validates that `init` has been run (checks for `.prompt-manager/config.yaml`)
2. Uses `--repo` flag if provided, otherwise reads URL from config
3. Clones repository to temporary directory
4. Validates that repository contains a `prompts/` directory
5. Copies `prompts/` directory to your project (overwrites local files)
6. Updates config with sync timestamp and commit hash
7. Cleans up temporary directory

**Conflict Resolution:**
The sync command always takes remote changes and overwrites local files. This is intentional - the central repository is the source of truth. If you need custom prompts, maintain them in the central repository.

**Example:**
```bash
# First sync
prompt-manager sync --repo https://github.com/example/prompts.git
```

**Output:**
```
Syncing prompts...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Repository: https://github.com/example/prompts.git

Cloning repository...
Extracting prompts...

✓ Sync complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Repository: https://github.com/example/prompts.git
Commit: abc1234
Synced to: /path/to/my-app-project/prompts
```

**Error Scenarios:**
- **Init not run:** "Configuration not found. Run 'prompt-manager init' first."
- **No repository URL:** "No repository URL configured. Use --repo flag to specify a repository."
- **Invalid repository URL:** "Failed to clone repository. Check URL and network connection."
- **Authentication failed:** "Authentication failed. Ensure Git credentials are configured."
- **Missing prompts/ directory:** "Repository does not contain a prompts/ directory."
- **Network errors:** Automatically retries 3 times with exponential backoff before failing

### Check Status

The `status` command displays information about the current sync state, including the repository URL, last sync time, and whether updates are available.

```bash
prompt-manager status
```

**What it shows:**
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
Git Sync Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Repository: https://github.com/example/prompts.git
Last sync:  2 hours ago
Commit:     abc1234

✓ Up to date
```

**Output (updates available):**
```
Git Sync Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

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
```

**Fields:**
- `repo_url` (string | null): Git repository URL to sync from
- `last_sync_timestamp` (string | null): ISO 8601 timestamp of last sync
- `last_sync_commit` (string | null): Short SHA hash of last synced commit

**Note:** This file is managed automatically by the CLI commands. Manual editing is not recommended unless recovering from corruption.

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

# Commit the configuration
git add .prompt-manager/ prompts/ rules/
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
