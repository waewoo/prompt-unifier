"""CLI commands for the Prompt Manager.

This module contains the CLI commands implemented using Typer,
including the validate command for prompt file validation.
"""

from pathlib import Path

import typer

from prompt_manager.core.batch_validator import BatchValidator
from prompt_manager.output.json_formatter import JSONFormatter
from prompt_manager.output.rich_formatter import RichFormatter


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
