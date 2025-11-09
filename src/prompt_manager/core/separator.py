"""Separator validation logic for prompt files.

This module validates the >>> separator that divides frontmatter from content.
"""

from prompt_manager.models.validation import ErrorCode, ValidationIssue, ValidationSeverity


class SeparatorValidator:
    """Validates the >>> separator in prompt files.

    The separator must:
    - Appear exactly once in the file
    - Be on its own line (no other characters)
    - Have no leading or trailing whitespace on its line
    - Be followed by non-empty content

    Examples:
        >>> validator = SeparatorValidator()
        >>> fm, content, issues = validator.validate_separator("name: test\\n>>>\\nContent")
        >>> len(issues)
        0
        >>> fm
        'name: test'
        >>> content
        'Content'
    """

    SEPARATOR = ">>>"

    def validate_separator(self, file_content: str) -> tuple[str, str, list[ValidationIssue]]:
        """Validate the separator in the file content.

        This method performs line-by-line analysis to detect:
        - Presence of exactly one separator
        - Separator on its own line without whitespace
        - Non-empty content after separator

        Args:
            file_content: The complete file content as a string

        Returns:
            A tuple containing:
            - frontmatter_text: Text before the separator (empty if errors)
            - content_text: Text after the separator (empty if errors)
            - issues: List of ValidationIssue objects for any problems found

        Examples:
            >>> validator = SeparatorValidator()
            >>> fm, content, issues = validator.validate_separator("name: test\\n>>>\\nPrompt")
            >>> len(issues)
            0
        """
        issues: list[ValidationIssue] = []
        lines = file_content.split("\n")

        # Find all lines that contain the separator
        separator_lines: list[int] = []
        for line_num, line in enumerate(lines, start=1):
            if self.SEPARATOR in line:
                separator_lines.append(line_num)

        # Check 1: No separator found
        if len(separator_lines) == 0:
            issues.append(
                ValidationIssue(
                    line=None,
                    severity=ValidationSeverity.ERROR,
                    code=ErrorCode.NO_SEPARATOR.value,
                    message="No '>>>' separator found in file",
                    excerpt=None,
                    suggestion=(
                        "Add a '>>>' separator on its own line between " "frontmatter and content"
                    ),
                )
            )
            return "", "", issues

        # Check 2: Multiple separators found
        if len(separator_lines) > 1:
            issues.append(
                ValidationIssue(
                    line=separator_lines[1],  # Report second separator location
                    severity=ValidationSeverity.ERROR,
                    code=ErrorCode.MULTIPLE_SEPARATORS.value,
                    message=(
                        f"Multiple '>>>' separators found ({len(separator_lines)}), "
                        "only 1 allowed"
                    ),
                    excerpt=None,
                    suggestion="Remove extra '>>>' separators, keep only one",
                )
            )
            # Continue validation with first separator to provide more feedback
            separator_line_num = separator_lines[0]
        else:
            separator_line_num = separator_lines[0]

        # Get the separator line (0-indexed)
        separator_line_idx = separator_line_num - 1
        separator_line = lines[separator_line_idx]

        # Check 3: Separator must be exactly ">>>" with no whitespace
        if separator_line != self.SEPARATOR:
            # Check if it's a whitespace issue or content issue
            if separator_line.strip() == self.SEPARATOR:
                # It's whitespace (leading or trailing)
                issues.append(
                    ValidationIssue(
                        line=separator_line_num,
                        severity=ValidationSeverity.ERROR,
                        code=ErrorCode.SEPARATOR_WHITESPACE.value,
                        message=(
                            "Separator '>>>' must not have leading or trailing "
                            "whitespace on its line"
                        ),
                        excerpt=f"{separator_line_num} | {separator_line}",
                        suggestion="Remove all whitespace before and after '>>>' on its line",
                    )
                )
            else:
                # It has other content
                issues.append(
                    ValidationIssue(
                        line=separator_line_num,
                        severity=ValidationSeverity.ERROR,
                        code=ErrorCode.SEPARATOR_NOT_ALONE.value,
                        message=(
                            "Separator '>>>' must be on its own line without " "other characters"
                        ),
                        excerpt=f"{separator_line_num} | {separator_line}",
                        suggestion="Move '>>>' to its own line with no other text",
                    )
                )

        # Split content at the first separator
        frontmatter_text = "\n".join(lines[:separator_line_idx])
        content_lines = lines[separator_line_idx + 1 :]
        content_text = "\n".join(content_lines)

        # Check 4: Empty content after separator
        if not content_text.strip():
            issues.append(
                ValidationIssue(
                    line=separator_line_num + 1 if separator_line_num < len(lines) else None,
                    severity=ValidationSeverity.ERROR,
                    code=ErrorCode.EMPTY_CONTENT.value,
                    message=("Content after '>>>' separator is empty or contains only whitespace"),
                    excerpt=None,
                    suggestion="Add prompt content after the '>>>' separator",
                )
            )

        return frontmatter_text, content_text, issues
