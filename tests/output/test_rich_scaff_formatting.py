"""Tests for SCAFF score Rich terminal formatting.

This module tests the RichFormatter class's SCAFF-specific formatting features,
including score display, component tables, and warning formatting.
"""

import re
from io import StringIO
from pathlib import Path

import pytest
from rich.console import Console

from prompt_unifier.models.scaff import SCARFFComponent, SCARFFScore
from prompt_unifier.models.validation import (
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


@pytest.fixture
def sample_scaff_score() -> SCARFFScore:
    """Create a sample SCAFF score for testing."""
    return SCARFFScore(
        components=[
            SCARFFComponent(component_name="Specific", score=18, status="excellent"),
            SCARFFComponent(component_name="Contextual", score=15, status="good"),
            SCARFFComponent(component_name="Actionable", score=16, status="good"),
            SCARFFComponent(component_name="Formatted", score=19, status="excellent"),
            SCARFFComponent(component_name="Focused", score=17, status="excellent"),
        ],
        total_score=85,
    )


def test_scaff_score_displays_with_color_coding_excellent(
    rich_formatter: RichFormatter, console_capture: StringIO, sample_scaff_score: SCARFFScore
) -> None:
    """Test that SCAFF score >= 80 displays in green (excellent)."""
    # Arrange
    directory = Path("/test/prompts")
    result = ValidationResult(
        file=Path("test-prompt.md"),
        status="passed",
        errors=[],
        warnings=[],
        scaff_score=sample_scaff_score,
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

    console = Console(file=console_capture, width=120, legacy_windows=False)
    rich_formatter.console = console

    # Act
    rich_formatter.format_summary(summary, directory)
    output = console_capture.getvalue()
    clean_output = strip_ansi(output)

    # Assert
    assert "SCAFF Score: 85/100" in clean_output
    assert "excellent" in clean_output.lower()


def test_scaff_score_displays_with_color_coding_good(
    rich_formatter: RichFormatter, console_capture: StringIO
) -> None:
    """Test that SCAFF score 60-79 displays in yellow (good)."""
    # Arrange
    directory = Path("/test/prompts")
    scaff_score = SCARFFScore(
        components=[
            SCARFFComponent(component_name="Specific", score=14, status="good"),
            SCARFFComponent(component_name="Contextual", score=13, status="good"),
            SCARFFComponent(component_name="Actionable", score=15, status="good"),
            SCARFFComponent(component_name="Formatted", score=14, status="good"),
            SCARFFComponent(component_name="Focused", score=14, status="good"),
        ],
        total_score=70,
    )
    result = ValidationResult(
        file=Path("test-prompt.md"),
        status="passed",
        errors=[],
        warnings=[],
        scaff_score=scaff_score,
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

    console = Console(file=console_capture, width=120, legacy_windows=False)
    rich_formatter.console = console

    # Act
    rich_formatter.format_summary(summary, directory)
    output = console_capture.getvalue()
    clean_output = strip_ansi(output)

    # Assert
    assert "SCAFF Score: 70/100" in clean_output
    assert "good" in clean_output.lower()


def test_scaff_score_displays_with_color_coding_poor(
    rich_formatter: RichFormatter, console_capture: StringIO
) -> None:
    """Test that SCAFF score < 60 displays in red (poor)."""
    # Arrange
    directory = Path("/test/prompts")
    scaff_score = SCARFFScore(
        components=[
            SCARFFComponent(component_name="Specific", score=10, status="poor"),
            SCARFFComponent(component_name="Contextual", score=8, status="poor"),
            SCARFFComponent(component_name="Actionable", score=12, status="good"),
            SCARFFComponent(component_name="Formatted", score=11, status="poor"),
            SCARFFComponent(component_name="Focused", score=9, status="poor"),
        ],
        total_score=50,
    )
    result = ValidationResult(
        file=Path("test-prompt.md"),
        status="passed",
        errors=[],
        warnings=[],
        scaff_score=scaff_score,
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

    console = Console(file=console_capture, width=120, legacy_windows=False)
    rich_formatter.console = console

    # Act
    rich_formatter.format_summary(summary, directory)
    output = console_capture.getvalue()
    clean_output = strip_ansi(output)

    # Assert
    assert "SCAFF Score: 50/100" in clean_output
    assert "poor" in clean_output.lower()


def test_scaff_component_table_displays_all_components(
    rich_formatter: RichFormatter, console_capture: StringIO, sample_scaff_score: SCARFFScore
) -> None:
    """Test that SCAFF component table shows all 5 components with scores and status."""
    # Arrange
    directory = Path("/test/prompts")
    result = ValidationResult(
        file=Path("test-prompt.md"),
        status="passed",
        errors=[],
        warnings=[],
        scaff_score=sample_scaff_score,
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

    console = Console(file=console_capture, width=120, legacy_windows=False)
    rich_formatter.console = console

    # Act
    rich_formatter.format_summary(summary, directory)
    output = console_capture.getvalue()
    clean_output = strip_ansi(output)

    # Assert - all component names present
    assert "Specific" in clean_output
    assert "Contextual" in clean_output
    assert "Actionable" in clean_output
    assert "Formatted" in clean_output
    assert "Focused" in clean_output

    # Assert - scores present
    assert "18" in clean_output  # Specific score
    assert "15" in clean_output  # Contextual score
    assert "16" in clean_output  # Actionable score
    assert "19" in clean_output  # Formatted score
    assert "17" in clean_output  # Focused score


def test_scaff_warning_formatted_with_warning_symbol(
    rich_formatter: RichFormatter, console_capture: StringIO
) -> None:
    """Test that SCAFF warnings display with warning symbol and yellow color."""
    # Arrange
    directory = Path("/test/prompts")
    warning = ValidationIssue(
        line=None,
        severity=ValidationSeverity.WARNING,
        code=WarningCode.SCAFF_NOT_SPECIFIC.value,
        message="Prompt lacks specific requirements or measurable goals",
        excerpt=None,
        suggestion="Add concrete requirements with measurable success criteria",
    )
    result = ValidationResult(
        file=Path("test-prompt.md"),
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

    console = Console(file=console_capture, width=120, legacy_windows=False)
    rich_formatter.console = console

    # Act
    rich_formatter.format_summary(summary, directory)
    output = console_capture.getvalue()
    clean_output = strip_ansi(output)

    # Assert
    assert "⚠" in clean_output  # Warning symbol
    assert "Prompt lacks specific requirements" in clean_output
    assert "Add concrete requirements with measurable success criteria" in clean_output


def test_scaff_statistics_in_summary_table(
    rich_formatter: RichFormatter, console_capture: StringIO
) -> None:
    """Test that summary table includes SCAFF warning count when SCAFF validation ran."""
    # Arrange
    directory = Path("/test/prompts")
    warning = ValidationIssue(
        line=None,
        severity=ValidationSeverity.WARNING,
        code=WarningCode.SCAFF_NOT_SPECIFIC.value,
        message="Prompt lacks specific requirements",
        excerpt=None,
        suggestion="Add concrete requirements",
    )
    scaff_score = SCARFFScore(
        components=[
            SCARFFComponent(component_name="Specific", score=10, status="poor"),
            SCARFFComponent(component_name="Contextual", score=15, status="good"),
            SCARFFComponent(component_name="Actionable", score=16, status="good"),
            SCARFFComponent(component_name="Formatted", score=18, status="excellent"),
            SCARFFComponent(component_name="Focused", score=17, status="excellent"),
        ],
        total_score=76,
    )
    result = ValidationResult(
        file=Path("test-prompt.md"),
        status="passed",
        errors=[],
        warnings=[warning],
        scaff_score=scaff_score,
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

    console = Console(file=console_capture, width=120, legacy_windows=False)
    rich_formatter.console = console

    # Act
    rich_formatter.format_summary(summary, directory)
    output = console_capture.getvalue()
    clean_output = strip_ansi(output)

    # Assert
    assert "SCAFF" in clean_output
    assert "1" in clean_output  # Warning count


def test_no_scaff_section_when_score_not_present(
    rich_formatter: RichFormatter, console_capture: StringIO
) -> None:
    """Test that SCAFF section is not displayed when scaff_score is None."""
    # Arrange
    directory = Path("/test/prompts")
    result = ValidationResult(
        file=Path("test-prompt.md"),
        status="passed",
        errors=[],
        warnings=[],
        scaff_score=None,  # No SCAFF score
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

    console = Console(file=console_capture, width=120, legacy_windows=False)
    rich_formatter.console = console

    # Act
    rich_formatter.format_summary(summary, directory)
    output = console_capture.getvalue()
    clean_output = strip_ansi(output)

    # Assert - SCAFF section should not be present
    assert "SCAFF Score:" not in clean_output
