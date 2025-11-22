"""Tests for the status command."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console

from prompt_unifier.cli.commands import status


@pytest.fixture
def mock_console():
    """Fixture for a mock Rich console."""
    return MagicMock(spec=Console)


@pytest.fixture
def mock_storage_dir(tmp_path: Path):
    """Fixture for storage directory."""
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    return tmp_path


class TestStatusCommand:
    """Tests for the status command."""

    @pytest.fixture(autouse=True)
    def setup_config(self, tmp_path):
        """Setup a dummy config file and mock cwd."""
        config_dir = tmp_path / ".prompt-unifier"
        config_dir.mkdir()
        (config_dir / "config.yaml").touch()

        with patch("pathlib.Path.cwd", return_value=tmp_path):
            yield

    @patch("prompt_unifier.cli.commands.console")
    @patch("prompt_unifier.cli.commands.ToolHandlerRegistry")
    def test_status_synced(self, mock_registry_cls, mock_console, mock_storage_dir):
        """Test status when all items are synced."""
        # Mock Registry and Handler
        mock_registry = MagicMock()
        mock_handler = MagicMock()
        mock_handler.get_name.return_value = "continue"

        # Mock get_deployment_status to return "synced"
        mock_handler.get_deployment_status.return_value = "synced"

        mock_registry.get_all_handlers.return_value = [mock_handler]
        mock_registry_cls.return_value = mock_registry

        # Mock ConfigManager
        with patch("prompt_unifier.cli.commands.ConfigManager") as mock_manager_cls:
            mock_manager = MagicMock()
            mock_config = MagicMock()
            mock_config.storage_path = str(mock_storage_dir)
            mock_config.target_handlers = ["continue"]
            mock_manager.load_config.return_value = mock_config
            mock_manager_cls.return_value = mock_manager

            # Mock parser to return one file
            with patch("prompt_unifier.cli.commands.ContentFileParser") as mock_parser_cls:
                mock_parser = MagicMock()
                mock_content = MagicMock()
                mock_content.title = "Test Prompt"
                mock_parser.parse_file.return_value = mock_content
                mock_parser_cls.return_value = mock_parser

                # Create a dummy prompt file
                (mock_storage_dir / "prompts" / "test.md").touch()

                status()

                # Verify output
                assert mock_console.print.called
                # Should verify that "Synced" is printed
                # We can check call_args_list for "Synced" string or style

    @patch("prompt_unifier.cli.commands.console")
    @patch("prompt_unifier.cli.commands.ToolHandlerRegistry")
    def test_status_outdated(self, mock_registry_cls, mock_console, mock_storage_dir):
        """Test status when items are outdated."""
        mock_registry = MagicMock()
        mock_handler = MagicMock()
        mock_handler.get_name.return_value = "continue"
        mock_handler.get_deployment_status.return_value = "outdated"
        mock_registry.get_all_handlers.return_value = [mock_handler]
        mock_registry_cls.return_value = mock_registry

        with patch("prompt_unifier.cli.commands.ConfigManager") as mock_manager_cls:
            mock_manager = MagicMock()
            mock_config = MagicMock()
            mock_config.storage_path = str(mock_storage_dir)
            mock_config.target_handlers = ["continue"]
            mock_manager.load_config.return_value = mock_config
            mock_manager_cls.return_value = mock_manager

            with patch("prompt_unifier.cli.commands.ContentFileParser") as mock_parser_cls:
                mock_parser = MagicMock()
                mock_content = MagicMock()
                mock_content.title = "Test Prompt"
                mock_parser.parse_file.return_value = mock_content
                mock_parser_cls.return_value = mock_parser

                (mock_storage_dir / "prompts" / "test.md").touch()

                status()

                assert mock_console.print.called

    @patch("prompt_unifier.cli.commands.console")
    @patch("prompt_unifier.cli.commands.ToolHandlerRegistry")
    def test_status_missing(self, mock_registry_cls, mock_console, mock_storage_dir):
        """Test status when items are missing."""
        mock_registry = MagicMock()
        mock_handler = MagicMock()
        mock_handler.get_name.return_value = "continue"
        mock_handler.get_deployment_status.return_value = "missing"
        mock_registry.get_all_handlers.return_value = [mock_handler]
        mock_registry_cls.return_value = mock_registry

        with patch("prompt_unifier.cli.commands.ConfigManager") as mock_manager_cls:
            mock_manager = MagicMock()
            mock_config = MagicMock()
            mock_config.storage_path = str(mock_storage_dir)
            mock_config.target_handlers = ["continue"]
            mock_manager.load_config.return_value = mock_config
            mock_manager_cls.return_value = mock_manager

            with patch("prompt_unifier.cli.commands.ContentFileParser") as mock_parser_cls:
                mock_parser = MagicMock()
                mock_content = MagicMock()
                mock_content.title = "Test Prompt"
                mock_parser.parse_file.return_value = mock_content
                mock_parser_cls.return_value = mock_parser

                (mock_storage_dir / "prompts" / "test.md").touch()

                status()

                assert mock_console.print.called
