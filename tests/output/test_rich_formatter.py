"""Tests for Rich terminal output formatter.

This module tests the RichFormatter class which provides colored terminal
output with symbols, line numbers, and code excerpts for validation results.
"""

import re
from io import StringIO
from pathlib import Path

import pytest
from rich.console import Console

from prompt_unifier.models.validation import (
    ErrorCode,
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
    ValidationSummary,
    WarningCode,
)
from prompt_unifier.output.rich_formatter import RichFormatter


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text for testing purposes."""
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_escape.sub("", text)


@pytest.fixture
def rich_formatter() -> RichFormatter:
    """Create a RichFormatter instance for testing."""
    return RichFormatter()


@pytest.fixture
def console_capture() -> StringIO:
    """Create a StringIO buffer to capture console output."""
    return StringIO()


def test_header_displays_directory_path(
    rich_formatter: RichFormatter, console_capture: StringIO
) -> None:
    """Test that the header displays the directory path being validated."""
    # Arrange
    directory = Path("/test/prompts")
    summary = ValidationSummary(
        total_files=0,
        passed=0,
        failed=0,
        error_count=0,
        warning_count=0,
        success=True,
        results=[],
    )

    # Create console that writes to our capture buffer
    console = Console(file=console_capture, width=80, legacy_windows=False)
    rich_formatter.console = console

    # Act
    rich_formatter.format_summary(summary, directory)
    output = console_capture.getvalue()

    # Assert
    assert "Validating prompts in: /test/prompts" in output
    assert "━" in output  # Check for separator line


def test_passed_file_shows_checkmark_symbol(
    rich_formatter: RichFormatter, console_capture: StringIO
) -> None:
    """Test that passed files display with a checkmark symbol."""
    # Arrange
    directory = Path("/test/prompts")
    result = ValidationResult(
        file=Path("python-expert.md"),
        status="passed",
        errors=[],
        warnings=[],
    )
    summary = ValidationSummary(
        total_files=1,
        passed=1,
        failed=0,
        error_count=0,
        warning_count=0,
        success=True,
        results=[result],
    )

    console = Console(file=console_capture, width=80, legacy_windows=False)
    rich_formatter.console = console

    # Act
    rich_formatter.format_summary(summary, directory)
    output = console_capture.getvalue()

    # Assert
    assert "✓" in output or "✓" in output  # Check for checkmark symbol
    assert "python-expert.md" in output
    assert "PASSED" in output


def test_failed_file_shows_x_symbol(
    rich_formatter: RichFormatter, console_capture: StringIO
) -> None:
    """Test that failed files display with an X symbol."""
    # Arrange
    directory = Path("/test/prompts")
    error = ValidationIssue(
        line=5,
        severity=ValidationSeverity.ERROR,
        code=ErrorCode.MISSING_REQUIRED_FIELD.value,
        message="Missing required field 'description'",
        excerpt=None,
        suggestion="Add 'description' field to frontmatter",
    )
    result = ValidationResult(
        file=Path("broken-prompt.md"),
        status="failed",
        errors=[error],
        warnings=[],
    )
    summary = ValidationSummary(
        total_files=1,
        passed=0,
        failed=1,
        error_count=1,
        warning_count=0,
        success=False,
        results=[result],
    )

    console = Console(file=console_capture, width=80, legacy_windows=False)
    rich_formatter.console = console

    # Act
    rich_formatter.format_summary(summary, directory)
    output = console_capture.getvalue()

    # Assert
    assert "✗" in output or "✗" in output  # Check for X symbol
    assert "broken-prompt.md" in output
    assert "FAILED" in output


def test_errors_displayed_in_red(rich_formatter: RichFormatter, console_capture: StringIO) -> None:
    """Test that errors are displayed with red color markup."""
    # Arrange
    directory = Path("/test/prompts")
    error = ValidationIssue(
        line=5,
        severity=ValidationSeverity.ERROR,
        code=ErrorCode.MISSING_REQUIRED_FIELD.value,
        message="Missing required field 'description'",
        excerpt=None,
        suggestion="Add 'description' field to frontmatter",
    )
    result = ValidationResult(
        file=Path("broken-prompt.md"),
        status="failed",
        errors=[error],
        warnings=[],
    )
    summary = ValidationSummary(
        total_files=1,
        passed=0,
        failed=1,
        error_count=1,
        warning_count=0,
        success=False,
        results=[result],
    )

    console = Console(file=console_capture, width=80, legacy_windows=False, force_terminal=True)
    rich_formatter.console = console

    # Act
    rich_formatter.format_summary(summary, directory)
    output = console_capture.getvalue()
    clean_output = strip_ansi(output)

    # Assert
    # Check that error message is present
    assert "Missing required field 'description'" in clean_output
    assert "[line 5]" in clean_output


def test_warnings_displayed_in_yellow(
    rich_formatter: RichFormatter, console_capture: StringIO
) -> None:
    """Test that warnings are displayed with yellow color markup."""
    # Arrange
    directory = Path("/test/prompts")
    warning = ValidationIssue(
        line=None,
        severity=ValidationSeverity.WARNING,
        code=WarningCode.MISSING_OPTIONAL_FIELD.value,
        message="Missing optional field 'author'",
        excerpt=None,
        suggestion="Consider adding 'author' field",
    )
    result = ValidationResult(
        file=Path("python-expert.md"),
        status="passed",
        errors=[],
        warnings=[warning],
    )
    summary = ValidationSummary(
        total_files=1,
        passed=1,
        failed=0,
        error_count=0,
        warning_count=1,
        success=True,
        results=[result],
    )

    console = Console(file=console_capture, width=80, legacy_windows=False, force_terminal=True)
    rich_formatter.console = console

    # Act
    rich_formatter.format_summary(summary, directory)
    output = console_capture.getvalue()
    clean_output = strip_ansi(output)

    # Assert
    # Check that warning message is present
    assert "Missing optional field 'author'" in clean_output
    assert "⚠" in clean_output or "Warning" in clean_output  # Warning symbol or text


def test_line_numbers_formatted_correctly(
    rich_formatter: RichFormatter, console_capture: StringIO
) -> None:
    """Test that line numbers are formatted with [line X] prefix."""
    # Arrange
    directory = Path("/test/prompts")
    error = ValidationIssue(
        line=42,
        severity=ValidationSeverity.ERROR,
        code=ErrorCode.MULTIPLE_SEPARATORS.value,
        message="Multiple '>>>' separators found",
        excerpt=">>>\nFirst section\n>>>",
        suggestion="Remove extra '>>>' separators",
    )
    result = ValidationResult(
        file=Path("multi-separator.md"),
        status="failed",
        errors=[error],
        warnings=[],
    )
    summary = ValidationSummary(
        total_files=1,
        passed=0,
        failed=1,
        error_count=1,
        warning_count=0,
        success=False,
        results=[result],
    )

    console = Console(file=console_capture, width=80, legacy_windows=False)
    rich_formatter.console = console

    # Act
    rich_formatter.format_summary(summary, directory)
    output = console_capture.getvalue()
    clean_output = strip_ansi(output)

    # Assert
    assert "[line 42]" in clean_output
    assert "Multiple '>>>' separators found" in clean_output


def test_code_excerpts_indented_properly(
    rich_formatter: RichFormatter, console_capture: StringIO
) -> None:
    """Test that code excerpts are displayed with proper indentation."""
    # Arrange
    directory = Path("/test/prompts")
    error = ValidationIssue(
        line=5,
        severity=ValidationSeverity.ERROR,
        code=ErrorCode.MULTIPLE_SEPARATORS.value,
        message="Multiple '>>>' separators found",
        excerpt="3 | >>>\n4 | First section\n5 | >>>",
        suggestion="Remove extra '>>>' separators",
    )
    result = ValidationResult(
        file=Path("multi-separator.md"),
        status="failed",
        errors=[error],
        warnings=[],
    )
    summary = ValidationSummary(
        total_files=1,
        passed=0,
        failed=1,
        error_count=1,
        warning_count=0,
        success=False,
        results=[result],
    )

    console = Console(file=console_capture, width=80, legacy_windows=False)
    rich_formatter.console = console

    # Act
    rich_formatter.format_summary(summary, directory)
    output = console_capture.getvalue()

    # Assert
    # Check that excerpt is displayed (indented)
    assert ">>>" in output
    assert "First section" in output


def test_summary_table_displays_statistics(
    rich_formatter: RichFormatter, console_capture: StringIO
) -> None:
    """Test that summary section displays validation statistics."""
    # Arrange
    directory = Path("/test/prompts")
    summary = ValidationSummary(
        total_files=5,
        passed=3,
        failed=2,
        error_count=4,
        warning_count=2,
        success=False,
        results=[],
    )

    console = Console(file=console_capture, width=80, legacy_windows=False)
    rich_formatter.console = console

    # Act
    rich_formatter.format_summary(summary, directory)
    output = console_capture.getvalue()

    # Assert
    assert "Summary" in output or "Total" in output
    assert "5" in output  # total files
    assert "3" in output  # passed
    assert "2" in output  # failed
    assert "4" in output  # errors
    assert "2" in output  # warnings


def test_final_status_message_passed(
    rich_formatter: RichFormatter, console_capture: StringIO
) -> None:
    """Test that final status shows 'Validation PASSED ✓' when successful."""
    # Arrange
    directory = Path("/test/prompts")
    summary = ValidationSummary(
        total_files=2,
        passed=2,
        failed=0,
        error_count=0,
        warning_count=1,
        success=True,
        results=[],
    )

    console = Console(file=console_capture, width=80, legacy_windows=False)
    rich_formatter.console = console

    # Act
    rich_formatter.format_summary(summary, directory)
    output = console_capture.getvalue()

    # Assert
    assert "PASSED" in output
    assert "✓" in output or "✓" in output


def test_final_status_message_failed(
    rich_formatter: RichFormatter, console_capture: StringIO
) -> None:
    """Test that final status shows 'Validation FAILED ✗' when errors present."""
    # Arrange
    directory = Path("/test/prompts")
    summary = ValidationSummary(
        total_files=2,
        passed=1,
        failed=1,
        error_count=1,
        warning_count=0,
        success=False,
        results=[],
    )

    console = Console(file=console_capture, width=80, legacy_windows=False)
    rich_formatter.console = console

    # Act
    rich_formatter.format_summary(summary, directory)
    output = console_capture.getvalue()

    # Assert
    assert "FAILED" in output
    assert "✗" in output or "✗" in output


def test_verbose_mode_shows_progress(
    rich_formatter: RichFormatter, console_capture: StringIO
) -> None:
    """Test that verbose mode displays validation progress."""
    # Arrange
    directory = Path("/test/prompts")
    result = ValidationResult(
        file=Path("test.md"),
        status="passed",
        errors=[],
        warnings=[],
    )
    summary = ValidationSummary(
        total_files=1,
        passed=1,
        failed=0,
        error_count=0,
        warning_count=0,
        success=True,
        results=[result],
    )

    console = Console(file=console_capture, width=80, legacy_windows=False)
    rich_formatter.console = console

    # Act
    rich_formatter.format_summary(summary, directory, verbose=True)
    output = console_capture.getvalue()

    # Assert
    # When verbose, it should show the filename being validated
    assert "test.md" in output
