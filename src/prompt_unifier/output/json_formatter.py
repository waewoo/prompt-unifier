"""JSON output formatter for validation results.

This module provides JSON formatting for validation results,
suitable for machine-readable output and integration with other tools.
"""

import json
from pathlib import Path

from prompt_unifier.models.validation import ValidationSummary


class JSONFormatter:
    """Formats validation results as JSON for machine-readable output.

    This formatter converts ValidationSummary objects into structured JSON
    with summary statistics and detailed results for each file.

    Examples:
        >>> formatter = JSONFormatter()
        >>> summary = ValidationSummary(...)
        >>> json_output = formatter.format_summary(summary, Path("./prompts"))
        >>> print(json_output)
    """

    def format_summary(self, summary: ValidationSummary, directory: Path) -> str:
        """Format a validation summary as JSON string.

        Converts the validation summary into a JSON structure containing:
        - summary: aggregate statistics (total_files, passed, failed, etc.)
        - results: array of per-file validation results with errors/warnings

        Args:
            summary: The validation summary containing all results
            directory: The directory that was validated

        Returns:
            Pretty-printed JSON string (indent=2)

        Examples:
            >>> formatter = JSONFormatter()
            >>> summary = ValidationSummary(
            ...     total_files=2,
            ...     passed=1,
            ...     failed=1,
            ...     error_count=1,
            ...     warning_count=0,
            ...     success=False,
            ...     results=[]
            ... )
            >>> json_str = formatter.format_summary(summary, Path("./prompts"))
        """
        # Build the JSON structure
        output = {
            "summary": {
                "total_files": summary.total_files,
                "passed": summary.passed,
                "failed": summary.failed,
                "error_count": summary.error_count,
                "warning_count": summary.warning_count,
                "success": summary.success,
            },
            "results": [
                {
                    "file": result.file.name,
                    "status": result.status,
                    "errors": [
                        {
                            "line": error.line,
                            "severity": error.severity.value,
                            "code": error.code,
                            "message": error.message,
                            "excerpt": error.excerpt,
                            "suggestion": error.suggestion,
                        }
                        for error in result.errors
                    ],
                    "warnings": [
                        {
                            "line": warning.line,
                            "severity": warning.severity.value,
                            "code": warning.code,
                            "message": warning.message,
                            "excerpt": warning.excerpt,
                            "suggestion": warning.suggestion,
                        }
                        for warning in result.warnings
                    ],
                }
                for result in summary.results
            ],
        }

        # Return pretty-printed JSON
        return json.dumps(output, indent=2)
