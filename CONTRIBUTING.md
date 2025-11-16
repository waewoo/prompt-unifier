# Contributing to Prompt Manager

Thank you for your interest in contributing to Prompt Manager! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Adding New Handlers](#adding-new-handlers)

---

## Code of Conduct

Please be respectful and constructive in all interactions. We aim to maintain a welcoming and inclusive community.

---

## Getting Started

### Prerequisites

- Python 3.11+ (Python 3.12+ recommended)
- Poetry for dependency management
- Git for version control
- Basic understanding of Python, CLI tools, and YAML

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:

```bash
git clone https://github.com/YOUR_USERNAME/prompt-manager.git
cd prompt-manager
```

3. Add the upstream remote:

```bash
git remote add upstream https://github.com/ORIGINAL_OWNER/prompt-manager.git
```

---

## Development Setup

### Install Dependencies

```bash
# Install all dependencies including dev dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install
```

### Verify Installation

```bash
# Run tests
make test

# Run linter
make lint

# Run type checker
make typecheck

# Run all checks
make check
```

---

## Making Changes

### Branch Naming

Create a descriptive branch for your changes:

```bash
git checkout -b feature/add-cursor-handler
git checkout -b fix/deployment-path-bug
git checkout -b docs/update-readme
```

**Branch prefixes:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions or fixes

### Commit Messages

Follow the conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Examples:**

```bash
feat(handlers): Add Cursor handler implementation

Implements ToolHandler for Cursor AI editor with subdirectory
support and proper YAML formatting.

Closes #123
```

```bash
fix(deploy): Correctly calculate relative paths for nested files

The deploy command was not preserving subdirectory structure
for files more than 2 levels deep.

Fixes #456
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation only
- `style` - Code style changes (formatting, etc.)
- `refactor` - Code refactoring
- `test` - Adding or updating tests
- `chore` - Maintenance tasks

---

## Coding Standards

### Python Style

We use **Ruff** for linting and formatting:

```bash
# Check code style
make lint

# Auto-format code
make format
```

**Key guidelines:**
- Follow PEP 8
- Maximum line length: 100 characters
- Use type hints for all functions
- Write docstrings for public APIs

### Type Checking

We use **mypy** in strict mode:

```bash
make typecheck
```

All code must pass type checking without errors.

### Code Organization

```
src/prompt_manager/
├── cli/           # CLI commands and main entry point
├── core/          # Core validation and parsing logic
├── handlers/      # Tool handler implementations
├── models/        # Pydantic models
├── git/           # Git integration services
├── config/        # Configuration management
├── output/        # Output formatters
└── utils/         # Utility functions

tests/
├── cli/           # CLI command tests
├── core/          # Core logic tests
├── handlers/      # Handler tests
├── integration/   # End-to-end integration tests
├── models/        # Model tests
└── fixtures/      # Test fixtures
```

### Documentation

- **Docstrings:** Use Google-style docstrings
- **Type hints:** Required for all public functions
- **Comments:** Explain "why", not "what"
- **README:** Update for user-facing changes
- **TEST.md:** Add tests for new features

**Example docstring:**

```python
def deploy(
    self,
    content: Prompt | Rule,
    base_path: Path,
    relative_path: Path | None = None,
) -> None:
    """Deploy content to the handler's target directory.

    Args:
        content: The prompt or rule to deploy
        base_path: Base deployment path (e.g., /home/user/.continue)
        relative_path: Optional subdirectory path to preserve structure

    Raises:
        DeploymentError: If deployment fails
        ValidationError: If content is invalid

    Example:
        >>> handler.deploy(prompt, Path.home() / ".continue", Path("backend/api"))
    """
```

---

## Testing

### Test Requirements

- **Coverage:** Minimum 95% required
- **All tests must pass:** `make test`
- **No regressions:** Existing tests must continue to pass

### Writing Tests

```bash
# Run all tests
make test

# Run specific test file
poetry run pytest tests/handlers/test_continue_handler.py

# Run with verbose output
poetry run pytest -v

# Run with coverage report
poetry run pytest --cov=src/prompt_manager --cov-report=html
```

### Test Structure

```python
def test_deploy_preserves_subdirectory_structure(tmp_path: Path) -> None:
    """Test that subdirectory structure is preserved during deployment."""
    # Arrange
    handler = ContinueToolHandler()
    prompt = create_test_prompt(title="api-prompt")
    relative_path = Path("backend/api")

    # Act
    handler.deploy(prompt, tmp_path, relative_path)

    # Assert
    expected_path = tmp_path / ".continue/prompts/backend/api/api-prompt.md"
    assert expected_path.exists()
    assert "invokable: true" in expected_path.read_text()
```

### Test Categories

1. **Unit Tests** - Test individual functions/methods
2. **Integration Tests** - Test component interactions
3. **End-to-End Tests** - Test complete workflows

---

## Submitting Changes

### Before Submitting

Ensure all quality checks pass:

```bash
# Run all checks (linting, type checking, tests)
make check
```

This runs:
- `make lint` - Code style checks
- `make typecheck` - Type checking
- `make test` - All tests with coverage

### Pull Request Process

1. **Update your branch** with latest upstream:

```bash
git fetch upstream
git rebase upstream/main
```

2. **Push your changes:**

```bash
git push origin feature/your-feature-name
```

3. **Create Pull Request** on GitHub with:
   - Clear title describing the change
   - Description of what changed and why
   - Reference to related issues (e.g., "Closes #123")
   - Screenshots/examples for UI changes

4. **Wait for review:**
   - Address reviewer feedback
   - Keep the PR updated with upstream changes
   - Ensure CI/CD checks pass

### Pull Request Template

```markdown
## Description

Brief description of changes made.

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## How Has This Been Tested?

- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Checklist

- [ ] My code follows the code style of this project
- [ ] I have updated the documentation accordingly
- [ ] I have added tests to cover my changes
- [ ] All new and existing tests passed
- [ ] `make check` passes without errors
```

---

## Adding New Handlers

To add support for a new AI coding assistant:

### 1. Create Handler Class

Create a new file in `src/prompt_manager/handlers/`:

```python
# src/prompt_manager/handlers/cursor_handler.py

from pathlib import Path
from prompt_manager.handlers.protocol import ToolHandler
from prompt_manager.models.prompt import Prompt
from prompt_manager.models.rule import Rule


class CursorToolHandler(ToolHandler):
    """Handler for Cursor AI editor."""

    @property
    def name(self) -> str:
        return "cursor"

    def deploy(
        self,
        content: Prompt | Rule,
        base_path: Path,
        relative_path: Path | None = None,
    ) -> None:
        """Deploy content to Cursor's configuration directory."""
        # Implementation here
        pass

    def validate_installation(self, base_path: Path) -> tuple[bool, str | None]:
        """Validate Cursor installation."""
        # Implementation here
        pass
```

### 2. Register Handler

Add to `src/prompt_manager/handlers/__init__.py`:

```python
from prompt_manager.handlers.cursor_handler import CursorToolHandler
from prompt_manager.handlers.registry import register_handler

register_handler(CursorToolHandler())
```

### 3. Add Tests

Create `tests/handlers/test_cursor_handler.py`:

```python
import pytest
from pathlib import Path
from prompt_manager.handlers.cursor_handler import CursorToolHandler


def test_cursor_handler_deploys_prompt(tmp_path: Path) -> None:
    """Test that Cursor handler deploys prompts correctly."""
    # Test implementation
    pass
```

### 4. Update Documentation

- Add handler to README.md "Handlers" section
- Add manual tests to TEST.md
- Update roadmap.md

### 5. Implementation Checklist

- [ ] Implements `ToolHandler` protocol
- [ ] Supports subdirectory structure preservation
- [ ] Handles relative paths correctly
- [ ] Creates backups before overwriting
- [ ] Validates installation
- [ ] Tests achieve ≥95% coverage
- [ ] Documentation updated
- [ ] All quality checks pass

---

## Questions or Need Help?

- **Issues:** Open a GitHub issue for bugs or feature requests
- **Discussions:** Use GitHub Discussions for questions
- **Documentation:** Check README.md and existing code

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
