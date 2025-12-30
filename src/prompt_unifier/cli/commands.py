"""CLI commands for the Prompt Unifier.

This module contains the CLI commands implemented using Typer,
including the validate command for prompt file validation and
Git integration commands (init, sync, status).
"""

import logging
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from prompt_unifier.cli.helpers import (
    check_all_content_status,
    check_duplicate_titles,
    create_directory_with_tracking,
    deploy_to_single_handler,
    determine_repo_configs,
    determine_storage_dir,
    determine_validation_targets,
    display_dry_run_preview,
    display_duplicate_titles_error,
    display_status_header,
    filter_content_files,
    initialize_status_handlers,
    resolve_validation_directory,
    scan_content_files,
    setup_continue_handler,
)
from prompt_unifier.config.manager import ConfigManager
from prompt_unifier.constants import CONFIG_DIR, CONFIG_FILE, ERROR_CONFIG_NOT_FOUND
from prompt_unifier.core.batch_validator import BatchValidator
from prompt_unifier.core.content_parser import ContentFileParser
from prompt_unifier.git.service import GitService
from prompt_unifier.handlers.kilo_code_handler import KiloCodeToolHandler
from prompt_unifier.handlers.registry import ToolHandlerRegistry
from prompt_unifier.models.git_config import GitConfig
from prompt_unifier.output.json_formatter import JSONFormatter
from prompt_unifier.output.rich_formatter import RichFormatter
from prompt_unifier.output.rich_table_formatter import RichTableFormatter

# Initialize Rich Console for formatted output
console = Console()

# Get logger for this module
logger = logging.getLogger(__name__)

# Constants for default values to avoid function calls in argument defaults
DEFAULT_PROMPT_NAME = None
DEFAULT_TAGS = None
DEFAULT_HANDLERS = None
DEFAULT_BASE_PATH = None
DEFAULT_CLEAN = False
DEFAULT_DRY_RUN = False
DEFAULT_INIT_STORAGE_PATH = None
DEFAULT_SYNC_REPO = None
DEFAULT_SYNC_STORAGE_PATH = None
DEFAULT_VALIDATE_DIRECTORY = None
DEFAULT_VALIDATE_JSON_OUTPUT = False
DEFAULT_VALIDATE_CONTENT_TYPE = "all"
DEFAULT_VALIDATE_SCAFF = True
DEFAULT_LIST_TOOL = None
DEFAULT_LIST_TAG = None
DEFAULT_LIST_SORT = "name"

DEFAULT_PROMPT_NAME_OPTION = typer.Option(
    DEFAULT_PROMPT_NAME,
    "--name",
    help=("Deploy only a specific prompt or rule by name (defaults to all content)"),
)

DEFAULT_TAGS_OPTION = typer.Option(
    DEFAULT_TAGS,
    "--tags",
    help=("Filter content to deploy by tags (comma-separated, defaults to no filter)"),
)

DEFAULT_HANDLERS_OPTION = typer.Option(
    None,
    "--handlers",
    help=(
        "Specify target handlers for deployment (comma-separated, "
        "defaults to 'continue'). Supported handlers: 'continue', 'kilocode'."
    ),
)

