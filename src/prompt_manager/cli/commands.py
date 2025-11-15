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
from prompt_manager.core.content_parser import ContentFileParser
from prompt_manager.git.service import GitService
from prompt_manager.handlers.continue_handler import ContinueToolHandler
from prompt_manager.handlers.registry import ToolHandlerRegistry
from prompt_manager.models.git_config import GitConfig
from prompt_manager.models.prompt import PromptFrontmatter
from prompt_manager.models.rule import RuleFrontmatter
from prompt_manager.output.json_formatter import JSONFormatter
from prompt_manager.output.rich_formatter import RichFormatter
from prompt_manager.utils.formatting import format_timestamp

# Initialize Rich Console for formatted output
console = Console()

# Constants for default values to avoid function calls in argument defaults
DEFAULT_PROMPT_NAME = None
DEFAULT_TAGS = None
DEFAULT_HANDLERS = None

DEFAULT_PROMPT_NAME_OPTION = typer.Option(
    DEFAULT_PROMPT_NAME,
    "--name",
    help="Name of the prompt to deploy (optional, deploys all if not specified)",
)
DEFAULT_TAGS_OPTION = typer.Option(
    DEFAULT_TAGS,
    "--tags",
    help="Tags to filter prompts and rules (optional, deploys all if not specified)",
)
DEFAULT_HANDLERS_OPTION = typer.Option(
    None,
    "--handlers",
    help="Target handlers to deploy to (optional, deploys to all registered if not specified)",
)


def validate(
    directory: Path | None = None,
    json_output: bool = False,
    verbose: bool = False,
    content_type: str = "all",
) -> None:
    """Validate prompt and rule files in a directory.

    Validates .md files against the format specification. Checks for
    required fields, valid YAML frontmatter, proper separator format,
    and UTF-8 encoding.

    If no directory is provided, validates files in the synchronized storage
    location (requires 'init' to have been run).

    Exit codes:
        0: Validation passed (warnings are acceptable)
        1: Validation failed (errors found)

    Examples:
        # Validate everything (prompts + rules)
        prompt-manager validate

        # Validate only prompts
        prompt-manager validate --type prompts

        # Validate only rules
        prompt-manager validate --type rules

        # Validate specific directory
        prompt-manager validate ./prompts

        # Validate with JSON output
        prompt-manager validate ./prompts --json

        # Validate with verbose progress
        prompt-manager validate --verbose
    """
    # If no directory provided, use storage path from config
    if directory is None:
        cwd = Path.cwd()
        config_path = cwd / ".prompt-manager" / "config.yaml"

        if not config_path.exists():
            typer.echo(
                "Error: No directory specified and configuration not found.\n"
                "Either provide a directory path or run 'prompt-manager init' first.",
                err=True,
            )
            raise typer.Exit(code=1)

        config_manager = ConfigManager()
        config = config_manager.load_config(config_path)

        if config is None or config.storage_path is None:
            typer.echo(
                "Error: Storage path not configured.\n"
                "Either provide a directory path or run 'prompt-manager init' to set up storage.",
                err=True,
            )
            raise typer.Exit(code=1)

        directory = Path(config.storage_path).expanduser().resolve()

        if verbose:
            console.print(f"[dim]Using storage path: {directory}[/dim]")

    # Validate content_type parameter
    if content_type not in ["all", "prompts", "rules"]:
        typer.echo(
            f"Error: Invalid --type '{content_type}'. Must be 'all', 'prompts', or 'rules'",
            err=True,
        )
        raise typer.Exit(code=1)

    # Determine which directory to validate based on content_type
    if content_type == "prompts":
        target_dir = directory / "prompts"
        if not target_dir.exists():
            typer.echo(f"Error: Prompts directory '{target_dir}' does not exist", err=True)
            raise typer.Exit(code=1)
        directory = target_dir
    elif content_type == "rules":
        target_dir = directory / "rules"
        if not target_dir.exists():
            typer.echo(f"Error: Rules directory '{target_dir}' does not exist", err=True)
            raise typer.Exit(code=1)
        directory = target_dir

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


