"""Helper functions for CLI commands to reduce cognitive complexity.

This module contains extracted helper functions from the main commands module
to improve maintainability and reduce cognitive complexity scores.
"""

import logging
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table

from prompt_unifier.config.manager import ConfigManager
from prompt_unifier.constants import MD_GLOB_PATTERN
from prompt_unifier.core.content_parser import ContentFileParser
from prompt_unifier.handlers.base_handler import VerificationResult
from prompt_unifier.handlers.continue_handler import ContinueToolHandler
from prompt_unifier.handlers.kilo_code_handler import KiloCodeToolHandler
from prompt_unifier.handlers.registry import ToolHandlerRegistry
from prompt_unifier.models.git_config import GitConfig
from prompt_unifier.models.prompt import PromptFrontmatter
from prompt_unifier.models.rule import RuleFrontmatter
from prompt_unifier.utils.formatting import format_timestamp
from prompt_unifier.utils.path_helpers import expand_env_vars

logger = logging.getLogger(__name__)
console = Console()

# Type aliases
ContentFile = tuple[Any, str, Path]  # (parsed_content, content_type, file_path)


def load_config_or_exit(config_path: Path) -> GitConfig:
    """Load configuration from path or exit with error.

    Args:
        config_path: Path to the config.yaml file.

    Returns:
        Loaded GitConfig object.

    Raises:
        typer.Exit: If configuration cannot be loaded.
    """
    import typer

    config_manager = ConfigManager()
    config = config_manager.load_config(config_path)

    if config is None:
        from rich.console import Console

        Console().print(
            "[red]Error: Failed to load configuration. "
            "Config file may be corrupted. Run 'prompt-unifier init' again.[/red]"
        )
        raise typer.Exit(code=1)

    return config


def scan_content_files(storage_dir: Path) -> list[ContentFile]:
    """Scan storage directory for content files (prompts and rules).

    Args:
        storage_dir: Path to the storage directory.

    Returns:
        List of (parsed_content, content_type, file_path) tuples.
    """
    parser = ContentFileParser()
    content_files: list[ContentFile] = []

    prompts_dir = storage_dir / "prompts"
    if prompts_dir.exists():
        for md_file in prompts_dir.glob(MD_GLOB_PATTERN):
            try:
                parsed_content = parser.parse_file(md_file)
                content_files.append((parsed_content, "prompt", md_file))
            except Exception as e:
                console.print(f"[yellow]Warning: Failed to parse {md_file}: {e}[/yellow]")

    rules_dir = storage_dir / "rules"
    if rules_dir.exists():
        for md_file in rules_dir.glob(MD_GLOB_PATTERN):
            try:
                parsed_content = parser.parse_file(md_file)
                content_files.append((parsed_content, "rule", md_file))
            except Exception as e:
                console.print(f"[yellow]Warning: Failed to parse {md_file}: {e}[/yellow]")

    logger.debug(f"Found {len(content_files)} content files")
    return content_files


def check_duplicate_titles(content_files: list[ContentFile]) -> dict[str, list[Path]]:
    """Check for duplicate titles in content files.

    Args:
        content_files: List of content file tuples.

    Returns:
        Dictionary mapping duplicate titles to their file paths.
    """
    title_to_files: dict[str, list[Path]] = {}
    for parsed_content, _, file_path in content_files:
        title = parsed_content.title
        if title not in title_to_files:
            title_to_files[title] = []
        title_to_files[title].append(file_path)

    return {title: files for title, files in title_to_files.items() if len(files) > 1}


def filter_content_files(
    content_files: list[ContentFile],
    prompt_name: str | None,
    deploy_tags: list[str] | None,
) -> list[ContentFile]:
    """Filter content files by name and tags.

    Args:
        content_files: List of content file tuples.
        prompt_name: Optional name to filter by.
        deploy_tags: Optional list of tags to filter by.

    Returns:
        Filtered list of content file tuples.
    """
    filtered = []
    for parsed_content, content_type, file_path in content_files:
        # Filter by name if specified
        if prompt_name and parsed_content.title != prompt_name:
            continue
        # Filter by tags if specified
        if deploy_tags:
            content_tags = getattr(parsed_content, "tags", []) or []
            if not any(tag in content_tags for tag in deploy_tags):
                continue
        filtered.append((parsed_content, content_type, file_path))

    logger.debug(f"After filtering: {len(filtered)} files to deploy")
    return filtered


