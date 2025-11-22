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

        Reads the file as binary, handles optional UTF-8 BOM, and attempts strict UTF-8 decoding.
        Returns the decoded content (with BOM stripped) or None with an INVALID_ENCODING issue.
        """
        issues: list[ValidationIssue] = []
        try:
            raw_bytes = file_path.read_bytes()
            # Handle UTF-8 BOM (EF BB BF)
            if raw_bytes.startswith(b"\xef\xbb\xbf"):
                raw_bytes = raw_bytes[3:]
            # Empty file is valid UTF-8
            if not raw_bytes:
                return "", issues
            # Attempt strict UTF-8 decode
            content = raw_bytes.decode("utf-8", errors="strict")
            return content, issues
        except UnicodeDecodeError as e:
            issues.append(
                ValidationIssue(
                    line=None,
                    severity=ValidationSeverity.ERROR,
                    code=ErrorCode.INVALID_ENCODING.value,
                    message=f"File is not valid UTF-8: {e}",
                    excerpt=None,
                    suggestion=(
                        "Convert file to UTF-8 encoding using a text editor or conversion tool."
                    ),
                )
            )
            return None, issues
        except FileNotFoundError:
            issues.append(
                ValidationIssue(
                    line=None,
                    severity=ValidationSeverity.ERROR,
                    code=ErrorCode.INVALID_ENCODING.value,
                    message=f"File not found: {file_path}",
                    excerpt=None,
                    suggestion="Check that the file path is correct and the file exists",
                )
            )
            return None, issues
        except PermissionError:
            issues.append(
                ValidationIssue(
                    line=None,
                    severity=ValidationSeverity.ERROR,
                    code=ErrorCode.INVALID_ENCODING.value,
                    message=f"Permission denied reading file: {file_path}",
                    excerpt=None,
                    suggestion="Check file permissions and ensure you have read access",
                )
            )
            return None, issues
        except OSError as e:
            issues.append(
                ValidationIssue(
                    line=None,
                    severity=ValidationSeverity.ERROR,
                    code=ErrorCode.INVALID_ENCODING.value,
                    message=f"Error reading file: {e}",
                    excerpt=None,
                    suggestion="Check file accessibility and system permissions",
                )
            )
            return None, issues
