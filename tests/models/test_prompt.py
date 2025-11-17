"""Tests for PromptFrontmatter Pydantic model.

This module tests the validation logic for prompt frontmatter including:
- Required fields validation (name, description)
- Optional fields acceptance (version, tags, author)
- Prohibited fields rejection (tools)
- Semantic versioning validation
- Non-empty string constraints
- Model serialization
"""

import pytest
from pydantic import ValidationError

from prompt_unifier.models.prompt import PromptFrontmatter


class TestPromptFrontmatterRequiredFields:
    """Test required fields validation."""

    def test_valid_minimal_prompt(self) -> None:
        """Test that prompt with only required fields is valid."""
        data = {
            "title": "test-prompt",
            "description": "A test prompt description",
        }
        prompt = PromptFrontmatter(**data)
        assert prompt.title == "test-prompt"
        assert prompt.description == "A test prompt description"
        assert prompt.version is None
        assert prompt.tags is None
        assert prompt.author is None

    def test_missing_name_field(self) -> None:
        """Test that missing 'name' field raises ValidationError."""
        data = {"description": "A description"}
        with pytest.raises(ValidationError) as exc_info:
            PromptFrontmatter(**data)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("title",) and error["type"] == "missing" for error in errors)

    def test_missing_description_field(self) -> None:
        """Test that missing 'description' field raises ValidationError."""
        data = {"title": "test-prompt"}
        with pytest.raises(ValidationError) as exc_info:
            PromptFrontmatter(**data)

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("description",) and error["type"] == "missing" for error in errors
        )

    def test_empty_name_rejected(self) -> None:
        """Test that empty 'name' string is rejected."""
        data = {
            "title": "",
            "description": "A description",
        }
        with pytest.raises(ValidationError) as exc_info:
            PromptFrontmatter(**data)

        errors = exc_info.value.errors()
        # Should fail validation for empty string
        assert any("title" in str(error["loc"]) for error in errors)

    def test_empty_description_rejected(self) -> None:
        """Test that empty 'description' string is rejected."""
        data = {
            "title": "test-prompt",
            "description": "",
        }
        with pytest.raises(ValidationError) as exc_info:
            PromptFrontmatter(**data)

        errors = exc_info.value.errors()
        # Should fail validation for empty string
        assert any("description" in str(error["loc"]) for error in errors)


class TestPromptFrontmatterOptionalFields:
    """Test optional fields acceptance."""

    def test_valid_prompt_with_all_fields(self) -> None:
        """Test that prompt with all optional fields is valid."""
        data = {
            "title": "full-prompt",
            "description": "A full featured prompt",
            "version": "1.0.0",
            "tags": ["python", "backend"],
            "author": "John Doe",
        }
        prompt = PromptFrontmatter(**data)
        assert prompt.title == "full-prompt"
        assert prompt.description == "A full featured prompt"
        assert prompt.version == "1.0.0"
        assert prompt.tags == ["python", "backend"]
        assert prompt.author == "John Doe"

    def test_optional_version_field(self) -> None:
        """Test that 'version' field is optional."""
        data = {
            "title": "test-prompt",
            "description": "A description",
            "version": "2.1.3",
        }
        prompt = PromptFrontmatter(**data)
        assert prompt.version == "2.1.3"

    def test_optional_tags_field(self) -> None:
        """Test that 'tags' field is optional and accepts list."""
        data = {
            "title": "test-prompt",
            "description": "A description",
            "tags": ["tag1", "tag2", "tag3"],
        }
        prompt = PromptFrontmatter(**data)
        assert prompt.tags == ["tag1", "tag2", "tag3"]

    def test_optional_author_field(self) -> None:
        """Test that 'author' field is optional."""
        data = {
            "title": "test-prompt",
            "description": "A description",
            "author": "Jane Smith",
        }
        prompt = PromptFrontmatter(**data)
        assert prompt.author == "Jane Smith"

    def test_empty_tags_list_allowed(self) -> None:
        """Test that empty tags list is allowed (will trigger warning elsewhere)."""
        data = {
            "title": "test-prompt",
            "description": "A description",
            "tags": [],
        }
        prompt = PromptFrontmatter(**data)
        assert prompt.tags == []