def resolve_handler_base_path(
    handler_name: str,
    cli_base_path: Path | None,
    config: GitConfig,
) -> Path | None:
    """Resolve base_path for a handler following precedence order.

    Priority order:
    1. CLI --base-path flag (highest priority)
    2. config.handlers[handler_name].base_path
    3. None (handler will default to Path.cwd())

    Args:
        handler_name: Name of the handler.
        cli_base_path: Base path from CLI flag.
        config: GitConfig object.

    Returns:
        Resolved Path or None.

    Raises:
        typer.Exit: If environment variable expansion fails.
    """
    import typer

    # Priority 1: CLI flag
    if cli_base_path is not None:
        return cli_base_path

    # Priority 2: Config handlers section
    if config.handlers and handler_name in config.handlers:
        handler_config = config.handlers[handler_name]
        if handler_config.base_path:
            try:
                expanded_path = expand_env_vars(handler_config.base_path)
                return Path(expanded_path).expanduser().resolve()
            except ValueError as e:
                console.print(f"[red]Error: {e}[/red]")
                console.print(
                    f"[yellow]Handler '{handler_name}' configuration contains "
                    f"invalid environment variable in base_path[/yellow]"
                )
                raise typer.Exit(code=1) from e

    # Priority 3: None (handler defaults to Path.cwd())
    return None


def _deploy_single_content_item(
    handler: Any,
    parsed_content: Any,
    content_type: str,
    file_path: Path,
    prompts_dir: Path,
    rules_dir: Path,
) -> None:
    """Deploy a single content item to the handler.

    Args:
        handler: The handler to deploy to.
        parsed_content: The parsed content object.
        content_type: Type of content ("prompt" or "rule").
        file_path: Path to the source file.
        prompts_dir: Path to prompts directory.
        rules_dir: Path to rules directory.
    """
    body = str(parsed_content.content) if hasattr(parsed_content, "content") else ""
    source_filename = file_path.name if file_path else None
    relative_path = _calculate_relative_path(file_path, content_type, prompts_dir, rules_dir)

    frontmatter_dict = parsed_content.model_dump(exclude={"content"})

    content_obj: PromptFrontmatter | RuleFrontmatter
    if content_type == "prompt":
        content_obj = PromptFrontmatter(**frontmatter_dict)
    elif content_type == "rule":
        content_obj = RuleFrontmatter(**frontmatter_dict)
    else:
        raise ValueError(f"Unsupported content type: {content_type}")

    handler.deploy(content_obj, content_type, body, source_filename, relative_path)


def _get_deployed_filename(
    handler: Any,
    parsed_content: Any,
    file_path: Path,
    prompts_dir: Path,
    rules_dir: Path,
    content_type: str,
) -> str | None:
    """Get the final deployed filename for a content item.

    Args:
        handler: The handler that deployed the content.
        parsed_content: The parsed content object.
        file_path: Path to the source file.
        prompts_dir: Path to prompts directory.
        rules_dir: Path to rules directory.
        content_type: Type of content.

    Returns:
        Final filename or None.
    """
    source_filename = file_path.name if file_path else None
    relative_path = _calculate_relative_path(file_path, content_type, prompts_dir, rules_dir)

    if isinstance(handler, KiloCodeToolHandler) and source_filename:
        return handler.calculate_deployed_filename(
            source_filename, parsed_content.title, relative_path
        )

    if source_filename:
        if relative_path and str(relative_path) != ".":
            return str(relative_path / source_filename)
        return source_filename

    return None


