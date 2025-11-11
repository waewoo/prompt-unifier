"""Tests for GitConfig Pydantic model.

This module tests the GitConfig model validation and structure.
"""

import pytest
from pydantic import ValidationError

from prompt_manager.models.git_config import GitConfig


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