class TestPromptFrontmatterSemanticVersioning:
    """Test semantic versioning validation."""

    def test_valid_semver_format(self) -> None:
        """Test that valid semantic versions are accepted."""
        valid_versions = ["1.0.0", "0.1.0", "10.20.30", "999.999.999"]

        for version in valid_versions:
            data = {
                "title": "test-prompt",
                "description": "A description",
                "version": version,
            }
            prompt = PromptFrontmatter(**data)
            assert prompt.version == version

    def test_invalid_semver_format_rejected(self) -> None:
        """Test that invalid semantic versions are rejected."""
        invalid_versions = [
            "1.0",  # Missing patch
            "1",  # Missing minor and patch
            "v1.0.0",  # Has 'v' prefix
            "1.0.0-alpha",  # Has pre-release
            "1.0.0.0",  # Too many parts
            "1.0.x",  # Non-numeric
        ]

        for version in invalid_versions:
            data = {
                "title": "test-prompt",
                "description": "A description",
                "version": version,
            }
            with pytest.raises(ValidationError) as exc_info:
                PromptFrontmatter(**data)

            errors = exc_info.value.errors()
            assert any("version" in str(error["loc"]) for error in errors)


class TestPromptFrontmatterProhibitedFields:
    """Test prohibited fields rejection."""

    def test_prohibited_tools_field_rejected(self) -> None:
        """Test that 'tools' field is rejected."""
        data = {
            "title": "test-prompt",
            "description": "A description",
            "tools": ["continue", "cursor"],
        }
        with pytest.raises(ValidationError) as exc_info:
            PromptFrontmatter(**data)

        # The error should mention 'tools' is not allowed
        error_msg = str(exc_info.value)
        assert "tools" in error_msg.lower()


class TestPromptFrontmatterFieldTypes:
    """Test field type validation."""

    def test_tags_must_be_list_of_strings(self) -> None:
        """Test that tags must be a list of strings."""
        data = {
            "title": "test-prompt",
            "description": "A description",
            "tags": "not-a-list",  # Should be list
        }
        with pytest.raises(ValidationError) as exc_info:
            PromptFrontmatter(**data)

        errors = exc_info.value.errors()
        assert any("tags" in str(error["loc"]) for error in errors)

    def test_name_must_be_string(self) -> None:
        """Test that name must be a string."""
        data = {
            "title": 123,  # Should be string
            "description": "A description",
        }
        with pytest.raises(ValidationError) as exc_info:
            PromptFrontmatter(**data)

        errors = exc_info.value.errors()
        assert any("title" in str(error["loc"]) for error in errors)


class TestPromptFrontmatterSerialization:
    """Test model serialization."""

    def test_model_serialization_to_dict(self) -> None:
        """Test that model can be serialized to dictionary."""
        data = {
            "title": "test-prompt",
            "description": "A description",
            "version": "1.0.0",
            "tags": ["python"],
            "author": "John Doe",
        }
        prompt = PromptFrontmatter(**data)
        serialized = prompt.model_dump()

        assert isinstance(serialized, dict)
        assert serialized["title"] == "test-prompt"
        assert serialized["description"] == "A description"
        assert serialized["version"] == "1.0.0"
        assert serialized["tags"] == ["python"]
        assert serialized["author"] == "John Doe"

    def test_model_serialization_with_none_values(self) -> None:
        """Test serialization with None values for optional fields."""
        data = {
            "title": "minimal-prompt",
            "description": "Minimal description",
        }
        prompt = PromptFrontmatter(**data)
        serialized = prompt.model_dump()

        assert serialized["title"] == "minimal-prompt"
        assert serialized["description"] == "Minimal description"
        assert serialized["version"] is None
        assert serialized["tags"] is None
        assert serialized["author"] is None
