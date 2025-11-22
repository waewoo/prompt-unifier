"""Main CLI application for Prompt Unifier.

This module sets up the Typer application and registers all CLI commands.
"""

from pathlib import Path

import typer

from prompt_unifier.cli.commands import (
    deploy as deploy_command,
)
from prompt_unifier.cli.commands import (
    init as init_command,
)
from prompt_unifier.cli.commands import (
    list_content as list_command,
)
from prompt_unifier.cli.commands import (
    status as status_command,
)
from prompt_unifier.cli.commands import (
    sync as sync_command,
)
from prompt_unifier.cli.commands import (
    validate as validate_command,
)
from prompt_unifier.utils import configure_logging

# Version
__version__ = "0.1.0"


def version_callback(value: bool) -> None:
    """Display version and exit."""
    if value:
        typer.echo(f"prompt-unifier version {__version__}")
        raise typer.Exit()


# Create the Typer app
app = typer.Typer(
    name="prompt-unifier",
    help="CLI tool for managing and validating AI assistant prompt files",
    add_completion=False,
)


@app.callback()
def main_callback(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
    verbose: int = typer.Option(
        0,
        "--verbose",
        "-v",
        count=True,
        help="Increase verbosity level (use -v for INFO, -vv for DEBUG)",
        is_eager=True,
    ),
    log_file: str | None = typer.Option(
        None,
        "--log-file",
        help="Write logs to the specified file path",
        is_eager=True,
    ),
) -> None:
    """Prompt Unifier CLI - Manage and validate AI prompt templates."""
    # Configure logging based on verbosity level and optional log file
    configure_logging(verbosity=verbose, log_file=log_file)


@app.command(name="validate", help="Validate prompt and rule files in a directory")
def validate(
    directory: str | None = typer.Argument(
        None, help="Directory to validate (defaults to synchronized storage)"
    ),
    json: bool = typer.Option(False, "--json"),
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
        type: Content type to validate: 'all' (default), 'prompts', or 'rules'
    """
    dir_path = Path(directory) if directory is not None else None
    validate_command(dir_path, json_output=json, content_type=type)


@app.command(name="init", help="Initialize prompt-unifier in current directory")
def init(
    storage_path: str | None = typer.Option(
        None,
        "--storage-path",
        help="Optional custom storage directory path (defaults to ~/.prompt-unifier/storage/)",
    ),
) -> None:
    """Initialize prompt-unifier configuration.

    Creates .prompt-unifier/ directory with config.yaml and centralized
    storage directory for prompts and rules.

    Args:
        storage_path: Custom path for centralized storage directory
                      (default: ~/.prompt-unifier/storage)
    """
    init_command(storage_path=storage_path)


@app.command(name="sync", help="Sync prompts from Git repositories")
def sync(
    repos: list[str] | None = typer.Option(  # noqa: B008
        None, "--repo", help="Git repository URL (can be specified multiple times)"
    ),
    storage_path: str | None = typer.Option(
        None,
        "--storage-path",
        help=(
            "Override storage path for this sync (defaults to config value or "
            "~/.prompt-unifier/storage/)"
        ),
    ),  # noqa: B008
) -> None:
    """Sync prompts from Git repositories to centralized storage.

    Supports multiple repositories with last-wins merge strategy.
    Later repositories override files from earlier ones if there are path conflicts.

    Args:
        repos: Git repository URLs (can specify multiple times with --repo URL1 --repo URL2)
        storage_path: Override storage path for this sync
    """
    sync_command(repos=repos, storage_path=storage_path)


@app.command(name="status", help="Display sync status and check for updates")
def status() -> None:
    """Display current sync status.

    Shows repository URL, last sync time, commit hash, and whether
    updates are available from the remote repository.
    """
    status_command()


@app.command(name="list", help="List available prompts and rules")
def list_content(
    tool: str | None = typer.Option(None, "--tool", "-t", help="Filter by target tool"),
    tag: str | None = typer.Option(None, "--tag", help="Filter by tag"),
    sort: str = typer.Option("name", "--sort", "-s", help="Sort by 'name' or 'date'"),
) -> None:
    """List available prompts and rules.

    Displays a table of all available prompts and rules, with optional filtering
    and sorting.
    """
    list_command(tool=tool, tag=tag, sort=sort)


@app.command(name="deploy", help="Deploy prompts and rules to tool handlers")
def deploy(
    prompt_name: str | None = typer.Option(
        None, "--name", help="Name of the prompt to deploy (optional)"
    ),
    tags: str | None = typer.Option(
        None, "--tags", help="Tags to filter (comma-separated, optional)"
    ),
    handlers: str | None = typer.Option(
        None, "--handlers", help="Handlers to deploy to (comma-separated, optional)"
    ),
    base_path: str | None = typer.Option(
        None,
        "--base-path",
        help="Custom base path for handler deployment (overrides config.yaml)",
    ),
    clean: bool = typer.Option(
        False,
        "--clean",
        help="Remove orphaned prompts/rules in destination (creates backups)",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview deployment without executing any file operations",
    ),
) -> None:
    """Deploy prompts and rules to the specified tool handlers.

    The base path for deployment is resolved in the following precedence order:
    1. CLI --base-path flag (highest priority)
    2. config.yaml handlers.<handler_name>.base_path
    3. Path.cwd() (default)

    Environment variables ($HOME, $USER, $PWD) in configured base_path are expanded.

    With --clean flag, files in the destination that don't exist in the source
    will be removed (backups are created before removal).

    With --dry-run flag, shows a preview of what would be deployed without
    actually executing any file operations.
    """
    tag_list = tags.split(",") if tags else None
    handler_list = handlers.split(",") if handlers else None
    base_path_obj = Path(base_path) if base_path else None
    deploy_command(
        prompt_name=prompt_name,
        tags=tag_list,
        handlers=handler_list,
        base_path=base_path_obj,
        clean=clean,
        dry_run=dry_run,
    )


def main() -> None:
    """Entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main()
