"""Tests for validation models and enums.

This module contains tests for:
- ValidationSeverity enum
- ErrorCode enum
- WarningCode enum
- ValidationIssue Pydantic model
- ValidationResult Pydantic model
"""

from pathlib import Path

import prompt_unifier.models.scaff  # noqa: F401 - Trigger model rebuild
from prompt_unifier.models.validation import (
    ErrorCode,
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
    WarningCode,
)


class TestValidationSeverity:
    """Test ValidationSeverity enum values."""

    def test_error_severity(self) -> None:
        """Test ERROR severity value."""
        assert ValidationSeverity.ERROR.value == "error"

    def test_warning_severity(self) -> None:
        """Test WARNING severity value."""
        assert ValidationSeverity.WARNING.value == "warning"

    def test_severity_members(self) -> None:
        """Test that enum has exactly 2 members."""
        assert len(ValidationSeverity) == 2
        assert set(ValidationSeverity) == {
            ValidationSeverity.ERROR,
            ValidationSeverity.WARNING,
        }


class TestErrorCode:
    """Test ErrorCode enum values."""

    def test_all_error_codes_present(self) -> None:
        """Test that all 16 error codes are defined (12 original + 4 functional test)."""
        expected_codes = {
            ErrorCode.INVALID_ENCODING,
            ErrorCode.MISSING_REQUIRED_FIELD,
            ErrorCode.INVALID_YAML,
            ErrorCode.NESTED_STRUCTURE,
            ErrorCode.NO_SEPARATOR,
            ErrorCode.MULTIPLE_SEPARATORS,
            ErrorCode.SEPARATOR_NOT_ALONE,
            ErrorCode.SEPARATOR_WHITESPACE,
            ErrorCode.EMPTY_CONTENT,
            ErrorCode.INVALID_SEMVER,
            ErrorCode.PROHIBITED_FIELD,
            ErrorCode.INVALID_FILE_EXTENSION,
            ErrorCode.FUNC_YAML_INVALID,
            ErrorCode.FUNC_FILE_MISSING,
            ErrorCode.FUNC_ASSERTION_FAILED,
            ErrorCode.FUNC_AI_EXECUTION_ERROR,
        }
        assert set(ErrorCode) == expected_codes
        assert len(ErrorCode) == 16

    def test_error_code_values(self) -> None:
        """Test error code string values."""
        assert ErrorCode.INVALID_ENCODING.value == "INVALID_ENCODING"
        assert ErrorCode.MISSING_REQUIRED_FIELD.value == "MISSING_REQUIRED_FIELD"
        assert ErrorCode.INVALID_YAML.value == "INVALID_YAML"


class TestWarningCode:
    """Test WarningCode enum values."""

    def test_all_warning_codes_present(self) -> None:
        """Test that all 13 warning codes are defined (3 + 5 SCAFF + 1 functional + 4 skill)."""
        expected_codes = {
            WarningCode.MISSING_OPTIONAL_FIELD,
            WarningCode.EMPTY_TAGS_LIST,
            WarningCode.MISSING_AUTHOR,
            WarningCode.SCAFF_NOT_SPECIFIC,
            WarningCode.SCAFF_LACKS_CONTEXT,
            WarningCode.SCAFF_NOT_ACTIONABLE,
            WarningCode.SCAFF_POORLY_FORMATTED,
            WarningCode.SCAFF_UNFOCUSED,
            WarningCode.FUNC_UNKNOWN_ASSERTION_TYPE,
            WarningCode.SKILL_NO_COMPATIBILITY,
            WarningCode.SKILL_CONTENT_TOO_SHORT,
            WarningCode.SKILL_NOT_ACTIONABLE,
            WarningCode.SKILL_POORLY_STRUCTURED,
        }
        assert set(WarningCode) == expected_codes
        assert len(WarningCode) == 13

    def test_warning_code_values(self) -> None:
        """Test warning code string values."""
        assert WarningCode.MISSING_OPTIONAL_FIELD.value == "MISSING_OPTIONAL_FIELD"
        assert WarningCode.EMPTY_TAGS_LIST.value == "EMPTY_TAGS_LIST"
        assert WarningCode.MISSING_AUTHOR.value == "MISSING_AUTHOR"

    def test_scaff_warning_code_values(self) -> None:
        """Test SCAFF warning code string values."""
        assert WarningCode.SCAFF_NOT_SPECIFIC.value == "SCAFF_NOT_SPECIFIC"
        assert WarningCode.SCAFF_LACKS_CONTEXT.value == "SCAFF_LACKS_CONTEXT"
        assert WarningCode.SCAFF_NOT_ACTIONABLE.value == "SCAFF_NOT_ACTIONABLE"
        assert WarningCode.SCAFF_POORLY_FORMATTED.value == "SCAFF_POORLY_FORMATTED"
        assert WarningCode.SCAFF_UNFOCUSED.value == "SCAFF_UNFOCUSED"


