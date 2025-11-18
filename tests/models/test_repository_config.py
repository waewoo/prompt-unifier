"""Tests for RepositoryConfig and updated GitConfig models for multi-repository support.

This module tests the new RepositoryConfig model and GitConfig changes for
handling multiple repositories.
"""

import pytest
from pydantic import ValidationError

from prompt_unifier.models.git_config import GitConfig, RepositoryConfig


class TestRepositoryConfig:
    """Test suite for RepositoryConfig Pydantic model."""

    def test_repository_config_with_required_url_only(self) -> None:
        """Test RepositoryConfig with only required url field."""
        repo = RepositoryConfig(url="https://github.com/example/prompts.git")

        assert repo.url == "https://github.com/example/prompts.git"
        assert repo.branch is None
        assert repo.auth_config is None
        assert repo.include_patterns is None
        assert repo.exclude_patterns is None

    def test_repository_config_with_all_fields(self) -> None:
        """Test RepositoryConfig with all optional fields populated."""
        repo = RepositoryConfig(
            url="https://github.com/example/prompts.git",
            branch="develop",
            auth_config={"method": "token", "token": "ghp_123"},
            include_patterns=["*.md", "python/**"],
            exclude_patterns=["**/temp/*", "*.tmp"],
        )

        assert repo.url == "https://github.com/example/prompts.git"
        assert repo.branch == "develop"
        assert repo.auth_config == {"method": "token", "token": "ghp_123"}
        assert repo.include_patterns == ["*.md", "python/**"]
        assert repo.exclude_patterns == ["**/temp/*", "*.tmp"]

    def test_repository_config_requires_url(self) -> None:
        """Test that url field is required and raises ValidationError if missing."""
        with pytest.raises(ValidationError) as exc_info:
            RepositoryConfig()  # type: ignore[call-arg]

        assert "url" in str(exc_info.value)

    def test_repository_config_serialization(self) -> None:
        """Test that RepositoryConfig serializes correctly with model_dump."""
        repo = RepositoryConfig(
            url="https://github.com/example/prompts.git",
            branch="main",
            include_patterns=["prompts/**"],
        )

        data = repo.model_dump()

        assert data["url"] == "https://github.com/example/prompts.git"
        assert data["branch"] == "main"
        assert data["include_patterns"] == ["prompts/**"]
        assert data["auth_config"] is None
        assert data["exclude_patterns"] is None


class TestGitConfigMultiRepo:
    """Test suite for GitConfig with multi-repository support."""

    def test_git_config_with_repos_list(self) -> None:
        """Test GitConfig with repos field containing list of RepositoryConfig."""
        config = GitConfig(
            repos=[
                RepositoryConfig(url="https://github.com/repo1/prompts.git"),
                RepositoryConfig(url="https://github.com/repo2/prompts.git", branch="dev"),
            ]
        )

        assert config.repos is not None
        assert len(config.repos) == 2
        assert config.repos[0].url == "https://github.com/repo1/prompts.git"
        assert config.repos[1].url == "https://github.com/repo2/prompts.git"
        assert config.repos[1].branch == "dev"

    def test_git_config_with_repo_metadata(self) -> None:
        """Test GitConfig with repo_metadata field for tracking sync info."""
        metadata = [
            {
                "url": "https://github.com/repo1/prompts.git",
                "branch": "main",
                "commit": "abc123",
                "timestamp": "2024-11-18T10:00:00Z",
            },
            {
                "url": "https://github.com/repo2/prompts.git",
                "branch": "dev",
                "commit": "def456",
                "timestamp": "2024-11-18T10:01:00Z",
            },
        ]

        config = GitConfig(repo_metadata=metadata)

        assert config.repo_metadata is not None
        assert len(config.repo_metadata) == 2
        assert config.repo_metadata[0]["url"] == "https://github.com/repo1/prompts.git"
        assert config.repo_metadata[1]["commit"] == "def456"

    def test_git_config_repos_field_is_optional(self) -> None:
        """Test that repos field is optional (can be None for init)."""
        config = GitConfig(repos=None)

        assert config.repos is None

    def test_git_config_serialization_with_repos(self) -> None:
        """Test GitConfig serialization with repos list for YAML output."""
        config = GitConfig(
            repos=[
                RepositoryConfig(
                    url="https://github.com/repo1/prompts.git",
                    branch="main",
                ),
                RepositoryConfig(
                    url="https://github.com/repo2/prompts.git",
                    include_patterns=["*.md"],
                ),
            ],
            storage_path="/home/user/.prompt-unifier/storage",
        )

        data = config.model_dump()

        assert "repos" in data
        assert len(data["repos"]) == 2
        assert data["repos"][0]["url"] == "https://github.com/repo1/prompts.git"
        assert data["repos"][0]["branch"] == "main"
        assert data["repos"][1]["include_patterns"] == ["*.md"]
        assert data["storage_path"] == "/home/user/.prompt-unifier/storage"