def _verify_single_deployment(
    handler: Any,
    parsed_content: Any,
    content_type: str,
    final_filename: str | None,
) -> VerificationResult | None:
    """Verify a single deployment if handler supports it.

    Args:
        handler: The handler to verify with.
        parsed_content: The parsed content object.
        content_type: Type of content.
        final_filename: The final deployed filename (can include relative path).
        relative_path: Relative path from content directory
        (unused directly by ContinueToolHandler).

    Returns:
        VerificationResult or None if handler doesn't support verification.
    """
    if not hasattr(handler, "verify_deployment_with_details"):
        return None

    # For ContinueToolHandler, final_filename already includes the relative path
    # For KiloCodeToolHandler, final_filename is just the name (as it flattens dirs)
    # The handler's verify_deployment_with_details will interpret file_name correctly
    # based on its own logic (e.g., using it as full relative path or just a name).
    # No need to pass relative_path separately to the handler's method.
    _file_name_for_verification = final_filename or parsed_content.title
    result: VerificationResult = handler.verify_deployment_with_details(
        content_name=parsed_content.title,
        content_type=content_type,
        file_name=_file_name_for_verification,
    )
    return result


def deploy_content_to_handler(
    handler: Any,
    content_files: list[ContentFile],
    prompts_dir: Path,
    rules_dir: Path,
) -> tuple[int, set[str], list[VerificationResult]]:
    """Deploy content files to a single handler.

    Args:
        handler: The handler to deploy to.
        content_files: List of content file tuples to deploy.
        prompts_dir: Path to prompts directory.
        rules_dir: Path to rules directory.

    Returns:
        Tuple of (deployed_count, deployed_filenames, verification_results).
    """
    handler_deployed = 0
    deployed_filenames: set[str] = set()
    verification_results: list[VerificationResult] = []

    for parsed_content, content_type, file_path in content_files:
        try:
            # Deploy single content item
            _deploy_single_content_item(
                handler, parsed_content, content_type, file_path, prompts_dir, rules_dir
            )
            handler_deployed += 1

            # Get final filename and track it
            final_filename = _get_deployed_filename(
                handler, parsed_content, file_path, prompts_dir, rules_dir, content_type
            )
            if final_filename:
                deployed_filenames.add(final_filename)

            logger.debug(f"Deployed: {parsed_content.title} ({content_type})")

            # Verify deployment if handler supports it
            verification_result = _verify_single_deployment(
                handler,
                parsed_content,
                content_type,
                final_filename,
            )
            if verification_result:
                verification_results.append(verification_result)

        except Exception as e:
            # Create a failed verification result for the summary table
            verification_results.append(
                VerificationResult(
                    file_name=parsed_content.title,
                    content_type=content_type,
                    status="failed",
                    details=str(e),
                )
            )
            logger.error(f"Failed to deploy {parsed_content.title}: {e}")
            _attempt_rollback(handler)

    return handler_deployed, deployed_filenames, verification_results


def _calculate_relative_path(
    file_path: Path,
    content_type: str,
    prompts_dir: Path,
    rules_dir: Path,
) -> Path | None:
    """Calculate relative path from content directory.

    Args:
        file_path: Path to the content file.
        content_type: Type of content ("prompt" or "rule").
        prompts_dir: Path to prompts directory.
        rules_dir: Path to rules directory.

    Returns:
        Relative path or None.
    """
    if content_type == "prompt" and prompts_dir:
        try:
            return file_path.parent.relative_to(prompts_dir)
        except ValueError:
            return None
    elif content_type == "rule" and rules_dir:
        try:
            return file_path.parent.relative_to(rules_dir)
        except ValueError:
            return None
    return None


def _attempt_rollback(handler: Any) -> None:
    """Attempt to rollback handler on deployment failure.

    Args:
        handler: The handler to rollback.
    """
    if hasattr(handler, "rollback"):
        try:
            handler.rollback()
            console.print("  [yellow]Rollback completed.[/yellow]")
        except Exception as rollback_e:
            console.print(f"  [red]Rollback failed: {rollback_e}[/red]")


def display_dry_run_preview(
    filtered_files: list[ContentFile],
    all_handlers: list[Any],
    prompts_dir: Path,
    rules_dir: Path,
) -> None:
    """Display a dry-run preview of what would be deployed.

    Args:
        filtered_files: List of content file tuples.
        all_handlers: List of handler objects.
        prompts_dir: Path to prompts directory.
        rules_dir: Path to rules directory.
    """
    console.print()
    console.print("[bold]Dry-run preview - No files will be modified[/bold]")
    console.print("━" * 80)

    for handler in all_handlers:
        handler_name = handler.get_name()
        console.print(f"\n[bold]Handler: {handler_name}[/bold]")

        # Check target directories
        _warn_missing_handler_dirs(handler)

        # Build and display preview table
        table = _build_preview_table(filtered_files, handler, prompts_dir, rules_dir)
        console.print(table)

    console.print()
    console.print(f"[bold]Total:[/bold] {len(filtered_files)} file(s) would be deployed")
    console.print()


