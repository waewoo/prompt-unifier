"""CLI commands for the Prompt Manager.

This module contains the CLI commands implemented using Typer,
including the validate command for prompt file validation and
Git integration commands (init, sync, status).
"""

from pathlib import Path

import typer
from rich.console import Console

from prompt_manager.config.manager import ConfigManager
from prompt_manager.core.batch_validator import BatchValidator
from prompt_manager.git.service import GitService
from prompt_manager.models.git_config import GitConfig
from prompt_manager.output.json_formatter import JSONFormatter
from prompt_manager.output.rich_formatter import RichFormatter
from prompt_manager.utils.formatting import format_timestamp

# Initialize Rich Console for formatted output
console = Console()


def validate(
    directory: Path,
    json_output: bool = False,
    verbose: bool = False,
) -> None:
    """Validate prompt file format in a directory.

    Validates all .md files in the specified directory against the prompt
    format specification. Checks for required fields, valid YAML frontmatter,
    proper separator format, and UTF-8 encoding.

    Exit codes:
        0: Validation passed (warnings are acceptable)
        1: Validation failed (errors found)

    Examples:
        # Validate prompts with Rich output
        prompt-manager validate ./prompts

        # Validate with JSON output
        prompt-manager validate ./prompts --json

        # Validate with verbose progress
        prompt-manager validate ./prompts --verbose
    """
    # Check if directory exists and is valid
    if not directory.exists():
        typer.echo(f"Error: Directory '{directory}' does not exist", err=True)
        raise typer.Exit(code=1)

    if not directory.is_dir():
        typer.echo(f"Error: '{directory}' is not a directory", err=True)
        raise typer.Exit(code=1)

    # Validate the directory
    validator = BatchValidator()
    summary = validator.validate_directory(directory)

    # Format and display results
    if json_output:
        json_formatter = JSONFormatter()
        json_str = json_formatter.format_summary(summary, directory)
        typer.echo(json_str)
    else:
        rich_formatter = RichFormatter()
        rich_formatter.format_summary(summary, directory, verbose=verbose)

    # Exit with appropriate code
    if not summary.success:
        raise typer.Exit(code=1)


def init() -> None:
    """Initialize prompt-manager configuration in current directory.

    Creates the .prompt-manager/ directory with config.yaml for storing
    repository sync settings. Also creates the prompts/ directory structure
    with subdirectories for rules, custom, and shared prompts.

    Exit codes:
        0: Initialization successful
        1: Initialization failed (e.g., already initialized)

    Examples:
        # Initialize in current directory
        prompt-manager init
    """
    try:
        # Get current working directory
        cwd = Path.cwd()

        # Create .prompt-manager/ directory
        prompt_manager_dir = cwd / ".prompt-manager"

        # Check if already initialized
        if prompt_manager_dir.exists():
            typer.echo(
                "Error: .prompt-manager/ directory already exists. "
                "Project is already initialized.",
                err=True,
            )
            raise typer.Exit(code=1)

        # Create .prompt-manager/ directory (exist_ok=False to catch race conditions)
        prompt_manager_dir.mkdir(parents=True, exist_ok=False)

        # Create config.yaml with empty placeholders
        config_manager = ConfigManager()
        config_path = prompt_manager_dir / "config.yaml"
        empty_config = GitConfig(repo_url=None, last_sync_timestamp=None, last_sync_commit=None)
        config_manager.save_config(config_path, empty_config)

        # Create prompts/ and rules/ directories
        prompts_dir = cwd / "prompts"
        prompts_dir.mkdir(parents=True, exist_ok=True)

        rules_dir = cwd / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)

        # Create .gitignore template if it doesn't exist
        gitignore_path = cwd / ".gitignore"
        if not gitignore_path.exists():
            gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