DEFAULT_BASE_PATH_OPTION = typer.Option(
    DEFAULT_BASE_PATH,
    "--base-path",
    help=(
        "Custom base path for handler deployment (overrides config.yaml, "
        "defaults to current working directory)"
    ),
)
DEFAULT_CLEAN_OPTION = typer.Option(
    DEFAULT_CLEAN,
    "--clean",
    help="Remove orphaned prompts/rules in destination (creates backups, default: False)",
)
DEFAULT_DRY_RUN_OPTION = typer.Option(
    DEFAULT_DRY_RUN,
    "--dry-run",
    help="Preview deployment without executing any file operations (default: False)",
)
DEFAULT_INIT_STORAGE_PATH_OPTION = typer.Option(
    DEFAULT_INIT_STORAGE_PATH,
    "--storage-path",
    help="Optional custom storage directory path (defaults to ~/.prompt-unifier/storage/)",
)
DEFAULT_SYNC_REPOS_OPTION = typer.Option(
    DEFAULT_SYNC_REPO, "--repo", help="Git repository URL (can be specified multiple times)"
)
DEFAULT_SYNC_STORAGE_PATH_OPTION = typer.Option(
    DEFAULT_SYNC_STORAGE_PATH,
    "--storage-path",
    help=(
        "Override storage path for this sync (defaults to config value or "
        "~/.prompt-unifier/storage/)"
    ),
)
DEFAULT_VALIDATE_DIRECTORY_ARG = typer.Argument(
    DEFAULT_VALIDATE_DIRECTORY, help="Directory to validate (defaults to synchronized storage)"
)
DEFAULT_VALIDATE_JSON_OPTION = typer.Option(
    DEFAULT_VALIDATE_JSON_OUTPUT,
    "--json",
    help="Output validation results in JSON format (default: False)",
)
DEFAULT_VALIDATE_CONTENT_TYPE_OPTION = typer.Option(
    DEFAULT_VALIDATE_CONTENT_TYPE,
    "--type",
    "-t",
    help="Content type to validate: all, prompts, or rules [default: all]",
)
DEFAULT_VALIDATE_SCAFF_OPTION = typer.Option(
    True,
    "--scaff/--no-scaff",
    help="Enable/disable SCAFF methodology validation (default: enabled)",
)
DEFAULT_VALIDATE_TEST = False
DEFAULT_VALIDATE_TEST_OPTION = typer.Option(
    DEFAULT_VALIDATE_TEST,
    "--test",
    help="Run functional tests from .test.yaml file (skips SCAFF validation)",
)
DEFAULT_LIST_TOOL_OPTION = typer.Option(
    DEFAULT_LIST_TOOL,
    "--tool",
    "-t",
    help="Filter content by target tool handler (default: no filter)",
)
DEFAULT_LIST_TAG_OPTION = typer.Option(
    DEFAULT_LIST_TAG, "--tag", help="Filter content by a specific tag (default: no filter)"
)
DEFAULT_LIST_SORT_OPTION = typer.Option(
    DEFAULT_LIST_SORT, "--sort", "-s", help="Sort content by 'name' (default) or 'date'"
)
DEFAULT_TEST_DIRECTORY_ARG = typer.Argument(
    None, help="File or directory to test (defaults to synchronized storage)"
)


def _validate_with_json_output(
    validator: Any, directories: list[Path], scaff_enabled: bool
) -> None:
    """Validate directories and output results as JSON."""
    json_formatter = JSONFormatter()
    all_success = True

    for dir_path in directories:
        # Automatically disable SCAFF for rules directories as it's designed for prompts
        current_scaff_enabled = scaff_enabled
        if dir_path.name == "rules":
            current_scaff_enabled = False
            logger.debug(f"Disabling SCAFF validation for rules directory: {dir_path}")

        logger.debug(f"Validating directory: {dir_path}")
        summary = validator.validate_directory(dir_path, scaff_enabled=current_scaff_enabled)
        logger.info(f"Validated {summary.total_files} files in {dir_path}")
        json_output_str = json_formatter.format_summary(summary, dir_path)
        typer.echo(json_output_str)

        if not summary.success:
            all_success = False

    if not all_success:
        raise typer.Exit(code=1)


def _display_directory_results(
    console: Console,
    dir_path: Path,
    is_rules: bool,
    summary: Any,
    table_formatter: RichTableFormatter,
    rich_formatter: RichFormatter,
    current_scaff_enabled: bool,
) -> None:
    """Display validation results for a single directory."""
    # Display header with prominent title
    section_title = "RULES" if is_rules else "PROMPTS"
    header_style = "bold blue" if is_rules else "bold magenta"
    border_style = "blue" if is_rules else "magenta"

    console.print()
    console.print(
        Panel(
            f"[dim]Directory: {dir_path}[/dim]",
            title=f"[{header_style}] {section_title} [/{header_style}]",
            border_style=border_style,
            expand=False,
            padding=(1, 2),
        )
    )
    console.print()

    # Display table
    table = table_formatter.format_validation_table(summary, show_scaff=current_scaff_enabled)
    console.print(table)
    console.print()

    # Display details for files with issues
    has_issues = any(r.errors or r.warnings for r in summary.results)
    if has_issues:
        console.print("[bold]Issue Details:[/bold]")
        console.print()
        for result in summary.results:
            if result.errors or result.warnings:
                # Use RichFormatter's internal method to display details
                # pylint: disable=protected-access
                rich_formatter._display_file_result(result)

    # Display summary statistics
    console.print("━" * 80)
    console.print("[bold]Summary:[/bold]")
    console.print(f"  Total files: {summary.total_files}")
    console.print(f"  Passed: [green]{summary.passed}[/green]")
    console.print(f"  Failed: [red]{summary.failed}[/red]")
    console.print(f"  Errors: [red]{summary.error_count}[/red]")
    console.print(f"  Warnings: [yellow]{summary.warning_count}[/yellow]")
    console.print()

    if not summary.success:
        console.print("[bold red]Validation FAILED ✗[/bold red]")
    else:
        console.print("[bold green]Validation PASSED ✓[/bold green]")

    console.print()


