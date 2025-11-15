from pathlib import Path

import pytest

from prompt_manager.config.manager import ConfigManager
from prompt_manager.models.git_config import GitConfig


class TestConfigManagerToolHandlers:
    """Test suite for ConfigManager's handling of tool handlers."""

    @pytest.fixture
    def config_manager(self) -> ConfigManager:
        """Fixture for ConfigManager instance."""
        return ConfigManager()

    @pytest.fixture
    def config_path(self, tmp_path: Path) -> Path:
        """Fixture for a temporary config file path."""
        return tmp_path / "config.yaml"

    def test_save_and_load_target_handlers(
        self, config_manager: ConfigManager, config_path: Path
    ) -> None:
        """Test that ConfigManager can save and load target handlers."""
        initial_config = GitConfig(
            repo_url="https://example.com/repo.git",
            last_sync_timestamp="2023-01-01T12:00:00Z",
            last_sync_commit="abc1234",
            storage_path="/tmp/storage",
            target_handlers=["continue", "cursor"],
        )
        config_manager.save_config(config_path, initial_config)

        loaded_config = config_manager.load_config(config_path)
        assert loaded_config is not None
        assert loaded_config.target_handlers == ["continue", "cursor"]

    def test_load_config_with_no_target_handlers_field(
        self, config_manager: ConfigManager, config_path: Path
    ) -> None:
        """Test loading config when target_handlers field is missing (should default to
        None)."""
        # Manually create a config file without target_handlers
        config_content = """
repo_url: https://example.com/repo.git
last_sync_timestamp: "2023-01-01T12:00:00Z"
last_sync_commit: abc1234
storage_path: /tmp/storage
"""
        config_path.write_text(config_content)

        loaded_config = config_manager.load_config(config_path)
        assert loaded_config is not None
        assert loaded_config.target_handlers is None

    def test_update_target_handlers(self, config_manager: ConfigManager, config_path: Path) -> None:
        """Test updating the list of target handlers."""
        initial_config = GitConfig(
            repo_url="https://example.com/repo.git",
            last_sync_timestamp="2023-01-01T12:00:00Z",
            last_sync_commit="abc1234",
            storage_path="/tmp/storage",
            target_handlers=["continue"],
        )
        config_manager.save_config(config_path, initial_config)

        # Simulate updating the config with new target handlers
        updated_config_data = initial_config.model_dump()
        updated_config_data["target_handlers"] = ["continue", "cursor"]
        updated_config = GitConfig(**updated_config_data)
        config_manager.save_config(config_path, updated_config)

        loaded_config = config_manager.load_config(config_path)
        assert loaded_config is not None
        assert loaded_config.target_handlers == ["continue", "cursor"]

    def test_save_config_with_empty_target_handlers(
        self, config_manager: ConfigManager, config_path: Path
    ) -> None:
        """Test saving config with an empty list of target handlers."""
        initial_config = GitConfig(
            repo_url="https://example.com/repo.git",
            last_sync_timestamp="2023-01-01T12:00:00Z",
            last_sync_commit="abc1234",
            storage_path="/tmp/storage",
            target_handlers=[],
        )
        config_manager.save_config(config_path, initial_config)

        loaded_config = config_manager.load_config(config_path)
        assert loaded_config is not None
        assert loaded_config.target_handlers == []
