"""Batch validation orchestrator for multiple prompt files.

This module provides the BatchValidator class for validating multiple
prompt files in a directory and aggregating the results.
"""

from pathlib import Path

from prompt_unifier.core.validator import PromptValidator
from prompt_unifier.models.validation import ValidationResult, ValidationSummary
from prompt_unifier.utils.file_scanner import FileScanner


class BatchValidator:
    """Orchestrates validation of multiple prompt files in a directory.

    The BatchValidator discovers all .md files in a directory tree,
    validates each file independently, and aggregates the results
    into a summary report with statistics.

    The validator continues processing all files even if individual
    files fail validation, ensuring complete error reporting.

    Examples:
        >>> validator = BatchValidator()
        >>> summary = validator.validate_directory(Path("./prompts"))
        >>> print(f"Validated {summary.total_files} files")
        Validated 5 files
        >>> print(f"Success: {summary.success}")
        Success: True
    """

    def __init__(self) -> None:
        """Initialize the BatchValidator with component validators."""
        self.file_scanner = FileScanner()
        self.prompt_validator = PromptValidator()

    def validate_directory(self, directory: Path) -> ValidationSummary:
        """Validate all .md files in a directory and return summary.

        This method performs the following steps:
        1. Scan directory recursively for .md files using FileScanner
        2. Validate each file independently using PromptValidator
        3. Collect all ValidationResult objects
        4. Compute summary statistics (total, passed, failed, error counts)
        5. Return ValidationSummary with all results and statistics

        Validation continues even if individual files fail, ensuring
        that all files are validated and all errors are reported.

        Args:
            directory: Path to the directory containing .md files to validate

        Returns:
            ValidationSummary containing aggregated statistics and individual
            file results

        Raises:
            FileNotFoundError: If the directory does not exist (raised by FileScanner)

        Examples:
            >>> validator = BatchValidator()
            >>> summary = validator.validate_directory(Path("./prompts"))
            >>> if summary.success:
            ...     print("All files passed validation!")
            ... else:
            ...     print(f"{summary.failed} files failed validation")
        """
        # Step 1: Discover all .md files
        md_files = self.file_scanner.scan_directory(directory)

        # Step 2: Validate each file independently
        results: list[ValidationResult] = []
        for file_path in md_files:
            result = self.prompt_validator.validate_file(file_path)
            results.append(result)

        # Step 3: Compute summary statistics
        total_files = len(results)
        passed_files = sum(1 for r in results if r.status == "passed")
        failed_files = sum(1 for r in results if r.status == "failed")

        # Count total errors and warnings across all files
        total_errors = sum(len(r.errors) for r in results)
        total_warnings = sum(len(r.warnings) for r in results)

        # Success is True if no errors across all files
        success = total_errors == 0

        # Step 4: Create and return ValidationSummary
        return ValidationSummary(
            total_files=total_files,
            passed=passed_files,
            failed=failed_files,
            error_count=total_errors,
            warning_count=total_warnings,
            success=success,
            results=results,
        )
