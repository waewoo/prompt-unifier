"""Utility for extracting code excerpts with context around error lines.

This module provides functionality to extract snippets of file content
with line numbers for displaying in validation error messages.
"""


class ExcerptFormatter:
    """Extracts and formats code excerpts with line numbers for error display.

    This formatter extracts a specified line along with surrounding context
    lines, formatting them with line numbers for clear error reporting.

    Examples:
        >>> formatter = ExcerptFormatter()
        >>> content = "line 1\\nline 2\\nline 3\\nline 4\\nline 5"
        >>> excerpt = formatter.extract_excerpt(content, line_number=3, context_lines=1)
        >>> print(excerpt)
        2 | line 2
        3 | line 3
        4 | line 4
    """

    def extract_excerpt(self, file_content: str, line_number: int, context_lines: int = 1) -> str:
        """Extract a code excerpt with context lines around a specific line.

        Extracts the specified line along with `context_lines` lines before and
        after it. Handles edge cases at the start and end of files gracefully.

        Args:
            file_content: The full content of the file as a string
            line_number: The line number to extract (1-indexed)
            context_lines: Number of lines to show before and after (default: 1)

        Returns:
            A formatted multi-line string with line numbers and content,
            in the format "N | content here"

        Examples:
            >>> formatter = ExcerptFormatter()
            >>> content = "name: test\\ndescription: Test\\n>>>\\nContent"
            >>> formatter.extract_excerpt(content, 2, 1)
            '1 | name: test\\n2 | description: Test\\n3 | >>>'
        """
        # Split content into lines
        lines = file_content.split("\n")

        # Calculate the range of lines to extract (1-indexed to 0-indexed conversion)
        start_line = max(0, line_number - context_lines - 1)
        end_line = min(len(lines), line_number + context_lines)

        # Extract the relevant lines with line numbers
        excerpt_lines = []
        for i in range(start_line, end_line):
            line_num = i + 1  # Convert back to 1-indexed
            line_content = lines[i] if i < len(lines) else ""
            excerpt_lines.append(f"{line_num} | {line_content}")

        return "\n".join(excerpt_lines)
