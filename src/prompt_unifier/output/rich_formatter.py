"""Rich terminal output formatter for validation results.

This module provides colored terminal output using the Rich library,
with symbols, line numbers, and formatted excerpts for validation results.
"""

from pathlib import Path

from rich.console import Console
from rich.markup import escape

from prompt_unifier.models.validation import (
    ValidationIssue,
    ValidationResult,
    ValidationSummary,
)


class RichFormatter:
    """Formats validation results for Rich terminal output.

    This formatter provides colored, symbol-enhanced terminal output for
    validation results including errors (red), warnings (yellow), checkmarks
    for passed files, and X marks for failed files.

    Attributes:
        ERROR_COLOR: Color for error messages (red)
        WARNING_COLOR: Color for warning messages (yellow)
        PASSED_SYMBOL: Symbol for passed files (✓)
        FAILED_SYMBOL: Symbol for failed files (✗)
        console: Rich Console instance for output

    Examples:
        >>> formatter = RichFormatter()
        >>> summary = ValidationSummary(...)
        >>> formatter.format_summary(summary, Path("./prompts"))
    """

    # Color and symbol constants
    ERROR_COLOR = "red"
    WARNING_COLOR = "yellow"
    SUCCESS_COLOR = "green"
    PASSED_SYMBOL = "✓"
    FAILED_SYMBOL = "✗"

    def __init__(self) -> None:
        """Initialize the RichFormatter with a Rich Console."""
        self.console = Console()

    def format_summary(
        self, summary: ValidationSummary, directory: Path, verbose: bool = False
    ) -> None:
        """Format and display a validation summary to the terminal.

        Displays a header, per-file results with errors/warnings, summary
        statistics table, and final status message.

        Args:
            summary: The validation summary containing all results
            directory: The directory that was validated
            verbose: If True, show detailed progress information

        Examples:
            >>> formatter = RichFormatter()
            >>> summary = ValidationSummary(
            ...     total_files=2,
            ...     passed=1,
            ...     failed=1,
            ...     error_count=1,
            ...     warning_count=0,
            ...     success=False,
            ...     results=[]
            ... )
            >>> formatter.format_summary(summary, Path("./prompts"))
        """
        # Display header with directory path
        self._display_header(directory)

        # Display each file result
        for result in summary.results:
            self._display_file_result(result, verbose)

        # Display summary statistics
        self._display_summary_table(summary)

        # Display final status message
        self._display_final_status(summary)

    def _display_header(self, directory: Path) -> None:
        """Display the validation header with directory path.

        Args:
            directory: The directory being validated
        """
        self.console.print(f"\nValidating prompts in: {directory}")
        self.console.print("━" * 80)
        self.console.print()

    def _display_file_result(self, result: ValidationResult, verbose: bool = False) -> None:
        """Display the validation result for a single file.

        Args:
            result: The validation result for the file
            verbose: If True, show detailed information
        """
        # Display file name with status symbol
        if result.status == "passed":
            status_symbol = self.PASSED_SYMBOL
            status_text = "PASSED"
            status_color = self.SUCCESS_COLOR
        else:
            status_symbol = self.FAILED_SYMBOL
            status_text = "FAILED"
            status_color = self.ERROR_COLOR

        self.console.print(
            f"[{status_color}]{status_symbol}[/{status_color}] "
            f"{result.file.name} "
            f"[{status_color}]({status_text})[/{status_color}]"
        )

        # Display errors
        for error in result.errors:
            self._display_issue(error, is_error=True)

        # Display warnings
        for warning in result.warnings:
            self._display_issue(warning, is_error=False)

        self.console.print()

    def _display_issue(self, issue: ValidationIssue, is_error: bool = True) -> None:
        """Display a single validation issue (error or warning).

        Args:
            issue: The validation issue to display
            is_error: True if this is an error, False if warning
        """
        # Determine color and symbol based on severity
        if is_error:
            color = self.ERROR_COLOR
            symbol = self.FAILED_SYMBOL
            prefix = "Error"
        else:
            color = self.WARNING_COLOR
            symbol = "⚠"
            prefix = "Warning"

        # Format line number (use "line N:" format to avoid brackets)
        line_info = f"[line {issue.line}] " if issue.line is not None else ""

        # Escape message and suggestion to prevent Rich markup interpretation
        escaped_message = escape(issue.message)
        escaped_suggestion = escape(issue.suggestion)
        escaped_line_info = escape(line_info)

        # Display the issue with color
        self.console.print(
            f"  [{color}]{symbol} {prefix} {escaped_line_info}: {escaped_message}[/{color}]"
        )

        # Display code excerpt if available
        if issue.excerpt:
            self._display_excerpt(issue.excerpt)

        # Display suggestion
        self.console.print(f"     [dim]Suggestion: {escaped_suggestion}[/dim]")

    def _display_excerpt(self, excerpt: str) -> None:
        """Display a code excerpt with indentation.

        Args:
            excerpt: The code excerpt to display (multi-line string with line numbers)
        """
        self.console.print("     [dim]Excerpt:[/dim]")
        for line in excerpt.split("\n"):
            if line.strip():  # Only display non-empty lines
                self.console.print(f"       [dim]{line}[/dim]")

    def _display_summary_table(self, summary: ValidationSummary) -> None:
        """Display a summary table with validation statistics.

        Args:
            summary: The validation summary with statistics
        """
        self.console.print("━" * 80)
        self.console.print("[bold]Summary:[/bold]")

        # Create a simple text-based summary (not using Rich Table for simplicity)
        self.console.print(f"  Total files: {summary.total_files}")
        self.console.print(
            f"  Passed: [{self.SUCCESS_COLOR}]{summary.passed}[/{self.SUCCESS_COLOR}]"
        )
        self.console.print(f"  Failed: [{self.ERROR_COLOR}]{summary.failed}[/{self.ERROR_COLOR}]")
        self.console.print(
            f"  Errors: [{self.ERROR_COLOR}]{summary.error_count}[/{self.ERROR_COLOR}]"
        )
        self.console.print(
            f"  Warnings: [{self.WARNING_COLOR}]{summary.warning_count}" f"[/{self.WARNING_COLOR}]"
        )
        self.console.print()

    def _display_final_status(self, summary: ValidationSummary) -> None:
        """Display the final validation status message.

        Args:
            summary: The validation summary with success status
        """
        if summary.success:
            self.console.print(
                f"[{self.SUCCESS_COLOR}]Validation PASSED "
                f"{self.PASSED_SYMBOL}[/{self.SUCCESS_COLOR}]"
            )
        else:
            self.console.print(
                f"[{self.ERROR_COLOR}]Validation FAILED "
                f"{self.FAILED_SYMBOL}[/{self.ERROR_COLOR}]"
            )
        self.console.print()
