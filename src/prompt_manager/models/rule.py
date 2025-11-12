"""Pydantic models for rule frontmatter validation.

This module defines the data model for validating rule file frontmatter,
including required and optional fields specific to rules/context files.
"""

import re
import warnings
from typing import Literal

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

    Required Fields:
        name: Non-empty string identifier for the rule (kebab-case)
        description: Non-empty string describing the rule's purpose
        type: Must be "rule" (literal)
        category: Rule category (one of predefined categories)

    Optional Fields:
        tags: List of string tags for categorization (max 10, lowercase)
        version: Semantic version string (e.g., "1.0.0")
        applies_to: List of languages/frameworks this rule applies to
        author: String identifying the rule author

    Examples:
        >>> # Minimal valid rule
        >>> rule = RuleFrontmatter(
        ...     name="python-style",
        ...     description="Python coding standards",
        ...     type="rule",
        ...     category="coding-standards"
        ... )
        >>> rule.name
        'python-style'

        >>> # Full rule with all fields
        >>> rule = RuleFrontmatter(
        ...     name="api-design-guide",
        ...     description="REST API design best practices",
        ...     type="rule",
        ...     category="architecture",
        ...     tags=["rest", "api", "http"],
        ...     version="1.2.0",
        ...     applies_to=["python", "fastapi"],
        ...     author="team-platform"
        ... )
        >>> rule.category
        'architecture'
    """

    # Required fields
    name: str = Field(description="Rule identifier (required, kebab-case)")
    description: str = Field(
        min_length=1, max_length=200, description="Rule description (required, 1-200 chars)"
    )
    type: Literal["rule"] = Field(default="rule", description="File type, must be 'rule'")
    category: str = Field(description="Rule category (required)")

    # Optional fields
    tags: list[str] = Field(
        default_factory=list, max_length=10, description="Searchable tags (max 10)"
    )
    version: str = Field(default="1.0.0", description="Semantic version (default: 1.0.0)")
    applies_to: list[str] = Field(
        default_factory=list,
        description="Languages/frameworks this rule applies to",
    )
    author: str | None = Field(default=None, description="Rule author (optional)")

    @field_validator("name")
    @classmethod
    def validate_name_format(cls, v: str) -> str:
        """Validate that name follows kebab-case format.

        Args:
            v: The name value to validate

        Returns:
            The validated name string

        Raises:
            ValueError: If name doesn't follow kebab-case format
        """
        if not v or not v.strip():
            raise ValueError("Field 'name' must be a non-empty string")

        # Kebab-case pattern: lowercase letters, numbers, hyphens
        # Must start with lowercase letter
        kebab_pattern = r"^[a-z][a-z0-9-]*$"
        if not re.match(kebab_pattern, v):
            raise ValueError(
                f"Field 'name' must be in kebab-case (lowercase with hyphens). "
                f"Got: '{v}'. Examples: python-style, api-guide, security-checklist"
            )
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate that description is non-empty.

        Args:
            v: The description value to validate

        Returns:
            The validated description string

        Raises:
            ValueError: If description is empty or only whitespace
        """
        if not v or not v.strip():
            raise ValueError("Field 'description' must be a non-empty string")
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

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate tags are lowercase without spaces.

        Args:
            v: The list of tags to validate

        Returns:
            The validated list of tags

        Raises:
            ValueError: If any tag contains uppercase or spaces
        """
        for tag in v:
            if not tag.islower() or " " in tag:
                raise ValueError(
                    f"Tag '{tag}' must be lowercase without spaces. "
                    f"Suggested: {tag.lower().replace(' ', '-')}"
                )
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

    Extends RuleFrontmatter to include the rule content (text after >>> separator).

    Additional Field:
        content: The rule content/body text (required, non-empty)

    Examples:
        >>> rule = RuleFile(
        ...     name="python-style",
        ...     description="Python coding standards",
        ...     type="rule",
        ...     category="coding-standards",
        ...     content="# Python Style Guide\\n\\nUse PEP 8..."
        ... )
        >>> len(rule.content) > 0
        True
    """

    content: str = Field(min_length=1, description="Rule content (after >>> separator)")

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
