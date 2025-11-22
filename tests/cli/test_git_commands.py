"""Tests for Git integration CLI commands (init, sync, status).

This module tests the init, sync, and status commands for Git repository
synchronization functionality.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer
from typer.testing import CliRunner

from prompt_unifier.cli.commands import init, status, sync
from prompt_unifier.models.git_config import GitConfig, RepositoryConfig


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


# Test 1: init command creates .prompt-unifier/ directory and config.yaml
def test_init_creates_prompt_unifier_directory_and_config(tmp_path: Path) -> None:
    """Test init command creates .prompt-unifier/ directory and config.yaml."""
    with patch("prompt_unifier.cli.commands.Path.cwd", return_value=tmp_path):
        with patch("prompt_unifier.cli.commands.ConfigManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager

            # Run init command
            init()

            # Verify .prompt-unifier/ directory was created
            prompt_unifier_dir = tmp_path / ".prompt-unifier"
            assert prompt_unifier_dir.exists()
            assert prompt_unifier_dir.is_dir()

            # Verify config.yaml was created with empty placeholders
            config_path = prompt_unifier_dir / "config.yaml"
            mock_manager.save_config.assert_called_once()
            call_args = mock_manager.save_config.call_args
            assert call_args[0][0] == config_path
            config: GitConfig = call_args[0][1]
            assert config.repos is None
            assert config.last_sync_timestamp is None
            assert config.repo_metadata is None


# Test 2: init command creates prompts/ and rules/ directories in centralized storage
def test_init_creates_prompts_directory_structure(tmp_path: Path) -> None:
    """Test init command creates prompts/ and rules/ directories in centralized storage."""
    with patch("prompt_unifier.cli.commands.Path.cwd", return_value=tmp_path):
        with patch("prompt_unifier.cli.commands.ConfigManager"):
            # Run init command
            init()

            # Verify prompts/ and rules/ are created in storage directory (not in tmp_path)
            storage_dir = Path.home() / ".prompt-unifier" / "storage"
            prompts_dir = storage_dir / "prompts"
            assert prompts_dir.exists()
            assert prompts_dir.is_dir()

            rules_dir = storage_dir / "rules"
            assert rules_dir.exists()
            assert rules_dir.is_dir()


# Test 3: init command creates .gitignore in storage directory
def test_init_creates_gitignore_without_ignoring_prompt_unifier(tmp_path: Path) -> None:
    """Test init command creates .gitignore in centralized storage directory."""
    with patch("prompt_unifier.cli.commands.Path.cwd", return_value=tmp_path):
        with patch("prompt_unifier.cli.commands.ConfigManager"):
            # Run init command
            init()

            # Verify .gitignore was created in storage directory
            storage_dir = Path.home() / ".prompt-unifier" / "storage"
            gitignore = storage_dir / ".gitignore"
            assert gitignore.exists()

            # Verify .prompt-unifier/ is NOT in .gitignore
            content = gitignore.read_text()
            assert ".prompt-unifier/" not in content
            assert ".prompt-unifier" not in content


# Test 4: init command is idempotent (succeeds when already initialized)
def test_init_is_idempotent_when_already_exists(tmp_path: Path) -> None:
    """Test init command is idempotent and succeeds when .prompt-unifier/ already exists."""
    with patch("prompt_unifier.cli.commands.Path.cwd", return_value=tmp_path):
        with patch("prompt_unifier.cli.commands.ConfigManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager

            # Create .prompt-unifier/ directory and config.yaml before running init
            (tmp_path / ".prompt-unifier").mkdir(parents=True)
            config_path = tmp_path / ".prompt-unifier" / "config.yaml"
            config_path.write_text("repo_url: null\nlast_sync_timestamp: null\n")

            # Mock load_config to return existing config
            from prompt_unifier.models.git_config import GitConfig

            mock_manager.load_config.return_value = GitConfig(
                repo_url=None,
                last_sync_timestamp=None,
                last_sync_commit=None,
                storage_path=str(tmp_path / "storage"),
            )

            # Run init command - should succeed (not raise)
            init()

            # Should not raise any exception - init is idempotent


# Test 5: sync command fails if init not run first (missing config.yaml)
def test_sync_fails_if_init_not_run(tmp_path: Path) -> None:
    """Test sync command fails if init not run first (missing config.yaml)."""
    with patch("prompt_unifier.cli.commands.Path.cwd", return_value=tmp_path):
        with patch("prompt_unifier.cli.commands.ConfigManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager
            # Simulate missing config
            mock_manager.load_config.return_value = None

            # Run sync command - should raise Exit(1)
            with pytest.raises(typer.Exit) as exc_info:
                sync(repos=None)

            assert exc_info.value.exit_code == 1


# Test 6: sync command with --repo flag stores URL and syncs prompts
def test_sync_with_repo_flag_stores_url_and_syncs(tmp_path: Path) -> None:
    """Test sync command with --repo flag uses multi-repo sync."""
    repo_url = "https://github.com/example/prompts.git"

    with patch("prompt_unifier.cli.commands.Path.cwd", return_value=tmp_path):
        with patch("prompt_unifier.cli.commands.ConfigManager") as mock_manager_class:
            with patch("prompt_unifier.cli.commands.GitService") as mock_service_class:
                # Setup mocks
                mock_manager = MagicMock()
                mock_manager_class.return_value = mock_manager
                mock_service = MagicMock()
                mock_service_class.return_value = mock_service

                # Create .prompt-unifier/config.yaml (actual file)
                (tmp_path / ".prompt-unifier").mkdir(parents=True)
                config_path = tmp_path / ".prompt-unifier" / "config.yaml"
                config_path.write_text("repos: null\n")

                # Mock config loading (empty config initially)
                mock_manager.load_config.return_value = GitConfig(repos=None)

                # Mock multi-repo sync
                mock_metadata = MagicMock()
                mock_metadata.get_repositories.return_value = [
                    {
                        "url": repo_url,
                        "branch": "main",
                        "commit": "abc1234",
                        "timestamp": "2024-11-18T14:30:00Z",
                    }
                ]
                mock_metadata.get_files.return_value = {"prompts/test.md": {}}
                mock_service.sync_multiple_repos.return_value = mock_metadata

                # Run sync command with --repo flag
                sync(repos=[repo_url])

                # Verify sync_multiple_repos was called
                assert mock_service.sync_multiple_repos.called

                # Verify config was updated with repo metadata
                mock_manager.update_multi_repo_sync_info.assert_called_once()


# Test 7: sync command without --repo flag reads repos from config
def test_sync_without_repo_flag_reads_from_config(tmp_path: Path) -> None:
    """Test sync command without --repo flag reads repos from config."""
    from prompt_unifier.models.git_config import RepositoryConfig

    repo_url = "https://github.com/example/prompts.git"

    with patch("prompt_unifier.cli.commands.Path.cwd", return_value=tmp_path):
        with patch("prompt_unifier.cli.commands.ConfigManager") as mock_manager_class:
            with patch("prompt_unifier.cli.commands.GitService") as mock_service_class:
                # Setup mocks
                mock_manager = MagicMock()
                mock_manager_class.return_value = mock_manager
                mock_service = MagicMock()
                mock_service_class.return_value = mock_service

                # Create .prompt-unifier/config.yaml (actual file)
                (tmp_path / ".prompt-unifier").mkdir(parents=True)
                config_path = tmp_path / ".prompt-unifier" / "config.yaml"
                config_path.write_text(f"repos:\n  - url: {repo_url}\n")

                # Mock config loading with existing repos
                mock_manager.load_config.return_value = GitConfig(
                    repos=[RepositoryConfig(url=repo_url)]
                )

                # Mock multi-repo sync
                mock_metadata = MagicMock()
                mock_metadata.get_repositories.return_value = []
                mock_metadata.get_files.return_value = {}
                mock_service.sync_multiple_repos.return_value = mock_metadata

                # Run sync command WITHOUT --repo flag
                sync(repos=None)

                # Verify sync_multiple_repos was called
                assert mock_service.sync_multiple_repos.called


# Test 8: status command displays repo URL, last sync time, and commit info
def test_status_displays_repo_info_and_updates(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test status command displays repo URL, last sync time, and commit info."""
    repo_url = "https://github.com/example/prompts.git"

    with patch("prompt_unifier.cli.commands.Path.cwd", return_value=tmp_path):
        with patch("prompt_unifier.cli.commands.ConfigManager") as mock_manager_class:
            # Setup mocks
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager

            # Create .prompt-unifier/config.yaml (actual file)
            (tmp_path / ".prompt-unifier").mkdir(parents=True)
            config_path = tmp_path / ".prompt-unifier" / "config.yaml"
            config_path.write_text(f"repos:\n  - url: {repo_url}\n")

            # Mock config loading with multi-repo metadata
            mock_manager.load_config.return_value = GitConfig(
                repos=[RepositoryConfig(url=repo_url)],
                repo_metadata=[
                    {
                        "url": repo_url,
                        "branch": "main",
                        "commit": "abc1234",
                        "timestamp": "2024-11-11T14:30:00Z",
                    }
                ],
                last_sync_timestamp="2024-11-11T14:30:00Z",
            )

            # Run status command
            status()

            # Capture output and verify content
            captured = capsys.readouterr()
            output = captured.out

            # Verify output contains repo URL
            assert repo_url in output

            # Verify output contains timestamp info
            assert "2024-11-11" in output

            # Verify output contains commit hash
            assert "abc1234" in output
