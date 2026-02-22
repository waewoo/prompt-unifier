"""Pydantic models for skill frontmatter validation.

This module defines the data model for validating skill files,
which are portable AI agent guidance packages deployed to KiloCode.
"""

import re
from typing import Any

from pydantic import BaseModel, Field, field_validator

SLUG_PATTERN = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$")


class SkillFrontmatter(BaseModel):
    """Pydantic model for skill frontmatter validation.

    Skills are portable AI agent guidance packages deployed to KiloCode
    as {name}/SKILL.md inside .kilocode/skills/ or .kilocode/skills-{mode}/.

    Required Fields:
        name: Slug identifier for the skill (max 64 chars, lowercase alphanumeric + hyphens)
        description: Brief description of the skill's purpose (max 1024 chars)

    Optional Fields:
        mode: Target mode (e.g., "code"); determines skills-{mode}/ deployment directory
        license: License identifier (e.g., "MIT")
        compatibility: Compatibility string
        metadata: Arbitrary key-value pairs

    Examples:
        >>> skill = SkillFrontmatter(name="code-review", description="Automated code review")
        >>> skill.name
        'code-review'

        >>> skill = SkillFrontmatter(
        ...     name="linting",
        ...     description="Run linting checks",
        ...     mode="code",
        ...     license="MIT",
        ... )
        >>> skill.mode
        'code'
    """

    name: str = Field(description="Skill slug identifier (required, max 64 chars)")
    description: str = Field(description="Skill description (required, max 1024 chars)")

    mode: str | None = Field(default=None, description="Target mode (optional)")
    license: str | None = Field(default=None, description="License identifier (optional)")
    compatibility: str | None = Field(default=None, description="Compatibility string (optional)")
    metadata: dict[str, Any] | None = Field(
        default=None, description="Arbitrary key-value metadata (optional)"
    )

    model_config = {"extra": "forbid", "str_strip_whitespace": True}

    @property
    def title(self) -> str:
        """Return skill name as title for compatibility with prompt/rule helpers."""
        return self.name

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name is a non-empty slug of at most 64 chars.

        Args:
            v: The name value to validate.

        Returns:
            The validated name string.

        Raises:
            ValueError: If name is empty, too long, or has invalid characters.
        """
        if not v:
            raise ValueError("Field 'name' must be a non-empty string")
        if len(v) > 64:
            raise ValueError(f"Field 'name' must be at most 64 characters (got {len(v)})")
        if not SLUG_PATTERN.match(v):
            raise ValueError(
                f"Field 'name' must match pattern ^[a-z0-9]([a-z0-9-]*[a-z0-9])?$ (got '{v}'). "
                "Use only lowercase letters, digits, and hyphens; "
                "must not start or end with a hyphen."
            )
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate description is non-empty and at most 1024 chars.

        Args:
            v: The description value to validate.

        Returns:
            The validated description string.

        Raises:
            ValueError: If description is empty or too long.
        """
        if not v or not v.strip():
            raise ValueError("Field 'description' must be a non-empty string")
        if len(v) > 1024:
            raise ValueError(f"Field 'description' must be at most 1024 characters (got {len(v)})")
        return v

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: str | None) -> str | None:
        """Validate mode follows the same slug pattern as name.

        Args:
            v: The mode value to validate (or None).

        Returns:
            The validated mode string or None.

        Raises:
            ValueError: If mode is present but has invalid characters.
        """
        if v is None:
            return v
        if not SLUG_PATTERN.match(v):
            raise ValueError(
                f"Field 'mode' must match pattern ^[a-z0-9]([a-z0-9-]*[a-z0-9])?$ (got '{v}'). "
                "Use only lowercase letters, digits, and hyphens; "
                "must not start or end with a hyphen."
            )
        return v


class SkillFile(SkillFrontmatter):
    """Complete skill file model including content.

    Extends SkillFrontmatter to include the skill body content.

    Additional Field:
        content: The skill body text (required, non-empty)

    Examples:
        >>> skill = SkillFile(
        ...     name="code-review",
        ...     description="Automated code review",
        ...     content="# Code Review\\n\\nReview all code changes...",
        ... )
        >>> len(skill.content) > 0
        True
    """

    content: str = Field(min_length=1, description="Skill body content (required, non-empty)")

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate that content is non-empty.

        Args:
            v: The content value to validate.

        Returns:
            The validated content string.

        Raises:
            ValueError: If content is empty or only whitespace.
        """
        if not v or not v.strip():
            raise ValueError("Field 'content' must be a non-empty string")
        return v
