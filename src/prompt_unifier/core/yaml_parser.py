"""YAML parsing and validation for prompt frontmatter.

This module parses YAML frontmatter and ensures it has a flat structure
(no nested dictionaries).
"""

from typing import Any

import yaml

from prompt_unifier.models.validation import ErrorCode, ValidationIssue, ValidationSeverity


class YAMLParser:
    """Parses and validates YAML frontmatter structure.

    This parser ensures:
    - Valid YAML syntax
    - Flat structure only (no nested dictionaries)
    - Values can be strings, lists of strings, or None

    Examples:
        >>> parser = YAMLParser()
        >>> data, issues = parser.parse_yaml("name: test\\ndescription: A test")
        >>> len(issues)
        0
        >>> data['name']
        'test'
    """

    def parse_yaml(self, yaml_text: str) -> tuple[dict[str, Any] | None, list[ValidationIssue]]:
        """Parse YAML text and validate its structure.

        This method:
        1. Parses YAML using safe_load
        2. Validates that the structure is flat (no nested dicts)
        3. Returns the parsed dictionary or None if errors occurred

        Args:
            yaml_text: The YAML text to parse (frontmatter section)

        Returns:
            A tuple containing:
            - parsed_dict: The parsed YAML as a dict, or None if errors occurred
            - issues: List of ValidationIssue objects for any problems found

        Examples:
            >>> parser = YAMLParser()
            >>> data, issues = parser.parse_yaml("name: test\\ndescription: Test")
            >>> data['name']
            'test'
        """
        issues: list[ValidationIssue] = []

        # Handle empty YAML
        if not yaml_text or not yaml_text.strip():
            return None, issues

        try:
            # Parse YAML with safe_load (security best practice)
            parsed = yaml.safe_load(yaml_text)

            # Handle case where YAML is empty or just comments
            if parsed is None:
                return None, issues

            # Ensure we have a dictionary
            if not isinstance(parsed, dict):
                issues.append(
                    ValidationIssue(
                        line=None,
                        severity=ValidationSeverity.ERROR,
                        code=ErrorCode.INVALID_YAML.value,
                        message="YAML frontmatter must be a dictionary/mapping",
                        excerpt=None,
                        suggestion="Ensure frontmatter is in key: value format",
                    )
                )
                return None, issues

            # Check for nested structures
            nested_issues = self._detect_nested_structures(parsed)
            if nested_issues:
                issues.extend(nested_issues)
                return None, issues

            return parsed, issues

        except yaml.YAMLError as e:
            # YAML syntax error
            line_number = None
            if hasattr(e, "problem_mark") and e.problem_mark:
                line_number = e.problem_mark.line + 1  # Convert 0-indexed to 1-indexed

            error_str = str(e)

            # Detect glob pattern error (unquoted * in arrays)
            if "while scanning an alias" in error_str and "*.py" in yaml_text:
                suggestion = (
                    "Glob patterns with '*' must be quoted in YAML arrays. "
                    'Use: applies_to: ["*.py"] instead of applies_to: [*.py]'
                )
            else:
                suggestion = "Check YAML syntax: ensure proper indentation, quotes, and structure"

            issues.append(
                ValidationIssue(
                    line=line_number,
                    severity=ValidationSeverity.ERROR,
                    code=ErrorCode.INVALID_YAML.value,
                    message=f"Invalid YAML syntax: {error_str}",
                    excerpt=None,
                    suggestion=suggestion,
                )
            )
            return None, issues

    def _detect_nested_structures(self, data: dict[str, Any]) -> list[ValidationIssue]:
        """Detect nested dictionary structures in YAML data.

        Args:
            data: The parsed YAML dictionary to check

        Returns:
            List of ValidationIssue objects for each nested structure found
        """
        issues: list[ValidationIssue] = []

        for key, value in data.items():
            # Check if value is a dictionary (nested structure)
            if isinstance(value, dict):
                issues.append(
                    ValidationIssue(
                        line=None,  # Line number not easily available after parsing
                        severity=ValidationSeverity.ERROR,
                        code=ErrorCode.NESTED_STRUCTURE.value,
                        message=(
                            f"Nested YAML structures are not allowed. "
                            f"Field '{key}' contains nested data"
                        ),
                        excerpt=None,
                        suggestion=(
                            f"Flatten the '{key}' field or remove it. "
                            "Only simple key-value pairs and lists are allowed"
                        ),
                    )
                )

            # Check if value is a list containing dictionaries
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        issues.append(
                            ValidationIssue(
                                line=None,
                                severity=ValidationSeverity.ERROR,
                                code=ErrorCode.NESTED_STRUCTURE.value,
                                message=(
                                    f"Nested YAML structures are not allowed. "
                                    f"Field '{key}' contains a list with nested dictionaries"
                                ),
                                excerpt=None,
                                suggestion=(
                                    f"Convert '{key}' to a simple list of strings "
                                    "or remove nested dictionaries"
                                ),
                            )
                        )
                        break  # Only report once per field

        return issues
