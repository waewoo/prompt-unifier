"""Pydantic models for prompt frontmatter validation.

This module defines the data model for validating prompt file frontmatter,
including required and optional fields, semantic versioning, and prohibited fields.
"""

import re
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class PromptFrontmatter(BaseModel):
    """Pydantic model for prompt frontmatter validation.

    This model validates the YAML frontmatter structure of prompt files,
    enforcing required fields, optional fields, and rejecting prohibited fields.

    Required Fields:
        name: Non-empty string identifier for the prompt
        description: Non-empty string describing the prompt's purpose

    Optional Fields:
        version: Semantic version string (e.g., "1.0.0")
        tags: List of string tags for categorization
        author: String identifying the prompt author

    Prohibited Fields:
        tools: Not allowed in this format

    Examples:
        >>> # Minimal valid prompt
        >>> prompt = PromptFrontmatter(name="test", description="A test prompt")
        >>> prompt.name
        'test'

        >>> # Full prompt with all fields
        >>> prompt = PromptFrontmatter(
        ...     name="python-expert",
        ...     description="Expert Python developer",
        ...     version="1.0.0",
        ...     tags=["python", "backend"],
        ...     author="John Doe"
        ... )
        >>> prompt.version
        '1.0.0'
    """

    # Required fields
    name: str = Field(description="Prompt identifier (required, non-empty)")
    description: str = Field(description="Prompt description (required, non-empty)")

    # Optional fields
    version: str | None = Field(
        default=None, description="Semantic version (optional, format: X.Y.Z)"
    )
    tags: list[str] | None = Field(default=None, description="List of tags (optional)")
    author: str | None = Field(default=None, description="Author name (optional)")

    @field_validator("name", "description")
    @classmethod
    def validate_non_empty_string(cls, v: str, info: Any) -> str:
        """Validate that name and description are non-empty strings.

        Args:
            v: The field value to validate
            info: Pydantic validation info containing field name

        Returns:
            The validated string value

        Raises:
            ValueError: If the string is empty or only whitespace
        """
        if not v or not v.strip():
            field_name = info.field_name
            raise ValueError(f"Field '{field_name}' must be a non-empty string")
        return v

    @field_validator("version")
    @classmethod
    def validate_semantic_version(cls, v: str | None) -> str | None:
        """Validate that version follows semantic versioning format.

        The format must be exactly: MAJOR.MINOR.PATCH where each part is numeric.
        Examples: "1.0.0", "2.1.3", "10.20.30"

        Args:
            v: The version string to validate (or None)

        Returns:
            The validated version string or None

        Raises:
            ValueError: If version format is invalid
        """
        if v is None:
            return v

        semver_pattern = r"^\d+\.\d+\.\d+$"
        if not re.match(semver_pattern, v):
            raise ValueError(
                f"Field 'version' must follow semantic versioning format (X.Y.Z). "
                f"Got: '{v}'. Expected format: '1.0.0'"
            )
        return v

    @model_validator(mode="after")
    def reject_prohibited_fields(self) -> "PromptFrontmatter":
        """Reject prohibited fields like 'tools'.

        This validator checks for fields that should not be present in the frontmatter.
        Since Pydantic v2 by default ignores extra fields, we need to check the
        original input data which isn't directly available in 'after' mode.

        This validator serves as a placeholder and will be enhanced by the validation
        pipeline to check for prohibited fields during YAML parsing before Pydantic
        validation.

        Returns:
            The validated model instance

        Note:
            Actual prohibition enforcement happens in the validation pipeline
            where we have access to the raw YAML dict before model instantiation.
        """
        return self

    model_config = {
        "extra": "forbid",  # Reject any extra fields not defined in the model
        "str_strip_whitespace": True,  # Strip whitespace from strings
    }
