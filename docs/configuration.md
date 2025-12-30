# Configuration

Prompt Unifier uses a YAML configuration file located at `~/.prompt-unifier/config.yaml`.

## Configuration Structure

The configuration file controls repositories, enabled tools, and tool-specific settings.

```yaml
# ~/.prompt-unifier/config.yaml

# List of Git repositories to sync
# Can be a simple list of URLs or detailed configurations
repos:
  - url: https://gitlab.com/waewoo/prompt-unifier-data.git # (1)
  - url: https://gitlab.com/my-org/team-prompts.git # (2)
    branch: develop
    # auth_config: # (3)
    #   method: ssh_key
    #   path: ~/.ssh/id_ed25519
    include_patterns: ["*.md", "python/**"] # (4)
    exclude_patterns: ["**/drafts/*"]

# Path to centralized storage directory for prompts and rules
# Defaults to ~/.prompt-unifier/storage/
storage_path: ~/.prompt-unifier/custom_storage # (5)

# List of tags to filter prompts and rules for deployment (optional)
# Only prompts/rules matching these tags will be deployed
deploy_tags:
  - python
  - review # (6)

# List of target handlers for deployment (optional)
# Only prompts/rules for these handlers will be deployed
target_handlers:
  - continue
  - kilocode # (7)

# Per-handler configuration including base paths
handlers:
  continue:
    base_path: $PWD/.continue # (8)
  kilocode:
    base_path: ${HOME}/.kilocode # (9)

# Auto-generated fields (do not edit manually)
last_sync_timestamp: '2025-11-27T18:19:37.633461+00:00'
repo_metadata:
  - url: https://gitlab.com/waewoo/prompt-unifier-data.git
    branch: main
    commit: c54cf4e
    timestamp: '2025-11-27T18:19:37.587247+00:00'
    base_path: $PWD/.continue # (9)
  kilo:
    base_path: ${HOME}/.kilocode # (10)

# Global AI provider for functional testing (optional)
# Can be overridden in individual .test.yaml files
ai_provider: mistral/mistral-small-latest # (11)
```

1. **Default Repository**: A simple repository configuration with just the URL.
1. **Detailed Repository Configuration**: Specify `url`, `branch`, and filtering patterns.
1. **Authentication Configuration (Reserved)**: Currently reserved for future use. For now, ensure
   your SSH agent or Git credential helper is configured globally.
1. **Inclusion/Exclusion Patterns**:
   - `include_patterns`: Only files matching these glob patterns will be synced.
   - `exclude_patterns`: Files matching these patterns will be excluded (applied after inclusion).
1. **Custom Storage Path**: Override the default location where prompts and rules are stored
   locally.
1. **Filter Deployment by Tags**: Deploy only prompts/rules that have the specified tags in their
   YAML frontmatter.
1. **Filter Deployment by Handlers**: Deploy only to the specified tool handlers (e.g., `continue`,
   `kilocode`).
1. **Custom Base Path for Continue**: Override where Continue's prompts are deployed (e.g., in the
   current working directory).
1. **Custom Base Path for Kilo Code**: Another example using an environment variable for the path.
1. **Global AI Provider**: The default model used for `test` command when not specified in the test
   file. Supports 100+ providers via LiteLLM.

## Repository Structure

To be compatible with Prompt Unifier, your Git repository should follow this simple structure:

```text
my-prompts-repo/
├── prompts/           # Directory containing prompt files
│   ├── my-prompt.md
│   └── ...
├── rules/             # Directory containing rule files
│   ├── my-rule.md
│   └── ...
├── README.md          # Optional
└── .gitignore         # Recommended
```

### Prompt File Format

Each file in `prompts/` must be a Markdown file with YAML frontmatter.

```markdown
---
title: "python-expert"
description: "Acts as a senior Python developer"
version: 1.0.0
tags: ["python", "coding"]
---

You are a senior Python developer. Your code is clean, efficient, and typed...
```

### Rule File Format

Each file in `rules/` uses a similar format.

```markdown
---
title: "pytest-best-practices"
description: "Standards for writing tests"
category: standards
tags: ["python", "testing"]
---

# Pytest Best Practices

- Use fixtures for setup...
```

## Multi-Repo Setup

If you configure multiple repositories, Prompt Unifier will merge them into your local storage.

- **Conflict Resolution**: If two repositories contain a prompt with the same filename, the one from
  the *last* repository in the list will take precedence (last-write-wins).
- **Best Practice**: Use unique prefixes for prompts in different repositories if you expect overlap
  (e.g., `team1-bug-report.md`, `team2-bug-report.md`).
