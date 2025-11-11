"""Main CLI application for Prompt Manager.

This module sets up the Typer application and registers all CLI commands.
"""

from pathlib import Path

import typer

from prompt_manager.cli.commands import validate as validate_command

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


def main() -> None:
    """Entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main()