def init(storage_path: str | None = typer.Option(None, "--storage-path")) -> None:
    """Initialize prompt-manager configuration in current directory.

    Creates the .prompt-manager/ directory with config.yaml for storing
    repository sync settings. Also creates the centralized storage directory
    (default: ~/.prompt-manager/storage) with prompts/ and rules/ subdirectories.

    This command is idempotent: running it multiple times will create only
    what's missing without failing if already initialized.

    Args:
        storage_path: Custom path for centralized storage (default: ~/.prompt-manager/storage)

    Exit codes:
        0: Initialization successful (including when already initialized)
        1: Initialization failed (e.g., permission errors)

    Examples:
        # Initialize with default storage location
        prompt-manager init

        # Initialize with custom storage location
        prompt-manager init --storage-path /custom/path/storage
    """
    try:
        # Get current working directory
        cwd = Path.cwd()

        # Create .prompt-manager/ directory
        prompt_manager_dir = cwd / ".prompt-manager"

        # Track what was created vs what already existed
        created_items = []
        existing_items = []

        # Determine storage path (custom or default)
        if storage_path and isinstance(storage_path, str):
            storage_dir = Path(storage_path).expanduser().resolve()
        else:
            # Try to read from existing config if available
            config_path = prompt_manager_dir / "config.yaml"
            if config_path.exists():
                config_manager = ConfigManager()
                existing_config = config_manager.load_config(config_path)
                if existing_config and existing_config.storage_path:
                    storage_dir = Path(existing_config.storage_path).expanduser().resolve()
                else:
                    storage_dir = Path.home() / ".prompt-manager" / "storage"
            else:
                storage_dir = Path.home() / ".prompt-manager" / "storage"

        # Create .prompt-manager/ directory if it doesn't exist
        if not prompt_manager_dir.exists():
            prompt_manager_dir.mkdir(parents=True, exist_ok=True)
            created_items.append(f"Created: {prompt_manager_dir}")
        else:
            existing_items.append(f"Exists: {prompt_manager_dir}")

        # Create config.yaml if it doesn't exist
        config_path = prompt_manager_dir / "config.yaml"
        if not config_path.exists():
            config_manager = ConfigManager()
            empty_config = GitConfig(
                repo_url=None,
                last_sync_timestamp=None,
                last_sync_commit=None,
                storage_path=str(storage_dir),
                deploy_tags=None,
                target_handlers=None,
            )
            config_manager.save_config(config_path, empty_config)
            created_items.append(f"Created: {config_path}")
        else:
            existing_items.append(f"Exists: {config_path}")

        # Create centralized storage directory
        if not storage_dir.exists():
            storage_dir.mkdir(parents=True, exist_ok=True)
            created_items.append(f"Created: {storage_dir}")
        else:
            existing_items.append(f"Exists: {storage_dir}")

        # Create prompts/ and rules/ directories in storage
        prompts_dir = storage_dir / "prompts"
        if not prompts_dir.exists():
            prompts_dir.mkdir(parents=True, exist_ok=True)
            created_items.append(f"Created: {prompts_dir}")
        else:
            existing_items.append(f"Exists: {prompts_dir}")

        rules_dir = storage_dir / "rules"
        if not rules_dir.exists():
            rules_dir.mkdir(parents=True, exist_ok=True)
            created_items.append(f"Created: {rules_dir}")
        else:
            existing_items.append(f"Exists: {rules_dir}")

        # Create .gitignore template in storage directory if it doesn't exist
        gitignore_path = storage_dir / ".gitignore"
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
virtualenv/
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
            created_items.append(f"Created: {gitignore_path}")
        else:
            existing_items.append(f"Exists: {gitignore_path}")

        # Display success message with Rich formatting
        if created_items:
            console.print("[green]✓[/green] Initialization complete")
        else:
            console.print("[green]✓[/green] Already initialized (all components exist)")

        console.print("━" * 80)

        # Display what was created
        if created_items:
            for item in created_items:
                console.print(f"[green]{item}[/green]")

        # Display what already existed (in dim style)
        if existing_items:
            for item in existing_items:
                console.print(f"[dim]{item}[/dim]")

        console.print()
        console.print(f"Storage: {storage_dir}")
        console.print()
        console.print("[dim]Next steps:[/dim]")
        console.print("  1. Run 'prompt-manager sync --repo <git-url>' to sync prompts")
        console.print("  2. Run 'prompt-manager status' to check sync status")
        console.print()

    except PermissionError:
        typer.echo(
            "Error: Permission denied. Check directory permissions.",
            err=True,
        )
        raise typer.Exit(code=1) from None
    except Exception as e:
        typer.echo(f"Error during initialization: {e}", err=True)
        raise typer.Exit(code=1) from e


