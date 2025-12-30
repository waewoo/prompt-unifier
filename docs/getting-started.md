# Getting Started

Welcome to Prompt Unifier! This guide will help you set up your environment and start managing your
prompts in minutes.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+**: Required for running the CLI.
- **Git**: Required for syncing repositories.

## Installation

You can install Prompt Unifier using `pip` or `poetry`.

=== "pip"

````
```bash
pip install prompt-unifier
```
````

=== "poetry"

````
```bash
poetry add prompt-unifier
```
````

## Initial Configuration

Once installed, initialize the application. This creates the necessary configuration files in your
home directory (`~/.prompt-unifier/`).

```bash
prompt-unifier init
```

You should see output similar to:

```text
✅ Config initialized at /home/user/.prompt-unifier/config.yaml
✅ Storage directory created at /home/user/.prompt-unifier/storage
```

## First Usage

Let's sync a repository and deploy prompts to your local environment.

### 1. Sync a Repository

We'll use the **official data repository** which contains a collection of standard prompts.

```bash
prompt-unifier sync --repo https://gitlab.com/waewoo/prompt-unifier-data.git
```

### 2. List Available Prompts

Verify that the prompts have been downloaded.

```bash
prompt-unifier list
```

### 3. Deploy to a Tool

If you use **Kilo Code** or **Continue**, you can deploy these prompts directly to your tool's
configuration.

```bash
# Deploy to all configured tools
prompt-unifier deploy

# OR deploy to a specific tool
prompt-unifier deploy --handlers continue
```

## Troubleshooting

!!! warning "Common Issues"

```
**"Command not found"**
: Ensure your Python scripts directory is in your system `$PATH`.

**"Git authentication failed"**
: If you are syncing a private repository, ensure your local Git is authenticated (e.g., via SSH keys or Credential Helper).

**"Validation Error"**
: If `sync` fails due to validation, the remote repository might contain malformed prompts. Use `prompt-unifier validate` to check local files.
```
