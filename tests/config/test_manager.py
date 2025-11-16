"""Tests for ConfigManager class.

This module tests configuration file creation, loading, saving, and updating
following the YAML patterns from core/yaml_parser.py.
"""

from pathlib import Path

import yaml

from prompt_manager.config.manager import ConfigManager
from prompt_manager.models.git_config import GitConfig, HandlerConfig


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
            "repo_url": "https://github.com/example/prompts.git",
            "last_sync_timestamp": "2024-11-11T14:30:00Z",
            "last_sync_commit": "abc1234",
        }
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(config_data, f, default_flow_style=False)

        # Load and verify backward compatibility
        config = manager.load_config(config_path)

        assert config is not None
        assert config.repo_url == "https://github.com/example/prompts.git"
        assert config.handlers is None  # Should default to None

    def test_save_config_preserves_handlers_section(self, tmp_path: Path) -> None:
        """Test that save_config preserves handlers section on update."""
        manager = ConfigManager()
        config_path = tmp_path / "config.yaml"

        # Create initial config with handlers
        initial_config = GitConfig(
            repo_url="https://github.com/example/prompts.git",
            last_sync_timestamp="2024-11-15T10:30:00Z",
            last_sync_commit="abc1234",
            handlers={
                "continue": HandlerConfig(base_path="$PWD/.continue"),
                "cursor": HandlerConfig(base_path="$HOME/.cursor"),
            },
        )
        manager.save_config(config_path, initial_config)

        # Load, modify, and save again
        loaded_config = manager.load_config(config_path)
        assert loaded_config is not None
        loaded_config.last_sync_commit = "def5678"
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
        """Test that update_sync_info preserves handlers configuration."""
        manager = ConfigManager()
        config_path = tmp_path / "config.yaml"

        # Create initial config with handlers
        initial_config = GitConfig(
            repo_url="https://github.com/example/prompts.git",
            last_sync_timestamp="2024-11-15T10:30:00Z",
            last_sync_commit="abc1234",
            handlers={
                "continue": HandlerConfig(base_path="$PWD/.continue"),
                "cursor": HandlerConfig(base_path="$HOME/.cursor"),
            },
        )
        manager.save_config(config_path, initial_config)

        # Update sync info
        manager.update_sync_info(
            config_path,
            "https://github.com/example/prompts.git",
            "new5678",
        )

        # Verify handlers section is preserved
        updated_config = manager.load_config(config_path)
        assert updated_config is not None
        assert updated_config.handlers is not None
        assert "continue" in updated_config.handlers
        assert updated_config.handlers["continue"].base_path == "$PWD/.continue"
        assert updated_config.last_sync_commit == "new5678"
