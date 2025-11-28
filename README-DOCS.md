# Documentation Maintenance Guide

## Local Development

### Install dependencies

```bash
poetry install --with docs
# Dependencies now include:
# - mkdocs-material
# - mkdocs-git-revision-date-localized-plugin
# - mkdocs-minify-plugin
# - mkdocs-include-markdown-plugin
```

### Preview locally

```bash
poetry run mkdocs serve
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

### Build static site

```bash
poetry run mkdocs build
```

## Deployment

Documentation is automatically deployed to GitLab Pages on push to `main`.

URL: [https://waewoo.gitlab.io/prompt-unifier](https://waewoo.gitlab.io/prompt-unifier)

## Structure

- `docs/` - Markdown source files
- `mkdocs.yml` - MkDocs configuration
- `.gitlab-ci.yml` - CI/CD pipeline (includes docs deployment)

## Adding Content

1. Create/edit markdown files in `docs/`.
1. Update navigation in `mkdocs.yml` if needed.
1. Test locally with `mkdocs serve`.
1. Commit and push.

## Tips

- Use admonitions for notes/warnings: `!!! note`.
- Code blocks support syntax highlighting.
- Images go in `docs/assets/`.
- Links are relative: `[text](../other-page.md)`.

## Style Guidelines

### Tone and Approach

- **Professional but accessible**: No unnecessary jargon.
- **Action-oriented**: Focus on "how to".
- **Concrete examples**: Real code, not pseudo-code.
- **Progressive disclosure**: Simple to advanced.

### Visual Elements

- Use **admonitions** Material (note, tip, warning, danger).
- **Emojis/Icons** for important sections.
- **Code blocks** with explanatory comments.
- **Tabs** for alternatives (pip vs poetry, etc.).

### Examples of Expected Patterns

**Admonition**:

```markdown
!!! tip "Pro Tip"
    Use `prompt-unifier sync --watch` to auto-sync on changes
```

**Tabs**:

```markdown
=== "pip"
    pip install prompt-unifier

=== "poetry"
    poetry add prompt-unifier
```

**Badges** (index.md):

```markdown
[![GitLab CI](https://gitlab.com/waewoo/prompt-unifier/badges/main/pipeline.svg)](https://gitlab.com/waewoo/prompt-unifier/-/pipelines)
```
