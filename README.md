# Prompt Unifier

[![PyPI Version](https://img.shields.io/pypi/v/prompt-unifier.svg)](https://pypi.org/project/prompt-unifier/) [![Python Version](https://img.shields.io/pypi/pyversions/prompt-unifier.svg)](https://pypi.org/project/prompt-unifier/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Code Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)](./htmlcov) [![CI/CD Status](https://img.shields.io/gitlab/pipeline-status/waewoo/prompt-unifier)](https://gitlab.com/waewoo/prompt-unifier/-/pipelines)

A Python CLI tool for managing AI prompt templates and coding rules with YAML frontmatter, enabling version control, validation, and deployment workflows.

---

## What is Prompt Unifier?

Managing AI prompts across a team can be chaotic, with templates scattered across local files, wikis, and chat threads. This leads to a lack of version control, standardization, and a single source of truth.

**Prompt Unifier** solves this by providing a centralized, Git-based workflow to **sync**, **validate**, and **deploy** prompt and rule files to your favorite AI coding assistants.

## Features

- ✅ **Git-Based Versioning**: Sync prompts from one or multiple Git repositories.
- ✅ **Centralized Management**: Use a single source of truth for all your prompts and rules.
- ✅ **Validation**: Catch errors in your prompt files before deploying them.
- ✅ **Easy Deployment**: A single command to deploy prompts to supported handlers (like **Continue**).
- ✅ **Structured Organization**: Recursively discovers files, preserving your subdirectory structure.
- ✅ **Multi-Repository Support**: Combine company-wide prompts with team-specific ones seamlessly.

## Installation

You can install `prompt-unifier` directly from PyPI using `pip`:

```bash
pip install prompt-unifier
```

**Prerequisites:**
- Python 3.11+
- Git 2.x+

## Quick Start

Get started in 60 seconds:

```bash
# 1. Initialize prompt-unifier in your project
# This creates a .prompt-unifier/config.yaml file.
prompt-unifier init

# 2. Sync prompts from a Git repository
# This clones the repo into a centralized local storage.
prompt-unifier sync --repo https://github.com/prompt-unifier/example-prompts.git

# 3. Deploy prompts to your AI assistant (e.g., Continue)
# This copies the prompts to the .continue/ folder in your project.
prompt-unifier deploy

# 4. Check the status of your synced repositories
prompt-unifier status
```

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
category: testing
tags: [python, pytest]
version: 1.0.0
---
# Pytest Best Practices

- Use fixtures for setup and teardown.
- Keep tests small and focused.
```

## Commands

The CLI provides several commands to manage your prompts.

<details><summary><code>prompt-unifier init</code> - Initialize configuration</summary>
<br>
Creates a <code>.prompt-unifier/config.yaml</code> file in your current directory. This file tracks which repositories you sync from and your deployment settings.
</details>

<details><summary><code>prompt-unifier sync</code> - Synchronize from Git</summary>
<br>
Clones or pulls prompts from one or more Git repositories into a centralized local storage path (<code>~/.prompt-unifier/storage/</code>). You can specify repositories via the command line or in the <code>config.yaml</code> file.

**Multi-Repository Sync:**
```bash
prompt-unifier sync \
  --repo https://github.com/company/global-prompts.git \
  --repo https://github.com/team/team-prompts.git
```
Files from later repositories will override files from earlier ones if they have the same path (last-wins strategy).
</details>

<details><summary><code>prompt-unifier status</code> - Check sync status</summary>
<br>
Displays the synchronization status, including when each repository was last synced and whether new commits are available on the remote.
</details>

<details><summary><code>prompt-unifier validate</code> - Validate files</summary>
<br>
Checks prompt and rule files for correct YAML frontmatter, required fields, and valid syntax. You can validate the central storage or a local directory of files.

```bash
# Validate the central storage
prompt-unifier validate

# Validate a local directory
prompt-unifier validate ./my-prompts/
```
</details>

<details><summary><code>prompt-unifier deploy</code> - Deploy to handlers</summary>
<br>
Copies the synchronized prompts and rules to the configuration directories of your AI coding assistants.

- **Default Handler:** `continue`
- **Default Destination:** `./.continue/` (in your current project)

You can filter which prompts to deploy using tags:
```bash
# Deploy only prompts tagged "python"
prompt-unifier deploy --tags python
```
</details>

## Development Setup

If you want to contribute to the development of `prompt-unifier`:

1.  **Clone the repository:**
    ```bash
    git clone https://gitlab.com/waewoo/prompt-unifier.git
    cd prompt-unifier
    ```

2.  **Install dependencies using Poetry:**
    ```bash
    poetry install
    ```

3.  **Install pre-commit hooks:**
    This will run linters and formatters automatically before each commit.
    ```bash
    poetry run pre-commit install
    ```

### Running Checks

This project uses a `Makefile` for common development tasks:

-   `make install`: Install dependencies.
-   `make test`: Run the test suite.
-   `make lint`: Check for linting issues with Ruff.
-   `make format`: Format code with Ruff.
-   `make typecheck`: Run static type analysis with mypy.
-   `make check`: Run all checks (lint, types, tests).

## Contributing

We welcome contributions! Please read our [**Contributing Guide (CONTRIBUTING.md)**](CONTRIBUTING.md) for more details on how to submit pull requests, report issues, and more.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
