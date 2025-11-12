"""Content file parser for both prompts and rules.

This module provides functionality to parse content files (prompts or rules)
and automatically detect the file type based on the frontmatter.
"""

from contextlib import suppress
from pathlib import Path

from prompt_manager.core.encoding import EncodingValidator
from prompt_manager.core.separator import SeparatorValidator
from prompt_manager.core.validator import PromptValidator
from prompt_manager.core.yaml_parser import YAMLParser
from prompt_manager.models import ContentFile, PromptFrontmatter, RuleFile
from prompt_manager.models.validation import ValidationResult


class ContentFileParser:
    """Parse and validate content files (prompts or rules).

    This parser automatically detects whether a file is a prompt or rule
    based on the 'type' field in the YAML frontmatter, then validates
    it against the appropriate model.

    Examples:
        >>> parser = ContentFileParser()
        >>> content_file = parser.parse_file(Path("my-rule.md"))
        >>> isinstance(content_file, RuleFile)
        True
    """

    def __init__(self) -> None:
        """Initialize the ContentFileParser with component validators."""
        self.encoding_validator = EncodingValidator()
        self.separator_validator = SeparatorValidator()
        self.yaml_parser = YAMLParser()

    def parse_file(self, file_path: Path) -> ContentFile:
        """Parse a content file and return appropriate model instance.

        Automatically detects file type from the 'type' field in frontmatter:
        - type: "rule" → Returns RuleFile instance
        - type: "prompt" or missing → Returns PromptFrontmatter instance

        Args:
            file_path: Path to the content file to parse

        Returns:
            Either PromptFrontmatter or RuleFile instance

        Raises:
            ValueError: If file cannot be read, parsed, or validated
            ValidationError: If content doesn't match the schema

        Examples:
            >>> parser = ContentFileParser()
            >>> rule = parser.parse_file(Path("python-style.md"))
            >>> rule.type
            'rule'
        """
        # Step 1: Validate encoding
        file_content, encoding_issues = self.encoding_validator.validate_encoding(file_path)

        if file_content is None:
            raise ValueError(f"Failed to read file {file_path}: encoding validation failed")

        # Step 2: Validate and split by separator
        frontmatter_text, content_text, separator_issues = (
            self.separator_validator.validate_separator(file_content)
        )

        if not frontmatter_text or not content_text:
            raise ValueError(f"Failed to parse file {file_path}: separator validation failed")

        # Step 3: Parse YAML frontmatter
        yaml_dict, yaml_issues = self.yaml_parser.parse_yaml(frontmatter_text)

        if yaml_dict is None:
            raise ValueError(f"Failed to parse YAML in file {file_path}: invalid YAML syntax")

        # Step 4: Detect file type from frontmatter
        file_type = yaml_dict.get("type", "prompt")  # Default to prompt

        # Step 5: Validate and instantiate appropriate model
        if file_type == "rule":
            # Remove 'type' field if present, as RuleFile doesn't have it
            rule_dict = {k: v for k, v in yaml_dict.items() if k != "type"}
            return RuleFile(**rule_dict, content=content_text)
        elif file_type == "prompt":
            # Remove 'type' field if present, as PromptFrontmatter doesn't have it
            prompt_dict = {k: v for k, v in yaml_dict.items() if k != "type"}
            return PromptFrontmatter(**prompt_dict)
        else:
            raise ValueError(
                f"Unknown file type '{file_type}' in {file_path}. " f"Must be 'prompt' or 'rule'"
            )

    def parse_file_with_validation(
        self, file_path: Path
    ) -> tuple[ContentFile | None, ValidationResult]:
        """Parse file and return both the parsed model and full validation result.

        This method provides complete validation feedback including all errors
        and warnings, while also attempting to return the parsed model if possible.

        Args:
            file_path: Path to the content file to parse

        Returns:
            Tuple of (parsed_model, validation_result)
            - parsed_model: ContentFile instance if parsing succeeded, None otherwise
            - validation_result: Full validation result with all errors/warnings

        Examples:
            >>> parser = ContentFileParser()
            >>> model, result = parser.parse_file_with_validation(Path("test.md"))
            >>> if result.is_valid:
            ...     print(f"Type: {model.type}")
        """
        # For now, use existing PromptValidator
        # TODO: Create RuleValidator and composite validator
        validator = PromptValidator()
        result = validator.validate_file(file_path)

        model = None
        if result.is_valid:
            with suppress(Exception):
                # Validation passed but parsing failed - shouldn't happen
                # but handle gracefully
                model = self.parse_file(file_path)

        return model, result


def parse_content_file(file_path: Path) -> ContentFile:
    """Parse a content file (prompt or rule) and return appropriate model.

    Convenience function that creates a parser and parses the file.
    Automatically detects file type from frontmatter.

    Args:
        file_path: Path to the content file to parse

    Returns:
        Either PromptFrontmatter or RuleFile instance

    Raises:
        ValueError: If file cannot be read, parsed, or validated
        ValidationError: If content doesn't match the schema

    Examples:
        >>> from pathlib import Path
        >>> rule = parse_content_file(Path("python-style.md"))
        >>> rule.type
        'rule'

        >>> prompt = parse_content_file(Path("code-review.md"))
        >>> prompt.type
        'prompt'
    """
    parser = ContentFileParser()
    return parser.parse_file(file_path)
