"""Output formatters for validation results.

This package provides formatters for displaying validation results in
different formats (Rich terminal output, JSON, etc.).
"""

from prompt_unifier.output.json_formatter import JSONFormatter
from prompt_unifier.output.rich_formatter import RichFormatter

__all__ = ["RichFormatter", "JSONFormatter"]