def sync(
    repo: str | None = typer.Option(None, "--repo"),
    storage_path: str | None = typer.Option(None, "--storage-path"),
) -> None:
    """Sync prompts from Git repository to centralized storage.

    Clones the remote repository to a temporary directory, extracts the
    prompts/ directory, and copies it to the centralized storage location.
    Updates the config.yaml with sync metadata.

    Args:
        repo: Git repository URL (optional if already configured)
        storage_path: Override storage path for this sync (optional)

    Exit codes:
        0: Sync successful
        1: Sync failed (e.g., init not run, invalid repo, network error)

    Examples:
        # First sync with repository URL
        prompt-manager sync --repo https://github.com/example/prompts.git

        # Subsequent syncs (reads URL from config)
        prompt-manager sync

        # Sync with custom storage path
        prompt-manager sync --storage-path /custom/path/storage
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

        # Determine storage path
        if storage_path and isinstance(storage_path, str):
            # Use --storage-path flag if provided
            storage_dir = Path(storage_path).expanduser().resolve()
        elif config.storage_path:
            # Use storage_path from config
            storage_dir = Path(config.storage_path).expanduser().resolve()
        else:
            # Use default storage path
            storage_dir = Path.home() / ".prompt-manager" / "storage"

        # Display sync start message
        console.print()
        console.print("[bold]Syncing prompts and rules...[/bold]")
        console.print("━" * 80)
        console.print(f"Repository: {repo_url}")
        console.print(f"Storage: {storage_dir}")
        console.print()

        # Clone repository to temporary directory
        git_service = GitService()
        console.print("[dim]Cloning repository...[/dim]")
        temp_dir, repo_obj = git_service.clone_to_temp(repo_url)

        try:
            # Get latest commit hash
            commit_hash = git_service.get_latest_commit(repo_obj)

            # Extract prompts/ and rules/ directories to storage
            console.print("[dim]Extracting prompts and rules...[/dim]")
            git_service.extract_prompts_dir(temp_dir, storage_dir)

            # Update config with sync information
            config_manager.update_sync_info(config_path, repo_url, commit_hash)

            # If storage_path was provided via flag, update config
            if storage_path and isinstance(storage_path, str):
                config.storage_path = str(storage_dir)
                config_manager.save_config(config_path, config)

            # Display success message
            console.print()
            console.print("[green]✓[/green] Sync complete")
            console.print("━" * 80)
            console.print(f"Repository: {repo_url}")
            console.print(f"Commit: {commit_hash}")
            console.print(f"Synced to: {storage_dir}")
            console.print()

        finally:
            # Clean up temporary directory
            import shutil

            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)

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

        # Display storage path
        if config.storage_path:
            storage_dir = Path(config.storage_path).expanduser().resolve()
            console.print(f"Storage: {storage_dir}")
        else:
            # Default storage path
            storage_dir = Path.home() / ".prompt-manager" / "storage"
            console.print(f"Storage: {storage_dir} [dim](default)[/dim]")

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


def deploy(
    prompt_name: str | None = DEFAULT_PROMPT_NAME_OPTION,
    tags: list[str] | None = DEFAULT_TAGS_OPTION,
    handlers: list[str] | None = DEFAULT_HANDLERS_OPTION,
) -> None:
    """
    Deploys prompts and rules to the specified tool handlers based on configuration and CLI options.
    """
    try:
        # Load configuration
        cwd = Path.cwd()
        config_path = cwd / ".prompt-manager" / "config.yaml"
        if not config_path.exists():
            typer.echo("Error: Configuration not found. Run 'prompt-manager init' first.", err=True)
            raise typer.Exit(code=1)

        config_manager = ConfigManager()
        config = config_manager.load_config(config_path)
        if config is None or config.storage_path is None:
            typer.echo("Error: Storage path not configured.", err=True)
            raise typer.Exit(code=1)

        storage_dir = Path(config.storage_path).expanduser().resolve()
        if not storage_dir.exists():
            typer.echo(f"Error: Storage directory '{storage_dir}' does not exist.", err=True)
            raise typer.Exit(code=1)

        # Determine deploy tags
        deploy_tags = tags if tags is not None else config.deploy_tags

        # Determine target handlers
        target_handlers = handlers if handlers is not None else config.target_handlers

        # Register handlers
        registry: ToolHandlerRegistry = ToolHandlerRegistry()
        registry.register(ContinueToolHandler())

        all_handlers = registry.get_all_handlers()
        if target_handlers:
            all_handlers = [h for h in all_handlers if h.get_name() in target_handlers]
            if not all_handlers:
                typer.echo(f"Error: No matching handlers found for {target_handlers}.", err=True)
                raise typer.Exit(code=1)

        # Scan for content files
        parser = ContentFileParser()
        content_files = []

        prompts_dir = storage_dir / "prompts"
        if prompts_dir.exists():
            for md_file in prompts_dir.glob("*.md"):
                try:
                    parsed_content = parser.parse_file(md_file)
                    content_files.append((parsed_content, "prompt", md_file))
                except Exception as e:
                    console.print(f"[yellow]Warning: Failed to parse {md_file}: {e}[/yellow]")

        rules_dir = storage_dir / "rules"
        if rules_dir.exists():
            for md_file in rules_dir.glob("*.md"):
                try:
                    parsed_content = parser.parse_file(md_file)
                    content_files.append((parsed_content, "rule", md_file))
                except Exception as e:
                    console.print(f"[yellow]Warning: Failed to parse {md_file}: {e}[/yellow]")

        # Filter by tags and name
        filtered_files = []
        for parsed_content, content_type, file_path in content_files:
            # Filter by name if specified
            if prompt_name and parsed_content.title != prompt_name:
                continue
            # Filter by tags if specified
            if deploy_tags:
                content_tags = getattr(parsed_content, "tags", []) or []
                if not any(tag in content_tags for tag in deploy_tags):
                    continue
            filtered_files.append((parsed_content, content_type, file_path))

        if not filtered_files:
            console.print("[yellow]No content files match the specified criteria.[/yellow]")
            return

        # Deploy to handlers
        total_deployed = 0
        for handler in all_handlers:
            handler_name = handler.get_name()
            console.print(f"Deploying to {handler_name}...")
            handler_deployed = 0
            for parsed_content, content_type, _file_path in filtered_files:
                try:
                    body = str(parsed_content.content) if hasattr(parsed_content, "content") else ""
                    if content_type == "prompt":
                        frontmatter_dict = parsed_content.model_dump(exclude={"content"})
                        prompt_content = PromptFrontmatter(**frontmatter_dict)
                        handler.deploy(prompt_content, content_type, body)
                    elif content_type == "rule":
                        frontmatter_dict = parsed_content.model_dump(exclude={"content"})
                        rule_content = RuleFrontmatter(**frontmatter_dict)
                        handler.deploy(rule_content, content_type, body)
                    handler_deployed += 1
                    total_deployed += 1
                    console.print(
                        f"  [green]✓[/green] Deployed {parsed_content.title} ({content_type})"
                    )
                except Exception as e:
                    console.print(
                        f"  [red]✗[/red] Failed to deploy {parsed_content.title} "
                        f"({content_type}): {e}"
                    )
                    # Attempt rollback if available
                    if hasattr(handler, "rollback"):
                        try:
                            handler.rollback()
                            console.print("  [yellow]Rollback completed.[/yellow]")
                        except Exception as rollback_e:
                            console.print(f"  [red]Rollback failed: {rollback_e}[/red]")

            if handler_deployed > 0:
                console.print(
                    f"[green]✓ Deployment to {handler_name} completed "
                    f"({handler_deployed} items).[/green]"
                )
            else:
                console.print(f"[yellow]⚠ No items deployed to {handler_name}.[/yellow]")

        console.print(
            f"\n[bold]Deployment summary:[/bold] {total_deployed} items deployed "
            f"to {len(all_handlers)} handler(s)."
        )

        # Don't exit with error code even if deployment fails partially
        return

    except Exception as e:
        typer.echo(f"Error during deployment: {e}", err=True)
        raise typer.Exit(code=1) from e
