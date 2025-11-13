"""Main CLI application for Prompt Manager.

This module sets up the Typer application and registers all CLI commands.
"""

from pathlib import Path

import typer

from prompt_manager.cli.commands import (
    init as init_command,
)
from prompt_manager.cli.commands import (
    status as status_command,
)
from prompt_manager.cli.commands import (
    sync as sync_command,
)
from prompt_manager.cli.commands import (
    validate as validate_command,
)

# Version
__version__ = "0.1.0"


def version_callback(value: bool) -> None:
    """Display version and exit."""
    if value:
        typer.echo(f"prompt-manager version {__version__}")
        raise typer.Exit()


# Create the Typer app
app = typer.Typer(
    name="prompt-manager",
    help="CLI tool for managing and validating AI assistant prompt files",
    add_completion=False,
)


@app.callback()
def main_callback(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """Prompt Manager CLI - Manage and validate AI prompt templates."""
    pass


@app.command(name="validate", help="Validate prompt and rule files in a directory")
def validate(
    directory: str | None = typer.Argument(
        None, help="Directory to validate (defaults to synchronized storage)"
    ),
    json: bool = typer.Option(False, "--json"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    type: str = typer.Option(
        "all", "--type", "-t", help="Content type to validate: all, prompts, or rules"
    ),
) -> None:
    """Validate prompt and rule files in a directory.

    If no directory is provided, validates files in the synchronized storage
    location (requires 'init' to have been run first).

    Args:
        directory: Directory containing prompt/rule files to validate (optional)
        json: Output in JSON format (use --json flag)
        verbose: Show detailed progress (use --verbose or -v flag)
        type: Content type to validate: 'all' (default), 'prompts', or 'rules'
    """
    dir_path = Path(directory) if directory is not None else None
    validate_command(dir_path, json_output=json, verbose=verbose, content_type=type)


@app.command(name="init", help="Initialize prompt-manager in current directory")
def init(
    storage_path: str | None = typer.Option(None, "--storage-path"),
) -> None:
    """Initialize prompt-manager configuration.

    Creates .prompt-manager/ directory with config.yaml and centralized
    storage directory for prompts and rules.

    Args:
        storage_path: Custom path for centralized storage directory
                      (default: ~/.prompt-manager/storage)
    """
    init_command(storage_path=storage_path)


@app.command(name="sync", help="Sync prompts from Git repository")
def sync(
    repo: str | None = typer.Option(None, "--repo"),
    storage_path: str | None = typer.Option(None, "--storage-path"),
) -> None:
    """Sync prompts from Git repository to centralized storage.

    Args:
        repo: Git repository URL (optional if already configured in config.yaml)
        storage_path: Override storage path for this sync
    """
    sync_command(repo=repo, storage_path=storage_path)


@app.command(name="status", help="Display sync status and check for updates")
def status() -> None:
    """Display current sync status.

    Shows repository URL, last sync time, commit hash, and whether
    updates are available from the remote repository.
    """
    status_command()


def main() -> None:
    """Entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main()
