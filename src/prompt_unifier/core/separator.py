"""Separator validation logic for content files.

This module validates the YAML frontmatter delimiters (---) that separate
frontmatter from content in standard Markdown format.
"""

from prompt_unifier.models.validation import ErrorCode, ValidationIssue, ValidationSeverity


class SeparatorValidator:
    """Validates YAML frontmatter delimiters in content files.

    The format must be:
    - File starts with '---' on line 1
    - YAML frontmatter in between
    - Second '---' to close frontmatter
    - Content after closing delimiter

    Examples:
        >>> validator = SeparatorValidator()
        >>> fm, content, issues = validator.validate_separator("---\\ntitle: test\\n---\\nContent")
        >>> len(issues)
        0
        >>> fm
        'title: test'
        >>> content
        'Content'
    """

    DELIMITER = "---"

    def validate_separator(self, file_content: str) -> tuple[str, str, list[ValidationIssue]]:
        """Validate the YAML frontmatter delimiters in the file content.

        This method performs line-by-line analysis to detect:
        - File starts with '---' delimiter
        - Presence of closing '---' delimiter
        - Non-empty frontmatter and content

        Args:
            file_content: The complete file content as a string

        Returns:
            A tuple containing:
            - frontmatter_text: YAML text between delimiters (empty if errors)
            - content_text: Markdown text after closing delimiter (empty if errors)
            - issues: List of ValidationIssue objects for any problems found

        Examples:
            >>> validator = SeparatorValidator()
            >>> content = "---\\ntitle: test\\n---\\nContent"
            >>> fm, content, issues = validator.validate_separator(content)
            >>> len(issues)
            0
        """
        issues: list[ValidationIssue] = []
        lines = file_content.split("\n")

        if not lines:
            issues.append(
                ValidationIssue(
                    line=None,
                    severity=ValidationSeverity.ERROR,
                    code=ErrorCode.NO_SEPARATOR.value,
                    message="File is empty",
                    excerpt=None,
                    suggestion="Add YAML frontmatter enclosed in '---' delimiters",
                )
            )
            return "", "", issues

        # Check 1: File must start with opening delimiter
        if lines[0].strip() != self.DELIMITER:
            issues.append(
                ValidationIssue(
                    line=1,
                    severity=ValidationSeverity.ERROR,
                    code=ErrorCode.NO_SEPARATOR.value,
                    message="File must start with '---' delimiter",
                    excerpt=f"1 | {lines[0]}" if lines[0] else "1 | (empty)",
                    suggestion="Add '---' as the first line of the file",
                )
            )
            return "", "", issues

        # Find closing delimiter (second ---)
        closing_delimiter_idx = None
        for idx in range(1, len(lines)):
            if lines[idx].strip() == self.DELIMITER:
                closing_delimiter_idx = idx
                break

        # Check 2: Must have closing delimiter
        if closing_delimiter_idx is None:
            issues.append(
                ValidationIssue(
                    line=None,
                    severity=ValidationSeverity.ERROR,
                    code=ErrorCode.NO_SEPARATOR.value,
                    message="No closing '---' delimiter found",
                    excerpt=None,
                    suggestion="Add '---' after the YAML frontmatter to close it",
                )
            )
            return "", "", issues

        # Extract frontmatter (between opening and closing delimiters)
        frontmatter_lines = lines[1:closing_delimiter_idx]
        frontmatter_text = "\n".join(frontmatter_lines)

        # Check 3: Frontmatter must not be empty
        if not frontmatter_text.strip():
            issues.append(
                ValidationIssue(
                    line=2,
                    severity=ValidationSeverity.ERROR,
                    code=ErrorCode.EMPTY_CONTENT.value,
                    message="YAML frontmatter is empty",
                    excerpt=None,
                    suggestion="Add YAML frontmatter between the '---' delimiters",
                )
            )

        # Extract content (after closing delimiter)
        content_lines = lines[closing_delimiter_idx + 1 :]
        content_text = "\n".join(content_lines)

        # Check 4: Content should not be empty (warning only)
        if not content_text.strip():
            line_num = closing_delimiter_idx + 2 if closing_delimiter_idx + 1 < len(lines) else None
            issues.append(
                ValidationIssue(
                    line=line_num,
                    severity=ValidationSeverity.ERROR,
                    code=ErrorCode.EMPTY_CONTENT.value,
                    message="Content after frontmatter is empty",
                    excerpt=None,
                    suggestion="Add markdown content after the closing '---' delimiter",
                )
            )

        return frontmatter_text, content_text, issues
