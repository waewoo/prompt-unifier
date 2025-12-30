# Advanced Usage

For power users and platform engineers, Prompt Unifier offers advanced configuration and integration
capabilities.

## Complex Scenarios

### Multi-Repository Setup

You might need prompts from different sources (e.g., a company-wide repo for policy prompts and a
team-specific repo for code prompts).

You can configure multiple repositories in `~/.prompt-unifier/config.yaml` for persistent sync:

```yaml
repositories:
  - https://gitlab.com/company/global-prompts.git
  - https://gitlab.com/team-backend/api-prompts.git
```

Alternatively, you can perform a **one-off sync** from multiple repositories directly via the CLI,
without modifying your configuration file:

```bash
prompt-unifier sync --repo https://gitlab.com/other/repo1.git --repo https://gitlab.com/other/repo2.git
```

This is useful for quickly pulling specific sets of prompts or testing new repositories.

### Selective Deployment

If you only want to update your configuration for a specific tool without touching others:

```bash
prompt-unifier deploy --handlers continue
```

## Configuration Advanced

### Custom Base Paths

By default, Prompt Unifier assumes standard installation paths (e.g., `~/.continue`). If you have a
custom setup, you can override these paths in your config.

**File:** `~/.prompt-unifier/config.yaml`

```yaml
handlers:
  continue:
    enabled: true
    base_path: /opt/custom/continue-config
  kilo:
    enabled: true
    base_path: /workspace/project/.kilocode
```

## CI/CD Integration

You can use Prompt Unifier in your CI/CD pipelines to validate prompts before they are merged into
your main branch.

### GitLab CI Example

Add this job to your pipeline to ensure no broken prompts break your team's workflow:

```yaml
validate-prompts:
  image: python:3.11
  script:
    - pip install prompt-unifier
    - prompt-unifier validate ./prompts
```

This will exit with a non-zero status code if any prompt file fails validation (e.g., missing
required YAML fields, invalid syntax).
