import re
from pathlib import Path

import yaml
from pydantic import ValidationError

from prompt_unifier.models.prompt import PromptFile, PromptFrontmatter
from prompt_unifier.models.rule import RuleFile, RuleFrontmatter
from prompt_unifier.models.validation import ValidationResult


class ContentFileParser:
    """
    Parses and validates content files (prompts or rules) with YAML frontmatter.
    """

    def __init__(self, separator: str = "---"):
        self.separator = separator
        self.frontmatter_pattern = re.compile(
            rf"^{re.escape(separator)}\s*\n(.*?)\n^{re.escape(separator)}\s*\n(.*)",
            re.DOTALL | re.MULTILINE,
        )

    def parse_file(
        self, file_path: Path
    ) -> PromptFile | RuleFile | PromptFrontmatter | RuleFrontmatter:
        """
        Parses a content file, separating frontmatter and body.
        """
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raise ValueError("encoding validation failed") from None

        match = self.frontmatter_pattern.match(content)

        if not match:
            raise ValueError("separator validation failed")

        frontmatter_str, body = match.groups()
        try:
            frontmatter = yaml.safe_load(frontmatter_str)
        except yaml.YAMLError:
            raise ValueError("invalid yaml") from None

        # Remove 'type' field for backward compatibility (ignored)
        frontmatter.pop("type", None)

        content_type = self._determine_content_type(file_path)

        if content_type == "prompt":
            return PromptFile(**frontmatter, content=body.strip())
        elif content_type == "rule":
            return RuleFile(**frontmatter, content=body.strip())
        else:
            raise ValueError(f"Unknown content type for file: {file_path}")

    def validate_file(self, file_path: Path) -> ValidationResult:
        """
        Validates a content file against the appropriate Pydantic model.
        """
        try:
            self.parse_file(file_path)
            return ValidationResult(file=file_path, status="passed")
        except (ValueError, ValidationError) as e:
            from prompt_unifier.models.validation import ValidationIssue, ValidationSeverity

            error_issue = ValidationIssue(
                line=None,
                severity=ValidationSeverity.ERROR,
                code="VALIDATION_ERROR",
                message=str(e),
                suggestion="Fix the validation error",
            )
            return ValidationResult(file=file_path, status="failed", errors=[error_issue])

    def _determine_content_type(self, file_path: Path) -> str:
        """
        Determines the content type (prompt or rule) based on the file's path.
        """
        if "rules" in file_path.parts:
            return "rule"
        else:
            # Default to prompt if not in rules directory
            return "prompt"


def parse_content_file(
    file_path: Path,
) -> PromptFile | RuleFile | PromptFrontmatter | RuleFrontmatter:
    """
    Convenience function to parse a content file.

    Args:
        file_path: Path to the content file to parse.

    Returns:
        Parsed content file object (PromptFile, RuleFile, etc.).
    """
    parser = ContentFileParser()
    return parser.parse_file(file_path)
