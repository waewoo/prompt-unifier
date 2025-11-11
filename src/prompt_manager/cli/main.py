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

# Create the Typer app
app = typer.Typer(
    name="prompt-manager",
    help="CLI tool for managing and validating AI assistant prompt files",
    add_completion=False,
)


@app.command(name="validate", help="Validate prompt file format in a directory")
def validate(
    directory: str,
    json: bool = typer.Option(False, "--json"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Validate prompt file format in a directory.

    Args:
        directory: Directory containing prompt files to validate
        json: Output in JSON format (use --json flag)
        verbose: Show detailed progress (use --verbose or -v flag)
    """
    validate_command(Path(directory), json_output=json, verbose=verbose)


@app.command(name="init", help="Initialize prompt-manager in current directory")
def init() -> None:
    """Initialize prompt-manager configuration.

    Creates .prompt-manager/ directory with config.yaml and prompts/
    directory structure in the current directory.
    """
    init_command()


@app.command(name="sync", help="Sync prompts from Git repository")
def sync(
    repo: str | None = typer.Option(
        None,
        "--repo",
        help="Git repository URL (optional if already configured)",
    ),
) -> None:
    """Sync prompts from Git repository.

    Args:
        repo: Git repository URL (optional if already configured in config.yaml)
    """
    sync_command(repo=repo)


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
