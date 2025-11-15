"""Tests for ConfigManager class.

This module tests configuration file creation, loading, saving, and updating
following the YAML patterns from core/yaml_parser.py.
"""

from pathlib import Path

import yaml

from prompt_manager.config.manager import ConfigManager
from prompt_manager.models.git_config import GitConfig


class TestConfigManager:
    """Test suite for ConfigManager class."""

    def test_save_config_creates_valid_yaml_file(self, tmp_path: Path) -> None:
        """Test that save_config creates a properly formatted YAML file with all required fields."""
        manager = ConfigManager()
        config_path = tmp_path / "config.yaml"

        config = GitConfig(
            repo_url="https://github.com/example/prompts.git",
            last_sync_timestamp="2024-11-11T14:30:00Z",
            last_sync_commit="abc1234",
        )

        manager.save_config(config_path, config)

        # Verify file was created
        assert config_path.exists()

        # Verify YAML is valid and contains expected fields
        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert data["repo_url"] == "https://github.com/example/prompts.git"
        assert data["last_sync_timestamp"] == "2024-11-11T14:30:00Z"
        assert data["last_sync_commit"] == "abc1234"

    def test_load_config_from_valid_yaml_file(self, tmp_path: Path) -> None:
        """Test that load_config successfully loads valid YAML configuration."""
        manager = ConfigManager()
        config_path = tmp_path / "config.yaml"

        # Create a valid config file
        config_data = {
            "repo_url": "https://github.com/example/prompts.git",
            "last_sync_timestamp": "2024-11-11T14:30:00Z",
            "last_sync_commit": "abc1234",
        }
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(config_data, f, default_flow_style=False)

        # Load and verify
        config = manager.load_config(config_path)

        assert config is not None
        assert config.repo_url == "https://github.com/example/prompts.git"
        assert config.last_sync_timestamp == "2024-11-11T14:30:00Z"
        assert config.last_sync_commit == "abc1234"

    def test_load_config_returns_none_for_missing_file(self, tmp_path: Path) -> None:
        """Test that load_config returns None and handles FileNotFoundError gracefully."""
        manager = ConfigManager()
        config_path = tmp_path / "nonexistent.yaml"

        config = manager.load_config(config_path)

        assert config is None

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
        """Test that update_sync_info updates timestamp and commit hash in existing config."""
        manager = ConfigManager()
        config_path = tmp_path / "config.yaml"

        # Create initial config
        initial_config = GitConfig(
            repo_url="https://github.com/example/prompts.git",
            last_sync_timestamp="2024-11-10T10:00:00Z",
            last_sync_commit="old1234",
        )
        manager.save_config(config_path, initial_config)

        # Update sync info
        new_repo_url = "https://github.com/example/prompts.git"
        new_commit_hash = "new5678"
        manager.update_sync_info(config_path, new_repo_url, new_commit_hash)

        # Load and verify update
        updated_config = manager.load_config(config_path)

        assert updated_config is not None
        assert updated_config.repo_url == new_repo_url
        assert updated_config.last_sync_commit == new_commit_hash
        # Timestamp should be updated (just verify it's different and valid ISO format)
        assert updated_config.last_sync_timestamp != "2024-11-10T10:00:00Z"
        assert "T" in updated_config.last_sync_timestamp  # ISO 8601 format check

    def test_save_config_with_none_values(self, tmp_path: Path) -> None:
        """Test that save_config properly handles None values for optional fields."""
        manager = ConfigManager()
        config_path = tmp_path / "config.yaml"

        # Create config with None values (like after init command)
        config = GitConfig(repo_url=None, last_sync_timestamp=None, last_sync_commit=None)

        manager.save_config(config_path, config)

        # Verify file was created and None values are properly saved
        assert config_path.exists()

        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # YAML represents None as null
        assert data["repo_url"] is None
        assert data["last_sync_timestamp"] is None
        assert data["last_sync_commit"] is None

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
        """Test that update_sync_info creates new config if file doesn't exist."""
        manager = ConfigManager()
        config_path = tmp_path / "new_config.yaml"

        # Update sync info on non-existent file (should create it)
        repo_url = "https://github.com/example/prompts.git"
        commit_hash = "abc1234"
        manager.update_sync_info(config_path, repo_url, commit_hash)

        # Verify file was created
        assert config_path.exists()

        # Load and verify
        config = manager.load_config(config_path)

        assert config is not None
        assert config.repo_url == repo_url
        assert config.last_sync_commit == commit_hash
        assert config.last_sync_timestamp is not None

    def test_save_config_with_deploy_fields(self, tmp_path: Path) -> None:
        """Test that save_config handles deploy_tags and target_handlers fields."""
        manager = ConfigManager()
        config_path = tmp_path / "config.yaml"

        config = GitConfig(
            repo_url="https://github.com/example/prompts.git",
            last_sync_timestamp="2024-11-11T14:30:00Z",
            last_sync_commit="abc1234",
            deploy_tags=["python", "review"],
            target_handlers=["continue", "cursor"],
        )

        manager.save_config(config_path, config)

        # Verify file was created
        assert config_path.exists()

        # Verify YAML contains new fields
        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert data["repo_url"] == "https://github.com/example/prompts.git"
        assert data["deploy_tags"] == ["python", "review"]
        assert data["target_handlers"] == ["continue", "cursor"]

    def test_load_config_with_deploy_fields(self, tmp_path: Path) -> None:
        """Test that load_config successfully loads config with deploy fields."""
        manager = ConfigManager()
        config_path = tmp_path / "config.yaml"

        # Create a valid config file with deploy fields
        config_data = {
            "repo_url": "https://github.com/example/prompts.git",
            "last_sync_timestamp": "2024-11-11T14:30:00Z",
            "last_sync_commit": "abc1234",
            "deploy_tags": ["python", "api"],
            "target_handlers": ["continue"],
        }
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(config_data, f, default_flow_style=False)

        # Load and verify
        config = manager.load_config(config_path)

        assert config is not None
        assert config.repo_url == "https://github.com/example/prompts.git"
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