class TestValidationIssue:
    """Test ValidationIssue Pydantic model."""

    def test_create_error_with_all_fields(self) -> None:
        """Test creating validation error with all fields populated."""
        issue = ValidationIssue(
            line=42,
            severity=ValidationSeverity.ERROR,
            code=ErrorCode.MISSING_REQUIRED_FIELD.value,
            message="Missing required field 'name'",
            excerpt="description: Test prompt",
            suggestion="Add field: name: <prompt-name>",
        )
        assert issue.line == 42
        assert issue.severity == ValidationSeverity.ERROR
        assert issue.code == ErrorCode.MISSING_REQUIRED_FIELD.value
        assert issue.message == "Missing required field 'name'"
        assert issue.excerpt == "description: Test prompt"
        assert issue.suggestion == "Add field: name: <prompt-name>"

    def test_create_warning_with_minimal_fields(self) -> None:
        """Test creating validation warning with minimal required fields."""
        issue = ValidationIssue(
            line=None,
            severity=ValidationSeverity.WARNING,
            code=WarningCode.MISSING_OPTIONAL_FIELD.value,
            message="Missing optional field 'version'",
            excerpt=None,
            suggestion="Consider adding version field for better tracking",
        )
        assert issue.line is None
        assert issue.severity == ValidationSeverity.WARNING
        assert issue.code == WarningCode.MISSING_OPTIONAL_FIELD.value
        assert issue.excerpt is None

    def test_json_serialization(self) -> None:
        """Test ValidationIssue serializes to JSON correctly."""
        issue = ValidationIssue(
            line=10,
            severity=ValidationSeverity.ERROR,
            code=ErrorCode.INVALID_YAML.value,
            message="Invalid YAML syntax",
            excerpt="name: test\n  bad indent",
            suggestion="Fix YAML indentation",
        )
        data = issue.model_dump()
        assert data["line"] == 10
        assert data["severity"] == ValidationSeverity.ERROR
        assert data["code"] == "INVALID_YAML"
        assert data["message"] == "Invalid YAML syntax"
        assert data["excerpt"] == "name: test\n  bad indent"
        assert data["suggestion"] == "Fix YAML indentation"

    def test_json_serialization_with_none_values(self) -> None:
        """Test ValidationIssue serializes None values correctly."""
        issue = ValidationIssue(
            line=None,
            severity=ValidationSeverity.WARNING,
            code=WarningCode.EMPTY_TAGS_LIST.value,
            message="Tags list is empty",
            excerpt=None,
            suggestion="Add relevant tags",
        )
        data = issue.model_dump()
        assert data["line"] is None
        assert data["excerpt"] is None