def _warn_missing_handler_dirs(handler: Any) -> None:
    """Warn if handler target directories don't exist.

    Args:
        handler: The handler to check.
    """
    if hasattr(handler, "prompts_dir") and not handler.prompts_dir.exists():
        console.print(
            f"[yellow]Warning: Target prompts directory does not exist: "
            f"{handler.prompts_dir}[/yellow]"
        )
    if hasattr(handler, "rules_dir") and not handler.rules_dir.exists():
        console.print(
            f"[yellow]Warning: Target rules directory does not exist: "
            f"{handler.rules_dir}[/yellow]"
        )


def _build_preview_table(
    filtered_files: list[ContentFile],
    handler: Any,
    prompts_dir: Path,
    rules_dir: Path,
) -> Table:
    """Build a preview table for dry-run mode.

    Args:
        filtered_files: List of content file tuples.
        handler: The handler being previewed.
        prompts_dir: Path to prompts directory.
        rules_dir: Path to rules directory.

    Returns:
        Rich Table object.
    """
    table = Table(show_header=True, header_style="bold")
    table.add_column("Source Path", style="dim")
    table.add_column("Target Path", style="dim")
    table.add_column("Type")
    table.add_column("Title")

    for parsed_content, content_type, file_path in filtered_files:
        source_filename = file_path.name
        relative_path = _calculate_relative_path(file_path, content_type, prompts_dir, rules_dir)

        target_path = _get_target_path(handler, content_type, source_filename, relative_path)

        table.add_row(
            str(file_path),
            str(target_path),
            content_type,
            parsed_content.title,
        )

    return table


def _get_target_path(
    handler: Any,
    content_type: str,
    source_filename: str,
    relative_path: Path | None,
) -> Path:
    """Get the target path for a content file.

    Args:
        handler: The handler.
        content_type: Type of content.
        source_filename: Source filename.
        relative_path: Relative path from content directory.

    Returns:
        Target path.
    """
    if content_type == "prompt" and hasattr(handler, "prompts_dir"):
        base_dir: Path = handler.prompts_dir
    elif content_type == "rule" and hasattr(handler, "rules_dir"):
        base_dir = handler.rules_dir
    else:
        return Path("N/A")

    if relative_path and str(relative_path) != ".":
        return Path(base_dir / relative_path / source_filename)
    return Path(base_dir / source_filename)


def get_content_deployment_status(
    handler: Any,
    content: Any,
    content_type: str,
    file_path: Path,
    prompts_dir: Path,
    rules_dir: Path,
) -> dict[str, Any] | None:
    """Get deployment status for a content item.

    Args:
        handler: The handler to check.
        content: The parsed content.
        content_type: Type of content.
        file_path: Path to the source file.
        prompts_dir: Path to prompts directory.
        rules_dir: Path to rules directory.

    Returns:
        Status dictionary with name, type, handler, status, file_path, details.
    """
    handler_name = handler.get_name()
    relative_path = _calculate_relative_path(file_path, content_type, prompts_dir, rules_dir)

    # Construct target file path
    target_file = _get_target_file_path(handler, content_type, file_path.name, relative_path)

    try:
        # Process content for comparison
        if not hasattr(content, "content"):
            return None

        processed_content = _process_content_for_status(handler, content, content_type)
        if processed_content is None:
            return None

        status = handler.get_deployment_status(
            content_name=content.title,
            content_type=content_type,
            source_content=processed_content,
            source_filename=file_path.name,
            relative_path=relative_path,
        )

        return {
            "name": content.title,
            "type": content_type,
            "handler": handler_name,
            "status": status,
            "file_path": str(target_file),
            "details": "",
        }

    except Exception as e:
        return {
            "name": content.title,
            "type": content_type,
            "handler": handler_name,
            "status": "failed",
            "file_path": str(target_file),
            "details": str(e),
        }


