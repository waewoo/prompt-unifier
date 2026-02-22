import re
from pathlib import Path

import yaml

from prompt_unifier.models.prompt import PromptFile
from prompt_unifier.models.rule import RuleFile
from prompt_unifier.models.skill import SkillFile
from prompt_unifier.models.validation import ValidationResult


class ContentFileParser:
    """
    Parses and validates content files (prompts, rules, or skills) with YAML frontmatter.
    Content type is determined automatically from the file path.
    """

    def __init__(self, separator: str = "---"):
        self.separator = separator
        self.frontmatter_pattern = re.compile(
            rf"^{re.escape(separator)}\s*\n(.*?)\n^{re.escape(separator)}\s*\n(.*)",
            re.DOTALL | re.MULTILINE,
        )

    def parse_file(self, file_path: Path) -> PromptFile | RuleFile | SkillFile:
        """
        Parses a content file, separating frontmatter and body.
        Handles prompts, rules, and skills based on file path.
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
        except yaml.YAMLError as e:
            raise ValueError(f"invalid yaml: {e}") from e

        content_type = self._determine_content_type(file_path)

        if content_type == "skill":
            return SkillFile(**frontmatter, content=body.strip())

        # Remove 'type' field for backward compatibility (ignored by prompt/rule models)
        frontmatter.pop("type", None)

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
        except ValueError as e:
            # Catches both ValueError and ValidationError (which inherits from ValueError)
            from prompt_unifier.models.validation import ValidationIssue, ValidationSeverity

            error_issue = ValidationIssue(
                line=None,
                severity=ValidationSeverity.ERROR,
                code="VALIDATION_ERROR",
                message=str(e),
                suggestion="Fix the validation error",
            )
            return ValidationResult(file=file_path, status="failed", errors=[error_issue])

    def parse_skill_file(self, path: Path) -> SkillFile:
        """Parse a skill file. Delegates to parse_file."""
        result = self.parse_file(path)
        if not isinstance(result, SkillFile):
            raise ValueError(f"Expected a skill file but got {type(result).__name__}: {path}")
        return result

    def _determine_content_type(self, file_path: Path) -> str:
        """
        Determines the content type based on the file's path.
        """
        if "skills" in file_path.parts:
            return "skill"
        elif "rules" in file_path.parts:
            return "rule"
        else:
            return "prompt"


def parse_content_file(file_path: Path) -> PromptFile | RuleFile | SkillFile:
    """
    Convenience function to parse a content file.

    Args:
        file_path: Path to the content file to parse.

    Returns:
        Parsed content file object (PromptFile, RuleFile, etc.).
    """
    parser = ContentFileParser()
    return parser.parse_file(file_path)
