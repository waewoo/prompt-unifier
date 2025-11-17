"""Validation models and enumerations for error/warning classification.

This module provides the data structures for representing validation results,
including error codes, severity levels, and validation issues.
"""

from enum import Enum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class ValidationSeverity(str, Enum):
    """Severity levels for validation issues.

    Attributes:
        ERROR: Critical validation failure that blocks deployment
        WARNING: Non-critical issue that does not block deployment
    """

    ERROR = "error"
    WARNING = "warning"


class ErrorCode(str, Enum):
    """Error codes for validation failures that block deployment.

    These errors represent critical format violations that must be fixed
    before the prompt file can be considered valid.
    """

    INVALID_ENCODING = "INVALID_ENCODING"
    """File is not valid UTF-8"""

    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    """Required field (name or description) is missing"""

    INVALID_YAML = "INVALID_YAML"
    """YAML syntax error in frontmatter"""

    NESTED_STRUCTURE = "NESTED_STRUCTURE"
    """Nested YAML structures are not allowed"""

    NO_SEPARATOR = "NO_SEPARATOR"
    """Missing >>> separator"""

    MULTIPLE_SEPARATORS = "MULTIPLE_SEPARATORS"
    """More than one >>> separator found"""

    SEPARATOR_NOT_ALONE = "SEPARATOR_NOT_ALONE"
    """Separator >>> is not on its own line"""

    SEPARATOR_WHITESPACE = "SEPARATOR_WHITESPACE"
    """Whitespace found around >>> separator"""

    EMPTY_CONTENT = "EMPTY_CONTENT"
    """No content after >>> separator"""

    INVALID_SEMVER = "INVALID_SEMVER"
    """Invalid semantic version format"""

    PROHIBITED_FIELD = "PROHIBITED_FIELD"
    """Prohibited field found in frontmatter (e.g., 'tools')"""

    INVALID_FILE_EXTENSION = "INVALID_FILE_EXTENSION"
    """File does not have .md extension"""


class WarningCode(str, Enum):
    """Warning codes for non-critical validation issues.

    These warnings do not block deployment but indicate potential improvements
    or missing optional information.
    """

    MISSING_OPTIONAL_FIELD = "MISSING_OPTIONAL_FIELD"
    """Optional field (version or author) is missing"""

    EMPTY_TAGS_LIST = "EMPTY_TAGS_LIST"
    """Tags list is empty"""

    MISSING_AUTHOR = "MISSING_AUTHOR"
    """Author field is not provided"""


class ValidationIssue(BaseModel):
    """Represents a single validation error or warning.

    This model captures all information about a validation issue including
    its location, severity, error code, message, and suggested fix.

    Attributes:
        line: Line number where the issue occurs (None if not applicable)
        severity: ERROR or WARNING severity level
        code: Specific error/warning code identifier
        message: Human-readable description of the issue
        excerpt: Code snippet showing the problematic content (optional)
        suggestion: Actionable suggestion for fixing the issue

    Examples:
        >>> issue = ValidationIssue(
        ...     line=5,
        ...     severity=ValidationSeverity.ERROR,
        ...     code=ErrorCode.MISSING_REQUIRED_FIELD.value,
        ...     message="Missing required field 'description'",
        ...     excerpt="name: test-prompt",
        ...     suggestion="Add 'description' field to frontmatter"
        ... )
        >>> issue.severity
        <ValidationSeverity.ERROR: 'error'>
    """

    line: int | None = Field(description="Line number of the issue (None if not line-specific)")
    severity: ValidationSeverity = Field(description="Severity level: ERROR or WARNING")
    code: str = Field(description="Error or warning code identifier")
    message: str = Field(description="Human-readable description of the issue")
    excerpt: str | None = Field(
        default=None, description="Code snippet showing problematic content"
    )
    suggestion: str = Field(description="Actionable suggestion for fixing the issue")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "line": 5,
                    "severity": "error",
                    "code": "MISSING_REQUIRED_FIELD",
                    "message": "Missing required field 'description'",
                    "excerpt": "name: test-prompt\n>>>",
                    "suggestion": "Add 'description' field to frontmatter",
                }
            ]
        }
    }