def _validate_with_rich_output(
    validator: Any, directories: list[Path], scaff_enabled: bool
) -> None:
    """Validate directories and output results with Rich formatting."""
    rich_formatter = RichFormatter()
    table_formatter = RichTableFormatter()
    all_success = True

    for dir_path in directories:
        # Determine if this is a rules directory
        is_rules = dir_path.name == "rules"
        current_scaff_enabled = scaff_enabled and not is_rules

        if is_rules:
            logger.debug(f"Disabling SCAFF validation for rules directory: {dir_path}")

        logger.debug(f"Validating directory: {dir_path}")
        summary = validator.validate_directory(dir_path, scaff_enabled=current_scaff_enabled)
        logger.info(
            f"Validated {summary.total_files} files: "
            f"{summary.passed} passed, {summary.failed} failed"
        )

        _display_directory_results(
            console,
            dir_path,
            is_rules,
            summary,
            table_formatter,
            rich_formatter,
            current_scaff_enabled,
        )

        if not summary.success:
            all_success = False

    if not all_success:
        raise typer.Exit(code=1)


def _resolve_prompt_path_and_title(test_file_path: Path) -> tuple[Path, str]:
    """Resolve corresponding prompt file path and title for a test file."""
    # Standard: file.md -> file.md.test.yaml
    prompt_filename = test_file_path.name.replace(".test.yaml", "")
    prompt_file_path = test_file_path.parent / prompt_filename

    # Try to resolve prompt title from frontmatter
    prompt_title = prompt_filename
    if not prompt_file_path.exists() and not prompt_filename.endswith(".md"):
        alt_path = test_file_path.parent / f"{prompt_filename}.md"
        if alt_path.exists():
            prompt_file_path = alt_path

    if prompt_file_path.exists():
        try:
            cf_parser = ContentFileParser()
            parsed_prompt = cf_parser.parse_file(prompt_file_path)
            prompt_title = parsed_prompt.title
        except Exception as e:
            logger.debug(f"Could not parse prompt title for {prompt_file_path}: {e}")

    return prompt_file_path, prompt_title


def _validate_ai_connection(executor: Any, provider: str) -> None:
    """Validate connection to AI provider and print troubleshooting tips on failure."""
    from prompt_unifier.ai.executor import AIExecutionError

    console.print("[dim]Validating connection to AI provider...[/dim]")
    try:
        executor.validate_connection(provider)
        console.print("[green]✓ Connection validated successfully[/green]\n")
    except AIExecutionError as e:
        console.print(f"[red]✗ Connection validation failed: {e}[/red]\n")
        # Provide helpful troubleshooting tips based on error type
        error_str = str(e).lower()
        if "api_key" in error_str or "authentication" in error_str:
            console.print("[yellow]Troubleshooting:[/yellow]")
            console.print("  • Check that your API key is set in .env file")
            console.print("  • Example: OPENAI_API_KEY=sk-your-key-here")
            console.print("  • Or export as environment variable:")
            console.print("    export OPENAI_API_KEY=your-key")
        elif "model" in error_str or "not found" in error_str:
            console.print("[yellow]Troubleshooting:[/yellow]")
            console.print(f"  • Model '{provider}' may not be available")
            console.print("  • Check supported models: https://docs.litellm.ai/docs/providers")
        elif "timeout" in error_str or "connection" in error_str:
            console.print("[yellow]Troubleshooting:[/yellow]")
            console.print("  • Check your internet connection")
            console.print("  • Verify firewall settings")
            if provider and "ollama" in provider:
                console.print("  • Ensure Ollama is running: ollama serve")
        raise