def _get_target_file_path(
    handler: Any,
    content_type: str,
    filename: str,
    relative_path: Path | None,
) -> Path:
    """Get target file path for status checking.

    Args:
        handler: The handler.
        content_type: Type of content.
        filename: The filename.
        relative_path: Relative path from content directory.

    Returns:
        Target file path.
    """
    if content_type == "prompt":
        base_dir: Path = handler.prompts_dir
    elif content_type == "rule":
        base_dir = handler.rules_dir
    else:
        base_dir = Path("")

    if relative_path and str(relative_path) != ".":
        return Path(base_dir / relative_path / filename)
    return Path(base_dir / filename)


def _process_content_for_status(
    handler: Any,
    content: Any,
    content_type: str,
) -> str | None:
    """Process content for status comparison.

    Args:
        handler: The handler.
        content: The parsed content.
        content_type: Type of content.

    Returns:
        Processed content string or None.
    """
    from prompt_unifier.models.prompt import PromptFile
    from prompt_unifier.models.rule import RuleFile

    if content_type == "prompt":
        if isinstance(handler, ContinueToolHandler) and isinstance(content, PromptFile):
            return handler._process_prompt_content(content, content.content)
        return str(content.content)

    elif content_type == "rule":
        if isinstance(handler, ContinueToolHandler) and isinstance(content, RuleFile):
            return handler._process_rule_content(content, content.content)
        return str(content.content)

    return None


def display_status_header(config: GitConfig, storage_dir: Path) -> None:
    """Display status header with storage and repository information.

    Args:
        config: GitConfig object.
        storage_dir: Path to the storage directory.
    """
    console.print()
    console.print("[bold]Prompt Unifier Status[/bold]")
    console.print("━" * 80)

    # Display storage path
    if config.storage_path:
        console.print(f"Storage: {storage_dir}")
    else:
        console.print(f"Storage: {storage_dir} [dim](default)[/dim]")

    # Display repository URLs
    _display_repository_info(config)

    # Display last sync information
    if config.last_sync_timestamp:
        human_readable = format_timestamp(config.last_sync_timestamp)
        console.print(f"Last sync: {human_readable}")
    else:
        console.print("Last sync: [yellow]Never[/yellow]")

    console.print()
    console.print("[bold]Deployment Status[/bold]")
    console.print("━" * 80)


def _get_repo_commit(config: GitConfig, repo_url: str) -> str | None:
    """Get commit hash for a repository from metadata.

    Args:
        config: GitConfig object.
        repo_url: Repository URL to find commit for.

    Returns:
        Commit hash or None if not found.
    """
    if not hasattr(config, "repo_metadata") or not config.repo_metadata:
        return None

    for metadata in config.repo_metadata:
        if metadata.get("url") == repo_url and "commit" in metadata:
            return metadata["commit"]
    return None


def _display_single_repo(config: GitConfig, idx: int, repo_config: Any) -> None:
    """Display information for a single repository.

    Args:
        config: GitConfig object.
        idx: Repository index.
        repo_config: Repository configuration.
    """
    console.print(f"  {idx}. {repo_config.url}")
    if repo_config.branch:
        console.print(f"     Branch: {repo_config.branch}")

    commit = _get_repo_commit(config, repo_config.url)
    if commit:
        console.print(f"     Commit: {commit}")


def _display_repository_info(config: GitConfig) -> None:
    """Display repository information from config.

    Args:
        config: GitConfig object.
    """
    if config.repos and len(config.repos) > 0:
        console.print(f"Repositories: {len(config.repos)}")
        for idx, repo_config in enumerate(config.repos, 1):
            _display_single_repo(config, idx, repo_config)
    else:
        console.print("Repositories: [yellow]Not configured[/yellow]")
        console.print()
        console.print("[dim]Run 'prompt-unifier sync --repo <git-url>' to configure[/dim]")
        console.print()


def initialize_status_handlers(config: GitConfig) -> list[Any]:
    """Initialize handlers for status checking.

    Args:
        config: GitConfig object.

    Returns:
        List of active handler objects.
    """
    registry = ToolHandlerRegistry()
    registry.register(ContinueToolHandler())

    target_handlers = config.target_handlers or ["continue"]
    handlers = registry.get_all_handlers()
    return [h for h in handlers if h.get_name() in target_handlers]