"""
            gitignore_path.write_text(gitignore_content)

        # Display success message with Rich formatting
        console.print("[green]✓[/green] Initialization complete")
        console.print("━" * 80)
        console.print(f"Created: {prompt_manager_dir}")
        console.print(f"Created: {config_path}")
        console.print(f"Created: {prompts_dir}")
        console.print(f"Created: {rules_dir}")
        if not gitignore_path.exists():
            console.print(f"Created: {gitignore_path}")
        console.print()
        console.print("[dim]Next steps:[/dim]")
        console.print("  1. Run 'prompt-manager sync --repo <git-url>' to sync prompts")
        console.print("  2. Run 'prompt-manager status' to check sync status")
        console.print()

    except FileExistsError:
        typer.echo(
            "Error: .prompt-manager/ directory already exists. " "Project is already initialized.",
            err=True,
        )
        raise typer.Exit(code=1) from None
    except PermissionError:
        typer.echo(
            "Error: Permission denied. Check directory permissions.",
            err=True,
        )
        raise typer.Exit(code=1) from None
    except Exception as e:
        typer.echo(f"Error during initialization: {e}", err=True)
        raise typer.Exit(code=1) from e


def sync(repo: str | None = typer.Option(None, "--repo")) -> None:
    """Sync prompts from Git repository.

    Clones the remote repository to a temporary directory, extracts the
    prompts/ directory, and copies it to the current project. Updates
    the config.yaml with sync metadata.

    Args:
        repo: Git repository URL (optional if already configured)

    Exit codes:
        0: Sync successful
        1: Sync failed (e.g., init not run, invalid repo, network error)

    Examples:
        # First sync with repository URL
        prompt-manager sync --repo https://github.com/example/prompts.git

        # Subsequent syncs (reads URL from config)
        prompt-manager sync
    """
    try:
        # Get current working directory
        cwd = Path.cwd()

        # Validate that init has been run
        config_path = cwd / ".prompt-manager" / "config.yaml"
        if not config_path.exists():
            typer.echo(
                "Error: Configuration not found. Run 'prompt-manager init' first.",
                err=True,
            )
            raise typer.Exit(code=1)

        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config(config_path)

        if config is None:
            typer.echo(
                "Error: Failed to load configuration. "
                "Config file may be corrupted. Run 'prompt-manager init' again.",
                err=True,
            )
            raise typer.Exit(code=1)

        # Determine repository URL
        if repo is not None:
            # Use --repo flag if provided
            repo_url = repo
        elif config.repo_url is not None:
            # Use URL from config
            repo_url = config.repo_url
        else:
            typer.echo(
                "Error: No repository URL configured. Use --repo flag to specify a repository.",
                err=True,
            )
            raise typer.Exit(code=1)

        # Display sync start message
        console.print()
        console.print("[bold]Syncing prompts...[/bold]")
        console.print("━" * 80)
        console.print(f"Repository: {repo_url}")
        console.print()

        # Clone repository to temporary directory
        git_service = GitService()
        console.print("[dim]Cloning repository...[/dim]")
        temp_dir, repo_obj = git_service.clone_to_temp(repo_url)

        # Get latest commit hash
        commit_hash = git_service.get_latest_commit(repo_obj)

        # Extract prompts/ directory
        console.print("[dim]Extracting prompts...[/dim]")
        git_service.extract_prompts_dir(temp_dir, cwd)

        # Update config with sync information
        config_manager.update_sync_info(config_path, repo_url, commit_hash)

        # Display success message
        console.print()
        console.print("[green]✓[/green] Sync complete")
        console.print("━" * 80)
        console.print(f"Repository: {repo_url}")
        console.print(f"Commit: {commit_hash}")
        console.print(f"Synced to: {cwd / 'prompts'}")
        console.print()

    except ValueError as e:
        # Git errors (invalid URL, auth failures, missing prompts/ directory)
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1) from e
    except PermissionError:
        typer.echo(
            "Error: Permission denied. Check directory permissions.",
            err=True,
        )
        raise typer.Exit(code=1) from None
    except Exception as e:
        # Unexpected errors
        typer.echo(f"Error during sync: {e}", err=True)
        raise typer.Exit(code=1) from e


def status() -> None:
    """Display current sync status and check for updates.

    Shows the configured repository URL, last sync timestamp, last synced
    commit, and whether updates are available from the remote repository.

    Exit codes:
        0: Always (status is informational)

    Examples:
        # Check sync status
        prompt-manager status
    """
    try:
        # Get current working directory
        cwd = Path.cwd()

        # Validate that init has been run
        config_path = cwd / ".prompt-manager" / "config.yaml"
        if not config_path.exists():
            typer.echo(
                "Error: Configuration not found. Run 'prompt-manager init' first.",
                err=True,
            )
            raise typer.Exit(code=1)

        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config(config_path)

        if config is None:
            typer.echo(
                "Error: Failed to load configuration. "
                "Config file may be corrupted. Run 'prompt-manager init' again.",
                err=True,
            )
            raise typer.Exit(code=1)

        # Display status header
        console.print()
        console.print("[bold]Prompt Manager Status[/bold]")
        console.print("━" * 80)

        # Display repository URL
        if config.repo_url:
            console.print(f"Repository: {config.repo_url}")
        else:
            console.print("Repository: [yellow]Not configured[/yellow]")
            console.print()
            console.print("[dim]Run 'prompt-manager sync --repo <git-url>' to configure[/dim]")
            console.print()
            return

        # Display last sync information with human-readable timestamp
        if config.last_sync_timestamp:
            human_readable = format_timestamp(config.last_sync_timestamp)
            console.print(f"Last sync: {human_readable}")
        else:
            console.print("Last sync: [yellow]Never[/yellow]")

        if config.last_sync_commit:
            console.print(f"Commit: {config.last_sync_commit}")
        else:
            console.print("Commit: [yellow]None[/yellow]")

        # Check for remote updates
        if config.last_sync_commit and config.repo_url:
            console.print()
            console.print("[dim]Checking for updates...[/dim]")

            try:
                git_service = GitService()
                has_updates, commits_behind = git_service.check_remote_updates(
                    config.repo_url, config.last_sync_commit
                )

                if has_updates:
                    console.print(
                        f"[yellow]⚠ Updates available[/yellow] ({commits_behind} commits behind)"
                    )
                    console.print()
                    console.print("[dim]Run 'prompt-manager sync' to update[/dim]")
                else:
                    console.print("[green]✓ Up to date[/green]")
            except Exception:
                # If update check fails, just show cached info
                console.print("[yellow]⚠ Could not check for updates[/yellow]")
                console.print("[dim]Check network connection or repository access[/dim]")

        console.print()

    except Exception as e:
        # Unexpected errors - but status should always exit with 0
        typer.echo(f"Error: {e}", err=True)
        # Status is informational - don't exit with error code
        console.print()
