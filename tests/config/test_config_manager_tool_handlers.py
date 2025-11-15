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

    def test_save_and_load_enabled_handlers(
        self, config_manager: ConfigManager, config_path: Path
    ) -> None:
        """Test that ConfigManager can save and load enabled handlers."""
        initial_config = GitConfig(
            repo_url="https://example.com/repo.git",
            last_sync_timestamp="2023-01-01T12:00:00Z",
            last_sync_commit="abc1234",
            storage_path="/tmp/storage",
            enabled_handlers=["handler_a", "handler_b"],
        )
        config_manager.save_config(config_path, initial_config)

        loaded_config = config_manager.load_config(config_path)
        assert loaded_config is not None
        assert loaded_config.enabled_handlers == ["handler_a", "handler_b"]

    def test_load_config_with_no_enabled_handlers_field(
        self, config_manager: ConfigManager, config_path: Path
    ) -> None:
        """Test loading config when enabled_handlers field is missing (should default to
        empty list)."""
        # Manually create a config file without enabled_handlers
        config_content = """
repo_url: https://example.com/repo.git
last_sync_timestamp: "2023-01-01T12:00:00Z"
last_sync_commit: abc1234
storage_path: /tmp/storage
"""
        config_path.write_text(config_content)

        loaded_config = config_manager.load_config(config_path)
        assert loaded_config is not None
        assert loaded_config.enabled_handlers == []

    def test_update_enabled_handlers(
        self, config_manager: ConfigManager, config_path: Path
    ) -> None:
        """Test updating the list of enabled handlers."""
        initial_config = GitConfig(
            repo_url="https://example.com/repo.git",
            last_sync_timestamp="2023-01-01T12:00:00Z",
            last_sync_commit="abc1234",
            storage_path="/tmp/storage",
            enabled_handlers=["handler_a"],
        )
        config_manager.save_config(config_path, initial_config)

        # Simulate updating the config with new enabled handlers
        updated_config_data = initial_config.model_dump()
        updated_config_data["enabled_handlers"] = ["handler_a", "handler_c"]
        updated_config = GitConfig(**updated_config_data)
        config_manager.save_config(config_path, updated_config)

        loaded_config = config_manager.load_config(config_path)
        assert loaded_config is not None
        assert loaded_config.enabled_handlers == ["handler_a", "handler_c"]

    def test_save_config_with_empty_enabled_handlers(
        self, config_manager: ConfigManager, config_path: Path
    ) -> None:
        """Test saving config with an empty list of enabled handlers."""
        initial_config = GitConfig(
            repo_url="https://example.com/repo.git",
            last_sync_timestamp="2023-01-01T12:00:00Z",
            last_sync_commit="abc1234",
            storage_path="/tmp/storage",
            enabled_handlers=[],
        )
        config_manager.save_config(config_path, initial_config)

        loaded_config = config_manager.load_config(config_path)
        assert loaded_config is not None
        assert loaded_config.enabled_handlers == []
