"""Main validation orchestrator for prompt files.

This module orchestrates the complete validation pipeline, coordinating
encoding, separator, YAML, and schema validation steps.
"""

from pathlib import Path
from typing import Any, Literal

from pydantic import ValidationError
from pydantic_core import ErrorDetails

from prompt_unifier.core.encoding import EncodingValidator
from prompt_unifier.core.separator import SeparatorValidator
from prompt_unifier.core.yaml_parser import YAMLParser
from prompt_unifier.models.prompt import PromptFrontmatter
from prompt_unifier.models.validation import (
    ErrorCode,
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
    WarningCode,
)


class PromptValidator:
    """Orchestrates the complete validation pipeline for prompt files.

    This validator coordinates all validation steps:
    1. UTF-8 encoding validation
    2. Separator detection and validation
    3. YAML parsing and structure validation
    4. Pydantic schema validation
    5. Warning detection for missing optional fields

    The validator continues processing even after errors to collect all
    issues in a single pass.

    Examples:
        >>> validator = PromptValidator()
        >>> from pathlib import Path
        >>> result = validator.validate_file(Path("prompt.md"))
        >>> result.is_valid
        True
    """

    def __init__(self) -> None:
        """Initialize the PromptValidator with component validators."""
        self.encoding_validator = EncodingValidator()
        self.separator_validator = SeparatorValidator()
        self.yaml_parser = YAMLParser()

    def validate_file(self, file_path: Path) -> ValidationResult:
        """Validate a prompt file through the complete pipeline.

        This method orchestrates all validation steps:
        1. Encoding validation (UTF-8 strict)
        2. Separator validation (exactly one >>> on its own line)
        3. YAML parsing (valid syntax, flat structure)
        4. Schema validation (Pydantic model)
        5. Warning detection (missing optional fields, empty tags)

        All errors and warnings are collected without early termination.

        Args:
            file_path: Path to the prompt file to validate

        Returns:
            ValidationResult containing file path, status, errors, and warnings

        Examples:
            >>> validator = PromptValidator()
            >>> result = validator.validate_file(Path("test.md"))
            >>> if result.is_valid:
            ...     print("Validation passed!")
        """
        all_errors: list[ValidationIssue] = []
        all_warnings: list[ValidationIssue] = []

        # Step 1: Encoding validation
        file_content, encoding_issues = self.encoding_validator.validate_encoding(file_path)
        all_errors.extend(
            [issue for issue in encoding_issues if issue.severity == ValidationSeverity.ERROR]
        )
        all_warnings.extend(
            [issue for issue in encoding_issues if issue.severity == ValidationSeverity.WARNING]
        )

        # If encoding failed, we can't proceed with content parsing
        if file_content is None:
            return ValidationResult(
                file=file_path,
                status="failed",
                errors=all_errors,
                warnings=all_warnings,
            )

        # Step 2: Separator validation
        frontmatter_text, content_text, separator_issues = (
            self.separator_validator.validate_separator(file_content)
        )
        all_errors.extend(
            [issue for issue in separator_issues if issue.severity == ValidationSeverity.ERROR]
        )
        all_warnings.extend(
            [issue for issue in separator_issues if issue.severity == ValidationSeverity.WARNING]
        )

        # Step 3: YAML parsing
        yaml_dict, yaml_issues = self.yaml_parser.parse_yaml(frontmatter_text)
        all_errors.extend(
            [issue for issue in yaml_issues if issue.severity == ValidationSeverity.ERROR]
        )
        all_warnings.extend(
            [issue for issue in yaml_issues if issue.severity == ValidationSeverity.WARNING]
        )

        # Step 4: Schema validation with Pydantic
        # Only proceed if we have a valid YAML dict
        if yaml_dict is not None:
            # Check for prohibited fields BEFORE Pydantic validation
            prohibited_issues = self._check_prohibited_fields(yaml_dict)
            all_errors.extend(prohibited_issues)

            # Attempt Pydantic validation
            pydantic_issues = self._validate_with_pydantic(yaml_dict)
            all_errors.extend(
                [issue for issue in pydantic_issues if issue.severity == ValidationSeverity.ERROR]
            )
            all_warnings.extend(
                [issue for issue in pydantic_issues if issue.severity == ValidationSeverity.WARNING]
            )

            # Step 5: Warning detection for missing optional fields
            warning_issues = self._detect_warnings(yaml_dict)
            all_warnings.extend(warning_issues)

        # Determine final status
        status: Literal["passed", "failed"] = "failed" if len(all_errors) > 0 else "passed"

        return ValidationResult(
            file=file_path,
            status=status,
            errors=all_errors,
            warnings=all_warnings,
        )

    def _check_prohibited_fields(self, yaml_dict: dict[str, Any]) -> list[ValidationIssue]:
        """Check for prohibited fields in the YAML dictionary.

        Args:
            yaml_dict: The parsed YAML dictionary to check

        Returns:
            List of ValidationIssue objects for each prohibited field found
        """
        issues: list[ValidationIssue] = []
        prohibited_fields = ["tools"]

        for field in prohibited_fields:
            if field in yaml_dict:
                issues.append(
                    ValidationIssue(
                        line=None,
                        severity=ValidationSeverity.ERROR,
                        code=ErrorCode.PROHIBITED_FIELD.value,
                        message=f"Prohibited field '{field}' found in frontmatter",
                        excerpt=None,
                        suggestion=f"Remove the '{field}' field from the frontmatter",
                    )
                )

        return issues

    def _validate_with_pydantic(self, yaml_dict: dict[str, Any]) -> list[ValidationIssue]:
        """Validate YAML data against the Pydantic model.

        This method attempts to instantiate the PromptFrontmatter model and
        translates any Pydantic ValidationError into our ValidationIssue format.

        Args:
            yaml_dict: The parsed YAML dictionary to validate

        Returns:
            List of ValidationIssue objects for any validation errors
        """
        issues: list[ValidationIssue] = []

        try:
            # Attempt to validate with Pydantic model
            PromptFrontmatter(**yaml_dict)
        except ValidationError as e:
            # Translate Pydantic errors to ValidationIssue objects
            for error in e.errors():
                issue = self._translate_pydantic_error(error)
                issues.append(issue)

        return issues

    def _translate_pydantic_error(self, error: ErrorDetails) -> ValidationIssue:
        """Translate a Pydantic validation error to a ValidationIssue.

        Maps Pydantic error types to our error codes and generates
        actionable suggestions.

        Args:
            error: Pydantic error details dictionary with 'type', 'loc', 'msg', etc.

        Returns:
            ValidationIssue object representing the error
        """
        error_type = error.get("type", "")
        location = error.get("loc", ())
        message = error.get("msg", "Validation error")

        # Extract field name from location tuple
        field_name = str(location[0]) if location else "unknown"

        # Determine error code and suggestion based on error type and field
        if error_type == "missing":
            code = ErrorCode.MISSING_REQUIRED_FIELD.value
            issue_message = f"Missing required field '{field_name}'"
            suggestion = f"Add '{field_name}' field to frontmatter"
        elif field_name == "version":
            # Any error on the version field is treated as INVALID_SEMVER
            # This includes type errors (e.g., YAML parsing 1.0 as float)
            # and value errors (e.g., invalid format like "1.0")
            code = ErrorCode.INVALID_SEMVER.value
            issue_message = f"Invalid semantic version format: {message}"
            suggestion = (
                "Use semantic versioning format (e.g., '1.0.0'). "
                "Ensure version is quoted in YAML if needed."
            )
        elif error_type == "extra_forbidden":
            code = ErrorCode.PROHIBITED_FIELD.value
            issue_message = f"Prohibited field '{field_name}' found in frontmatter"
            suggestion = f"Remove the '{field_name}' field from the frontmatter"
        else:
            # Generic validation error
            code = ErrorCode.MISSING_REQUIRED_FIELD.value  # Default
            issue_message = f"Validation error for field '{field_name}': {message}"
            suggestion = f"Fix the '{field_name}' field according to the error message"

        return ValidationIssue(
            line=None,  # Pydantic errors don't have line numbers
            severity=ValidationSeverity.ERROR,
            code=code,
            message=issue_message,
            excerpt=None,
            suggestion=suggestion,
        )

    def _detect_warnings(self, yaml_dict: dict[str, Any]) -> list[ValidationIssue]:
        """Detect warnings for missing optional fields and empty values.

        Checks for:
        - Missing 'version' field
        - Missing 'author' field
        - Empty 'tags' list

        Args:
            yaml_dict: The parsed YAML dictionary to check

        Returns:
            List of ValidationIssue objects with warnings
        """
        warnings: list[ValidationIssue] = []

        # Check for missing optional fields
        optional_fields = ["version", "author"]
        for field in optional_fields:
            if field not in yaml_dict or yaml_dict[field] is None:
                warnings.append(
                    ValidationIssue(
                        line=None,
                        severity=ValidationSeverity.WARNING,
                        code=WarningCode.MISSING_OPTIONAL_FIELD.value,
                        message=f"Missing optional field '{field}'",
                        excerpt=None,
                        suggestion=f"Consider adding '{field}' field to provide more metadata",
                    )
                )

        # Check for empty tags list
        if "tags" in yaml_dict:
            tags = yaml_dict["tags"]
            if isinstance(tags, list) and len(tags) == 0:
                warnings.append(
                    ValidationIssue(
                        line=None,
                        severity=ValidationSeverity.WARNING,
                        code=WarningCode.EMPTY_TAGS_LIST.value,
                        message="Tags list is empty",
                        excerpt=None,
                        suggestion=(
                            "Add tags to categorize this prompt, or remove the empty " "tags field"
                        ),
                    )
                )

        return warnings
