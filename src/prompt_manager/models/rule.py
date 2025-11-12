"""Pydantic models for rule frontmatter validation.

This module defines the data model for validating rule file frontmatter,
including required and optional fields specific to rules/context files.
"""

import re
import warnings
from typing import Any

from pydantic import BaseModel, Field, field_validator

# Valid rule categories
VALID_CATEGORIES = [
    "coding-standards",
    "architecture",
    "security",
    "testing",
    "documentation",
    "performance",
    "deployment",
    "git",
]


class RuleFrontmatter(BaseModel):
    """Pydantic model for rule frontmatter validation.

    This model validates the YAML frontmatter structure of rule files,
    enforcing required fields for rules and providing rule-specific validation.

    Type detection is based on file location (rules/ directory), not a type field.

    Required Fields:
        title: Human-readable title for the rule
        description: Brief description of the rule's purpose
        category: Rule category (one of predefined categories)

    Optional Fields:
        tags: List of string tags (YAML array format: [tag1, tag2], max 10)
        version: Semantic version string (e.g., "1.0.0")
        applies_to: List of glob patterns for files (e.g., [*.py, *.js])
        author: String identifying the rule author
        language: Primary language for the rule (e.g., "python")

    Examples:
        >>> # Minimal valid rule
        >>> rule = RuleFrontmatter(
        ...     title="Python Style Guide",
        ...     description="Python coding standards",
        ...     category="coding-standards"
        ... )
        >>> rule.title
        'Python Style Guide'

        >>> # Full rule with all fields
        >>> rule = RuleFrontmatter(
        ...     title="API Design Patterns",
        ...     description="REST API design best practices",
        ...     category="architecture",
        ...     tags=["rest", "api", "http"],
        ...     version="1.2.0",
        ...     applies_to=["*.py", "api/*.js"],
        ...     author="team-platform",
        ...     language="python"
        ... )
        >>> rule.category
        'architecture'
    """

    # Required fields
    title: str = Field(description="Rule title (required, human-readable)")
    description: str = Field(
        min_length=1, max_length=200, description="Rule description (required, 1-200 chars)"
    )
    category: str = Field(description="Rule category (required)")

    # Optional fields
    tags: list[str] = Field(
        default_factory=list, max_length=10, description="Searchable tags (max 10, YAML array)"
    )
    version: str = Field(default="1.0.0", description="Semantic version (default: 1.0.0)")
    applies_to: list[str] = Field(
        default_factory=list,
        description="Glob patterns for files this rule applies to (e.g., [*.py])",
    )
    author: str | None = Field(default=None, description="Rule author (optional)")
    language: str | None = Field(default=None, description="Primary language (optional)")

    @field_validator("title", "description")
    @classmethod
    def validate_non_empty_string(cls, v: str, info: Any) -> str:
        """Validate that title and description are non-empty.

        Args:
            v: The field value to validate
            info: Pydantic validation info containing field name

        Returns:
            The validated string

        Raises:
            ValueError: If the string is empty or only whitespace
        """
        if not v or not v.strip():
            field_name = info.field_name
            raise ValueError(f"Field '{field_name}' must be a non-empty string")
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validate category and warn if non-standard.

        Args:
            v: The category value to validate

        Returns:
            The category string (standard or custom)
        """
        if v not in VALID_CATEGORIES:
            warnings.warn(
                f"Non-standard category '{v}'. "
                f"Standard categories: {', '.join(VALID_CATEGORIES)}",
                UserWarning,
                stacklevel=2,
            )
        return v

    @field_validator("applies_to")
    @classmethod
    def validate_glob_patterns(cls, v: list[str]) -> list[str]:
        """Validate glob patterns in applies_to field.

        Ensures patterns are non-empty strings. Basic validation only,
        actual glob pattern syntax is not strictly validated.

        Args:
            v: The list of glob patterns to validate

        Returns:
            The validated list of patterns

        Raises:
            ValueError: If any pattern is empty
        """
        for pattern in v:
            if not pattern or not pattern.strip():
                raise ValueError("Glob patterns in 'applies_to' must be non-empty strings")
        return v

    @field_validator("version")
    @classmethod
    def validate_semantic_version(cls, v: str) -> str:
        """Validate that version follows semantic versioning format.

        Args:
            v: The version string to validate

        Returns:
            The validated version string

        Raises:
            ValueError: If version format is invalid
        """
        semver_pattern = r"^\d+\.\d+\.\d+$"
        if not re.match(semver_pattern, v):
            raise ValueError(
                f"Field 'version' must follow semantic versioning format (X.Y.Z). "
                f"Got: '{v}'. Expected format: '1.0.0'"
            )
        return v

    model_config = {
        "extra": "forbid",  # Reject any extra fields not defined in the model
        "str_strip_whitespace": True,  # Strip whitespace from strings
    }


class RuleFile(RuleFrontmatter):
    """Complete rule file model including content.

    Extends RuleFrontmatter to include the rule content (text after closing ---).

    Additional Field:
        content: The rule content/body text (required, non-empty)

    Examples:
        >>> rule = RuleFile(
        ...     title="Python Style Guide",
        ...     description="Python coding standards",
        ...     category="coding-standards",
        ...     content="# Python Style Guide\\n\\nUse PEP 8..."
        ... )
        >>> len(rule.content) > 0
        True
    """

    content: str = Field(min_length=1, description="Rule content (markdown after closing ---)")

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate that content is non-empty.

        Args:
            v: The content value to validate

        Returns:
            The validated content string

        Raises:
            ValueError: If content is empty or only whitespace
        """
        if not v or not v.strip():
            raise ValueError("Field 'content' must be a non-empty string")
        return v