def _run_single_functional_test(
    test_file_path: Path,
    global_provider: str | None = None,
    executor: Any | None = None,
) -> dict[str, Any]:
    """Run functional tests for a single test file."""
    from prompt_unifier.cli.helpers import (
        create_functional_test_summary,
        format_assertion_failures,
        format_functional_test_results,
    )
    from prompt_unifier.core.functional_test_parser import FunctionalTestParser
    from prompt_unifier.core.functional_validator import FunctionalValidator

    prompt_file_path, prompt_title = _resolve_prompt_path_and_title(test_file_path)

    console.print(f"\n[bold underline]Testing: {prompt_title}[/bold underline]")
    if prompt_file_path.exists():
        console.print(f"[dim]Prompt file: {prompt_file_path}[/dim]")
    else:
        console.print(f"[yellow]Warning: Prompt file not found: {prompt_file_path}[/yellow]")

    # Parse test file
    parser = FunctionalTestParser(test_file_path)
    test_spec = parser.parse()

    if test_spec is None:
        console.print(f"[yellow]Warning: Failed to parse test file: {test_file_path}[/yellow]")
        return {
            "success": False,
            "name": prompt_title,
            "total": 0,
            "passed": 0,
            "failed": 0,
            "pass_rate": 0,
            "path": str(test_file_path.absolute()),
        }

    provider = test_spec.provider or global_provider
    if not provider:
        console.print("[red]Error: No AI provider specified.[/red]")
        return {
            "success": False,
            "name": prompt_title,
            "total": 0,
            "passed": 0,
            "failed": 0,
            "pass_rate": 0,
            "path": str(test_file_path.absolute()),
        }

    console.print(f"[cyan]Running functional tests with AI provider: {provider}[/cyan]")

    try:
        from prompt_unifier.ai.executor import AIExecutor

        if executor is None:
            executor = AIExecutor()

        # Only validate connection if this is NOT the global provider (already validated)
        if provider != global_provider:
            _validate_ai_connection(executor, provider)
    except Exception:
        return {
            "success": False,
            "name": prompt_title,
            "total": 0,
            "passed": 0,
            "failed": 0,
            "pass_rate": 0,
            "path": str(test_file_path.absolute()),
        }

    # Execute functional tests with AI
    func_validator = FunctionalValidator(test_spec)
    results = func_validator.validate_with_ai(
        prompt_file=prompt_file_path, executor=executor, provider=provider
    )

    # Display results
    console.print("[bold]Functional Test Results[/bold]\n" + "━" * 80)
    console.print(format_functional_test_results(results))
    console.print()

    # Determine status and summary
    all_passed = all(r.status == "PASS" for r in results)
    total = len(results)
    passed = sum(1 for r in results if r.status == "PASS")
    rate = (passed / total * 100) if total > 0 else 0

    summary_style = "green" if all_passed else "red"
    console.print(
        Panel(
            create_functional_test_summary(results),
            title=f"[{summary_style}]Summary[/{summary_style}]",
            border_style=summary_style,
        )
    )
    console.print()

    if not all_passed:
        console.print("[bold red]Failure Details:[/bold red]")
        for result in results:
            if result.status == "FAIL":
                console.print(f"\n[bold]{result.scenario_description}:[/bold]")
                console.print(format_assertion_failures(result))
        console.print()

    return {
        "success": all_passed,
        "name": prompt_title,
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": rate,
        "path": str(test_file_path.absolute()),
    }


def _discover_functional_test_files(targets: list[Path] | None) -> list[Path]:
    """Discover all .test.yaml files based on input targets or storage."""
    from prompt_unifier.core.functional_test_parser import FunctionalTestParser

    if not targets:
        # Discovery mode in default locations
        search_dirs: list[Path] = []
        try:
            search_dirs.append(resolve_validation_directory(None, CONFIG_DIR, CONFIG_FILE))
        except Exception as e:
            logger.debug(f"Could not resolve storage directory: {e}")
        cwd = Path.cwd()
        if cwd not in search_dirs:
            search_dirs.append(cwd)

        test_files = []
        for s_dir in search_dirs:
            logger.debug(f"Scanning for functional tests in: {s_dir}")
            found = list(s_dir.glob("**/*.test.yaml"))
            if found:
                logger.info(f"Found {len(found)} test file(s) in {s_dir}")
                test_files.extend(found)

        if not test_files:
            search_paths_str = ", ".join(str(d) for d in search_dirs)
            console.print(f"[yellow]No test files found in: {search_paths_str}[/yellow]")
            raise typer.Exit(code=1)

        return sorted(set(test_files))

    # Handle explicit targets (files or directories)
    test_files = []
    for target in targets:
        if target.is_file():
            if target.name.endswith(".test.yaml"):
                test_files.append(target)
            else:
                test_file_path = FunctionalTestParser.get_test_file_path(target)
                if test_file_path.exists():
                    test_files.append(test_file_path)
                else:
                    console.print(f"[yellow]Warning: Test file not found for: {target}[/yellow]")
        elif target.is_dir():
            logger.debug(f"Scanning for functional tests in: {target}")
            found = list(target.glob("**/*.test.yaml"))
            if found:
                test_files.extend(found)
            else:
                console.print(f"[yellow]Warning: No test files found in: {target}[/yellow]")

    if not test_files:
        console.print("[red]Error: No test files found for provided targets.[/red]")
        raise typer.Exit(code=1)

    return sorted(set(test_files))


def _get_global_ai_provider() -> str | None:
    """Load global AI provider from configuration or environment."""
    import os

    # 1. Try to load from configuration file
    try:
        config_path = Path.cwd() / CONFIG_DIR / CONFIG_FILE
        if config_path.exists():
            config_manager = ConfigManager()
            config = config_manager.load_config(config_path)
            if config and config.ai_provider:
                logger.info(f"Using AI provider from config: {config.ai_provider}")
                return config.ai_provider
    except Exception as e:
        logger.debug(f"Could not load AI provider from config: {e}")

    # 2. Fallback to environment variable
    env_provider = os.getenv("DEFAULT_LLM_MODEL")
    if env_provider:
        logger.info(f"Using AI provider from environment: {env_provider}")
        return env_provider

    return None


