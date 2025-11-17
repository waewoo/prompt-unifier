"""Tests for JSON output formatter.

This module tests the JSONFormatter class which converts validation results
to JSON format for machine-readable output.
"""

import json
from pathlib import Path

import pytest

from prompt_unifier.models.validation import (
    ErrorCode,
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
    ValidationSummary,
    WarningCode,
)
from prompt_unifier.output.json_formatter import JSONFormatter


@pytest.fixture
def json_formatter() -> JSONFormatter:
    """Create a JSONFormatter instance for testing."""
    return JSONFormatter()


def test_summary_section_structure(json_formatter: JSONFormatter) -> None:
    """Test that JSON output has correct summary section structure."""
    # Arrange
    directory = Path("/test/prompts")
    summary = ValidationSummary(
        total_files=3,
        passed=2,
        failed=1,
        error_count=2,
        warning_count=1,
        success=False,
        results=[],
    )

    # Act
    json_output = json_formatter.format_summary(summary, directory)
    data = json.loads(json_output)

    # Assert
    assert "summary" in data
    assert data["summary"]["total_files"] == 3
    assert data["summary"]["passed"] == 2
    assert data["summary"]["failed"] == 1
    assert data["summary"]["error_count"] == 2
    assert data["summary"]["warning_count"] == 1
    assert data["summary"]["success"] is False


def test_results_array_structure(json_formatter: JSONFormatter) -> None:
    """Test that JSON output has correct results array structure."""
    # Arrange
    directory = Path("/test/prompts")
    result = ValidationResult(file=Path("test.md"), status="passed", errors=[], warnings=[])
    summary = ValidationSummary(
        total_files=1,
        passed=1,
        failed=0,
        error_count=0,
        warning_count=0,
        success=True,
        results=[result],
    )

    # Act
    json_output = json_formatter.format_summary(summary, directory)
    data = json.loads(json_output)

    # Assert
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 1
    assert data["results"][0]["file"] == "test.md"
    assert data["results"][0]["status"] == "passed"
    assert data["results"][0]["errors"] == []
    assert data["results"][0]["warnings"] == []


def test_error_object_structure(json_formatter: JSONFormatter) -> None:
    """Test that error objects have correct structure with all fields."""
    # Arrange
    directory = Path("/test/prompts")
    error = ValidationIssue(
        line=10,
        severity=ValidationSeverity.ERROR,
        code=ErrorCode.MISSING_REQUIRED_FIELD.value,
        message="Missing required field 'name'",
        excerpt="description: Test prompt\nversion: 1.0.0",
        suggestion="Add 'name' field to frontmatter",
    )
    result = ValidationResult(file=Path("broken.md"), status="failed", errors=[error], warnings=[])
    summary = ValidationSummary(
        total_files=1,
        passed=0,
        failed=1,
        error_count=1,
        warning_count=0,
        success=False,
        results=[result],
    )

    # Act
    json_output = json_formatter.format_summary(summary, directory)
    data = json.loads(json_output)

    # Assert
    error_obj = data["results"][0]["errors"][0]
    assert error_obj["line"] == 10
    assert error_obj["severity"] == "error"
    assert error_obj["code"] == "MISSING_REQUIRED_FIELD"
    assert error_obj["message"] == "Missing required field 'name'"
    assert error_obj["excerpt"] == "description: Test prompt\nversion: 1.0.0"
    assert error_obj["suggestion"] == "Add 'name' field to frontmatter"


def test_warning_object_structure(json_formatter: JSONFormatter) -> None:
    """Test that warning objects have correct structure."""
    # Arrange
    directory = Path("/test/prompts")
    warning = ValidationIssue(
        line=None,
        severity=ValidationSeverity.WARNING,
        code=WarningCode.MISSING_AUTHOR.value,
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

    # Act
    json_output = json_formatter.format_summary(summary, directory)
    data = json.loads(json_output)

    # Assert
    warning_obj = data["results"][0]["warnings"][0]
    assert warning_obj["line"] is None
    assert warning_obj["severity"] == "warning"
    assert warning_obj["code"] == "MISSING_AUTHOR"
    assert warning_obj["message"] == "Missing optional field 'author'"
    assert warning_obj["excerpt"] is None
    assert warning_obj["suggestion"] == "Consider adding 'author' field"


def test_json_serialization_valid(json_formatter: JSONFormatter) -> None:
    """Test that output is valid JSON that can be parsed."""
    # Arrange
    directory = Path("/test/prompts")
    summary = ValidationSummary(
        total_files=1,
        passed=1,
        failed=0,
        error_count=0,
        warning_count=0,
        success=True,
        results=[],
    )

    # Act
    json_output = json_formatter.format_summary(summary, directory)

    # Assert - should not raise JSONDecodeError
    data = json.loads(json_output)
    assert isinstance(data, dict)


def test_json_pretty_printing(json_formatter: JSONFormatter) -> None:
    """Test that JSON output is pretty-printed with indentation."""
    # Arrange
    directory = Path("/test/prompts")
    summary = ValidationSummary(
        total_files=1,
        passed=1,
        failed=0,
        error_count=0,
        warning_count=0,
        success=True,
        results=[],
    )

    # Act
    json_output = json_formatter.format_summary(summary, directory)

    # Assert - pretty-printed JSON should have newlines and indentation
    assert "\n" in json_output
    assert "  " in json_output  # Check for indentation
    # Should be readable (not minified)
    lines = json_output.split("\n")
    assert len(lines) > 3  # More than one line