class TestValidationResult:
    """Test ValidationResult Pydantic model."""

    def test_create_passed_result_no_issues(self) -> None:
        """Test creating validation result that passed with no issues."""
        result = ValidationResult(
            file=Path("/prompts/test.md"),
            status="passed",
            errors=[],
            warnings=[],
        )
        assert result.file == Path("/prompts/test.md")
        assert result.status == "passed"
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
        assert result.is_valid is True

    def test_create_failed_result_with_errors(self) -> None:
        """Test creating validation result that failed with errors."""
        error = ValidationIssue(
            line=5,
            severity=ValidationSeverity.ERROR,
            code=ErrorCode.MISSING_REQUIRED_FIELD.value,
            message="Missing required field 'name'",
            excerpt=None,
            suggestion="Add name field",
        )
        result = ValidationResult(
            file=Path("/prompts/bad.md"),
            status="failed",
            errors=[error],
            warnings=[],
        )
        assert result.file == Path("/prompts/bad.md")
        assert result.status == "failed"
        assert len(result.errors) == 1
        assert result.errors[0].code == ErrorCode.MISSING_REQUIRED_FIELD.value
        assert result.is_valid is False

    def test_passed_result_with_warnings_only(self) -> None:
        """Test validation result passes with warnings but no errors."""
        warning = ValidationIssue(
            line=None,
            severity=ValidationSeverity.WARNING,
            code=WarningCode.MISSING_AUTHOR.value,
            message="Missing optional field 'author'",
            excerpt=None,
            suggestion="Consider adding author",
        )
        result = ValidationResult(
            file=Path("/prompts/test.md"),
            status="passed",
            errors=[],
            warnings=[warning],
        )
        assert result.status == "passed"
        assert len(result.warnings) == 1
        assert len(result.errors) == 0
        assert result.is_valid is True  # Warnings don't block

    def test_failed_result_with_multiple_errors(self) -> None:
        """Test validation result with multiple errors."""
        errors = [
            ValidationIssue(
                line=1,
                severity=ValidationSeverity.ERROR,
                code=ErrorCode.MISSING_REQUIRED_FIELD.value,
                message="Missing 'name'",
                excerpt=None,
                suggestion="Add name",
            ),
            ValidationIssue(
                line=2,
                severity=ValidationSeverity.ERROR,
                code=ErrorCode.INVALID_YAML.value,
                message="Invalid YAML",
                excerpt=None,
                suggestion="Fix YAML",
            ),
        ]
        result = ValidationResult(
            file=Path("/prompts/bad.md"),
            status="failed",
            errors=errors,
            warnings=[],
        )
        assert len(result.errors) == 2
        assert result.is_valid is False

    def test_json_serialization(self) -> None:
        """Test ValidationResult serializes to JSON correctly."""
        error = ValidationIssue(
            line=10,
            severity=ValidationSeverity.ERROR,
            code=ErrorCode.NO_SEPARATOR.value,
            message="No separator found",
            excerpt=None,
            suggestion="Add >>> separator",
        )
        result = ValidationResult(
            file=Path("/prompts/test.md"),
            status="failed",
            errors=[error],
            warnings=[],
        )
        data = result.model_dump()
        assert str(data["file"]) == str(Path("/prompts/test.md"))
        assert data["status"] == "failed"
        assert len(data["errors"]) == 1
        assert data["errors"][0]["code"] == "NO_SEPARATOR"

    def test_is_valid_property(self) -> None:
        """Test is_valid computed property logic."""
        # Valid: no errors
        valid_result = ValidationResult(
            file=Path("test.md"), status="passed", errors=[], warnings=[]
        )
        assert valid_result.is_valid is True

        # Invalid: has errors
        invalid_result = ValidationResult(
            file=Path("test.md"),
            status="failed",
            errors=[
                ValidationIssue(
                    line=1,
                    severity=ValidationSeverity.ERROR,
                    code=ErrorCode.INVALID_YAML.value,
                    message="Error",
                    excerpt=None,
                    suggestion="Fix",
                )
            ],
            warnings=[],
        )
        assert invalid_result.is_valid is False