def validate(
    directory: Path | None = DEFAULT_VALIDATE_DIRECTORY_ARG,
    json_output: bool = DEFAULT_VALIDATE_JSON_OPTION,
    content_type: str = DEFAULT_VALIDATE_CONTENT_TYPE_OPTION,
    scaff: bool = DEFAULT_VALIDATE_SCAFF_OPTION,
    test: bool = False,
) -> None:
    """Validate prompt and rule files.

    Validates .md files against the format specification. Checks for
    required fields, valid YAML frontmatter, proper separator format,
    and UTF-8 encoding.

    Additionally, runs SCAFF methodology validation by default to assess
    prompt quality (Specific, Contextual, Actionable, Formatted, Focused).
    Use --no-scaff to disable SCAFF validation.

    If no directory/file is provided, validates files in the synchronized storage
    location (requires 'init' to have been run).

    Exit codes:
        0: Validation passed (warnings are acceptable)
        1: Validation failed (errors found)

    Examples:
        # Validate everything (prompts + rules) with SCAFF
        prompt-unifier validate

        # Validate specific file
        prompt-unifier validate prompts/my-prompt.md

        # Validate without SCAFF methodology checks
        prompt-unifier validate --no-scaff

        # Validate specific directory
        prompt-unifier validate ./prompts

        # Validate with JSON output
        prompt-unifier validate ./prompts --json
    """
    if test:
        return test_prompts([directory] if directory else None, provider=None)

    logger.info("Starting validation")

    # 1. Resolve target (file or directory)
    # If not provided, resolve_validation_directory will use config or fail
    try:
        target = resolve_validation_directory(directory, CONFIG_DIR, CONFIG_FILE)
    except typer.Exit:
        # If no config and no directory provided, default to current dir if directory was None
        if directory is None:
            target = Path.cwd()
        else:
            raise

    # 2. Handle single file validation
    if target.is_file():
        if target.suffix.lower() != ".md":
            typer.echo(
                f"Error: Neither prompts/ nor rules/ directory exists in '{target}'",
                err=True,
            )
            raise typer.Exit(code=1)

        logger.info(f"Validating single file: {target}")
        validator = BatchValidator()
        # validate_directory works because it uses FileScanner which handles single files

        # Determine if SCAFF should be enabled (disabled for rules by naming convention)
        is_rule = "rules" in target.parts
        current_scaff_enabled = scaff and not is_rule

        summary = validator.validate_directory(target, scaff_enabled=current_scaff_enabled)

        if json_output:
            json_formatter = JSONFormatter()
            typer.echo(json_formatter.format_summary(summary, target.parent))
        else:
            rich_formatter = RichFormatter()
            table_formatter = RichTableFormatter()
            _display_directory_results(
                console,
                target.parent,
                is_rule,
                summary,
                table_formatter,
                rich_formatter,
                current_scaff_enabled,
            )

        if not summary.success:
            raise typer.Exit(code=1)
        return

    # 3. Handle directory validation (Discovery mode)
    # Determine which directories to validate based on content_type
    directories = determine_validation_targets(target, content_type)

    logger.info(f"Found {len(directories)} directory(ies) to validate")

    # Run validation
    validator = BatchValidator()

    if json_output:
        _validate_with_json_output(validator, directories, scaff_enabled=scaff)
    else:
        _validate_with_rich_output(validator, directories, scaff_enabled=scaff)

    logger.info("Validation complete")


