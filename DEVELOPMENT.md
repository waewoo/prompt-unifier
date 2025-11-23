# Development Guide

This document provides technical details for developers working on the `prompt-unifier` codebase. For guidelines on submitting changes, see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Table of Contents

- [Development Setup](#development-setup)
- [Core Workflow](#core-workflow)
- [Testing](#testing)
- [Code Style and Quality](#code-style-and-quality)
- [CI/CD Pipeline](#cicd-pipeline)
- [Release Process](#release-process)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [Logging System](#logging-system)
- [Adding New Tool Handlers](#adding-new-tool-handlers)

---

## Development Setup

### Prerequisites

| Requirement | Version | Check Installation      |
|-------------|---------|-------------------------|
| **Python**  | 3.11+   | `python --version`      |
| **Poetry**  | 1.7+    | `poetry --version`      |
| **Git**     | 2.x+    | `git --version`         |

### 1. Clone the Repository

```bash
git clone https://gitlab.com/waewoo/prompt-unifier.git
cd prompt-unifier
```

### 2. Install Dependencies

This project uses [Poetry](https://python-poetry.org/) for dependency management. The `Makefile` provides a convenient way to install everything.

```bash
# This runs `poetry install`
make install
```

### 3. Install Pre-commit Hooks

Pre-commit hooks automatically run linters and formatters before each commit to enforce code quality.

```bash
poetry run pre-commit install
```

---

## Core Workflow

All common tasks are managed through the `Makefile`.

### Main Commands

- `make check`: Run all quality checks (lint, types, tests). **Run this before every commit.**
- `make format`: Auto-format code with Ruff.
- `make lint`: Check for code style issues with Ruff.
- `make typecheck`: Run static type analysis with mypy.
- `make test`: Run the full test suite and generate a coverage report.

---

## Testing

We use `pytest` for testing.

### Running Tests

```bash
# Run all tests and generate a coverage report
make test

# Run tests in a specific file
poetry run pytest tests/cli/test_commands.py

# Run tests in a specific directory
poetry run pytest tests/handlers/

# Run tests with verbose output
poetry run pytest -v
```

### Test Coverage

A minimum of **95% test coverage** is required. After running `make test`, you can view a detailed HTML report by opening `htmlcov/index.html` in your browser.

```bash
# For macOS users
open htmlcov/index.html

# For Linux users
xdg-open htmlcov/index.html
```

---

## Code Style and Quality

Code quality is enforced automatically by pre-commit hooks and the CI pipeline.

- **Linting & Formatting**: We use [Ruff](https://github.com/astral-sh/ruff) for fast linting and formatting. Configuration is in `pyproject.toml`.
- **Type Checking**: We use [mypy](http://mypy-lang.org/) in `strict` mode for static type analysis.

You can run these checks manually at any time:
```bash
make lint
make typecheck
make format
```

---

## CI/CD Pipeline

The project uses GitLab CI for continuous integration. The pipeline is defined in `.gitlab-ci.yml`.

### Local CI Testing

You can run the CI pipeline locally using `gitlab-ci-local`, which is helpful for debugging pipeline issues without making commits.

**Prerequisites:**
- Node.js and npm
- `npm install -g gitlab-ci-local`

**Makefile Commands:**
- `make test-ci`: Run the full test suite in a Docker environment mirroring the CI setup.
- `make test-ci-job JOB=<name>`: Run a specific job from the pipeline (e.g., `make test-ci-job JOB=lint`).
- `make test-ci-list`: List all available jobs in the pipeline.

### Pipeline Stages

The pipeline typically includes these stages:
1.  **lint**: Checks code style.
2.  **typecheck**: Runs static type analysis.
3.  **test**: Executes the pytest suite and checks coverage.
4.  **security**: Runs security scans for vulnerabilities and secrets.

---

## Release Process

Releases are managed using `commitizen` and are automated via the `Makefile`.

To create a new release:
1.  Ensure you are on the `main` branch and all changes are committed.
2.  Run the `make release` command with the type of version bump.

```bash
# Create a patch release (e.g., 0.4.0 -> 0.4.1)
make release VERSION_BUMP=patch

# Create a minor release (e.g., 0.4.1 -> 0.5.0)
make release VERSION_BUMP=minor
```

This command will:
1.  Run all quality checks (`make check`).
2.  Bump the version number in `pyproject.toml` and `src/prompt_unifier/__init__.py`.
3.  Commit the version bump.
4.  Create a new Git tag.
5.  Push the commit and tag to the `main` branch.

---

## Project Structure

```
prompt-unifier/
├── src/prompt_unifier/   # Main source code
│   ├── cli/              # CLI commands (Typer)
│   ├── config/           # Configuration management
│   ├── core/             # Core logic (validation, parsing)
│   ├── git/              # Git integration services
│   ├── handlers/         # Handlers for AI tools (Continue, etc.)
│   ├── models/           # Pydantic data models
│   └── output/           # Output formatters (Rich, JSON)
├── tests/                # Test suite
│   ├── cli/
│   ├── core/
│   ├── integration/      # End-to-end tests
│   └── fixtures/         # Test data and fixtures
├── .gitlab-ci.yml        # GitLab CI/CD pipeline configuration
├── Makefile              # Makefile with development commands
├── pyproject.toml        # Project metadata and dependencies
└── README.md             # User-facing documentation
```

---

## Architecture

The data flows from your Git repositories to a central storage location on your machine, and then is deployed to the AI tools in your project.

```text
┌──────────────────────────┐      ┌───────────────────────────┐      ┌───────────────────────────┐
│                          │      │                           │      │                           │
│   Git Repository 1       ├─┐    │                           │      │    AI Assistant           │
│  (Global Prompts)        │ │    │                           │      │    (e.g., Continue)       │
│                          │ │    │                           │      │                           │
└──────────────────────────┘ │    │                           │      └───────────────────────────┘
                             │    │                           │                 ▲
                             ├────►   Centralized Storage     ├─────────────────┘
                             │    │ (~/.prompt-unifier/storage)│      (deploy)
┌──────────────────────────┐ │    │                           │
│                          │ │    │                           │
│   Git Repository 2       ├─┘    │                           │
│   (Team Prompts)         │(sync)│                           │
│                          │      │                           │
└──────────────────────────┘      └───────────────────────────┘
```

---

## Logging System

The project uses a centralized logging system based on Python's built-in `logging` module with Rich integration for colored terminal output.

### Configuration

Logging is configured globally via CLI flags:

```bash
# Default: WARNING level only
prompt-unifier validate

# INFO level (-v)
prompt-unifier -v sync --repo https://example.com/repo.git

# DEBUG level (-vv)
prompt-unifier -vv deploy --handlers continue

# With file logging
prompt-unifier -vv --log-file debug.log validate
```

### Using Logging in Code

When adding logging to a module, follow this pattern:

```python
import logging

logger = logging.getLogger(__name__)

def my_function():
    logger.debug("Detailed tracing info")  # -vv
    logger.info("Progress information")     # -v
    logger.warning("Important warnings")    # default
    logger.error("Error messages")          # always shown
```

### Log Levels

| Level   | Verbosity | Use Case                                      |
|---------|-----------|-----------------------------------------------|
| WARNING | Default   | Important issues, deprecations                |
| INFO    | `-v`      | Progress info, file counts, operation status  |
| DEBUG   | `-vv`     | Detailed tracing, variable values, full paths |

### Implementation Details

- **Console output**: Uses `rich.logging.RichHandler` writing to stderr (keeps stdout clean for JSON/piping)
- **File output**: Plain text format with timestamps for parsing
- **Module**: `src/prompt_unifier/utils/logging_config.py`

### Adding Logging to New Modules

1. Import logging and create a logger:
   ```python
   import logging
   logger = logging.getLogger(__name__)
   ```

2. Use appropriate log levels:
   - `logger.debug()` for detailed tracing
   - `logger.info()` for progress/status
   - `logger.warning()` for issues that don't stop execution
   - `logger.error()` for errors (usually followed by exception handling)

---

## Adding New Tool Handlers

This section provides a comprehensive guide for adding support for new AI tools to `prompt-unifier`. By following this tutorial, you'll learn how to create a handler that deploys prompts and rules to your target tool.

### Overview: The Handler Architecture

`prompt-unifier` uses the **Strategy Pattern** to support multiple AI tools. Each tool (Continue, Cursor, Windsurf, etc.) has its own "handler" - a class that knows how to deploy prompts and rules to that specific tool's expected locations and formats.

The architecture consists of three main components:

1. **ToolHandler Protocol**: Defines the interface that all handlers must implement
2. **Concrete Handlers**: Tool-specific implementations (e.g., `ContinueToolHandler`)
3. **ToolHandlerRegistry**: Manages handler registration and retrieval

This design allows you to add support for new tools without modifying existing code - you simply create a new handler class and register it.

### Understanding the ToolHandler Protocol

The `ToolHandler` Protocol (defined in `src/prompt_unifier/handlers/protocol.py`) specifies the interface that all handlers must implement. Let's examine each component:

#### Type Hints for Beginners

Before diving into the Protocol, here's a quick explanation of the Python type hints you'll encounter:

- **`Path`**: From `pathlib`, represents a filesystem path. More powerful than strings for path manipulation.
- **`Any`**: From `typing`, indicates that a parameter can be any type. Used when the exact type varies (e.g., `PromptFrontmatter` or `RuleFrontmatter`).
- **`Protocol`**: From `typing`, defines a structural interface. Classes don't need to explicitly inherit from it - they just need to implement the required methods.
- **`@runtime_checkable`**: A decorator that allows using `isinstance()` checks with the Protocol at runtime.

#### The Protocol Definition

```python
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ToolHandler(Protocol):
    """
    Protocol for defining a ToolHandler.

    Any class implementing this protocol must provide the specified methods
    and attributes.
    """

    # Required directory attributes
    prompts_dir: Path  # Where prompts are deployed
    rules_dir: Path    # Where rules are deployed
```

The `@runtime_checkable` decorator is important - it allows the registry to verify that your handler correctly implements the Protocol using `isinstance(handler, ToolHandler)`.

#### Required Methods

Your handler must implement these 6 required methods:

##### 1. `deploy()`

Deploys a single prompt or rule to the tool's directory.

```python
def deploy(
    self,
    content: Any,                      # PromptFrontmatter or RuleFrontmatter
    content_type: str,                 # "prompt" or "rule"
    body: str = "",                    # The markdown content body
    source_filename: str | None = None,  # Original filename to preserve
    relative_path: Path | None = None,   # Subdirectory structure to preserve
) -> None:
    """Deploys content to the tool's directory."""
    ...
```

##### 2. `get_status()`

Returns the handler's current status.

```python
def get_status(self) -> str:
    """
    Returns: "active", "inactive", or "error"
    """
    ...
```

##### 3. `get_name()`

Returns the unique identifier for this handler.

```python
def get_name(self) -> str:
    """
    Returns: Handler name (e.g., "continue", "cursor")
    """
    ...
```

##### 4. `rollback()`

Restores backup files after a failed deployment.

```python
def rollback(self) -> None:
    """Rolls back deployment by restoring .bak files."""
    ...
```

##### 5. `clean_orphaned_files()`

Removes files that are no longer in the deployment set.

```python
def clean_orphaned_files(self, deployed_filenames: set[str]) -> int:
    """
    Args:
        deployed_filenames: Set of filenames that were just deployed

    Returns:
        Number of files removed
    """
    ...
```

##### 6. `get_deployment_status()`

Checks if a specific content item is synced, outdated, or missing.

```python
def get_deployment_status(
    self,
    content_name: str,
    content_type: str,
    source_content: str,
    source_filename: str | None = None,
    relative_path: Path | None = None,
) -> str:
    """
    Returns: "synced", "outdated", "missing", or "error"
    """
    ...
```

#### Optional Advanced Method

For enhanced verification reporting, you can also implement:

```python
def verify_deployment_with_details(
    self,
    content_name: str,
    content_type: str,
    file_name: str,
    relative_path: Path | None = None,
) -> VerificationResult:
    """Returns detailed verification results."""
    ...
```

### Understanding the ToolHandlerRegistry

The `ToolHandlerRegistry` (in `src/prompt_unifier/handlers/registry.py`) manages all available handlers:

```python
from prompt_unifier.handlers.protocol import ToolHandler


class ToolHandlerRegistry:
    """Central registry for discovering and managing ToolHandler implementations."""

    def __init__(self) -> None:
        self._handlers: dict[str, ToolHandler] = {}

    def register(self, handler: ToolHandler) -> None:
        """
        Register a handler instance.

        Raises:
            TypeError: If handler doesn't conform to ToolHandler protocol
            ValueError: If handler name is already registered
        """
        if not isinstance(handler, ToolHandler):
            raise TypeError("Only instances conforming to ToolHandler protocol can be registered.")
        if handler.get_name() in self._handlers:
            raise ValueError(f"ToolHandler with name '{handler.get_name()}' is already registered.")
        self._handlers[handler.get_name()] = handler

    def get_handler(self, name: str) -> ToolHandler:
        """Retrieve a handler by name."""
        if name not in self._handlers:
            raise ValueError(f"ToolHandler with name '{name}' not found.")
        return self._handlers[name]

    def list_handlers(self) -> list[str]:
        """List names of all registered handlers."""
        return list(self._handlers.keys())

    def get_all_handlers(self) -> list[ToolHandler]:
        """Get all registered handler instances."""
        return list(self._handlers.values())
```

### Tutorial: Creating an ExampleToolHandler

Let's create a complete handler for a hypothetical "ExampleAI" tool. This example demonstrates all required methods plus advanced features like verification reports.

#### Step 1: Create the Handler File

Create `src/prompt_unifier/handlers/example_handler.py`:

```python
"""Handler for ExampleAI tool deployment."""

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

import yaml
from rich.console import Console
from rich.table import Table

from prompt_unifier.handlers.protocol import ToolHandler
from prompt_unifier.models.prompt import PromptFrontmatter
from prompt_unifier.models.rule import RuleFrontmatter

# Console for Rich output
console = Console()

# Color constants for consistent styling
ERROR_COLOR = "red"
WARNING_COLOR = "yellow"
SUCCESS_COLOR = "green"


@dataclass
class VerificationResult:
    """Data class for storing verification result details."""

    file_name: str
    content_type: str
    status: str  # "passed", "failed", "warning"
    details: str


class ExampleToolHandler(ToolHandler):
    """
    Tool handler for ExampleAI assistant.

    Deploys prompts and rules to the .example-ai directory structure:
    - .example-ai/prompts/  - For prompt files
    - .example-ai/rules/    - For rule files
    """

    def __init__(self, base_path: Path | None = None):
        """
        Initialize the ExampleAI handler.

        Args:
            base_path: Base directory for deployment. Defaults to current
                      working directory if not specified.
        """
        self.name = "example"

        # Default base_path is current working directory
        # This supports project-local tool installations
        self.base_path = base_path if base_path else Path.cwd()

        # Define directory structure for this tool
        self.prompts_dir = self.base_path / ".example-ai" / "prompts"
        self.rules_dir = self.base_path / ".example-ai" / "rules"

        # Auto-create directories if they don't exist
        if not self.prompts_dir.exists():
            self.prompts_dir.mkdir(parents=True, exist_ok=True)
            console.print(f"[cyan]Created ExampleAI prompts directory: {self.prompts_dir}[/cyan]")

        if not self.rules_dir.exists():
            self.rules_dir.mkdir(parents=True, exist_ok=True)
            console.print(f"[cyan]Created ExampleAI rules directory: {self.rules_dir}[/cyan]")

    def validate_tool_installation(self) -> bool:
        """
        Validate that the ExampleAI tool installation is accessible.

        Checks that directories exist and are writable.

        Returns:
            bool: True if validation succeeds

        Raises:
            PermissionError: If directories cannot be created/written
            OSError: If directories cannot be accessed
        """
        try:
            # Check if base_path exists
            if not self.base_path.exists():
                console.print(
                    f"[yellow]Base path does not exist, creating: {self.base_path}[/yellow]"
                )
                self.base_path.mkdir(parents=True, exist_ok=True)

            # Check .example-ai directory
            example_dir = self.base_path / ".example-ai"
            if not example_dir.exists():
                example_dir.mkdir(parents=True, exist_ok=True)
                console.print(f"[green]Created ExampleAI directory: {example_dir}[/green]")

            # Ensure prompts and rules directories exist
            if not self.prompts_dir.exists():
                self.prompts_dir.mkdir(parents=True, exist_ok=True)
            if not self.rules_dir.exists():
                self.rules_dir.mkdir(parents=True, exist_ok=True)

            # Test write access
            test_file = self.prompts_dir / ".write_test"
            try:
                test_file.touch()
                test_file.unlink()
            except (PermissionError, OSError) as e:
                console.print(f"[red]Error: Directory not writable: {e}[/red]")
                raise PermissionError(f"Directory not writable: {e}") from e

            console.print(f"[green]ExampleAI installation validated at: {self.base_path}[/green]")
            return True

        except PermissionError:
            console.print(f"[red]Permission error at {self.base_path}[/red]")
            raise
        except OSError as e:
            console.print(f"[red]Error validating installation: {e}[/red]")
            raise

    def _backup_file(self, file_path: Path) -> None:
        """
        Create a backup of an existing file before overwriting.

        Args:
            file_path: Path to the file to backup
        """
        if file_path.exists():
            backup_path = file_path.with_suffix(file_path.suffix + ".bak")
            file_path.rename(backup_path)
            console.print(f"[yellow]Backed up {file_path.name} to {backup_path.name}[/yellow]")

    def _process_prompt_content(self, prompt: PromptFrontmatter, body: str) -> str:
        """
        Process prompt content for ExampleAI format.

        Transforms the universal frontmatter format into ExampleAI's expected format.

        Args:
            prompt: The prompt frontmatter object
            body: The markdown content body

        Returns:
            Formatted content string ready for deployment
        """
        # Map universal fields to ExampleAI's expected format
        example_frontmatter: dict[str, Any] = {
            "name": prompt.title,
            "description": prompt.description,
            # ExampleAI-specific field - always set to true for prompts
            "enabled": True,
        }

        # Add optional fields if present
        if prompt.category:
            example_frontmatter["category"] = prompt.category
        if prompt.version:
            example_frontmatter["version"] = prompt.version
        if prompt.tags:
            example_frontmatter["tags"] = prompt.tags
        if prompt.author:
            example_frontmatter["author"] = prompt.author
        if prompt.language:
            example_frontmatter["language"] = prompt.language

        # Convert to YAML string
        frontmatter_str = yaml.safe_dump(example_frontmatter, sort_keys=False)

        # Format with YAML frontmatter delimiters
        return f"---\n{frontmatter_str.rstrip()}\n---\n{body}"

    def _process_rule_content(self, rule: RuleFrontmatter, body: str) -> str:
        """
        Process rule content for ExampleAI format.

        Args:
            rule: The rule frontmatter object
            body: The markdown content body

        Returns:
            Formatted content string ready for deployment
        """
        # Map universal fields to ExampleAI's expected format
        example_frontmatter: dict[str, Any] = {
            "name": rule.title,
        }

        # Add optional fields
        if rule.description:
            example_frontmatter["description"] = rule.description
        if rule.applies_to:
            # ExampleAI uses "patterns" instead of "globs"
            example_frontmatter["patterns"] = rule.applies_to

        # ExampleAI-specific: rules are disabled by default
        example_frontmatter["autoApply"] = False

        if rule.category:
            example_frontmatter["category"] = rule.category
        if rule.version:
            example_frontmatter["version"] = rule.version
        if rule.tags:
            example_frontmatter["tags"] = rule.tags
        if rule.author:
            example_frontmatter["author"] = rule.author
        if rule.language:
            example_frontmatter["language"] = rule.language

        frontmatter_str = yaml.safe_dump(example_frontmatter, sort_keys=False)
        return f"---\n{frontmatter_str.rstrip()}\n---\n{body}"

    def deploy(
        self,
        content: Any,
        content_type: str,
        body: str = "",
        source_filename: str | None = None,
        relative_path: Path | None = None,
    ) -> None:
        """
        Deploy a prompt or rule to ExampleAI directories.

        Args:
            content: PromptFrontmatter or RuleFrontmatter object
            content_type: "prompt" or "rule"
            body: The markdown content body
            source_filename: Original filename to preserve (optional)
            relative_path: Subdirectory structure to preserve (optional)
        """
        # Determine target filename
        if source_filename:
            filename = source_filename if source_filename.endswith(".md") else f"{source_filename}.md"
        else:
            # Fallback to title-based naming
            filename = f"{content.title}.md"

        # Process content based on type
        if content_type == "prompt":
            if not isinstance(content, PromptFrontmatter):
                raise ValueError("Content must be a PromptFrontmatter instance for type 'prompt'")
            processed_content = self._process_prompt_content(content, body)
            base_dir = self.prompts_dir
        elif content_type == "rule":
            if not isinstance(content, RuleFrontmatter):
                raise ValueError("Content must be a RuleFrontmatter instance for type 'rule'")
            processed_content = self._process_rule_content(content, body)
            base_dir = self.rules_dir
        else:
            raise ValueError(f"Unsupported content type: {content_type}")

        # Handle subdirectory structure
        if relative_path and str(relative_path) != ".":
            target_dir = base_dir / relative_path
            target_dir.mkdir(parents=True, exist_ok=True)
            target_file_path = target_dir / filename
        else:
            target_file_path = base_dir / filename

        # Backup existing file and write new content
        self._backup_file(target_file_path)
        target_file_path.write_text(processed_content, encoding="utf-8")

        console.print(
            f"[green]Deployed {content.title} ({content_type}) to {target_file_path}[/green]"
        )

    def get_status(self) -> str:
        """
        Return the handler's current status.

        Returns:
            "active" if directories exist, "inactive" otherwise
        """
        if self.prompts_dir.exists() and self.rules_dir.exists():
            return "active"
        return "inactive"

    def get_name(self) -> str:
        """
        Return the unique handler name.

        Returns:
            Handler identifier string
        """
        return self.name

    def _remove_empty_directories(self, base_dir: Path) -> None:
        """
        Remove empty directories within a base directory.

        Walks the directory tree bottom-up to remove empty subdirectories.

        Args:
            base_dir: The base directory to clean
        """
        # Collect all directories
        all_dirs = []
        for dir_path in base_dir.rglob("*"):
            if dir_path.is_dir():
                all_dirs.append(dir_path)

        # Sort by depth (deepest first)
        all_dirs.sort(key=lambda p: len(p.parts), reverse=True)

        for dir_path in all_dirs:
            try:
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    console.print(f"[dim]Removed empty directory: {dir_path}[/dim]")
            except OSError:
                pass  # Directory not empty or other issue

    def rollback(self) -> None:
        """
        Roll back deployment by restoring backup files.

        Finds all .bak files and restores them to their original names.
        Also cleans up empty directories after restoration.
        """
        # Restore backups in prompts directory
        for backup_file in self.prompts_dir.glob("**/*.bak"):
            original_path = backup_file.with_suffix("")
            try:
                backup_file.rename(original_path)
                console.print(f"[yellow]Restored {original_path.name} from backup[/yellow]")
            except (OSError, FileNotFoundError) as e:
                console.print(f"[yellow]Warning: Could not restore {backup_file.name}: {e}[/yellow]")

        # Restore backups in rules directory
        for backup_file in self.rules_dir.glob("**/*.bak"):
            original_path = backup_file.with_suffix("")
            try:
                backup_file.rename(original_path)
                console.print(f"[yellow]Restored {original_path.name} from backup[/yellow]")
            except (OSError, FileNotFoundError) as e:
                console.print(f"[yellow]Warning: Could not restore {backup_file.name}: {e}[/yellow]")

        # Clean up empty directories
        self._remove_empty_directories(self.prompts_dir)
        self._remove_empty_directories(self.rules_dir)

    def clean_orphaned_files(self, deployed_filenames: set[str]) -> int:
        """
        Remove files that are no longer in the deployment set.

        Also removes .bak backup files recursively.

        Args:
            deployed_filenames: Set of filenames that were just deployed

        Returns:
            Number of files removed
        """
        removed_count = 0

        # Remove .bak files in prompts directory (recursive)
        for file_path in self.prompts_dir.glob("**/*.bak"):
            file_path.unlink()
            console.print(f"  [dim]Removed backup file: {file_path.name}[/dim]")
            removed_count += 1

        # Remove orphaned .md files in root prompts directory only
        for file_path in self.prompts_dir.glob("*.md"):
            if file_path.name not in deployed_filenames:
                file_path.unlink()
                console.print(f"  [yellow]Removed orphaned prompt: {file_path.name}[/yellow]")
                removed_count += 1

        # Remove .bak files in rules directory (recursive)
        for file_path in self.rules_dir.glob("**/*.bak"):
            file_path.unlink()
            console.print(f"  [dim]Removed backup file: {file_path.name}[/dim]")
            removed_count += 1

        # Remove orphaned .md files in root rules directory only
        for file_path in self.rules_dir.glob("*.md"):
            if file_path.name not in deployed_filenames:
                file_path.unlink()
                console.print(f"  [yellow]Removed orphaned rule: {file_path.name}[/yellow]")
                removed_count += 1

        return removed_count

    def get_deployment_status(
        self,
        content_name: str,
        content_type: str,
        source_content: str,
        source_filename: str | None = None,
        relative_path: Path | None = None,
    ) -> str:
        """
        Check the deployment status of a content item.

        Uses SHA-256 hash comparison to detect changes.

        Args:
            content_name: The name/title of the content
            content_type: "prompt" or "rule"
            source_content: The expected processed content
            source_filename: Optional specific filename
            relative_path: Optional subdirectory path

        Returns:
            "synced", "outdated", "missing", or "error"
        """
        # Determine filename
        if source_filename:
            filename = source_filename if source_filename.endswith(".md") else f"{source_filename}.md"
        else:
            filename = f"{content_name}.md"

        # Determine target directory
        if content_type == "prompt":
            base_dir = self.prompts_dir
        elif content_type == "rule":
            base_dir = self.rules_dir
        else:
            return "error"

        # Build full path with relative_path if provided
        if relative_path and str(relative_path) != ".":
            target_file = base_dir / relative_path / filename
        else:
            target_file = base_dir / filename

        # Check if file exists
        if not target_file.exists():
            return "missing"

        try:
            # Read deployed content
            deployed_content = target_file.read_text(encoding="utf-8")

            # Compare content hashes
            source_hash = sha256(source_content.encode("utf-8")).hexdigest()
            deployed_hash = sha256(deployed_content.encode("utf-8")).hexdigest()

            if source_hash == deployed_hash:
                return "synced"
            else:
                return "outdated"

        except (OSError, UnicodeDecodeError):
            return "error"

    # =========================================================================
    # Advanced Features: Verification Reports
    # =========================================================================

    def verify_deployment_with_details(
        self,
        content_name: str,
        content_type: str,
        file_name: str,
        relative_path: Path | None = None,
    ) -> VerificationResult:
        """
        Verify deployment with detailed result information.

        Args:
            content_name: Name/title of the content
            content_type: "prompt" or "rule"
            file_name: The filename of the deployed file
            relative_path: Optional subdirectory path

        Returns:
            VerificationResult with status and details
        """
        # Ensure .md extension
        actual_file_name = file_name if file_name.endswith(".md") else f"{file_name}.md"

        # Determine base directory
        if content_type == "prompt":
            base_dir = self.prompts_dir
        elif content_type == "rule":
            base_dir = self.rules_dir
        else:
            return VerificationResult(
                file_name=file_name,
                content_type=content_type,
                status="failed",
                details=f"Unsupported content type: {content_type}",
            )

        # Build target path
        if relative_path and str(relative_path) != ".":
            target_file_path = base_dir / relative_path / actual_file_name
        else:
            target_file_path = base_dir / actual_file_name

        # Check file exists
        if not target_file_path.exists():
            return VerificationResult(
                file_name=file_name,
                content_type=content_type,
                status="failed",
                details=f"File does not exist: {target_file_path}",
            )

        # Read and verify content
        try:
            deployed_content = target_file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            return VerificationResult(
                file_name=file_name,
                content_type=content_type,
                status="failed",
                details=f"Cannot read file: {e}",
            )

        # Tool-specific validation for prompts
        if content_type == "prompt":
            parts = deployed_content.split("---", 2)
            if len(parts) < 3:
                return VerificationResult(
                    file_name=file_name,
                    content_type=content_type,
                    status="failed",
                    details="Invalid format: missing frontmatter delimiters",
                )

            frontmatter_str = parts[1].strip()
            try:
                frontmatter = yaml.safe_load(frontmatter_str)
                if not isinstance(frontmatter, dict):
                    return VerificationResult(
                        file_name=file_name,
                        content_type=content_type,
                        status="failed",
                        details="Invalid frontmatter: not a dictionary",
                    )
                # Check for ExampleAI-specific required field
                if not frontmatter.get("enabled"):
                    return VerificationResult(
                        file_name=file_name,
                        content_type=content_type,
                        status="failed",
                        details="Missing or false 'enabled' field in frontmatter",
                    )
            except yaml.YAMLError as e:
                return VerificationResult(
                    file_name=file_name,
                    content_type=content_type,
                    status="failed",
                    details=f"Invalid YAML frontmatter: {e}",
                )

        return VerificationResult(
            file_name=file_name,
            content_type=content_type,
            status="passed",
            details="File verified successfully",
        )

    def aggregate_verification_results(self, results: list[VerificationResult]) -> dict[str, int]:
        """
        Aggregate verification results into summary counts.

        Args:
            results: List of VerificationResult objects

        Returns:
            Dictionary with passed, failed, warnings, and total counts
        """
        summary = {
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "total": len(results),
        }

        for result in results:
            if result.status == "passed":
                summary["passed"] += 1
            elif result.status == "failed":
                summary["failed"] += 1
            elif result.status == "warning":
                summary["warnings"] += 1

        return summary

    def display_verification_report(
        self,
        results: list[VerificationResult],
        console: Console | None = None,
    ) -> None:
        """
        Display a Rich-formatted verification report.

        Args:
            results: List of VerificationResult objects
            console: Optional Console instance (uses module console if None)
        """
        output_console = globals()["console"] if console is None else console

        # Header
        output_console.print()
        output_console.print(f"[bold]Verification Report: {self.name}[/bold]")
        output_console.print("-" * 60)

        # Build table
        table = Table(show_header=True, header_style="bold")
        table.add_column("File", style="dim")
        table.add_column("Type")
        table.add_column("Status")
        table.add_column("Details", style="dim")

        for result in results:
            if result.status == "passed":
                status_text = f"[{SUCCESS_COLOR}]PASSED[/{SUCCESS_COLOR}]"
            elif result.status == "failed":
                status_text = f"[{ERROR_COLOR}]FAILED[/{ERROR_COLOR}]"
            else:
                status_text = f"[{WARNING_COLOR}]WARNING[/{WARNING_COLOR}]"

            table.add_row(
                result.file_name,
                result.content_type,
                status_text,
                result.details,
            )

        output_console.print(table)

        # Summary
        summary = self.aggregate_verification_results(results)
        output_console.print()
        output_console.print("[bold]Summary:[/bold]")
        output_console.print(f"  Total: {summary['total']}")
        output_console.print(f"  Passed: [{SUCCESS_COLOR}]{summary['passed']}[/{SUCCESS_COLOR}]")
        output_console.print(f"  Failed: [{ERROR_COLOR}]{summary['failed']}[/{ERROR_COLOR}]")
        output_console.print(
            f"  Warnings: [{WARNING_COLOR}]{summary['warnings']}[/{WARNING_COLOR}]"
        )

        if summary["failed"] > 0:
            output_console.print()
            output_console.print(
                f"[{WARNING_COLOR}]Warning: {summary['failed']} verification(s) failed.[/{WARNING_COLOR}]"
            )

        output_console.print()
```

### Testing Your Handler

Follow Test-Driven Development (TDD) - write tests before implementing features,then ensure they pass.

#### Step 1: Create the Test File

Create `tests/handlers/test_example_handler.py`:

```python
"""Tests for ExampleToolHandler."""

import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from prompt_unifier.handlers.example_handler import ExampleToolHandler
from prompt_unifier.models.prompt import PromptFrontmatter
from prompt_unifier.models.rule import RuleFrontmatter


@pytest.fixture
def mock_base_dir(tmp_path: Path) -> Path:
    """Create a temporary base directory for testing."""
    return tmp_path / "test_base"


@pytest.fixture
def example_handler(mock_base_dir: Path) -> ExampleToolHandler:
    """Create an ExampleToolHandler instance for testing."""
    return ExampleToolHandler(base_path=mock_base_dir)


@pytest.fixture
def mock_prompt() -> PromptFrontmatter:
    """Create a mock prompt for testing."""
    return PromptFrontmatter(
        title="Test Prompt",
        description="A test prompt",
    )


@pytest.fixture
def mock_rule() -> RuleFrontmatter:
    """Create a mock rule for testing."""
    return RuleFrontmatter(
        title="Test Rule",
        description="A test rule",
        category="testing",
    )


class TestExampleToolHandlerInit:
    """Tests for handler initialization."""

    def test_init_creates_directories(self, example_handler: ExampleToolHandler):
        """Test that init creates required directories."""
        assert example_handler.prompts_dir.exists()
        assert example_handler.rules_dir.exists()

    def test_init_with_custom_base_path(self, tmp_path: Path):
        """Test initialization with custom base path."""
        custom_base = tmp_path / "custom"
        handler = ExampleToolHandler(base_path=custom_base)

        assert handler.base_path == custom_base
        assert handler.prompts_dir == custom_base / ".example-ai" / "prompts"
        assert handler.rules_dir == custom_base / ".example-ai" / "rules"


class TestExampleToolHandlerDeploy:
    """Tests for the deploy method."""

    def test_deploy_prompt_creates_file(
        self, example_handler: ExampleToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that deploying a prompt creates the correct file."""
        example_handler.deploy(mock_prompt, "prompt", "Test content body")

        target_file = example_handler.prompts_dir / f"{mock_prompt.title}.md"
        assert target_file.exists()

        content = target_file.read_text()
        assert "name: Test Prompt" in content
        assert "description: A test prompt" in content
        assert "enabled: true" in content
        assert "Test content body" in content

    def test_deploy_rule_creates_file(
        self, example_handler: ExampleToolHandler, mock_rule: RuleFrontmatter
    ):
        """Test that deploying a rule creates the correct file."""
        example_handler.deploy(mock_rule, "rule", "Rule content body")

        target_file = example_handler.rules_dir / f"{mock_rule.title}.md"
        assert target_file.exists()

        content = target_file.read_text()
        assert "name: Test Rule" in content
        assert "description: A test rule" in content
        assert "autoApply: false" in content

    def test_deploy_with_source_filename(
        self, example_handler: ExampleToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that source_filename is preserved."""
        source_filename = "custom-name.md"
        example_handler.deploy(
            mock_prompt, "prompt", "Content", source_filename=source_filename
        )

        target_file = example_handler.prompts_dir / source_filename
        assert target_file.exists()

    def test_deploy_with_relative_path(
        self, example_handler: ExampleToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that relative_path creates subdirectory structure."""
        relative_path = Path("subdir/nested")
        example_handler.deploy(
            mock_prompt, "prompt", "Content", relative_path=relative_path
        )

        target_file = example_handler.prompts_dir / relative_path / f"{mock_prompt.title}.md"
        assert target_file.exists()

    def test_deploy_creates_backup(
        self, example_handler: ExampleToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that existing files are backed up before overwriting."""
        target_file = example_handler.prompts_dir / f"{mock_prompt.title}.md"
        target_file.write_text("original content")

        example_handler.deploy(mock_prompt, "prompt", "New content")

        backup_file = target_file.with_suffix(".md.bak")
        assert backup_file.exists()
        assert backup_file.read_text() == "original content"

    def test_deploy_with_wrong_content_type_raises_error(
        self, example_handler: ExampleToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that wrong content type raises ValueError."""
        with pytest.raises(ValueError, match="Content must be a RuleFrontmatter"):
            example_handler.deploy(mock_prompt, "rule", "Content")

    def test_deploy_with_unsupported_type_raises_error(
        self, example_handler: ExampleToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that unsupported content type raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported content type"):
            example_handler.deploy(mock_prompt, "invalid", "Content")


class TestExampleToolHandlerStatus:
    """Tests for status-related methods."""

    def test_get_status_active(self, example_handler: ExampleToolHandler):
        """Test get_status returns 'active' when directories exist."""
        assert example_handler.get_status() == "active"

    def test_get_status_inactive(self, example_handler: ExampleToolHandler):
        """Test get_status returns 'inactive' when directories are missing."""
        shutil.rmtree(example_handler.prompts_dir)
        assert example_handler.get_status() == "inactive"

    def test_get_name(self, example_handler: ExampleToolHandler):
        """Test get_name returns correct handler name."""
        assert example_handler.get_name() == "example"


class TestExampleToolHandlerRollback:
    """Tests for the rollback method."""

    def test_rollback_restores_backups(self, example_handler: ExampleToolHandler):
        """Test that rollback restores backup files."""
        # Create a backup file
        backup_file = example_handler.prompts_dir / "test.md.bak"
        backup_file.write_text("backup content")

        # Create current file
        current_file = example_handler.prompts_dir / "test.md"
        current_file.write_text("current content")

        example_handler.rollback()

        # Backup should be restored
        assert current_file.read_text() == "backup content"
        assert not backup_file.exists()

    def test_rollback_no_backups(self, example_handler: ExampleToolHandler):
        """Test that rollback doesn't fail when no backups exist."""
        example_handler.rollback()  # Should not raise


class TestExampleToolHandlerCleanOrphanedFiles:
    """Tests for clean_orphaned_files method."""

    def test_clean_removes_orphaned_files(self, example_handler: ExampleToolHandler):
        """Test that orphaned files are removed."""
        # Create orphaned file
        orphan = example_handler.prompts_dir / "orphan.md"
        orphan.write_text("orphan content")

        removed = example_handler.clean_orphaned_files(set())

        assert removed == 1
        assert not orphan.exists()

    def test_clean_preserves_deployed_files(
        self, example_handler: ExampleToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test that deployed files are not removed."""
        example_handler.deploy(mock_prompt, "prompt", "Content")

        deployed = {f"{mock_prompt.title}.md"}
        removed = example_handler.clean_orphaned_files(deployed)

        assert removed == 0
        assert (example_handler.prompts_dir / f"{mock_prompt.title}.md").exists()

    def test_clean_removes_backup_files(self, example_handler: ExampleToolHandler):
        """Test that .bak files are removed."""
        backup = example_handler.prompts_dir / "old.md.bak"
        backup.write_text("old backup")

        removed = example_handler.clean_orphaned_files(set())

        assert removed == 1
        assert not backup.exists()


class TestExampleToolHandlerDeploymentStatus:
    """Tests for get_deployment_status method."""

    def test_status_synced(
        self, example_handler: ExampleToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test status is 'synced' when content matches."""
        example_handler.deploy(mock_prompt, "prompt", "Content")

        # Get the processed content
        processed = example_handler._process_prompt_content(mock_prompt, "Content")

        status = example_handler.get_deployment_status(
            content_name=mock_prompt.title,
            content_type="prompt",
            source_content=processed,
        )

        assert status == "synced"

    def test_status_missing(self, example_handler: ExampleToolHandler):
        """Test status is 'missing' when file doesn't exist."""
        status = example_handler.get_deployment_status(
            content_name="nonexistent",
            content_type="prompt",
            source_content="content",
        )

        assert status == "missing"

    def test_status_outdated(
        self, example_handler: ExampleToolHandler, mock_prompt: PromptFrontmatter
    ):
        """Test status is 'outdated' when content differs."""
        example_handler.deploy(mock_prompt, "prompt", "Original content")

        # Check with different content
        processed = example_handler._process_prompt_content(mock_prompt, "Different content")

        status = example_handler.get_deployment_status(
            content_name=mock_prompt.title,
            content_type="prompt",
            source_content=processed,
        )

        assert status == "outdated"
```

#### Step 2: Run Your Tests

```bash
# Run only your handler tests
poetry run pytest tests/handlers/test_example_handler.py -v

# Run with coverage
poetry run pytest tests/handlers/test_example_handler.py --cov=prompt_unifier.handlers.example_handler
```

### CLI Integration

To make your handler available in the `deploy` command, you need to register it in `src/prompt_unifier/cli/commands.py`.

#### Step 1: Import Your Handler

At the top of `commands.py`, add your import:

```python
from prompt_unifier.handlers.example_handler import ExampleToolHandler
```

#### Step 2: Resolve Base Path

In the `deploy()` function, add base path resolution for your handler (around line 1101):

```python
# Resolve base paths for each handler
continue_base_path = resolve_handler_base_path("continue")
example_base_path = resolve_handler_base_path("example")  # Add this
```

#### Step 3: Instantiate and Register

After the `ContinueToolHandler` registration (around line 1120), add:

```python
# Register ExampleToolHandler
if example_base_path is not None:
    example_handler = ExampleToolHandler(base_path=example_base_path)
else:
    example_handler = ExampleToolHandler()

try:
    example_handler.validate_tool_installation()
except (PermissionError, OSError) as e:
    console.print("[red]Error: Failed to validate ExampleAI installation[/red]")
    console.print(f"[red]Details: {e}[/red]")
    raise typer.Exit(code=1) from e

registry.register(example_handler)
```

#### Step 4: Update __init__.py

Export your handler in `src/prompt_unifier/handlers/__init__.py`:

```python
from prompt_unifier.handlers.example_handler import ExampleToolHandler

__all__ = [
    "ContinueToolHandler",
    "ExampleToolHandler",  # Add this
    "ToolHandler",
    "ToolHandlerRegistry",
]
```

### Handler Validation Flow

When the `deploy` command runs, handlers go through this validation flow:

1. **Instantiation**: Handler is created with resolved `base_path`
2. **Validation**: `validate_tool_installation()` is called to ensure directories are accessible
3. **Registration**: Handler is registered with the `ToolHandlerRegistry`
4. **Deployment**: For each content file, `deploy()` is called
5. **Verification**: If implemented, `verify_deployment_with_details()` is called
6. **Report**: Results are displayed using `display_verification_report()`

If validation fails, the deployment is aborted with an error message.

### File Structure Checklist

When adding a new handler, create/modify these files:

- [ ] `src/prompt_unifier/handlers/<tool>_handler.py` - Handler implementation
- [ ] `tests/handlers/test_<tool>_handler.py` - Test suite
- [ ] `src/prompt_unifier/handlers/__init__.py` - Export handler
- [ ] `src/prompt_unifier/cli/commands.py` - Register handler in deploy command

### Naming Conventions

Follow these naming patterns for consistency:

| Item | Pattern | Example |
|------|---------|---------|
| Handler class | `<Tool>ToolHandler` | `CursorToolHandler` |
| Handler file | `<tool>_handler.py` | `cursor_handler.py` |
| Test file | `test_<tool>_handler.py` | `test_cursor_handler.py` |
| Handler name | `<tool>` (lowercase) | `"cursor"` |
| Directory | `.<tool>` or tool's convention | `.cursor` |

### Best Practices

1. **Follow the ContinueToolHandler pattern**: It's a complete reference implementation with all features.

2. **Handle all edge cases**: Empty content, unicode characters, missing directories, permission errors.

3. **Provide informative console output**: Use Rich formatting with appropriate colors.

4. **Support subdirectory structures**: Many projects organize prompts in subdirectories.

5. **Implement backup/rollback**: Always backup before overwriting, support rollback on failure.

6. **Use content hashing**: For `get_deployment_status()`, compare SHA-256 hashes for reliability.

7. **Write comprehensive tests**: Aim for 95%+ coverage on your handler.

8. **Document tool-specific transformations**: If your tool expects specific frontmatter fields, document them clearly.

### Troubleshooting

**Handler not appearing in deploy:**
- Verify it's registered in `commands.py`
- Check that `get_name()` returns the correct identifier
- Ensure it's exported in `__init__.py`

**Protocol conformance errors:**
- Run `isinstance(handler, ToolHandler)` to check conformance
- Verify all required methods are implemented
- Check that `prompts_dir` and `rules_dir` attributes exist

**Tests failing:**
- Use `tmp_path` fixture for isolation
- Mock filesystem operations when testing edge cases
- Check path separators on Windows vs Linux
