"""Tests for ConfigManager class.

This module tests configuration file creation, loading, saving, and updating
following the YAML patterns from core/yaml_parser.py.
"""

from pathlib import Path

import yaml

from prompt_unifier.config.manager import ConfigManager
from prompt_unifier.models.git_config import GitConfig, HandlerConfig


class TestConfigManager:
    """Test suite for ConfigManager class."""

    def test_save_config_creates_valid_yaml_file(self, tmp_path: Path) -> None:
        """Test that save_config creates a properly formatted YAML file with all required fields."""
        from prompt_unifier.models.git_config import RepositoryConfig

        manager = ConfigManager()
        config_path = tmp_path / "config.yaml"

        config = GitConfig(
            repos=[RepositoryConfig(url="https://github.com/example/prompts.git")],
            last_sync_timestamp="2024-11-11T14:30:00Z",
            repo_metadata=[
                {
                    "url": "https://github.com/example/prompts.git",
                    "branch": "main",
                    "commit": "abc1234",
                    "timestamp": "2024-11-11T14:30:00Z",
                }
            ],
        )

        manager.save_config(config_path, config)

        # Verify file was created
        assert config_path.exists()

        # Verify YAML is valid and contains expected fields
        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert data["repos"] is not None
        assert len(data["repos"]) == 1
        assert data["repos"][0]["url"] == "https://github.com/example/prompts.git"
        assert data["last_sync_timestamp"] == "2024-11-11T14:30:00Z"
        assert data["repo_metadata"] is not None
        assert len(data["repo_metadata"]) == 1
        assert data["repo_metadata"][0]["commit"] == "abc1234"

    def test_load_config_from_valid_yaml_file(self, tmp_path: Path) -> None:
        """Test that load_config successfully loads valid YAML configuration."""
        manager = ConfigManager()
        config_path = tmp_path / "config.yaml"

        # Create a valid config file
        config_data = {
            "repos": [{"url": "https://github.com/example/prompts.git"}],
            "last_sync_timestamp": "2024-11-11T14:30:00Z",
            "repo_metadata": [
                {
                    "url": "https://github.com/example/prompts.git",
                    "branch": "main",
                    "commit": "abc1234",
                    "timestamp": "2024-11-11T14:30:00Z",
                }
            ],
        }
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(config_data, f, default_flow_style=False)

        # Load and verify
        config = manager.load_config(config_path)

        assert config is not None
        assert config.repos is not None
        assert len(config.repos) == 1
        assert config.repos[0].url == "https://github.com/example/prompts.git"
        assert config.last_sync_timestamp == "2024-11-11T14:30:00Z"
        assert config.repo_metadata is not None
        assert len(config.repo_metadata) == 1
        assert config.repo_metadata[0]["commit"] == "abc1234"

    def test_load_config_returns_none_for_missing_file(self, tmp_path: Path) -> None:
        """Test that load_config returns None and handles FileNotFoundError gracefully."""
        manager = ConfigManager()
        config_path = tmp_path / "nonexistent.yaml"

        config = manager.load_config(config_path)

        assert config is None

    def test_load_config_returns_default_for_empty_yaml_file(self, tmp_path: Path) -> None:
        """Test that load_config returns default GitConfig for empty YAML file."""
        manager = ConfigManager()
        config_path = tmp_path / "empty.yaml"

        # Create an empty YAML file (yaml.safe_load returns None)
        config_path.touch()

        config = manager.load_config(config_path)

        # Should return default GitConfig, not None
        assert config is not None
        assert config.repos is None
        assert config.last_sync_timestamp is None

    def test_load_config_handles_corrupted_yaml_with_clear_error(self, tmp_path: Path) -> None:
        """Test that load_config handles corrupted YAML gracefully with clear error message."""
        manager = ConfigManager()
        config_path = tmp_path / "corrupted.yaml"

        # Create corrupted YAML file
        with open(config_path, "w", encoding="utf-8") as f:
            f.write("repo_url: https://example.com\n")
            f.write("last_sync_timestamp: [invalid: yaml: structure\n")
            f.write("last_sync_commit: abc1234\n")

        # Should return None for corrupted file
        config = manager.load_config(config_path)

        assert config is None

    def test_update_sync_info_updates_existing_config(self, tmp_path: Path) -> None:
        """Test that update_multi_repo_sync_info updates timestamp and repo metadata.

        Tests that existing config is properly updated with new metadata.
        """
        from prompt_unifier.models.git_config import RepositoryConfig

        manager = ConfigManager()
        config_path = tmp_path / "config.yaml"

        # Create initial config
        initial_config = GitConfig(
            repos=[RepositoryConfig(url="https://github.com/example/prompts.git")],
            last_sync_timestamp="2024-11-10T10:00:00Z",
            repo_metadata=[
                {
                    "url": "https://github.com/example/prompts.git",
                    "branch": "main",
                    "commit": "old1234",
                    "timestamp": "2024-11-10T10:00:00Z",
                }
            ],
        )
        manager.save_config(config_path, initial_config)

        # Update sync info with new metadata
        new_metadata = [
            {
                "url": "https://github.com/example/prompts.git",
                "branch": "main",
                "commit": "new5678",
                "timestamp": "2024-11-11T14:30:00Z",
            }
        ]
        manager.update_multi_repo_sync_info(config_path, new_metadata)

        # Load and verify update
        updated_config = manager.load_config(config_path)

        assert updated_config is not None
        assert updated_config.repo_metadata is not None
        assert len(updated_config.repo_metadata) == 1
        assert updated_config.repo_metadata[0]["commit"] == "new5678"
        # Timestamp should be updated
        assert updated_config.last_sync_timestamp != "2024-11-10T10:00:00Z"
        assert "T" in updated_config.last_sync_timestamp  # ISO 8601 format check

    def test_save_config_with_none_values(self, tmp_path: Path) -> None:
        """Test that save_config properly handles None values for optional fields."""
        manager = ConfigManager()
        config_path = tmp_path / "config.yaml"

        # Create config with None values (like after init command)
        config = GitConfig(repos=None, last_sync_timestamp=None, repo_metadata=None)

        manager.save_config(config_path, config)

        # Verify file was created and None values are properly saved
        assert config_path.exists()

        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # YAML represents None as null
        assert data["repos"] is None
        assert data["last_sync_timestamp"] is None
        assert data["repo_metadata"] is None

    def test_load_config_validates_yaml_is_dictionary(self, tmp_path: Path) -> None:
        """Test that load_config validates the YAML file contains a dictionary structure."""
        manager = ConfigManager()
        config_path = tmp_path / "invalid.yaml"

        # Create YAML file that's not a dictionary (it's a list)
        with open(config_path, "w", encoding="utf-8") as f:
            f.write("- item1\n")
            f.write("- item2\n")

        # Should return None for invalid structure
        config = manager.load_config(config_path)

        assert config is None

    def test_update_sync_info_creates_config_if_missing(self, tmp_path: Path) -> None:
        """Test that update_multi_repo_sync_info creates new config if file doesn't exist."""
        manager = ConfigManager()
        config_path = tmp_path / "new_config.yaml"

        # Update sync info on non-existent file (should create it)
        repo_metadata = [
            {
                "url": "https://github.com/example/prompts.git",
                "branch": "main",
                "commit": "abc1234",
                "timestamp": "2024-11-18T14:30:00Z",
            }
        ]
        manager.update_multi_repo_sync_info(config_path, repo_metadata)

        # Verify file was created
        assert config_path.exists()

        # Load and verify
        config = manager.load_config(config_path)

        assert config is not None
        assert config.repo_metadata is not None
        assert len(config.repo_metadata) == 1
        assert config.repo_metadata[0]["commit"] == "abc1234"
        assert config.last_sync_timestamp is not None

    def test_save_config_with_deploy_fields(self, tmp_path: Path) -> None:
        """Test that save_config handles deploy_tags and target_handlers fields."""
        from prompt_unifier.models.git_config import RepositoryConfig

        manager = ConfigManager()
        config_path = tmp_path / "config.yaml"

        config = GitConfig(
            repos=[RepositoryConfig(url="https://github.com/example/prompts.git")],
            last_sync_timestamp="2024-11-11T14:30:00Z",
            repo_metadata=[
                {
                    "url": "https://github.com/example/prompts.git",
                    "branch": "main",
                    "commit": "abc1234",
                    "timestamp": "2024-11-11T14:30:00Z",
                }
            ],
            deploy_tags=["python", "review"],
            target_handlers=["continue", "cursor"],
        )

        manager.save_config(config_path, config)

        # Verify file was created
        assert config_path.exists()

        # Verify YAML contains new fields
        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert data["repos"] is not None
        assert data["repos"][0]["url"] == "https://github.com/example/prompts.git"
        assert data["deploy_tags"] == ["python", "review"]
        assert data["target_handlers"] == ["continue", "cursor"]

    def test_load_config_with_deploy_fields(self, tmp_path: Path) -> None:
        """Test that load_config successfully loads config with deploy fields."""
        manager = ConfigManager()
        config_path = tmp_path / "config.yaml"

        # Create a valid config file with deploy fields
        config_data = {
            "repos": [{"url": "https://github.com/example/prompts.git"}],
            "last_sync_timestamp": "2024-11-11T14:30:00Z",
            "repo_metadata": [
                {
                    "url": "https://github.com/example/prompts.git",
                    "branch": "main",
                    "commit": "abc1234",
                    "timestamp": "2024-11-11T14:30:00Z",
                }
            ],
            "deploy_tags": ["python", "api"],
            "target_handlers": ["continue"],
        }
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(config_data, f, default_flow_style=False)

        # Load and verify
        config = manager.load_config(config_path)

        assert config is not None
        assert config.repos is not None
        assert config.repos[0].url == "https://github.com/example/prompts.git"
        assert config.deploy_tags == ["python", "api"]
        assert config.target_handlers == ["continue"]

    def test_save_config_with_none_deploy_fields(self, tmp_path: Path) -> None:
        """Test that save_config properly handles None values for deploy fields."""
        manager = ConfigManager()
        config_path = tmp_path / "config.yaml"

        # Create config with None deploy fields
        config = GitConfig(
            repo_url="https://github.com/example/prompts.git",
            deploy_tags=None,
            target_handlers=None,
        )

        manager.save_config(config_path, config)

        # Verify file was created and None values are properly saved
        assert config_path.exists()

        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # YAML represents None as null
        assert data["deploy_tags"] is None
        assert data["target_handlers"] is None

    # Task Group 2: ConfigManager Handlers Integration Tests

    def test_save_config_with_handlers_section(self, tmp_path: Path) -> None:
        """Test that save_config correctly serializes handlers configuration."""
        manager = ConfigManager()
        config_path = tmp_path / "config.yaml"

        config = GitConfig(
            repo_url="https://github.com/example/prompts.git",
            handlers={
                "continue": HandlerConfig(base_path="$PWD/.continue"),
                "cursor": HandlerConfig(base_path="$HOME/.cursor"),
                "windsurf": HandlerConfig(base_path="/custom/path/.windsurf"),
            },
        )

        manager.save_config(config_path, config)

        # Verify file was created
        assert config_path.exists()

        # Verify YAML contains handlers section with correct structure
        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert "handlers" in data
        assert data["handlers"]["continue"]["base_path"] == "$PWD/.continue"
        assert data["handlers"]["cursor"]["base_path"] == "$HOME/.cursor"
        assert data["handlers"]["windsurf"]["base_path"] == "/custom/path/.windsurf"

    def test_load_config_with_handlers_section(self, tmp_path: Path) -> None:
        """Test that load_config correctly deserializes handlers configuration."""
        manager = ConfigManager()
        config_path = tmp_path / "config.yaml"

        # Create a config file with handlers section
        config_data = {
            "repo_url": "https://github.com/example/prompts.git",
            "last_sync_timestamp": "2024-11-15T10:30:00Z",
            "last_sync_commit": "abc1234",
            "handlers": {
                "continue": {"base_path": "$PWD/.continue"},
                "cursor": {"base_path": "$PWD/.cursor"},
                "windsurf": {"base_path": "$PWD/.windsurf"},
                "aider": {"base_path": "$PWD/.aider"},
            },
        }
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(config_data, f, default_flow_style=False)

        # Load and verify
        config = manager.load_config(config_path)

        assert config is not None
        assert config.handlers is not None
        assert "continue" in config.handlers
        assert config.handlers["continue"].base_path == "$PWD/.continue"
        assert config.handlers["cursor"].base_path == "$PWD/.cursor"
        assert config.handlers["windsurf"].base_path == "$PWD/.windsurf"
        assert config.handlers["aider"].base_path == "$PWD/.aider"

    def test_load_config_with_missing_handlers_defaults_to_none(self, tmp_path: Path) -> None:
        """Test that load_config defaults handlers to None when section is missing."""
        manager = ConfigManager()
        config_path = tmp_path / "config.yaml"

        # Create a config file without handlers section (backward compatibility)
        config_data = {
            "repos": [{"url": "https://github.com/example/prompts.git"}],
            "last_sync_timestamp": "2024-11-11T14:30:00Z",
            "repo_metadata": [
                {
                    "url": "https://github.com/example/prompts.git",
                    "branch": "main",
                    "commit": "abc1234",
                    "timestamp": "2024-11-11T14:30:00Z",
                }
            ],
        }
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(config_data, f, default_flow_style=False)

        # Load and verify backward compatibility
        config = manager.load_config(config_path)

        assert config is not None
        assert config.repos is not None
        assert config.repos[0].url == "https://github.com/example/prompts.git"
        assert config.handlers is None  # Should default to None

    def test_save_config_preserves_handlers_section(self, tmp_path: Path) -> None:
        """Test that save_config preserves handlers section on update."""
        from prompt_unifier.models.git_config import RepositoryConfig

        manager = ConfigManager()
        config_path = tmp_path / "config.yaml"

        # Create initial config with handlers
        initial_config = GitConfig(
            repos=[RepositoryConfig(url="https://github.com/example/prompts.git")],
            last_sync_timestamp="2024-11-15T10:30:00Z",
            repo_metadata=[
                {
                    "url": "https://github.com/example/prompts.git",
                    "branch": "main",
                    "commit": "abc1234",
                    "timestamp": "2024-11-15T10:30:00Z",
                }
            ],
            handlers={
                "continue": HandlerConfig(base_path="$PWD/.continue"),
                "cursor": HandlerConfig(base_path="$HOME/.cursor"),
            },
        )
        manager.save_config(config_path, initial_config)

        # Load, modify, and save again
        loaded_config = manager.load_config(config_path)
        assert loaded_config is not None
        loaded_config.repo_metadata[0]["commit"] = "def5678"
        manager.save_config(config_path, loaded_config)

        # Verify handlers section is still present
        final_config = manager.load_config(config_path)
        assert final_config is not None
        assert final_config.handlers is not None
        assert "continue" in final_config.handlers
        assert final_config.handlers["continue"].base_path == "$PWD/.continue"

    def test_load_config_with_handlers_none_base_path(self, tmp_path: Path) -> None:
        """Test that load_config handles handlers with None base_path (use default)."""
        manager = ConfigManager()
        config_path = tmp_path / "config.yaml"

        # Create config with handler that has no base_path specified
        config_data = {
            "repo_url": "https://github.com/example/prompts.git",
            "handlers": {
                "continue": {"base_path": None},  # Explicitly None (use default)
                "cursor": {"base_path": "$PWD/.cursor"},
            },
        }
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(config_data, f, default_flow_style=False)

        # Load and verify
        config = manager.load_config(config_path)

        assert config is not None
        assert config.handlers is not None
        assert config.handlers["continue"].base_path is None  # Should be None
        assert config.handlers["cursor"].base_path == "$PWD/.cursor"

    def test_save_config_with_none_handlers(self, tmp_path: Path) -> None:
        """Test that save_config properly handles None handlers field."""
        manager = ConfigManager()
        config_path = tmp_path / "config.yaml"

        # Create config with None handlers (no per-handler configuration)
        config = GitConfig(
            repo_url="https://github.com/example/prompts.git",
            handlers=None,
        )

        manager.save_config(config_path, config)

        # Verify file was created and None value is properly saved
        assert config_path.exists()

        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # YAML represents None as null
        assert data["handlers"] is None

    def test_update_sync_info_preserves_handlers_section(self, tmp_path: Path) -> None:
        """Test that update_multi_repo_sync_info preserves handlers configuration."""
        from prompt_unifier.models.git_config import RepositoryConfig

        manager = ConfigManager()
        config_path = tmp_path / "config.yaml"

        # Create initial config with handlers
        initial_config = GitConfig(
            repos=[RepositoryConfig(url="https://github.com/example/prompts.git")],
            last_sync_timestamp="2024-11-15T10:30:00Z",
            repo_metadata=[
                {
                    "url": "https://github.com/example/prompts.git",
                    "branch": "main",
                    "commit": "abc1234",
                    "timestamp": "2024-11-15T10:30:00Z",
                }
            ],
            handlers={
                "continue": HandlerConfig(base_path="$PWD/.continue"),
                "cursor": HandlerConfig(base_path="$HOME/.cursor"),
            },
        )
        manager.save_config(config_path, initial_config)

        # Update sync info with new metadata
        new_metadata = [
            {
                "url": "https://github.com/example/prompts.git",
                "branch": "main",
                "commit": "new5678",
                "timestamp": "2024-11-16T14:30:00Z",
            }
        ]
        manager.update_multi_repo_sync_info(config_path, new_metadata)

        # Verify handlers section is preserved
        updated_config = manager.load_config(config_path)
        assert updated_config is not None
        assert updated_config.handlers is not None
        assert "continue" in updated_config.handlers
        assert updated_config.handlers["continue"].base_path == "$PWD/.continue"
        assert updated_config.repo_metadata[0]["commit"] == "new5678"