def check_all_content_status(
    active_handlers: list[Any],
    content_files: list[ContentFile],
    prompts_dir: Path,
    rules_dir: Path,
) -> list[dict[str, Any]]:
    """Check deployment status for all content files against handlers.

    Args:
        active_handlers: List of handler objects to check against.
        content_files: List of content file tuples.
        prompts_dir: Path to prompts directory.
        rules_dir: Path to rules directory.

    Returns:
        List of status dictionaries.
    """
    status_items: list[dict[str, Any]] = []

    with console.status("[bold green]Checking deployment status...[/bold green]"):
        for handler in active_handlers:
            for content, content_type, file_path in content_files:
                status_item = get_content_deployment_status(
                    handler, content, content_type, file_path, prompts_dir, rules_dir
                )
                if status_item:
                    status_items.append(status_item)

    return status_items


def determine_storage_dir(
    storage_path: str | None,
    config: GitConfig | None,
    default_path: Path | None = None,
) -> Path:
    """Determine the storage directory from various sources.

    Priority order:
    1. Explicit storage_path parameter
    2. Config storage_path
    3. Default path

    Args:
        storage_path: Explicit storage path string.
        config: GitConfig object (may be None).
        default_path: Default path to use if others not available.

    Returns:
        Resolved Path to storage directory.
    """
    if storage_path and isinstance(storage_path, str):
        return Path(storage_path).expanduser().resolve()
    elif config and config.storage_path:
        return Path(config.storage_path).expanduser().resolve()
    elif default_path:
        return default_path
    else:
        return Path.home() / ".prompt-unifier" / "storage"


def create_directory_with_tracking(
    dir_path: Path,
    created_items: list[str],
    existing_items: list[str],
) -> None:
    """Create a directory if it doesn't exist and track the result.

    Args:
        dir_path: Path to the directory to create.
        created_items: List to append created message to.
        existing_items: List to append existing message to.
    """
    if not dir_path.exists():
        dir_path.mkdir(parents=True, exist_ok=True)
        created_items.append(f"Created: {dir_path}")
        logger.info(f"Created directory: {dir_path}")
    else:
        existing_items.append(f"Exists: {dir_path}")


def determine_repo_configs(
    cli_repos: list[str] | None,
    config: GitConfig,
) -> list[Any]:
    """Determine repository configurations from CLI or config.

    Args:
        cli_repos: Repository URLs from CLI.
        config: GitConfig object.

    Returns:
        List of RepositoryConfig objects.

    Raises:
        typer.Exit: If no repositories are configured.
    """
    import typer

    from prompt_unifier.models.git_config import RepositoryConfig

    if cli_repos is not None and len(cli_repos) > 0:
        repo_configs = [RepositoryConfig(url=repo_url) for repo_url in cli_repos]
        logger.info(f"Using {len(repo_configs)} repositories from CLI")
        return repo_configs
    elif config.repos is not None and len(config.repos) > 0:
        logger.info(f"Using {len(config.repos)} repositories from config")
        return config.repos
    else:
        console.print(
            "[red]Error: No repository URLs configured. "
            "Use --repo flag to specify repositories.[/red]"
        )
        raise typer.Exit(code=1)


def setup_continue_handler(
    base_path: Path | None,
    config: GitConfig,
) -> ContinueToolHandler:
    """Setup and validate Continue handler with resolved base path.

    Args:
        base_path: CLI base path override.
        config: GitConfig object.

    Returns:
        Validated ContinueToolHandler instance.

    Raises:
        typer.Exit: If handler validation fails.
    """
    import typer

    continue_base_path = resolve_handler_base_path("continue", base_path, config)

    if continue_base_path is not None:
        handler = ContinueToolHandler(base_path=continue_base_path)
    else:
        handler = ContinueToolHandler()

    try:
        handler.validate_tool_installation()
    except OSError as e:
        console.print("[red]Error: Failed to validate Continue installation[/red]")
        console.print(f"[red]Details: {e}[/red]")
        console.print(
            "[yellow]Suggestion: Check that the base path is accessible and writable[/yellow]"
        )
        raise typer.Exit(code=1) from e

    return handler


