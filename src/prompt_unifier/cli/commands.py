"""CLI commands for the Prompt Unifier.

This module contains the CLI commands implemented using Typer,
including the validate command for prompt file validation and
Git integration commands (init, sync, status).
"""

from pathlib import Path

import typer
from rich.console import Console

from prompt_unifier.config.manager import ConfigManager
from prompt_unifier.core.batch_validator import BatchValidator
from prompt_unifier.core.content_parser import ContentFileParser
from prompt_unifier.git.service import GitService
from prompt_unifier.handlers.continue_handler import ContinueToolHandler
from prompt_unifier.handlers.registry import ToolHandlerRegistry
from prompt_unifier.models.git_config import GitConfig, RepositoryConfig
from prompt_unifier.models.prompt import PromptFrontmatter
from prompt_unifier.models.rule import RuleFrontmatter
from prompt_unifier.output.json_formatter import JSONFormatter
from prompt_unifier.output.rich_formatter import RichFormatter
from prompt_unifier.utils.formatting import format_timestamp
from prompt_unifier.utils.path_helpers import expand_env_vars

# Initialize Rich Console for formatted output
console = Console()

# Constants for default values to avoid function calls in argument defaults
DEFAULT_PROMPT_NAME = None
DEFAULT_TAGS = None
DEFAULT_HANDLERS = None
DEFAULT_BASE_PATH = None

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
DEFAULT_BASE_PATH_OPTION = typer.Option(
    DEFAULT_BASE_PATH,
    "--base-path",
    help=(
        "Custom base path for handler deployment "
        "(overrides config.yaml, works with --handlers flag)"
    ),
)
DEFAULT_CLEAN = False
DEFAULT_CLEAN_OPTION = typer.Option(
    DEFAULT_CLEAN,
    "--clean",
    help=(
        "Remove prompts/rules in destination that don't exist in source "
        "(creates backups before removal)"
    ),
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
        prompt-unifier validate

        # Validate only prompts
        prompt-unifier validate --type prompts

        # Validate only rules
        prompt-unifier validate --type rules

        # Validate specific directory
        prompt-unifier validate ./prompts

        # Validate with JSON output
        prompt-unifier validate ./prompts --json

        # Validate with verbose progress
        prompt-unifier validate --verbose
    """
    # If no directory provided, use storage path from config
    if directory is None:
        cwd = Path.cwd()
        config_path = cwd / ".prompt-unifier" / "config.yaml"

        if not config_path.exists():
            typer.echo(
                "Error: No directory specified and configuration not found.\n"
                "Either provide a directory path or run 'prompt-unifier init' first.",
                err=True,
            )
            raise typer.Exit(code=1)

        config_manager = ConfigManager()
        config = config_manager.load_config(config_path)

        if config is None or config.storage_path is None:
            typer.echo(
                "Error: Storage path not configured.\n"
                "Either provide a directory path or run 'prompt-unifier init' to set up storage.",
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
        directories = [target_dir]
    elif content_type == "rules":
        target_dir = directory / "rules"
        if not target_dir.exists():
            typer.echo(f"Error: Rules directory '{target_dir}' does not exist", err=True)
            raise typer.Exit(code=1)
        directories = [target_dir]
    else:
        # Validate both prompts and rules
        directories = []
        prompts_dir = directory / "prompts"
        rules_dir = directory / "rules"
        if prompts_dir.exists():
            directories.append(prompts_dir)
        if rules_dir.exists():
            directories.append(rules_dir)

        if not directories:
            typer.echo(
                f"Error: Neither prompts/ nor rules/ directory exists in '{directory}'",
                err=True,
            )
            raise typer.Exit(code=1)

    # Run validation
    validator = BatchValidator()

    if json_output:
        # JSON output mode - validate first directory and combine results
        json_formatter = JSONFormatter()
        all_success = True

        for dir_path in directories:
            summary = validator.validate_directory(dir_path)
            json_output_str = json_formatter.format_summary(summary, dir_path)
            typer.echo(json_output_str)

            if not summary.success:
                all_success = False

        # Exit with error code if any validation failed
        if not all_success:
            raise typer.Exit(code=1)
    else:
        # Rich formatted output
        rich_formatter = RichFormatter()
        all_success = True

        for dir_path in directories:
            summary = validator.validate_directory(dir_path)
            rich_formatter.format_summary(summary, directory=dir_path, verbose=verbose)

            if not summary.success:
                all_success = False

        if not all_success:
            raise typer.Exit(code=1)


def init(storage_path: str | None = None) -> None:
    """Initialize Prompt Unifier in the current directory.

    Creates the .prompt-unifier/ directory and config.yaml in the
    current working directory. This must be run before using other
    commands.

    Args:
        storage_path: Optional custom storage directory path. If not provided,
                     uses ~/.prompt-unifier/storage or existing config value.

    Exit codes:
        0: Initialization successful (including when already initialized)
        1: Initialization failed (e.g., permission errors)

    Examples:
        # Initialize with default storage location
        prompt-unifier init

        # Initialize with custom storage location
        prompt-unifier init --storage-path /custom/path/storage
    """
    try:
        # Get current working directory
        cwd = Path.cwd()

        # Create .prompt-unifier/ directory
        prompt_unifier_dir = cwd / ".prompt-unifier"

        # Track what was created vs what already existed
        created_items = []
        existing_items = []

        # Determine storage path (custom or default)
        if storage_path and isinstance(storage_path, str):
            storage_dir = Path(storage_path).expanduser().resolve()
        else:
            # Try to read from existing config if available
            config_path = prompt_unifier_dir / "config.yaml"
            if config_path.exists():
                config_manager = ConfigManager()
                existing_config = config_manager.load_config(config_path)
                if existing_config and existing_config.storage_path:
                    storage_dir = Path(existing_config.storage_path).expanduser().resolve()
                else:
                    storage_dir = Path.home() / ".prompt-unifier" / "storage"
            else:
                storage_dir = Path.home() / ".prompt-unifier" / "storage"

        # Create .prompt-unifier/ directory if it doesn't exist
        if not prompt_unifier_dir.exists():
            prompt_unifier_dir.mkdir(parents=True, exist_ok=True)
            created_items.append(f"Created: {prompt_unifier_dir}")
        else:
            existing_items.append(f"Exists: {prompt_unifier_dir}")

        # Create config.yaml if it doesn't exist
        config_path = prompt_unifier_dir / "config.yaml"
        if not config_path.exists():
            config_manager = ConfigManager()
            empty_config = GitConfig(
                repos=None,
                last_sync_timestamp=None,
                repo_metadata=None,
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

    except PermissionError:
        typer.echo(
            "Error: Permission denied. Check directory permissions.",
            err=True,
        )
        raise typer.Exit(code=1) from None
    except Exception as e:
        # Unexpected errors
        typer.echo(f"Error during initialization: {e}", err=True)
        raise typer.Exit(code=1) from e


def sync(repos: list[str] | None = None, storage_path: str | None = None) -> None:
    """Sync prompts from Git repositories to centralized storage.

    Clones remote repositories to temporary directories, extracts the
    prompts/ and rules/ directories, and copies them to the centralized storage location.
    Updates the config.yaml with sync metadata.

    Supports multiple repositories with last-wins merge strategy - later repositories
    override files from earlier ones if there are path conflicts.

    Args:
        repos: Git repository URLs (optional if already configured in config.yaml)
        storage_path: Override storage path for this sync (optional)

    Exit codes:
        0: Sync successful
        1: Sync failed (e.g., init not run, invalid repo, network error)

    Examples:
        # Sync with multiple repository URLs
        prompt-unifier sync --repo https://github.com/repo1/prompts.git --repo https://github.com/repo2/prompts.git

        # Subsequent syncs (reads repos from config.yaml)
        prompt-unifier sync

        # Sync with custom storage path
        prompt-unifier sync --storage-path /custom/path/storage
    """
    try:
        # Get current working directory
        cwd = Path.cwd()

        # Validate that init has been run
        config_path = cwd / ".prompt-unifier" / "config.yaml"
        if not config_path.exists():
            typer.echo(
                "Error: Configuration not found. Run 'prompt-unifier init' first.",
                err=True,
            )
            raise typer.Exit(code=1)

        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config(config_path)

        if config is None:
            typer.echo(
                "Error: Failed to load configuration. "
                "Config file may be corrupted. Run 'prompt-unifier init' again.",
                err=True,
            )
            raise typer.Exit(code=1)

        # Determine repository configurations
        repo_configs: list[RepositoryConfig] = []

        if repos is not None and len(repos) > 0:
            # Use --repo flags if provided (CLI override)
            for repo_url in repos:
                repo_configs.append(RepositoryConfig(url=repo_url))
        elif config.repos is not None and len(config.repos) > 0:
            # Use repos from config.yaml
            repo_configs = config.repos
        else:
            typer.echo(
                "Error: No repository URLs configured. Use --repo flag to specify repositories.",
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
            storage_dir = Path.home() / ".prompt-unifier" / "storage"

        # Display sync start message
        console.print()
        console.print("[bold]Syncing prompts and rules from multiple repositories...[/bold]")
        console.print("━" * 80)
        console.print(f"Repositories: {len(repo_configs)}")
        console.print(f"Storage: {storage_dir}")
        console.print()

        # Use GitService to sync multiple repositories
        git_service = GitService()
        console.print("[dim]Validating repositories...[/dim]")

        # Sync multiple repos using the GitService method
        metadata = git_service.sync_multiple_repos(
            repos=repo_configs,
            storage_path=storage_dir,
            clear_storage=True,
        )

        # Update config with sync information
        repositories_list = metadata.get_repositories()
        config_manager.update_multi_repo_sync_info(config_path, repositories_list)

        # Reload config to get the updated repo_metadata
        # (update_multi_repo_sync_info always creates a valid config)
        config = config_manager.load_config(config_path)
        if config is None:
            raise ValueError(
                "Configuration is unexpectedly None after sync. This indicates a "
                "problem with config file creation or loading."
            )

        # Save repos to config if they were provided via CLI (so subsequent syncs can use them)
        # Also save storage_path if provided via flag
        if (repos is not None and len(repos) > 0) or storage_path:
            if repos is not None and len(repos) > 0:
                config.repos = repo_configs
            if storage_path:
                config.storage_path = str(storage_dir)
            config_manager.save_config(config_path, config)

        # Display success message
        console.print()
        console.print("[green]✓[/green] Multi-repository sync complete")
        console.print("━" * 80)

        # Display repository details
        for repo_info in repositories_list:
            console.print(f"Repository: {repo_info['url']}")
            console.print(f"  Branch: {repo_info['branch']}")
            console.print(f"  Commit: {repo_info['commit']}")
            console.print()

        # Display summary statistics
        files = metadata.get_files()
        console.print(f"Total files synced: {len(files)}")
        # Note: Conflict detection would need to be tracked separately during sync
        console.print(f"Repositories synced: {len(repositories_list)}")
        console.print(f"Synced to: {storage_dir}")
        console.print(f"Metadata: {storage_dir / '.repo-metadata.json'}")
        console.print()

    except ValueError as e:
        # Git errors (invalid URL, auth failures, missing prompts/ directory, validation errors)
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
        prompt-unifier status
    """
    try:
        # Get current working directory
        cwd = Path.cwd()

        # Validate that init has been run
        config_path = cwd / ".prompt-unifier" / "config.yaml"
        if not config_path.exists():
            typer.echo(
                "Error: Configuration not found. Run 'prompt-unifier init' first.",
                err=True,
            )
            raise typer.Exit(code=1)

        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config(config_path)

        if config is None:
            typer.echo(
                "Error: Failed to load configuration. "
                "Config file may be corrupted. Run 'prompt-unifier init' again.",
                err=True,
            )
            raise typer.Exit(code=1)

        # Display status header
        console.print()
        console.print("[bold]Prompt Unifier Status[/bold]")
        console.print("━" * 80)

        # Display storage path
        if config.storage_path:
            storage_dir = Path(config.storage_path).expanduser().resolve()
            console.print(f"Storage: {storage_dir}")
        else:
            # Default storage path
            storage_dir = Path.home() / ".prompt-unifier" / "storage"
            console.print(f"Storage: {storage_dir} [dim](default)[/dim]")

        # Display repository URLs (support multi-repo)
        if config.repos and len(config.repos) > 0:
            console.print(f"Repositories: {len(config.repos)}")
            for idx, repo_config in enumerate(config.repos, 1):
                console.print(f"  {idx}. {repo_config.url}")
                if repo_config.branch:
                    console.print(f"     Branch: {repo_config.branch}")
        else:
            console.print("Repositories: [yellow]Not configured[/yellow]")
            console.print()
            console.print("[dim]Run 'prompt-unifier sync --repo <git-url>' to configure[/dim]")
            console.print()
            return

        # Display last sync information with human-readable timestamp
        if config.last_sync_timestamp:
            human_readable = format_timestamp(config.last_sync_timestamp)
            console.print(f"Last sync: {human_readable}")
        else:
            console.print("Last sync: [yellow]Never[/yellow]")

        # Display repo metadata if available
        if config.repo_metadata and len(config.repo_metadata) > 0:
            console.print(f"Last synced repositories: {len(config.repo_metadata)}")
            for repo_meta in config.repo_metadata:
                console.print(f"  - {repo_meta.get('url', 'Unknown')}")
                if "commit" in repo_meta:
                    console.print(f"    Commit: {repo_meta['commit']}")

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
    base_path: Path | None = DEFAULT_BASE_PATH_OPTION,
    clean: bool = DEFAULT_CLEAN_OPTION,
) -> None:
    """
    Deploys prompts and rules to the specified tool handlers based on configuration and CLI options.

    The base path for deployment is resolved in the following precedence order:
    1. CLI --base-path flag (highest priority)
    2. config.yaml handlers.<handler_name>.base_path
    3. Path.cwd() (default, handler will use this if no base_path specified)

    Environment variables ($HOME, $USER, $PWD) in configured base_path are automatically expanded.
    """
    try:
        # Load configuration
        cwd = Path.cwd()
        config_path = cwd / ".prompt-unifier" / "config.yaml"
        if not config_path.exists():
            typer.echo("Error: Configuration not found. Run 'prompt-unifier init' first.", err=True)
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

        # Helper function to resolve base_path for a specific handler
        def resolve_handler_base_path(handler_name: str) -> Path | None:
            """
            Resolve base_path for a handler following precedence order:
            1. CLI --base-path flag (highest priority)
            2. config.handlers[handler_name].base_path
            3. None (handler will default to Path.cwd())

            Returns:
                Path object or None (None means handler should use default)
            """
            # Priority 1: CLI flag
            if base_path is not None:
                return base_path

            # Priority 2: Config handlers section
            if config.handlers and handler_name in config.handlers:
                handler_config = config.handlers[handler_name]
                if handler_config.base_path:
                    try:
                        # Expand environment variables
                        expanded_path = expand_env_vars(handler_config.base_path)
                        return Path(expanded_path).expanduser().resolve()
                    except ValueError as e:
                        # Missing environment variable
                        console.print(f"[red]Error: {e}[/red]")
                        console.print(
                            f"[yellow]Handler '{handler_name}' configuration contains "
                            f"invalid environment variable in base_path[/yellow]"
                        )
                        raise typer.Exit(code=1) from e

            # Priority 3: None (handler defaults to Path.cwd())
            return None

        # Register handlers with resolved base paths
        registry: ToolHandlerRegistry = ToolHandlerRegistry()

        # For each handler type, resolve and instantiate with appropriate base_path
        # Currently only ContinueToolHandler is implemented
        continue_base_path = resolve_handler_base_path("continue")

        # Instantiate handler with base_path (or None to use default)
        if continue_base_path is not None:
            continue_handler = ContinueToolHandler(base_path=continue_base_path)
        else:
            continue_handler = ContinueToolHandler()

        # Validate tool installation before deployment
        try:
            continue_handler.validate_tool_installation()
        except (PermissionError, OSError) as e:
            console.print("[red]Error: Failed to validate Continue installation[/red]")
            console.print(f"[red]Details: {e}[/red]")
            console.print(
                "[yellow]Suggestion: Check that the base path is accessible and writable[/yellow]"
            )
            raise typer.Exit(code=1) from e

        registry.register(continue_handler)

        all_handlers = registry.get_all_handlers()
        if target_handlers:
            all_handlers = [h for h in all_handlers if h.get_name() in target_handlers]
            if not all_handlers:
                typer.echo(f"Error: No matching handlers found for {target_handlers}.", err=True)
                raise typer.Exit(code=1)

        # Scan for content files (recursive discovery using glob("**/*.md"))
        parser = ContentFileParser()
        content_files = []

        prompts_dir = storage_dir / "prompts"
        if prompts_dir.exists():
            for md_file in prompts_dir.glob("**/*.md"):
                try:
                    parsed_content = parser.parse_file(md_file)
                    content_files.append((parsed_content, "prompt", md_file))
                except Exception as e:
                    console.print(f"[yellow]Warning: Failed to parse {md_file}: {e}[/yellow]")

        rules_dir = storage_dir / "rules"
        if rules_dir.exists():
            for md_file in rules_dir.glob("**/*.md"):
                try:
                    parsed_content = parser.parse_file(md_file)
                    content_files.append((parsed_content, "rule", md_file))
                except Exception as e:
                    console.print(f"[yellow]Warning: Failed to parse {md_file}: {e}[/yellow]")

        # Check for duplicate titles before filtering
        title_to_files: dict[str, list[Path]] = {}
        for parsed_content, _, file_path in content_files:
            title = parsed_content.title
            if title not in title_to_files:
                title_to_files[title] = []
            title_to_files[title].append(file_path)

        # Detect duplicates
        duplicates = {title: files for title, files in title_to_files.items() if len(files) > 1}
        if duplicates:
            console.print("[red]Error: Duplicate titles detected![/red]")
            console.print()
            console.print("The following titles are used in multiple files:")
            console.print()
            for title, files in duplicates.items():
                console.print(f"  Title: [yellow]{title}[/yellow]")
                for file_path in files:
                    console.print(f"    - {file_path}")
                console.print()
            console.print(
                "[yellow]Please ensure each prompt/rule has a unique title "
                "before deploying.[/yellow]"
            )
            raise typer.Exit(code=1)

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
        total_cleaned = 0
        for handler in all_handlers:
            handler_name = handler.get_name()
            console.print(f"Deploying to {handler_name}...")
            handler_deployed = 0
            deployed_filenames: set[str] = set()

            for parsed_content, content_type, file_path in filtered_files:
                try:
                    body = str(parsed_content.content) if hasattr(parsed_content, "content") else ""
                    # Extract original filename to preserve it in deployment
                    source_filename = file_path.name if file_path else None

                    # Calculate relative path from prompts/ or rules/ directory
                    relative_path = None
                    if content_type == "prompt" and prompts_dir:
                        try:
                            relative_path = file_path.parent.relative_to(prompts_dir)
                        except ValueError:
                            # File is not under prompts_dir, use None (root)
                            relative_path = None
                    elif content_type == "rule" and rules_dir:
                        try:
                            relative_path = file_path.parent.relative_to(rules_dir)
                        except ValueError:
                            # File is not under rules_dir, use None (root)
                            relative_path = None

                    if content_type == "prompt":
                        frontmatter_dict = parsed_content.model_dump(exclude={"content"})
                        prompt_content = PromptFrontmatter(**frontmatter_dict)
                        handler.deploy(
                            prompt_content, content_type, body, source_filename, relative_path
                        )
                    elif content_type == "rule":
                        frontmatter_dict = parsed_content.model_dump(exclude={"content"})
                        rule_content = RuleFrontmatter(**frontmatter_dict)
                        handler.deploy(
                            rule_content, content_type, body, source_filename, relative_path
                        )
                    handler_deployed += 1
                    total_deployed += 1
                    # Track deployed filename for cleanup
                    if source_filename:
                        deployed_filenames.add(source_filename)
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

            # Clean orphaned files if requested
            if clean and hasattr(handler, "clean_orphaned_files"):
                console.print(f"Cleaning orphaned files in {handler_name}...")
                try:
                    removed = handler.clean_orphaned_files(deployed_filenames)
                    total_cleaned += removed
                    if removed > 0:
                        console.print(f"  [yellow]Cleaned {removed} orphaned file(s)[/yellow]")
                except Exception as e:
                    console.print(f"  [red]✗[/red] Failed to clean orphaned files: {e}")

            if handler_deployed > 0:
                console.print(
                    f"[green]✓ Deployment to {handler_name} completed "
                    f"({handler_deployed} items).[/green]"
                )
            else:
                console.print(f"[yellow]⚠ No items deployed to {handler_name}.[/yellow]")

        summary_parts = [f"{total_deployed} items deployed to {len(all_handlers)} handler(s)"]
        if clean and total_cleaned > 0:
            summary_parts.append(f"{total_cleaned} orphaned file(s) cleaned")

        console.print(f"\n[bold]Deployment summary:[/bold] {', '.join(summary_parts)}.")

        # Don't exit with error code even if deployment fails partially
        return

    except Exception as e:
        typer.echo(f"Error during deployment: {e}", err=True)
        raise typer.Exit(code=1) from e
