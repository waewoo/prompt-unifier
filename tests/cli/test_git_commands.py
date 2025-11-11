"""Tests for Git integration CLI commands (init, sync, status).

This module tests the init, sync, and status commands for Git repository
synchronization functionality.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer
from typer.testing import CliRunner

from prompt_manager.cli.commands import init, status, sync
from prompt_manager.models.git_config import GitConfig


@pytest.fixture
def runner() -> CliRunner:
    """Create Typer CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_git_service() -> MagicMock:
    """Create mock GitService for testing."""
    return MagicMock()


@pytest.fixture
def mock_config_manager() -> MagicMock:
    """Create mock ConfigManager for testing."""
    return MagicMock()


# Test 1: init command creates .prompt-manager/ directory and config.yaml
def test_init_creates_prompt_manager_directory_and_config(tmp_path: Path) -> None:
    """Test init command creates .prompt-manager/ directory and config.yaml."""
    with patch("prompt_manager.cli.commands.Path.cwd", return_value=tmp_path):
        with patch("prompt_manager.cli.commands.ConfigManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager

            # Run init command
            init()

            # Verify .prompt-manager/ directory was created
            prompt_manager_dir = tmp_path / ".prompt-manager"
            assert prompt_manager_dir.exists()
            assert prompt_manager_dir.is_dir()

            # Verify config.yaml was created with empty placeholders
            config_path = prompt_manager_dir / "config.yaml"
            mock_manager.save_config.assert_called_once()
            call_args = mock_manager.save_config.call_args
            assert call_args[0][0] == config_path
            config: GitConfig = call_args[0][1]
            assert config.repo_url is None
            assert config.last_sync_timestamp is None
            assert config.last_sync_commit is None


# Test 2: init command creates prompts/ and rules/ directories
def test_init_creates_prompts_directory_structure(tmp_path: Path) -> None:
    """Test init command creates prompts/ and rules/ directories at project root."""
    with patch("prompt_manager.cli.commands.Path.cwd", return_value=tmp_path):
        with patch("prompt_manager.cli.commands.ConfigManager"):
            # Run init command
            init()

            # Verify prompts/ directory was created
            prompts_dir = tmp_path / "prompts"
            assert prompts_dir.exists()
            assert prompts_dir.is_dir()

            # Verify rules/ directory was created
            rules_dir = tmp_path / "rules"
            assert rules_dir.exists()
            assert rules_dir.is_dir()


# Test 3: init command creates .gitignore if it doesn't exist (without ignoring .prompt-manager/)
def test_init_creates_gitignore_without_ignoring_prompt_manager(tmp_path: Path) -> None:
    """Test init command creates .gitignore without ignoring .prompt-manager/."""
    with patch("prompt_manager.cli.commands.Path.cwd", return_value=tmp_path):
        with patch("prompt_manager.cli.commands.ConfigManager"):
            # Run init command
            init()

            # Verify .gitignore was created
            gitignore = tmp_path / ".gitignore"
            assert gitignore.exists()

            # Verify .prompt-manager/ is NOT in .gitignore
            content = gitignore.read_text()
            assert ".prompt-manager/" not in content
            assert ".prompt-manager" not in content


# Test 4: init command fails if .prompt-manager/ already exists
def test_init_fails_if_prompt_manager_already_exists(tmp_path: Path) -> None:
    """Test init command fails if .prompt-manager/ already exists."""
    with patch("prompt_manager.cli.commands.Path.cwd", return_value=tmp_path):
        # Create .prompt-manager/ directory before running init
        (tmp_path / ".prompt-manager").mkdir(parents=True)

        # Run init command - should raise Exit(1)
        with pytest.raises(typer.Exit) as exc_info:
            init()

        assert exc_info.value.exit_code == 1


# Test 5: sync command fails if init not run first (missing config.yaml)
def test_sync_fails_if_init_not_run(tmp_path: Path) -> None:
    """Test sync command fails if init not run first (missing config.yaml)."""
    with patch("prompt_manager.cli.commands.Path.cwd", return_value=tmp_path):
        with patch("prompt_manager.cli.commands.ConfigManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager
            # Simulate missing config
            mock_manager.load_config.return_value = None

            # Run sync command - should raise Exit(1)
            with pytest.raises(typer.Exit) as exc_info:
                sync(repo=None)

            assert exc_info.value.exit_code == 1


# Test 6: sync command with --repo flag stores URL and syncs prompts
def test_sync_with_repo_flag_stores_url_and_syncs(tmp_path: Path) -> None:
    """Test sync command with --repo flag stores URL and syncs prompts."""
    repo_url = "https://github.com/example/prompts.git"

    with patch("prompt_manager.cli.commands.Path.cwd", return_value=tmp_path):
        with patch("prompt_manager.cli.commands.ConfigManager") as mock_manager_class:
            with patch("prompt_manager.cli.commands.GitService") as mock_service_class:
                # Setup mocks
                mock_manager = MagicMock()
                mock_manager_class.return_value = mock_manager
                mock_service = MagicMock()
                mock_service_class.return_value = mock_service

                # Create .prompt-manager/config.yaml (actual file)
                (tmp_path / ".prompt-manager").mkdir(parents=True)
                config_path = tmp_path / ".prompt-manager" / "config.yaml"
                config_path.write_text(
                    "repo_url: null\nlast_sync_timestamp: null\nlast_sync_commit: null\n"
                )

                # Mock config loading (empty config initially)
                mock_manager.load_config.return_value = GitConfig(
                    repo_url=None, last_sync_timestamp=None, last_sync_commit=None
                )

                # Mock git operations
                mock_repo = MagicMock()
                temp_path = tmp_path / "temp"
                mock_service.clone_to_temp.return_value = (temp_path, mock_repo)
                mock_service.get_latest_commit.return_value = "abc1234"

                # Run sync command with --repo flag
                sync(repo=repo_url)

                # Verify clone was called with correct URL
                mock_service.clone_to_temp.assert_called_once_with(repo_url)

                # Verify extract_prompts_dir was called
                mock_service.extract_prompts_dir.assert_called_once()

                # Verify config was updated with repo URL and commit
                mock_manager.update_sync_info.assert_called_once_with(
                    config_path, repo_url, "abc1234"
                )


# Test 7: sync command without --repo flag reads URL from config
def test_sync_without_repo_flag_reads_from_config(tmp_path: Path) -> None:
    """Test sync command without --repo flag reads URL from config."""
    repo_url = "https://github.com/example/prompts.git"

    with patch("prompt_manager.cli.commands.Path.cwd", return_value=tmp_path):
        with patch("prompt_manager.cli.commands.ConfigManager") as mock_manager_class:
            with patch("prompt_manager.cli.commands.GitService") as mock_service_class:
                # Setup mocks
                mock_manager = MagicMock()
                mock_manager_class.return_value = mock_manager
                mock_service = MagicMock()
                mock_service_class.return_value = mock_service

                # Create .prompt-manager/config.yaml (actual file)
                (tmp_path / ".prompt-manager").mkdir(parents=True)
                config_path = tmp_path / ".prompt-manager" / "config.yaml"
                config_path.write_text(
                    "repo_url: null\nlast_sync_timestamp: null\nlast_sync_commit: null\n"
                )

                # Mock config loading with existing repo URL
                mock_manager.load_config.return_value = GitConfig(
                    repo_url=repo_url,
                    last_sync_timestamp="2024-11-11T14:30:00Z",
                    last_sync_commit="xyz7890",
                )

                # Mock git operations
                mock_repo = MagicMock()
                temp_path = tmp_path / "temp"
                mock_service.clone_to_temp.return_value = (temp_path, mock_repo)
                mock_service.get_latest_commit.return_value = "abc1234"

                # Run sync command WITHOUT --repo flag
                sync(repo=None)

                # Verify clone was called with URL from config
                mock_service.clone_to_temp.assert_called_once_with(repo_url)


# Test 8: status command displays repo URL, last sync time, and update availability
def test_status_displays_repo_info_and_updates(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test status command displays repo URL, last sync time, and update availability."""
    repo_url = "https://github.com/example/prompts.git"

    with patch("prompt_manager.cli.commands.Path.cwd", return_value=tmp_path):
        with patch("prompt_manager.cli.commands.ConfigManager") as mock_manager_class:
            with patch("prompt_manager.cli.commands.GitService") as mock_service_class:
                # Setup mocks
                mock_manager = MagicMock()
                mock_manager_class.return_value = mock_manager
                mock_service = MagicMock()
                mock_service_class.return_value = mock_service

                # Create .prompt-manager/config.yaml (actual file)
                (tmp_path / ".prompt-manager").mkdir(parents=True)
                config_path = tmp_path / ".prompt-manager" / "config.yaml"
                config_path.write_text(
                    "repo_url: null\nlast_sync_timestamp: null\nlast_sync_commit: null\n"
                )

                # Mock config loading
                mock_manager.load_config.return_value = GitConfig(
                    repo_url=repo_url,
                    last_sync_timestamp="2024-11-11T14:30:00Z",
                    last_sync_commit="abc1234",
                )

                # Mock check for updates - updates available
                mock_service.check_remote_updates.return_value = (True, 3)

                # Run status command
                status()

                # Verify check_remote_updates was called
                mock_service.check_remote_updates.assert_called_once_with(repo_url, "abc1234")

                # Capture output and verify content
                captured = capsys.readouterr()
                output = captured.out

                # Verify output contains repo URL
                assert repo_url in output

                # Verify output contains timestamp info
                assert "2024-11-11" in output or "sync" in output.lower()

                # Verify output contains commit hash
                assert "abc1234" in output

                # Verify output indicates updates available
                assert "updates" in output.lower() or "behind" in output.lower() or "3" in output
