"""Tests for GitConfig Pydantic model.

This module tests the GitConfig model validation and structure.
"""

import pytest
from pydantic import ValidationError

from prompt_unifier.models.git_config import GitConfig, HandlerConfig


class TestGitConfig:
    """Test suite for GitConfig Pydantic model."""

    def test_git_config_accepts_all_none_values(self) -> None:
        """Test that GitConfig can be created with all None values (for init command)."""
        config = GitConfig(repo_url=None, last_sync_timestamp=None, last_sync_commit=None)

        assert config.repo_url is None
        assert config.last_sync_timestamp is None
        assert config.last_sync_commit is None

    def test_git_config_accepts_valid_values(self) -> None:
        """Test that GitConfig accepts valid string values for all fields."""
        config = GitConfig(
            repo_url="https://github.com/example/prompts.git",
            last_sync_timestamp="2024-11-11T14:30:00Z",
            last_sync_commit="abc1234",
        )

        assert config.repo_url == "https://github.com/example/prompts.git"
        assert config.last_sync_timestamp == "2024-11-11T14:30:00Z"
        assert config.last_sync_commit == "abc1234"

    def test_git_config_validates_field_types(self) -> None:
        """Test that GitConfig validates field types correctly."""
        # Should raise validation error for invalid types
        with pytest.raises(ValidationError):
            GitConfig(
                repo_url=123,  # type: ignore[arg-type]  # Invalid: should be str or None
                last_sync_timestamp=None,
                last_sync_commit=None,
            )

    def test_git_config_model_dump_includes_all_fields(self) -> None:
        """Test that model_dump includes all fields for serialization."""
        config = GitConfig(
            repo_url="https://github.com/example/prompts.git",
            last_sync_timestamp="2024-11-11T14:30:00Z",
            last_sync_commit="abc1234",
        )

        data = config.model_dump()

        assert "repo_url" in data
        assert "last_sync_timestamp" in data
        assert "last_sync_commit" in data
        assert data["repo_url"] == "https://github.com/example/prompts.git"
        assert data["last_sync_timestamp"] == "2024-11-11T14:30:00Z"
        assert data["last_sync_commit"] == "abc1234"


class TestHandlerConfig:
    """Test suite for HandlerConfig Pydantic model."""

    def test_handler_config_with_base_path(self) -> None:
        """Test that HandlerConfig can be created with a base_path value."""
        config = HandlerConfig(base_path="$HOME/.continue")

        assert config.base_path == "$HOME/.continue"

    def test_handler_config_with_none_base_path(self) -> None:
        """Test that HandlerConfig accepts None for base_path (optional field)."""
        config = HandlerConfig(base_path=None)

        assert config.base_path is None

    def test_handler_config_default_base_path_is_none(self) -> None:
        """Test that HandlerConfig defaults base_path to None if not provided."""
        config = HandlerConfig()

        assert config.base_path is None

    def test_handler_config_serialization(self) -> None:
        """Test that HandlerConfig serializes correctly with model_dump."""
        config = HandlerConfig(base_path="$PWD/.continue")

        data = config.model_dump()

        assert "base_path" in data
        assert data["base_path"] == "$PWD/.continue"

    def test_handler_config_deserialization(self) -> None:
        """Test that HandlerConfig deserializes correctly from dict."""
        data = {"base_path": "/custom/path/.continue"}

        config = HandlerConfig(**data)

        assert config.base_path == "/custom/path/.continue"

    def test_handler_config_validates_field_types(self) -> None:
        """Test that HandlerConfig validates field types correctly."""
        # Should raise validation error for invalid types
        with pytest.raises(ValidationError):
            HandlerConfig(base_path=123)  # type: ignore[arg-type]  # Invalid: should be str or None


class TestGitConfigHandlersField:
    """Test suite for GitConfig handlers field."""

    def test_git_config_with_handlers_dict(self) -> None:
        """Test that GitConfig accepts handlers dict containing multiple handlers."""
        config = GitConfig(
            repo_url="https://github.com/example/prompts.git",
            handlers={
                "continue": HandlerConfig(base_path="$PWD/.continue"),
                "cursor": HandlerConfig(base_path="$PWD/.cursor"),
            },
        )

        assert config.handlers is not None
        assert "continue" in config.handlers
        assert "cursor" in config.handlers
        assert config.handlers["continue"].base_path == "$PWD/.continue"
        assert config.handlers["cursor"].base_path == "$PWD/.cursor"

    def test_git_config_handlers_field_optional(self) -> None:
        """Test backward compatibility - handlers field is optional."""
        config = GitConfig(
            repo_url="https://github.com/example/prompts.git",
            last_sync_timestamp="2024-11-11T14:30:00Z",
        )

        assert config.handlers is None

    def test_git_config_serialization_with_handlers(self) -> None:
        """Test that GitConfig serializes correctly with handlers section."""
        config = GitConfig(
            repo_url="https://github.com/example/prompts.git",
            handlers={
                "continue": HandlerConfig(base_path="$HOME/.continue"),
                "windsurf": HandlerConfig(base_path="$PWD/.windsurf"),
            },
        )

        data = config.model_dump()

        assert "handlers" in data
        assert data["handlers"] is not None
        assert "continue" in data["handlers"]
        assert "windsurf" in data["handlers"]
        assert data["handlers"]["continue"]["base_path"] == "$HOME/.continue"
        assert data["handlers"]["windsurf"]["base_path"] == "$PWD/.windsurf"

    def test_git_config_deserialization_with_handlers(self) -> None:
        """Test that GitConfig deserializes from YAML with handlers section."""
        data = {
            "repo_url": "https://github.com/example/prompts.git",
            "last_sync_timestamp": "2024-11-11T14:30:00Z",
            "last_sync_commit": "abc1234",
            "handlers": {
                "continue": {"base_path": "$PWD/.continue"},
                "aider": {"base_path": "/custom/aider"},
            },
        }

        config = GitConfig(**data)

        assert config.handlers is not None
        assert len(config.handlers) == 2
        assert isinstance(config.handlers["continue"], HandlerConfig)
        assert config.handlers["continue"].base_path == "$PWD/.continue"
        assert config.handlers["aider"].base_path == "/custom/aider"