def test_prompts(targets: list[Path] | None = None, provider: str | None = None) -> None:
    """Run functional tests for prompt files using AI."""
    logger.info("Running functional tests")

    test_files = _discover_functional_test_files(targets)
    console.print(f"Total discovered test file(s): {len(test_files)}")

    # Priority: 1. CLI flag, 2. Config file, 3. DEFAULT_LLM_MODEL env var
    global_provider = provider or _get_global_ai_provider()
    executor = None

    # Pre-validate global provider connection to fail early if misconfigured
    if global_provider:
        from prompt_unifier.ai.executor import AIExecutor

        executor = AIExecutor()
        try:
            _validate_ai_connection(executor, global_provider)
        except Exception:
            # Troubleshooting info is already printed by _validate_ai_connection
            raise typer.Exit(code=1) from None

    all_results = [_run_single_functional_test(tf, global_provider, executor) for tf in test_files]

    # FINAL RECAP TABLE
    if len(all_results) > 1:
        console.print("\n" + "━" * 80 + "\n[bold]FUNCTIONAL TEST RECAP[/bold]\n" + "━" * 80)
        recap_table = Table(show_header=True, header_style="bold magenta")
        recap_table.add_column("Name", style="cyan")
        recap_table.add_column("Status", justify="center")
        recap_table.add_column("Scenarios", justify="right")
        recap_table.add_column("Pass Rate", justify="right")
        recap_table.add_column("Path", style="dim", no_wrap=False)

        for res in all_results:
            style = "green" if res["success"] else "bold red"
            status = f"[{style}]{'PASSED' if res['success'] else 'FAILED'}[/{style}]"
            recap_table.add_row(
                res["name"],
                status,
                f"{res['passed']}/{res['total']}",
                f"{res['pass_rate']:.1f}%",
                res["path"],
            )
        console.print(recap_table)
        console.print()

    if all(r["success"] for r in all_results):
        logger.info("All functional tests passed")
    else:
        logger.error("Some functional tests failed")
        raise typer.Exit(code=1)


def init(
    storage_path: str | None = DEFAULT_INIT_STORAGE_PATH_OPTION,
) -> None:
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
    logger.info("Initializing prompt-unifier")

    try:
        # Get current working directory
        cwd = Path.cwd()

        # Create .prompt-unifier/ directory
        prompt_unifier_dir = cwd / CONFIG_DIR

        # Track what was created vs what already existed
        created_items: list[str] = []
        existing_items: list[str] = []

        # Determine storage path (custom or default)
        config_path = prompt_unifier_dir / CONFIG_FILE
        existing_config = None
        if config_path.exists():
            config_manager = ConfigManager()
            existing_config = config_manager.load_config(config_path)

        storage_dir = determine_storage_dir(storage_path, existing_config)
        logger.debug(f"Using storage path: {storage_dir}")

        # Create .prompt-unifier/ directory if it doesn't exist
        create_directory_with_tracking(prompt_unifier_dir, created_items, existing_items)

        # Create config.yaml if it doesn't exist
        config_path = prompt_unifier_dir / CONFIG_FILE
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
            logger.info(f"Created config file: {config_path}")
        else:
            existing_items.append(f"Exists: {config_path}")

        # Create centralized storage directory and subdirectories
        create_directory_with_tracking(storage_dir, created_items, existing_items)
        create_directory_with_tracking(storage_dir / "prompts", created_items, existing_items)
        create_directory_with_tracking(storage_dir / "rules", created_items, existing_items)

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
            logger.info(f"Initialization complete: created {len(created_items)} items")
        else:
            console.print("[green]✓[/green] Already initialized (all components exist)")
            logger.info("Already initialized")

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


