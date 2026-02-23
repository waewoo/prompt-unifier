"""Batch validation orchestrator for multiple prompt files.

This module provides the BatchValidator class for validating multiple
prompt files in a directory and aggregating the results.
"""

import logging
from pathlib import Path

from prompt_unifier.core.content_parser import ContentFileParser
from prompt_unifier.core.scaff_validator import SCARFFValidator
from prompt_unifier.core.skill_validator import SkillContentValidator
from prompt_unifier.core.validator import PromptValidator
from prompt_unifier.models.validation import (
    ValidationResult,
    ValidationSummary,
)
from prompt_unifier.utils.file_scanner import FileScanner

# Get logger for this module
logger = logging.getLogger(__name__)


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
        self.scaff_validator = SCARFFValidator()
        self.skill_parser = ContentFileParser()
        self.skill_content_validator = SkillContentValidator()

    def validate_directory(self, directory: Path, scaff_enabled: bool = True) -> ValidationSummary:
        """Validate all .md files in a directory and return summary.

        This method performs the following steps:
        1. Scan directory recursively for .md files using FileScanner
        2. Validate each file independently using PromptValidator
        3. Optionally run SCAFF validation if scaff_enabled is True
        4. Collect all ValidationResult objects
        5. Compute summary statistics (total, passed, failed, error counts)
        6. Return ValidationSummary with all results and statistics

        Validation continues even if individual files fail, ensuring
        that all files are validated and all errors are reported.

        Args:
            directory: Path to the directory containing .md files to validate
            scaff_enabled: Enable SCAFF methodology validation (default: True)

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
        logger.debug(f"Scanning directory: {directory}")

        # Step 1: Discover all .md files
        md_files = self.file_scanner.scan_directory(directory)

        logger.info(f"Found {len(md_files)} .md files to validate")

        # Step 2: Validate each file independently
        results: list[ValidationResult] = []
        for file_path in md_files:
            logger.debug(f"Validating file: {file_path}")

            # Format validation (required)
            result = self.prompt_validator.validate_file(file_path)

            # SCAFF validation (optional, enabled by default)
            if scaff_enabled and result.status == "passed":
                # Only run SCAFF validation if format validation passed
                # Read file content for SCAFF analysis
                try:
                    content = file_path.read_text(encoding="utf-8")

                    # Extract content after separator (handles both formats)
                    prompt_content = content
                    if ">>>" in content:
                        # Rules format: key: value >>> content
                        _, prompt_content = content.split(">>>", 1)
                        prompt_content = prompt_content.strip()
                    elif content.startswith("---"):
                        # Prompts format: ---\nkey: value\n---\ncontent
                        parts = content.split("---", 2)
                        if len(parts) >= 3:
                            prompt_content = parts[2].strip()

                    # Run SCAFF validation
                    scaff_score = self.scaff_validator.validate_content(prompt_content)

                    # Generate SCAFF issues (warnings) for failed components
                    scaff_issues = self.scaff_validator.generate_issues(prompt_content)

                    # Attach SCAFF score to result
                    result.scaff_score = scaff_score

                    # Merge SCAFF warnings into result.warnings
                    result.warnings.extend(scaff_issues)

                    logger.debug(
                        f"SCAFF validation for {file_path}: "
                        f"score={scaff_score.total_score}/100, "
                        f"warnings={len(scaff_issues)}"
                    )
                except Exception as e:
                    logger.warning(f"SCAFF validation failed for {file_path}: {e}")
                    # Continue without SCAFF score if validation fails

            results.append(result)

        # Step 3: Compute and return ValidationSummary
        return self._build_summary(results)

    def validate_skill_directory(self, directory: Path) -> ValidationSummary:
        """Validate all .md files in a skills directory using SkillFrontmatter schema.

        Skills are validated against the SkillFrontmatter schema (name, description,
        optional mode/license/...), then content quality checks are applied via
        SkillContentValidator (warnings only, no errors).

        Args:
            directory: Path to the directory containing skill .md files.

        Returns:
            ValidationSummary with aggregated results.
        """
        logger.debug(f"Scanning skills directory: {directory}")
        md_files = self.file_scanner.scan_directory(directory)
        logger.info(f"Found {len(md_files)} skill file(s) to validate")

        results: list[ValidationResult] = []
        for fp in md_files:
            result = self.skill_parser.validate_file(fp)

            if result.status == "passed":
                try:
                    parsed = self.skill_parser.parse_skill_file(fp)
                    skill_issues = self.skill_content_validator.generate_issues(
                        parsed, parsed.content
                    )
                    result.warnings.extend(skill_issues)
                    logger.debug(f"Skill content validation for {fp}: warnings={len(skill_issues)}")
                except Exception as e:
                    logger.warning(f"Skill content validation failed for {fp}: {e}")

            results.append(result)

        return self._build_summary(results)

    def _build_summary(self, results: list[ValidationResult]) -> ValidationSummary:
        """Build a ValidationSummary from a list of results."""
        total_files = len(results)
        passed_files = sum(1 for r in results if r.status == "passed")
        failed_files = sum(1 for r in results if r.status == "failed")
        total_errors = sum(len(r.errors) for r in results)
        total_warnings = sum(len(r.warnings) for r in results)

        return ValidationSummary(
            total_files=total_files,
            passed=passed_files,
            failed=failed_files,
            error_count=total_errors,
            warning_count=total_warnings,
            success=total_errors == 0,
            results=results,
        )
