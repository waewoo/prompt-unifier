# Prompt Manager CLI

A Python CLI tool for managing AI prompt templates with YAML frontmatter, enabling version control, validation, and deployment workflows.

## Installation

### Prerequisites
- Python 3.12+ (Python 3.11+ supported for compatibility)
- Poetry

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

# Validate prompts (future feature)
poetry run prompt-manager validate prompts/
```

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

## Documentation

See `agent-os/product/` for full product documentation.

## Contributing

Pull requests welcome. Please ensure `make check` passes before submitting.

## License

MIT
