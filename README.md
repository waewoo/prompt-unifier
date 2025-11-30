# Prompt Unifier

[![PyPI Version](https://img.shields.io/pypi/v/prompt-unifier.svg)](https://pypi.org/project/prompt-unifier/)
[![Python Version](https://img.shields.io/pypi/pyversions/prompt-unifier.svg)](https://pypi.org/project/prompt-unifier/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)](./htmlcov)
[![pipeline status](https://img.shields.io/gitlab/pipeline-status/waewoo%2Fprompt-unifier?branch=main)](https://gitlab.com/waewoo/prompt-unifier/-/pipelines)

A Python CLI tool for managing AI prompt templates and coding rules with YAML frontmatter, enabling
version control, validation, and deployment workflows.

______________________________________________________________________

## What is Prompt Unifier?

Managing AI prompts across a team can be chaotic, with templates scattered across local files,
wikis, and chat threads. This leads to a lack of version control, standardization, and a single
source of truth.

**Prompt Unifier** solves this by providing a centralized, Git-based workflow to **sync**,
**validate**, and **deploy** prompt and rule files to your favorite AI coding assistants.

## Features

- ✅ **Git-Based Versioning**: Sync prompts from one or multiple Git repositories.
- ✅ **Centralized Management**: Use a single source of truth for all your prompts and rules.
- ✅ **Validation**: Catch errors in your prompt files before deploying them.
- ✅ **SCAFF Method Validation**: Analyze prompt quality using the SCAFF methodology (Specific,
  Contextual, Actionable, Formatted, Focused) with scoring and actionable suggestions.
- ✅ **Easy Deployment**: A single command to deploy prompts to supported handlers (like
  **Continue**).
- ✅ **Structured Organization**: Recursively discovers files, preserving your subdirectory
  structure.
- ✅ **Multi-Repository Support**: Combine company-wide prompts with team-specific ones seamlessly.
- ✅ **Centralized Logging**: Global verbose mode (`-v`, `-vv`) and file logging (`--log-file`) for
  debugging.

## Current Handler Support

**Prompt Unifier** currently supports the following AI assistants as handlers:

- **Continue** - Full support with YAML frontmatter preservation
- **Kilo Code** - Full support with pure Markdown deployment (no YAML frontmatter)

We plan to integrate with more AI tools and platforms in the future to provide a wider range of
deployment options.

## How it Works: The Workflow

Prompt Unifier streamlines the management and deployment of your AI prompts and rules through a
clear, three-stage workflow:

```text
┌───────────────────────────┐         ┌───────────────────────┐         ┌────────────────────────────┐
│   Remote Git Repositories │         │   Local Storage       │         │   AI Tool Configuration    │
│  (e.g., GitHub, GitLab)   ├─────────► (~/.prompt-unifier/storage) ├───► (e.g., ~/.continue/prompts)│
│    - Global Prompts       │  (Sync) │    - Merged Prompts   │(Deploy) │    - Prompts & Rules       │
│    - Team Rules           │         │    - Merged Rules     │         │      for Active Use        │
└───────────────────────────┘         └───────────────────────┘         └────────────────────────────┘
         ▲                                     ▲
         │                                     │
         └─────────────────────────────────────┘
                 (Version Control & Source of Truth)
```

1. **Sync from Remote Repositories**: You define one or more Git repositories containing your
   structured prompts and rules. **Prompt Unifier** fetches these, resolving conflicts with a
   "last-wins" strategy, and stores them in a centralized local directory. This ensures all your
   content is version-controlled and readily available.
1. **Local Storage**: All synced prompts and rules reside in a dedicated local storage area (e.g.,
   `~/.prompt-unifier/storage`). This acts as your single source of truth, where content is
   validated and prepared for deployment.
1. **Deploy to AI Tool Configuration**: With a simple command, the tool copies the relevant prompts
   and rules from your local storage to the specific configuration directories of your AI assistant
   (e.g., `~/.continue/prompts` for the **Continue** handler). This makes your standardized and
   validated content immediately available for use within your AI development environment.

## Installation

You can install `prompt-unifier` directly from PyPI using `pip`:

```bash
pip install prompt-unifier
```

**Prerequisites:**

- Python 3.11+
- Git 2.x+
- Poetry (for development)

## Quick Start

Get started in 60 seconds:

```bash
# 1. Initialize prompt-unifier in your project
# This creates a .prompt-unifier/config.yaml file.
prompt-unifier init

# 2. Sync prompts from a Git repository
# This clones the repo into a centralized local storage.
prompt-unifier sync --repo https://gitlab.com/waewoo/prompt-unifier-data.git

# 3. Deploy prompts to your AI assistant (e.g., Continue)
# This copies the prompts to the .continue/ folder in your project.
prompt-unifier deploy

# 4. Check the status of your synced repositories
prompt-unifier status
```

## Example Repository

An example repository with prompts and rules is available as a template:

**[prompt-unifier-data](https://gitlab.com/waewoo/prompt-unifier-data)** - A collection of
DevOps-focused prompts and coding rules ready to use with Prompt Unifier.

This repository includes:

- Structured prompts and rules with proper YAML frontmatter
- GitLab CI pipeline for validation
- Auto-bump release mechanism with semantic versioning

You can fork this repository to create your own prompt collection, or use it directly as a starting
point.

## Core Concepts

The tool manages two types of files, both using **YAML frontmatter**.

### Prompts

AI prompt templates, typically stored in a `prompts/` directory within your Git repository.

**Example: `prompts/backend/api-design.md`**

```markdown
---
title: api-design-review
description: Reviews an API design for best practices.
version: 1.1.0
tags: [python, api, backend]
---
# API Design Review

You are an expert API designer. Please review the following API design...
```

### Rules

Coding standards and best practices, typically stored in a `rules/` directory.

**Example: `rules/testing/pytest-best-practices.md`**

```markdown
---
title: pytest-best-practices
description: Best practices for writing tests with pytest.
category: standards
tags: [python, pytest]
version: 1.0.0
---
# Pytest Best Practices

- Use fixtures for setup and teardown.
- Keep tests small and focused.
```

## Commands

The CLI provides several commands to manage your prompts.

### Global Options

These options can be used with any command:

- <code>--verbose</code>, <code>-v</code>: Increase verbosity level. Use `-v` for INFO, `-vv` for
  DEBUG.
- <code>--log-file TEXT</code>: Write logs to a file for persistent debugging.
- <code>--version</code>, <code>-V</code>: Show version and exit.
- <code>--help</code>: Show help message and exit.

```bash
# Run any command with verbose output
prompt-unifier -v validate

# Debug mode with file logging
prompt-unifier -vv --log-file debug.log sync --repo https://github.com/example/prompts.git
```

<details><summary><code>prompt-unifier init</code> - Initialize configuration</summary>
<br>
Creates a <code>.prompt-unifier/config.yaml</code> file in your current directory. This file tracks which repositories you sync from and your deployment settings. It also sets up a local storage directory (default: <code>~/.prompt-unifier/storage/</code>) with <code>prompts/</code>, <code>rules/</code> subdirectories and a <code>.gitignore</code> file.

**Options:**

- <code>--storage-path TEXT</code>: Specify a custom storage directory path instead of the default.

</details>

<details><summary><code>prompt-unifier sync</code> - Synchronize from Git</summary>
<br>
Clones or pulls prompts from one or more Git repositories into a centralized local storage path. You can specify repositories via the command line or in the <code>config.yaml</code> file. The configuration is updated with metadata about the synced repositories.

**Options:**

- <code>--repo TEXT</code>: Git repository URL (can be specified multiple times).
- <code>--storage-path TEXT</code>: Override the default storage path for this sync.

**Multi-Repository Sync with Last-Wins Strategy:** When multiple repositories are synced, files with
identical paths will be overwritten by content from later repositories in the sync order.

```bash
prompt-unifier sync \
  --repo https://github.com/company/global-prompts.git \
  --repo https://github.com/team/team-prompts.git \
  --storage-path /custom/path/storage
```

</details>

<details><summary><code>prompt-unifier status</code> - Check sync status</summary>
<br>
Displays the synchronization status, including when each repository was last synced and whether new commits are available on the remote. It also checks the deployment status of prompts and rules against configured handlers.
</details>

<details><summary><code>prompt-unifier validate</code> - Validate files</summary>
<br>
Checks prompt and rule files for correct YAML frontmatter, required fields, and valid syntax. Also includes SCAFF methodology validation (Specific, Contextual, Actionable, Formatted, Focused) to ensure prompt quality. You can validate the central storage or a local directory of files.

**Options:**

- <code>\[DIRECTORY\]</code>: Optional. Directory to validate (defaults to synchronized storage).
- <code>--json</code>: Output validation results in JSON format.
- <code>--type TEXT</code>, <code>-t TEXT</code>: Specify content type to validate: 'all',
  'prompts', or 'rules' \[default: 'all'\].
- <code>--scaff/--no-scaff</code>: Enable/disable SCAFF methodology validation \[default: enabled\].

**SCAFF Validation:**

By default, the validate command analyzes your prompts against the SCAFF methodology:

- **Specific**: Clear requirements with measurable goals
- **Contextual**: Background information and problem context
- **Actionable**: Concrete action steps and instructions
- **Formatted**: Proper Markdown structure and organization
- **Focused**: Single topic with appropriate length (500-2000 words optimal)

Each prompt receives a score (0-100) and actionable suggestions for improvement. SCAFF validation is
non-blocking (warnings only) and can be disabled with `--no-scaff`.

Use the global <code>-v</code> flag for verbose output (e.g., <code>prompt-unifier -v
validate</code>).

```bash
# Validate with SCAFF checks (default)
prompt-unifier validate

# Validate without SCAFF checks
prompt-unifier validate --no-scaff

# Validate a local directory with SCAFF
prompt-unifier validate ./my-prompts/

# Get JSON output with SCAFF scores
prompt-unifier validate --json
```

</details>

<details><summary><code>prompt-unifier list</code> - List content</summary>
<br>
Displays a table of all available prompts and rules in your centralized storage. You can filter and sort the content using various options.

**Options:**

- <code>--tool</code>, <code>-t TEXT</code>: Filter content by target tool handler.
- <code>--tag TEXT</code>: Filter content by a specific tag.
- <code>--sort</code>, <code>-s TEXT</code>: Sort content by 'name' (default) or 'date'.

Use the global <code>-v</code> flag for verbose output (e.g., <code>prompt-unifier -v list</code>).

```bash
# List all content
prompt-unifier list

# List prompts tagged "python" with verbose output
prompt-unifier -v list --tag python

# List content sorted by date
prompt-unifier list --sort date
```

</details>

<details><summary><code>prompt-unifier deploy</code> - Deploy to handlers</summary>
<br>
Copies the synchronized prompts and rules to the configuration directories of your AI coding assistants.

- **Default Handler:** `continue`
- **Supported Handlers:** `continue`, `kilocode`
- **Default Destinations:**
  - **Continue**: Deploys to `./.continue/` in your current project.
    - Prompts: `./.continue/prompts/`
    - Rules: `./.continue/rules/`
  - **Kilo Code**: Deploys to `./.kilocode/` in your current project.
    - Prompts (Workflows): `./.kilocode/workflows/`
    - Rules: `./.kilocode/rules/`
- **Base Path Override:** Can be overridden via CLI <code>--base-path</code> or handler-specific
  configuration in <code>config.yaml</code>.

**Handler-Specific Behavior:**

- **Continue**: Preserves YAML frontmatter in deployed files
- **Kilo Code**: Converts to pure Markdown (no YAML frontmatter), uses flat directory structure with
  directory-prefixed file naming

**Deployment Options:**

- <code>--name TEXT</code>: Deploy only a specific prompt or rule by name.
- <code>--tags TEXT</code>: Filter content to deploy by tags (comma-separated).
- <code>--handlers TEXT</code>: Specify target handlers for deployment (comma-separated). Supported:
  'continue', 'kilocode'.
- <code>--base-path PATH</code>: Custom base path for handler deployment (overrides config.yaml).
- <code>--clean</code>: Remove orphaned prompts/rules in destination that are not in your source
  (creates backups before removal).
- <code>--dry-run</code>: Preview deployment without executing any file operations.

After deployment, a detailed verification report is provided, outlining the status of each deployed
item.

```bash
# Deploy only prompts tagged "python", with cleanup, and preview changes
prompt-unifier deploy --tags python --clean --dry-run

# Deploy to Kilo Code handler
prompt-unifier deploy --handlers kilocode

# Deploy to both Continue and Kilo Code
prompt-unifier deploy --handlers continue,kilocode
```

</details>

## Development Setup

If you want to contribute to the development of `prompt-unifier`:

1. **Clone the repository:**

   ```bash
   git clone https://gitlab.com/waewoo/prompt-unifier.git
   cd prompt-unifier
   ```

1. **Install dependencies using Poetry:**

   ```bash
   poetry install
   ```

1. **Install pre-commit hooks:** This will run linters and formatters automatically before each
   commit.

   ```bash
   poetry run pre-commit install
   ```

### Running Checks

This project uses a **Makefile-driven architecture** that serves as the single entry point for all
development and CI/CD operations. Commands are organized into functional groups:

#### Environment Setup

- `make env-install`: Install dependencies and git hooks (first-time setup)
- `make env-update`: Update all dependencies (refreshing lock file)
- `make env-clean`: Cleanup temporary files and caches

#### Application Development

- `make app-run ARGS="--version"`: Run the CLI with arguments
- `make app-lint`: Run static analysis (lint, format, types via pre-commit)
- `make app-test`: Run unit tests with coverage
- `make app-check-all`: Run FULL validation (lint + test + CI check)

#### CI/CD Simulation

- `make ci-pipeline`: Run FULL GitLab pipeline locally in Docker
- `make ci-job JOB=<name>`: Run specific GitLab CI job locally
- `make ci-validate`: Validate `.gitlab-ci.yml` syntax
- `make ci-list`: List all available CI jobs
- `make ci-image-build`: Build custom CI base Docker image
- `make ci-image-push`: Push CI base image to registry

#### Security Scanning

- `make sec-all`: Run ALL security scans (code + secrets + deps)
- `make sec-code`: SAST scan with Bandit
- `make sec-secrets`: Secret detection
- `make sec-deps`: Dependency vulnerability check with pip-audit

#### Package & Release

- `make pkg-build`: Build wheel/sdist packages
- `make pkg-changelog`: Generate changelog
- `make pkg-notes VERSION=x.y.z`: Generate release notes
- `make pkg-publish VERSION_BUMP=<patch|minor|major>`: Create release and push tags
- `make pkg-prepare-release`: Auto-bump version (CI only)
- `make pkg-publish-package`: Upload to PyPI (CI only)

#### Documentation

- `make docs-install`: Install documentation dependencies
- `make docs-live PORT=8000`: Serve docs locally with live reload
- `make docs-build`: Build static documentation site

Run `make help` to see all available targets with descriptions.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.