def display_duplicate_titles_error(duplicates: dict[str, list[Path]]) -> None:
    """Display error message for duplicate titles.

    Args:
        duplicates: Dictionary mapping titles to list of file paths.
    """
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
        "[yellow]Please ensure each prompt/rule has a unique title before deploying.[/yellow]"
    )


def deploy_to_single_handler(
    handler: Any,
    filtered_files: list[ContentFile],
    prompts_dir: Path,
    rules_dir: Path,
    clean: bool,
) -> tuple[int, int]:
    """Deploy content to a single handler and handle cleanup.

    Args:
        handler: Tool handler to deploy to.
        filtered_files: List of filtered content files.
        prompts_dir: Path to prompts directory.
        rules_dir: Path to rules directory.
        clean: Whether to clean orphaned files.

    Returns:
        Tuple of (deployed_count, cleaned_count).
    """
    handler_name = handler.get_name()
    logger.info(f"Deploying to handler: {handler_name}")

    # Deploy content using helper
    handler_deployed, deployed_filenames, verification_results = deploy_content_to_handler(
        handler, filtered_files, prompts_dir, rules_dir
    )

    # Clean orphaned files if requested
    cleaned_count = 0
    if clean and hasattr(handler, "clean_orphaned_files"):
        removed_results = _clean_orphaned_files(handler, handler_name, deployed_filenames)
        cleaned_count = len(removed_results)
        verification_results.extend(removed_results)

    # Display verification report
    if verification_results and hasattr(handler, "display_verification_report"):
        handler.display_verification_report(verification_results)

    return handler_deployed, cleaned_count


def _clean_orphaned_files(
    handler: Any,
    handler_name: str,
    deployed_filenames: set[str],
) -> list[VerificationResult]:
    """Clean orphaned files from handler.

    Args:
        handler: Tool handler.
        handler_name: Name of the handler.
        deployed_filenames: Set of deployed filenames.

    Returns:
        List of VerificationResult objects for removed files.
    """
    console.print(f"Cleaning orphaned files in {handler_name}...")
    try:
        removed_results: list[VerificationResult] = handler.clean_orphaned_files(deployed_filenames)
        removed_count = len(removed_results)
        if removed_count > 0:
            console.print(f"  [yellow]Cleaned {removed_count} orphaned file(s)[/yellow]")
            logger.info(f"Cleaned {removed_count} orphaned files")
        return removed_results
    except Exception as e:
        console.print(f"  [red]✗[/red] Failed to clean orphaned files: {e}")
        return []


def _display_handler_completion(handler_name: str, deployed_count: int) -> None:
    """Display handler completion message.

    Args:
        handler_name: Name of the handler.
        deployed_count: Number of items deployed.
    """
    if deployed_count > 0:
        console.print(
            f"[green]✓ Deployment to {handler_name} completed ({deployed_count} items).[/green]"
        )
    else:
        console.print(f"[yellow]⚠ No items deployed to {handler_name}.[/yellow]")


def resolve_validation_directory(
    directory: Path | None,
    config_dir: str,
    config_file: str,
) -> Path:
    """Resolve the directory to validate.

    Args:
        directory: User-provided directory or None.
        config_dir: Name of config directory.
        config_file: Name of config file.

    Returns:
        Resolved directory path.

    Raises:
        typer.Exit: If directory cannot be resolved.
    """
    import typer

    if directory is not None:
        return directory

    cwd = Path.cwd()
    config_path = cwd / config_dir / config_file

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

    resolved = Path(config.storage_path).expanduser().resolve()
    logger.info(f"Using storage path: {resolved}")
    return resolved


