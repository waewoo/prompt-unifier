"""Tests for the list command."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console

from prompt_unifier.cli.commands import list_content


@pytest.fixture
def mock_console():
    """Fixture for a mock Rich console."""
    return MagicMock(spec=Console)


@pytest.fixture
def mock_storage_dir(tmp_path: Path):
    """Fixture for storage directory with some content."""
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()

    # Create a prompt
    (prompts_dir / "prompt1.md").write_text("---\nname: Prompt 1\ntags: [tag1, tag2]\n---\nContent")

    # Create another prompt
    (prompts_dir / "prompt2.md").write_text("---\nname: Prompt 2\ntags: [tag2]\n---\nContent")

    # Create a rule
    (rules_dir / "rule1.md").write_text("---\nname: Rule 1\ncategory: style\n---\nContent")

    return tmp_path


class TestListCommand:
    """Tests for the list command."""

    @pytest.fixture(autouse=True)
    def setup_config(self, tmp_path):
        """Setup a dummy config file and mock cwd."""
        config_dir = tmp_path / ".prompt-unifier"
        config_dir.mkdir()
        (config_dir / "config.yaml").touch()

        # We need to patch Path.cwd to return tmp_path
        with patch("pathlib.Path.cwd", return_value=tmp_path):
            yield

    @patch("prompt_unifier.cli.commands.console")
    def test_list_all(self, mock_console, mock_storage_dir):
        """Test listing all content."""
        # Mock ConfigManager
        with patch("prompt_unifier.cli.commands.ConfigManager") as mock_manager_cls:
            mock_manager = MagicMock()
            mock_config = MagicMock()
            mock_config.storage_path = str(mock_storage_dir)
            mock_manager.load_config.return_value = mock_config
            mock_manager_cls.return_value = mock_manager

            list_content(verbose=False, tool=None, tag=None, sort="name")

            # Verify table was printed
            assert mock_console.print.called
            # We expect at least one call to print a Table
            args = mock_console.print.call_args[0]
            assert len(args) > 0

    @patch("prompt_unifier.cli.commands.console")
    def test_list_filter_by_tag(self, mock_console, mock_storage_dir):
        """Test filtering by tag."""
        with patch("prompt_unifier.cli.commands.ConfigManager") as mock_manager_cls:
            mock_manager = MagicMock()
            mock_config = MagicMock()
            mock_config.storage_path = str(mock_storage_dir)
            mock_manager.load_config.return_value = mock_config
            mock_manager_cls.return_value = mock_manager

            # Filter by tag1 (only prompt1 has it)
            list_content(verbose=False, tool=None, tag="tag1", sort="name")

            assert mock_console.print.called

    @patch("prompt_unifier.cli.commands.console")
    def test_list_verbose(self, mock_console, mock_storage_dir):
        """Test verbose output."""
        with patch("prompt_unifier.cli.commands.ConfigManager") as mock_manager_cls:
            mock_manager = MagicMock()
            mock_config = MagicMock()
            mock_config.storage_path = str(mock_storage_dir)
            mock_manager.load_config.return_value = mock_config
            mock_manager_cls.return_value = mock_manager

            list_content(verbose=True, tool=None, tag=None, sort="name")

            # Should print more details (Syntax objects)
            assert mock_console.print.called

    @patch("prompt_unifier.cli.commands.console")
    def test_list_empty(self, mock_console, tmp_path):
        """Test listing when no content exists."""
        with patch("prompt_unifier.cli.commands.ConfigManager") as mock_manager_cls:
            mock_manager = MagicMock()
            mock_config = MagicMock()
            mock_config.storage_path = str(tmp_path)  # Empty dir
            mock_manager.load_config.return_value = mock_config
            mock_manager_cls.return_value = mock_manager

            list_content(verbose=False, tool=None, tag=None, sort="name")

            # Should print a message about no content
            assert mock_console.print.called

    @patch("prompt_unifier.cli.commands.console")
    def test_list_sort_by_date(self, mock_console, mock_storage_dir):
        """Test sorting by modification date."""
        with patch("prompt_unifier.cli.commands.ConfigManager") as mock_manager_cls:
            mock_manager = MagicMock()
            mock_config = MagicMock()
            mock_config.storage_path = str(mock_storage_dir)
            mock_manager.load_config.return_value = mock_config
            mock_manager_cls.return_value = mock_manager

            list_content(verbose=False, tool=None, tag=None, sort="date")

            # Verify table was printed
            assert mock_console.print.called

    @patch("prompt_unifier.cli.commands.console")
    def test_list_filter_by_tool(self, mock_console, mock_storage_dir):
        """Test filtering by tool (placeholder logic)."""
        with patch("prompt_unifier.cli.commands.ConfigManager") as mock_manager_cls:
            mock_manager = MagicMock()
            mock_config = MagicMock()
            mock_config.storage_path = str(mock_storage_dir)
            mock_manager.load_config.return_value = mock_config
            mock_manager_cls.return_value = mock_manager

            # Filter by tool - currently a placeholder
            list_content(verbose=False, tool="continue", tag=None, sort="name")

            assert mock_console.print.called
