# Configuration

Prompt Unifier uses a YAML configuration file located at `~/.prompt-unifier/config.yaml`.

## Configuration Structure

The configuration file controls repositories, enabled tools, and tool-specific settings.

```yaml
# ~/.prompt-unifier/config.yaml

# List of Git repositories to sync
# Can be a simple list of URLs or detailed configurations
repositories:
  - https://gitlab.com/waewoo/prompt-unifier-data.git # (1)
  - url: https://gitlab.com/my-org/team-prompts.git # (2)
    branch: develop
    # auth_config: # (3)
    #   method: ssh_key
    #   path: ~/.ssh/id_ed25519
    include_patterns: ["*.md", "python/**"] # (4)
    exclude_patterns: ["**/drafts/*"]
  - url: https://github.com/community/awesome-prompts.git
    auth_config:
      method: token
      token: ghp_YOUR_GITHUB_TOKEN # (5)

# Path to centralized storage directory for prompts and rules
# Defaults to ~/.prompt-unifier/storage/
storage_path: ~/.prompt-unifier/custom_storage # (6)

# List of tags to filter prompts and rules for deployment (optional)
# Only prompts/rules matching these tags will be deployed
deploy_tags:
  - python
  - review # (7)

# List of target handlers for deployment (optional)
# Only prompts/rules for these handlers will be deployed
target_handlers:
  - continue
  - kilo # (8)

# Per-handler configuration including base paths
handlers:
  continue:
    base_path: $PWD/.continue # (9)
  kilo:
    base_path: ${HOME}/.kilocode # (10)
```

1. **Default Repository**: The simplest way to define a repository.
1. **Detailed Repository Configuration**: Specify `url`, `branch`, and filtering patterns.
1. **Authentication Configuration (Optional)**:
   - `method`: `ssh_key` (uses your SSH agent), `token` (uses provided `token`), `credential_helper`
     (uses Git credential helper).
   - `path`: (for `ssh_key`) Path to the private SSH key.
   - `token`: (for `token`) The personal access token.
1. **Inclusion Patterns**: Only files matching these glob patterns will be synced from this
   repository.
1. **Token Authentication**: Use a Personal Access Token (PAT) for private repositories. **Warning:
   Avoid hardcoding tokens in `config.yaml` for security reasons. Use environment variables or Git
   credential helpers instead.**
1. **Custom Storage Path**: Override the default location where prompts and rules are stored
   locally.
1. **Filter Deployment by Tags**: Deploy only prompts/rules that have the specified tags in their
   YAML frontmatter.
1. **Filter Deployment by Handlers**: Deploy only to the specified tool handlers.
1. **Custom Base Path for Continue**: Override where Continue's prompts are deployed (e.g., in the
   current working directory).
1. **Custom Base Path for Kilo Code**: Another example using an environment variable for the path.

## Repository Structure

To be compatible with Prompt Unifier, your Git repository should follow this simple structure:

```text
my-prompts-repo/
├── prompts/           # Directory containing prompt files
│   ├── my-prompt.md
│   └── ...
├── README.md          # Optional
└── .gitignore         # Recommended
```

### Prompt File Format

Each file in `prompts/` must be a Markdown file with YAML frontmatter.

```markdown
---
name: "Python Expert"
description: "Acts as a senior Python developer"
authors: ["Jane Doe"]
tags: ["python", "coding"]
tools: ["kilo", "continue"]
---

You are a senior Python developer. Your code is clean, efficient, and typed...
```

## Multi-Repo Setup

If you configure multiple repositories, Prompt Unifier will merge them into your local storage.

- **Conflict Resolution**: If two repositories contain a prompt with the same filename, the one from
  the *last* repository in the list will take precedence (last-write-wins).
- **Best Practice**: Use unique prefixes for prompts in different repositories if you expect overlap
  (e.g., `team1-bug-report.md`, `team2-bug-report.md`).
