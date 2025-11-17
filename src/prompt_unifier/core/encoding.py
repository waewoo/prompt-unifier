"""UTF-8 encoding validation for prompt files.

This module validates that files are encoded in UTF-8 with strict error handling.
"""

from pathlib import Path

from prompt_unifier.models.validation import ErrorCode, ValidationIssue, ValidationSeverity


class EncodingValidator:
    """Validates UTF-8 encoding for prompt files.

    This validator ensures files are valid UTF-8 with strict error handling.
    Files that cannot be decoded as UTF-8 are rejected.

    Examples:
        >>> validator = EncodingValidator()
        >>> from pathlib import Path
        >>> # Assuming valid_file.md exists with UTF-8 encoding
        >>> content, issues = validator.validate_encoding(Path("valid_file.md"))
        >>> len(issues)
        0
    """

    def validate_encoding(self, file_path: Path) -> tuple[str | None, list[ValidationIssue]]:
        """Validate that the file is encoded in UTF-8.

        Attempts to read the file with strict UTF-8 encoding. If the file
        cannot be decoded as UTF-8, an INVALID_ENCODING error is generated.

        Args:
            file_path: Path to the file to validate

        Returns:
            A tuple containing:
            - file_content: The file content as a string, or None if encoding failed
            - issues: List of ValidationIssue objects for any problems found

        Note:
            File system errors (FileNotFoundError, PermissionError) are caught
            and converted to validation issues. When encoding fails, None is
            returned for content to allow the rest of the pipeline to skip
            processing.

        Examples:
            >>> validator = EncodingValidator()
            >>> content, issues = validator.validate_encoding(Path("test.md"))
            >>> if content is None:
            ...     print("Encoding validation failed")
        """
        issues: list[ValidationIssue] = []

        try:
            # Read file with strict UTF-8 encoding (no error tolerance)
            content = file_path.read_text(encoding="utf-8", errors="strict")
            return content, issues

        except UnicodeDecodeError as e:
            # Invalid UTF-8 bytes detected
            issues.append(
                ValidationIssue(
                    line=None,  # Cannot determine line number for encoding errors
                    severity=ValidationSeverity.ERROR,
                    code=ErrorCode.INVALID_ENCODING.value,
                    message=f"File is not valid UTF-8: {e.reason}",
                    excerpt=None,
                    suggestion=(
                        "Convert file to UTF-8 encoding using a text editor "
                        "or encoding conversion tool"
                    ),
                )
            )
            return None, issues

        except FileNotFoundError:
            # File does not exist
            issues.append(
                ValidationIssue(
                    line=None,
                    severity=ValidationSeverity.ERROR,
                    code=ErrorCode.INVALID_ENCODING.value,  # Using generic error code
                    message=f"File not found: {file_path}",
                    excerpt=None,
                    suggestion="Check that the file path is correct and the file exists",
                )
            )
            return None, issues

        except PermissionError:
            # Cannot read file due to permissions
            issues.append(
                ValidationIssue(
                    line=None,
                    severity=ValidationSeverity.ERROR,
                    code=ErrorCode.INVALID_ENCODING.value,  # Using generic error code
                    message=f"Permission denied reading file: {file_path}",
                    excerpt=None,
                    suggestion="Check file permissions and ensure you have read access",
                )
            )
            return None, issues

        except OSError as e:
            # Other file system errors
            issues.append(
                ValidationIssue(
                    line=None,
                    severity=ValidationSeverity.ERROR,
                    code=ErrorCode.INVALID_ENCODING.value,  # Using generic error code
                    message=f"Error reading file: {e}",
                    excerpt=None,
                    suggestion="Check file accessibility and system permissions",
                )
            )
            return None, issues