class ValidationResult(BaseModel):
    """Represents the validation result for a single file.

    This model aggregates all validation issues found in a file and
    determines the overall validation status.

    Attributes:
        file: Path to the validated file
        status: "passed" if no errors, "failed" if any errors present
        errors: List of validation errors (block deployment)
        warnings: List of validation warnings (do not block)

    Properties:
        is_valid: True if status is "passed" (no errors)

    Examples:
        >>> from pathlib import Path
        >>> result = ValidationResult(
        ...     file=Path("test.md"),
        ...     status="passed",
        ...     errors=[],
        ...     warnings=[]
        ... )
        >>> result.is_valid
        True
    """

    file: Path = Field(description="Path to the validated file")
    status: Literal["passed", "failed"] = Field(description="Overall validation status")
    errors: list[ValidationIssue] = Field(
        default_factory=list, description="List of validation errors"
    )
    warnings: list[ValidationIssue] = Field(
        default_factory=list, description="List of validation warnings"
    )

    @property
    def is_valid(self) -> bool:
        """Check if the validation passed (no errors).

        Returns:
            True if there are no errors, False otherwise
        """
        return len(self.errors) == 0

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "file": "python-expert.md",
                    "status": "passed",
                    "errors": [],
                    "warnings": [
                        {
                            "line": None,
                            "severity": "warning",
                            "code": "MISSING_OPTIONAL_FIELD",
                            "message": "Missing optional field 'author'",
                            "excerpt": None,
                            "suggestion": "Consider adding 'author' field",
                        }
                    ],
                }
            ]
        }
    }


class ValidationSummary(BaseModel):
    """Represents the aggregated validation summary for multiple files.

    This model aggregates validation results across all files in a
    directory and provides summary statistics.

    Attributes:
        total_files: Total number of files validated
        passed: Number of files that passed validation (no errors)
        failed: Number of files that failed validation (had errors)
        error_count: Total number of errors across all files
        warning_count: Total number of warnings across all files
        success: True if no errors across all files, False otherwise
        results: List of individual file validation results

    Examples:
        >>> from pathlib import Path
        >>> summary = ValidationSummary(
        ...     total_files=3,
        ...     passed=2,
        ...     failed=1,
        ...     error_count=1,
        ...     warning_count=2,
        ...     success=False,
        ...     results=[]
        ... )
        >>> summary.success
        False
    """

    total_files: int = Field(description="Total number of files validated")
    passed: int = Field(description="Number of files that passed validation")
    failed: int = Field(description="Number of files that failed validation")
    error_count: int = Field(description="Total number of errors across all files")
    warning_count: int = Field(description="Total number of warnings across all files")
    success: bool = Field(description="True if no errors across all files, False otherwise")
    results: list[ValidationResult] = Field(
        default_factory=list, description="Individual file validation results"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "total_files": 3,
                    "passed": 2,
                    "failed": 1,
                    "error_count": 1,
                    "warning_count": 2,
                    "success": False,
                    "results": [
                        {
                            "file": "python-expert.md",
                            "status": "passed",
                            "errors": [],
                            "warnings": [
                                {
                                    "line": None,
                                    "severity": "warning",
                                    "code": "MISSING_OPTIONAL_FIELD",
                                    "message": "Missing optional field 'author'",
                                    "excerpt": None,
                                    "suggestion": "Consider adding 'author' field",
                                }
                            ],
                        },
                        {
                            "file": "broken-prompt.md",
                            "status": "failed",
                            "errors": [
                                {
                                    "line": 1,
                                    "severity": "error",
                                    "code": "MISSING_REQUIRED_FIELD",
                                    "message": "Missing required field 'description'",
                                    "excerpt": "name: broken-prompt\n>>>",
                                    "suggestion": "Add 'description' field to frontmatter",
                                }
                            ],
                            "warnings": [],
                        },
                    ],
                }
            ]
        }
    }