def determine_validation_targets(
    directory: Path,
    content_type: str,
) -> list[Path]:
    """Determine which directories to validate based on content type.

    Args:
        directory: Base directory.
        content_type: Type of content to validate ('all', 'prompts', or 'rules').

    Returns:
        List of directories to validate.

    Raises:
        typer.Exit: If content_type is invalid or directories don't exist.
    """
    import typer

    if content_type not in ("all", "prompts", "rules"):
        typer.echo(
            f"Error: Invalid --type '{content_type}'. Must be 'all', 'prompts', or 'rules'",
            err=True,
        )
        raise typer.Exit(code=1)

    logger.debug(f"Validating content type: {content_type}")

    # Check if the provided directory is part of a prompts/ or rules/ hierarchy
    # We check if 'prompts' or 'rules' is in the path parts
    path_parts = [p.lower() for p in directory.parts]
    in_prompts = "prompts" in path_parts
    in_rules = "rules" in path_parts

    # If we are already inside a specific hierarchy, validate this directory directly
    if in_prompts:
        if content_type == "rules":
            typer.echo(
                f"Error: Target '{directory}' is in a prompts hierarchy "
                "but --type rules was specified",
                err=True,
            )
            raise typer.Exit(code=1)
        return [directory]

    if in_rules:
        if content_type == "prompts":
            typer.echo(
                f"Error: Target '{directory}' is in a rules hierarchy "
                "but --type prompts was specified",
                err=True,
            )
            raise typer.Exit(code=1)
        return [directory]

    # Standard discovery behavior: look for subdirectories
    if content_type == "prompts":
        target_dir = directory / "prompts"
        if not target_dir.exists():
            typer.echo(f"Error: Prompts directory '{target_dir}' does not exist", err=True)
            raise typer.Exit(code=1)
        return [target_dir]

    if content_type == "rules":
        target_dir = directory / "rules"
        if not target_dir.exists():
            typer.echo(f"Error: Rules directory '{target_dir}' does not exist", err=True)
            raise typer.Exit(code=1)
        return [target_dir]

    # Discovery mode for 'all': find both prompts and rules subdirectories
    directories: list[Path] = []
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

    return directories


def format_functional_test_results(results: list[Any]) -> Table:
    """Format functional test results as a Rich table.

    Args:
        results: List of FunctionalTestResult objects

    Returns:
        Rich Table object with formatted results
    """
    from prompt_unifier.models.functional_test import FunctionalTestResult

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Scenario", style="cyan", no_wrap=False)
    table.add_column("Status", justify="center")
    table.add_column("Passed", justify="right")
    table.add_column("Failed", justify="right")
    table.add_column("Details", style="dim", no_wrap=False)

    for result in results:
        if not isinstance(result, FunctionalTestResult):
            continue

        # Format status with color
        status_style = "green" if result.status == "PASS" else "bold red"
        status_display = f"[{status_style}]{result.status.upper()}[/{status_style}]"

        # Format details (show first failure if any)
        details = ""
        if result.failures and len(result.failures) > 0:
            first_failure = result.failures[0]
            details = (
                f"{first_failure.get('type', 'unknown')}: "
                f"{first_failure.get('error_message', 'Failed')}"
            )

        table.add_row(
            result.scenario_description,
            status_display,
            str(result.passed_count),
            str(result.failed_count),
            details,
        )

    return table


def create_functional_test_summary(results: list[Any]) -> str:
    """Create summary panel text for functional test results.

    Args:
        results: List of FunctionalTestResult objects

    Returns:
        Summary text for display in panel
    """
    from prompt_unifier.models.functional_test import FunctionalTestResult

    total_scenarios = len(results)
    passed_scenarios = sum(
        1 for r in results if isinstance(r, FunctionalTestResult) and r.status == "PASS"
    )
    failed_scenarios = total_scenarios - passed_scenarios
    pass_rate = (passed_scenarios / total_scenarios * 100) if total_scenarios > 0 else 0

    summary_parts = [
        f"Total scenarios: {total_scenarios}",
        f"[green]Passed: {passed_scenarios}[/green]",
        f"[red]Failed: {failed_scenarios}[/red]",
        f"Pass rate: {pass_rate:.1f}%",
    ]

    return "\n".join(summary_parts)


def format_assertion_failures(result: Any) -> str:
    """Format detailed failure information for a test result.

    Args:
        result: FunctionalTestResult object

    Returns:
        Formatted failure details string
    """
    from prompt_unifier.models.functional_test import FunctionalTestResult

    if not isinstance(result, FunctionalTestResult) or not result.failures:
        return ""

    lines = []
    for failure in result.failures:
        lines.append(
            f"  • {failure.get('type', 'unknown')}: {failure.get('error_message', 'Failed')}"
        )
        lines.append(f"    Expected: {failure.get('expected', 'N/A')}")
        excerpt = failure.get("actual_excerpt", "")
        if excerpt:
            lines.append(f"    Actual (excerpt): {excerpt}")

    return "\n".join(lines)