def sync(
    repos: list[str] | None = DEFAULT_SYNC_REPOS_OPTION,
    storage_path: str | None = DEFAULT_SYNC_STORAGE_PATH_OPTION,
) -> None:
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
    logger.info("Starting sync operation")

    try:
        # Get current working directory
        cwd = Path.cwd()

        # Validate that init has been run
        config_path = cwd / CONFIG_DIR / CONFIG_FILE
        if not config_path.exists():
            typer.echo(ERROR_CONFIG_NOT_FOUND, err=True)
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

        # Determine repository configurations and storage path
        repo_configs = determine_repo_configs(repos, config)
        storage_dir = determine_storage_dir(storage_path, config)
        logger.debug(f"Storage path: {storage_dir}")

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
        logger.info(f"Sync complete: {len(files)} files from {len(repositories_list)} repos")
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
    Also checks deployment status of prompts and rules against target handlers.

    Exit codes:
        0: Always (status is informational)

    Examples:
        # Check sync status
        prompt-unifier status
    """
    logger.info("Checking status")

    try:
        # Get current working directory
        cwd = Path.cwd()

        # Validate that init has been run
        config_path = cwd / CONFIG_DIR / CONFIG_FILE
        if not config_path.exists():
            typer.echo(ERROR_CONFIG_NOT_FOUND, err=True)
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

        # Get storage directory
        if config.storage_path:
            storage_dir = Path(config.storage_path).expanduser().resolve()
        else:
            storage_dir = Path.home() / CONFIG_DIR / "storage"

        # Display status header with storage and repository info
        display_status_header(config, storage_dir)

        # Initialize handlers
        active_handlers = initialize_status_handlers(config)
        if not active_handlers:
            console.print("[yellow]No active handlers configured.[/yellow]")
            return

        # Scan for content files
        if not storage_dir.exists():
            console.print("[yellow]Storage directory does not exist.[/yellow]")
            return

        content_files = scan_content_files(storage_dir)
        if not content_files:
            console.print("[yellow]No prompts or rules found in storage.[/yellow]")
            return

        # Check status for each file against each handler
        prompts_dir = storage_dir / "prompts"
        rules_dir = storage_dir / "rules"
        status_items = check_all_content_status(
            active_handlers, content_files, prompts_dir, rules_dir
        )

        # Display status table
        formatter = RichTableFormatter()
        table = formatter.format_status_table(status_items)
        console.print(table)
        console.print()

        logger.info(f"Status check complete: {len(status_items)} items checked")

    except Exception as e:
        # Unexpected errors - but status should always exit with 0
        typer.echo(f"Error: {e}", err=True)
        # Status is informational - don't exit with error code
        console.print()


def _resolve_list_storage_dir() -> Path:
    """Resolve storage directory for list command.

    Returns:
        Path to storage directory.

    Raises:
        typer.Exit: If storage directory doesn't exist.
    """
    cwd = Path.cwd()
    config_path = cwd / CONFIG_DIR / CONFIG_FILE

    config_manager = ConfigManager()
    config = config_manager.load_config(config_path) if config_path.exists() else None

    if config and config.storage_path:
        storage_dir = Path(config.storage_path).expanduser().resolve()
    else:
        storage_dir = Path.home() / CONFIG_DIR / "storage"

    logger.debug(f"Storage path: {storage_dir}")

    if not storage_dir.exists():
        typer.echo(f"Error: Storage directory '{storage_dir}' does not exist.", err=True)
        raise typer.Exit(code=1)

    return storage_dir


def _scan_directory_for_content(
    directory: Path,
    content_type: str,
    parser: ContentFileParser,
) -> list[tuple[Any, str, Path]]:
    """Scan a directory for content files.

    Args:
        directory: Directory to scan.
        content_type: Type of content ('prompt' or 'rule').
        parser: Content file parser.

    Returns:
        List of (parsed_content, content_type, file_path) tuples.
    """
    content_files = []
    if directory.exists():
        for md_file in directory.glob("**/*.md"):
            try:
                parsed_content = parser.parse_file(md_file)
                content_files.append((parsed_content, content_type, md_file))
            except Exception as e:
                console.print(f"[yellow]Warning: Failed to parse {md_file}: {e}[/yellow]")
    return content_files


def _filter_and_sort_content(
    content_files: list[tuple[Any, str, Path]],
    tag: str | None,
    sort: str,
) -> list[tuple[Any, str, Path]]:
    """Filter and sort content files.

    Args:
        content_files: List of content file tuples.
        tag: Tag to filter by (or None).
        sort: Sort order ('date' or 'name').

    Returns:
        Filtered and sorted content files.
    """
    # Filter by tag
    if tag:
        content_files = [
            (c, t, p)
            for c, t, p in content_files
            if hasattr(c, "tags") and c.tags and tag in c.tags
        ]
        logger.debug(f"Filtered by tag '{tag}': {len(content_files)} files")

    # Sort
    if sort == "date":
        content_files.sort(key=lambda x: x[2].stat().st_mtime, reverse=True)
    else:
        content_files.sort(key=lambda x: x[0].title)

    return content_files


def list_content(
    tool: str | None = DEFAULT_LIST_TOOL_OPTION,
    tag: str | None = DEFAULT_LIST_TAG_OPTION,
    sort: str = DEFAULT_LIST_SORT_OPTION,
) -> None:
    """List available prompts and rules.

    Displays a table of all available prompts and rules, with optional filtering
    and sorting.

    Examples:
        # List all content
        prompt-unifier list

        # Filter by tag
        prompt-unifier list --tag coding

        # Sort by date
        prompt-unifier list --sort date
    """
    logger.info("Listing content")
    if tool:
        logger.warning(f"Tool filtering (--tool {tool}) not yet implemented")

    try:
        storage_dir = _resolve_list_storage_dir()

        # Scan for content files
        parser = ContentFileParser()
        content_files = _scan_directory_for_content(storage_dir / "prompts", "prompt", parser)
        content_files.extend(_scan_directory_for_content(storage_dir / "rules", "rule", parser))

        logger.info(f"Found {len(content_files)} content files")

        if not content_files:
            console.print("[yellow]No prompts or rules found.[/yellow]")
            return

        # Filter and sort
        content_files = _filter_and_sort_content(content_files, tag, sort)

        # Display table
        formatter = RichTableFormatter()
        formatted_files = [(c, t, str(p)) for c, t, p in content_files]
        table = formatter.format_list_table(formatted_files)
        console.print(table)

        logger.info(f"Listed {len(content_files)} content files")

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1) from e


def _load_and_validate_config() -> tuple[Path, Any]:
    """Load deployment configuration and validate storage directory."""
    cwd = Path.cwd()
    config_path = cwd / CONFIG_DIR / CONFIG_FILE
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

    logger.debug(f"Storage path: {storage_dir}")
    return storage_dir, config


def _setup_deployment_handlers(
    base_path: Path | None,
    config: Any,
    target_handlers: list[str] | None,
) -> list[Any]:
    """Setup and filter deployment handlers based on configuration."""
    from prompt_unifier.cli.helpers import resolve_handler_base_path

    registry: ToolHandlerRegistry = ToolHandlerRegistry()

    # Determine which handlers to register based on target_handlers
    register_continue = not target_handlers or "continue" in target_handlers
    register_kilocode = not target_handlers or "kilocode" in target_handlers

    # Register Continue handler if needed
    if register_continue:
        continue_handler = setup_continue_handler(base_path, config)
        registry.register(continue_handler)

    # Register Kilo Code handler if needed
    if register_kilocode:
        kilo_base_path = resolve_handler_base_path("kilocode", base_path, config)
        kilo_handler = KiloCodeToolHandler(base_path=kilo_base_path)
        try:
            kilo_handler.validate_tool_installation()
            registry.register(kilo_handler)
        except OSError as e:
            logger.warning(f"Kilo Code handler validation failed: {e}")
            # Don't fail - just don't register this handler

    all_handlers = registry.get_all_handlers()
    if target_handlers and not all_handlers:
        typer.echo(f"Error: No matching handlers found for {target_handlers}.", err=True)
        raise typer.Exit(code=1)

    return all_handlers


def _prepare_content_for_deployment(
    storage_dir: Path,
    prompt_name: str | None,
    deploy_tags: list[str] | None,
) -> list[tuple[str, str, Path]]:
    """Scan, validate, and filter content files for deployment."""
    content_files = scan_content_files(storage_dir)
    logger.info(f"Found {len(content_files)} content files")

    duplicates = check_duplicate_titles(content_files)
    if duplicates:
        display_duplicate_titles_error(duplicates)
        raise typer.Exit(code=1)

    filtered_files = filter_content_files(content_files, prompt_name, deploy_tags)
    return filtered_files


def deploy(
    prompt_name: str | None = DEFAULT_PROMPT_NAME_OPTION,
    tags: list[str] | None = DEFAULT_TAGS_OPTION,
    handlers: list[str] | None = DEFAULT_HANDLERS_OPTION,
    base_path: Path | None = DEFAULT_BASE_PATH_OPTION,
    clean: bool = DEFAULT_CLEAN_OPTION,
    dry_run: bool = DEFAULT_DRY_RUN_OPTION,
) -> None:
    """
    Deploys prompts and rules to the specified tool handlers based on configuration and CLI options.

    The base path for deployment is resolved in the following precedence order:
    1. CLI --base-path flag (highest priority)
    2. config.yaml handlers.<handler_name>.base_path
    3. Path.cwd() (default, handler will use this if no base_path specified)

    Environment variables ($HOME, $USER, $PWD) in configured base_path are automatically expanded.
    """
    logger.info("Starting deployment")

    try:
        storage_dir, config = _load_and_validate_config()
        deploy_tags = tags if tags is not None else config.deploy_tags
        target_handlers = handlers if handlers is not None else config.target_handlers
        all_handlers = _setup_deployment_handlers(base_path, config, target_handlers)
        filtered_files = _prepare_content_for_deployment(storage_dir, prompt_name, deploy_tags)

        if not filtered_files:
            console.print("[yellow]No content files match the specified criteria.[/yellow]")
            return

        prompts_dir = storage_dir / "prompts"
        rules_dir = storage_dir / "rules"

        if dry_run:
            logger.info("Dry-run mode: showing preview")
            display_dry_run_preview(filtered_files, all_handlers, prompts_dir, rules_dir)
            return

        total_deployed = 0
        total_cleaned = 0

        for handler in all_handlers:
            handler_deployed, cleaned = deploy_to_single_handler(
                handler, filtered_files, prompts_dir, rules_dir, clean
            )
            total_deployed += handler_deployed
            total_cleaned += cleaned

        summary_parts = [f"{total_deployed} items deployed to {len(all_handlers)} handler(s)"]
        if clean and total_cleaned > 0:
            summary_parts.append(f"{total_cleaned} orphaned file(s) cleaned")

        console.print(f"\n[bold]Deployment summary:[/bold] {', '.join(summary_parts)}.")
        logger.info(f"Deployment complete: {total_deployed} items to {len(all_handlers)} handlers")

    except Exception as e:
        typer.echo(f"Error during deployment: {e}", err=True)
        raise typer.Exit(code=1) from e
