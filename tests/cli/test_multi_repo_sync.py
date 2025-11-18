"""Tests for multi-repository sync CLI command.

This module tests the sync command with multiple --repo flags for
multi-repository synchronization functionality.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer

from prompt_unifier.cli.commands import sync
from prompt_unifier.models.git_config import GitConfig, RepositoryConfig


@pytest.fixture
def mock_git_service() -> MagicMock:
    """Create mock GitService for testing."""
    service = MagicMock()
    # Mock sync_multiple_repos to return a mock metadata object
    mock_metadata = MagicMock()
    mock_metadata.get_summary.return_value = {
        "total_files": 25,
        "total_conflicts": 3,
        "repositories": [
            {
                "url": "https://github.com/repo1/prompts.git",
                "branch": "main",
                "commit": "abc1234",
            },
            {
                "url": "https://github.com/repo2/prompts.git",
                "branch": "develop",
                "commit": "def5678",
            },
        ],
    }
    service.sync_multiple_repos.return_value = mock_metadata
    return service


@pytest.fixture
def mock_config_manager() -> MagicMock:
    """Create mock ConfigManager for testing."""
    manager = MagicMock()
    # Mock load_config to return a valid config with repos
    config = GitConfig(
        repos=[
            RepositoryConfig(url="https://github.com/config/repo1.git"),
            RepositoryConfig(url="https://github.com/config/repo2.git", branch="dev"),
        ],
        storage_path="/home/user/.prompt-unifier/storage",
    )
    manager.load_config.return_value = config
    return manager


# Test 1: sync command accepts multiple --repo flags and processes them
def test_sync_accepts_multiple_repo_flags(tmp_path: Path) -> None:
    """Test sync command accepts and processes multiple --repo flags."""
    config_dir = tmp_path / ".prompt-unifier"
    config_dir.mkdir()
    config_path = config_dir / "config.yaml"

    with patch("prompt_unifier.cli.commands.Path.cwd", return_value=tmp_path):
        with patch("prompt_unifier.cli.commands.ConfigManager") as mock_manager_class:
            with patch("prompt_unifier.cli.commands.GitService") as mock_service_class:
                # Setup mocks
                mock_manager = MagicMock()
                mock_manager_class.return_value = mock_manager

                config = GitConfig(storage_path=str(tmp_path / "storage"))
                mock_manager.load_config.return_value = config

                mock_service = MagicMock()
                mock_service_class.return_value = mock_service

                # Mock sync_multiple_repos return
                mock_metadata = MagicMock()
                mock_metadata.get_summary.return_value = {
                    "total_files": 10,
                    "total_conflicts": 0,
                    "repositories": [
                        {
                            "url": "https://github.com/repo1/prompts.git",
                            "branch": "main",
                            "commit": "abc1234",
                        },
                        {
                            "url": "https://github.com/repo2/prompts.git",
                            "branch": "main",
                            "commit": "def5678",
                        },
                    ],
                }
                mock_service.sync_multiple_repos.return_value = mock_metadata

                # Create config file
                config_path.write_text("repos: []")

                # Run sync with multiple --repo flags
                repos = [
                    "https://github.com/repo1/prompts.git",
                    "https://github.com/repo2/prompts.git",
                ]
                sync(repos=repos, storage_path=None)

                # Verify sync_multiple_repos was called
                assert mock_service.sync_multiple_repos.called
                call_args = mock_service.sync_multiple_repos.call_args
                repos_arg = call_args[1]["repos"]

                # Verify both repos were passed
                assert len(repos_arg) == 2
                assert repos_arg[0].url == "https://github.com/repo1/prompts.git"
                assert repos_arg[1].url == "https://github.com/repo2/prompts.git"


# Test 2: CLI --repo flags override config.yaml repos
def test_cli_repo_flags_override_config(tmp_path: Path) -> None:
    """Test that CLI --repo flags override config.yaml repos."""
    config_dir = tmp_path / ".prompt-unifier"
    config_dir.mkdir()
    config_path = config_dir / "config.yaml"

    with patch("prompt_unifier.cli.commands.Path.cwd", return_value=tmp_path):
        with patch("prompt_unifier.cli.commands.ConfigManager") as mock_manager_class:
            with patch("prompt_unifier.cli.commands.GitService") as mock_service_class:
                # Setup mocks
                mock_manager = MagicMock()
                mock_manager_class.return_value = mock_manager

                # Config has repos defined
                config = GitConfig(
                    repos=[
                        RepositoryConfig(url="https://github.com/config/repo1.git"),
                        RepositoryConfig(url="https://github.com/config/repo2.git"),
                    ],
                    storage_path=str(tmp_path / "storage"),
                )
                mock_manager.load_config.return_value = config

                mock_service = MagicMock()
                mock_service_class.return_value = mock_service

                # Mock sync_multiple_repos return
                mock_metadata = MagicMock()
                mock_metadata.get_summary.return_value = {
                    "total_files": 5,
                    "total_conflicts": 0,
                    "repositories": [
                        {
                            "url": "https://github.com/cli/override.git",
                            "branch": "main",
                            "commit": "xyz9876",
                        }
                    ],
                }
                mock_service.sync_multiple_repos.return_value = mock_metadata

                # Create config file
                config_path.write_text("repos: []")

                # Run sync with CLI --repo flag (should override config)
                cli_repos = ["https://github.com/cli/override.git"]
                sync(repos=cli_repos, storage_path=None)

                # Verify sync_multiple_repos was called with CLI repos, NOT config repos
                call_args = mock_service.sync_multiple_repos.call_args
                repos_arg = call_args[1]["repos"]

                assert len(repos_arg) == 1
                assert repos_arg[0].url == "https://github.com/cli/override.git"
                # Verify config repos were NOT used
                assert repos_arg[0].url != "https://github.com/config/repo1.git"


# Test 3: sync command uses config.yaml repos when no CLI flags provided
def test_sync_uses_config_repos_when_no_cli_flags(tmp_path: Path) -> None:
    """Test sync command uses config.yaml repos when no --repo flags provided."""
    config_dir = tmp_path / ".prompt-unifier"
    config_dir.mkdir()
    config_path = config_dir / "config.yaml"

    with patch("prompt_unifier.cli.commands.Path.cwd", return_value=tmp_path):
        with patch("prompt_unifier.cli.commands.ConfigManager") as mock_manager_class:
            with patch("prompt_unifier.cli.commands.GitService") as mock_service_class:
                # Setup mocks
                mock_manager = MagicMock()
                mock_manager_class.return_value = mock_manager

                # Config has repos defined
                config = GitConfig(
                    repos=[
                        RepositoryConfig(url="https://github.com/config/repo1.git"),
                        RepositoryConfig(
                            url="https://github.com/config/repo2.git", branch="develop"
                        ),
                    ],
                    storage_path=str(tmp_path / "storage"),
                )
                mock_manager.load_config.return_value = config

                mock_service = MagicMock()
                mock_service_class.return_value = mock_service

                # Mock sync_multiple_repos return
                mock_metadata = MagicMock()
                mock_metadata.get_summary.return_value = {
                    "total_files": 15,
                    "total_conflicts": 1,
                    "repositories": [
                        {
                            "url": "https://github.com/config/repo1.git",
                            "branch": "main",
                            "commit": "abc1234",
                        },
                        {
                            "url": "https://github.com/config/repo2.git",
                            "branch": "develop",
                            "commit": "def5678",
                        },
                    ],
                }
                mock_service.sync_multiple_repos.return_value = mock_metadata

                # Create config file
                config_path.write_text("repos: []")

                # Run sync without CLI --repo flags
                sync(repos=None, storage_path=None)

                # Verify sync_multiple_repos was called with config repos
                call_args = mock_service.sync_multiple_repos.call_args
                repos_arg = call_args[1]["repos"]

                assert len(repos_arg) == 2
                assert repos_arg[0].url == "https://github.com/config/repo1.git"
                assert repos_arg[1].url == "https://github.com/config/repo2.git"
                assert repos_arg[1].branch == "develop"


# Test 4: sync command fails when no repos provided (neither CLI nor config)
def test_sync_fails_when_no_repos_provided(tmp_path: Path) -> None:
    """Test sync command exits with error when no repos provided."""
    config_dir = tmp_path / ".prompt-unifier"
    config_dir.mkdir()
    config_path = config_dir / "config.yaml"

    with patch("prompt_unifier.cli.commands.Path.cwd", return_value=tmp_path):
        with patch("prompt_unifier.cli.commands.ConfigManager") as mock_manager_class:
            # Setup mocks
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager

            # Config has NO repos defined
            config = GitConfig(repos=None, storage_path=str(tmp_path / "storage"))
            mock_manager.load_config.return_value = config

            # Create config file
            config_path.write_text("repos: null")

            # Run sync without CLI --repo flags and no config repos
            # Should raise typer.Exit with code 1
            with pytest.raises(typer.Exit) as exc_info:
                sync(repos=None, storage_path=None)

            assert exc_info.value.exit_code == 1


# Test 5: sync command displays progress for each repository
def test_sync_displays_progress_for_each_repository(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test sync command displays progress information for each repository."""
    config_dir = tmp_path / ".prompt-unifier"
    config_dir.mkdir()
    config_path = config_dir / "config.yaml"

    with patch("prompt_unifier.cli.commands.Path.cwd", return_value=tmp_path):
        with patch("prompt_unifier.cli.commands.ConfigManager") as mock_manager_class:
            with patch("prompt_unifier.cli.commands.GitService") as mock_service_class:
                with patch("prompt_unifier.cli.commands.console") as mock_console:
                    # Setup mocks
                    mock_manager = MagicMock()
                    mock_manager_class.return_value = mock_manager

                    config = GitConfig(storage_path=str(tmp_path / "storage"))
                    mock_manager.load_config.return_value = config

                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service

                    # Mock sync_multiple_repos return
                    mock_metadata = MagicMock()
                    mock_metadata.get_repositories.return_value = [
                        {
                            "url": "https://github.com/repo1/prompts.git",
                            "branch": "main",
                            "commit": "abc1234",
                            "timestamp": "2024-11-18T14:30:00Z",
                        },
                        {
                            "url": "https://github.com/repo2/prompts.git",
                            "branch": "develop",
                            "commit": "def5678",
                            "timestamp": "2024-11-18T14:30:00Z",
                        },
                    ]
                    mock_metadata.get_files.return_value = {
                        f"prompts/file{i}.md": {} for i in range(20)
                    }
                    mock_service.sync_multiple_repos.return_value = mock_metadata

                    # Create config file
                    config_path.write_text("repos: []")

                    # Run sync
                    repos = [
                        "https://github.com/repo1/prompts.git",
                        "https://github.com/repo2/prompts.git",
                    ]
                    sync(repos=repos, storage_path=None)

                    # Verify console.print was called with repository info
                    print_calls = [str(call) for call in mock_console.print.call_args_list]
                    assert any("repo1" in call for call in print_calls)
                    assert any("repo2" in call for call in print_calls)


# Test 6: sync command displays completion summary with all repos
def test_sync_displays_completion_summary(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test sync command displays completion summary with all synced repos."""
    config_dir = tmp_path / ".prompt-unifier"
    config_dir.mkdir()
    config_path = config_dir / "config.yaml"

    with patch("prompt_unifier.cli.commands.Path.cwd", return_value=tmp_path):
        with patch("prompt_unifier.cli.commands.ConfigManager") as mock_manager_class:
            with patch("prompt_unifier.cli.commands.GitService") as mock_service_class:
                with patch("prompt_unifier.cli.commands.console") as mock_console:
                    # Setup mocks
                    mock_manager = MagicMock()
                    mock_manager_class.return_value = mock_manager

                    config = GitConfig(storage_path=str(tmp_path / "storage"))
                    mock_manager.load_config.return_value = config

                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service

                    # Mock sync_multiple_repos return
                    mock_metadata = MagicMock()
                    mock_metadata.get_repositories.return_value = [
                        {
                            "url": "https://github.com/repo1/prompts.git",
                            "branch": "main",
                            "commit": "abc1234",
                            "timestamp": "2024-11-18T14:30:00Z",
                        },
                        {
                            "url": "https://github.com/repo2/prompts.git",
                            "branch": "develop",
                            "commit": "def5678",
                            "timestamp": "2024-11-18T14:30:00Z",
                        },
                    ]
                    mock_metadata.get_files.return_value = {
                        f"prompts/file{i}.md": {} for i in range(30)
                    }
                    mock_service.sync_multiple_repos.return_value = mock_metadata

                    # Create config file
                    config_path.write_text("repos: []")

                    # Run sync
                    repos = [
                        "https://github.com/repo1/prompts.git",
                        "https://github.com/repo2/prompts.git",
                    ]
                    sync(repos=repos, storage_path=None)

                    # Verify console.print was called with summary info
                    print_calls = [str(call) for call in mock_console.print.call_args_list]

                    # Check for total files in output
                    assert any("30" in call or "files" in call for call in print_calls)

                    # Check for repository count
                    assert any("2" in call or "Repositories" in call for call in print_calls)

                    # Check for commit hashes in output
                    assert any("abc1234" in call for call in print_calls)
                    assert any("def5678" in call for call in print_calls)


# Test 7: sync command handles validation errors gracefully
def test_sync_handles_validation_errors(tmp_path: Path) -> None:
    """Test sync command handles validation errors with clear messages."""
    config_dir = tmp_path / ".prompt-unifier"
    config_dir.mkdir()
    config_path = config_dir / "config.yaml"

    with patch("prompt_unifier.cli.commands.Path.cwd", return_value=tmp_path):
        with patch("prompt_unifier.cli.commands.ConfigManager") as mock_manager_class:
            with patch("prompt_unifier.cli.commands.GitService") as mock_service_class:
                # Setup mocks
                mock_manager = MagicMock()
                mock_manager_class.return_value = mock_manager

                config = GitConfig(storage_path=str(tmp_path / "storage"))
                mock_manager.load_config.return_value = config

                mock_service = MagicMock()
                mock_service_class.return_value = mock_service

                # Mock sync_multiple_repos to raise ValueError (validation error)
                mock_service.sync_multiple_repos.side_effect = ValueError(
                    "Repository 1/2 validation failed: https://invalid.git\n\n"
                    "Repository not found. Please verify the URL is correct."
                )

                # Create config file
                config_path.write_text("repos: []")

                # Run sync with invalid repo - should exit with code 1
                with pytest.raises(typer.Exit) as exc_info:
                    sync(repos=["https://invalid.git"], storage_path=None)

                assert exc_info.value.exit_code == 1


# Test 8: sync command updates config with repo_metadata after successful sync
def test_sync_updates_config_with_repo_metadata(tmp_path: Path) -> None:
    """Test sync command updates config with repo_metadata after successful sync."""
    config_dir = tmp_path / ".prompt-unifier"
    config_dir.mkdir()
    config_path = config_dir / "config.yaml"

    with patch("prompt_unifier.cli.commands.Path.cwd", return_value=tmp_path):
        with patch("prompt_unifier.cli.commands.ConfigManager") as mock_manager_class:
            with patch("prompt_unifier.cli.commands.GitService") as mock_service_class:
                # Setup mocks
                mock_manager = MagicMock()
                mock_manager_class.return_value = mock_manager

                config = GitConfig(storage_path=str(tmp_path / "storage"))
                mock_manager.load_config.return_value = config

                mock_service = MagicMock()
                mock_service_class.return_value = mock_service

                # Mock sync_multiple_repos return
                mock_metadata = MagicMock()
                mock_metadata.get_repositories.return_value = [
                    {
                        "url": "https://github.com/repo1/prompts.git",
                        "branch": "main",
                        "commit": "abc1234",
                        "timestamp": "2024-11-18T14:30:00Z",
                    }
                ]
                mock_metadata.get_files.return_value = {
                    f"prompts/file{i}.md": {} for i in range(10)
                }
                mock_service.sync_multiple_repos.return_value = mock_metadata

                # Create config file
                config_path.write_text("repos: []")

                # Run sync
                repos = ["https://github.com/repo1/prompts.git"]
                sync(repos=repos, storage_path=None)

                # Verify update_multi_repo_sync_info was called
                assert mock_manager.update_multi_repo_sync_info.called
                call_args = mock_manager.update_multi_repo_sync_info.call_args
                assert call_args[0][0] == config_path
                repo_metadata = call_args[0][1]
                assert len(repo_metadata) == 1
                assert repo_metadata[0]["url"] == "https://github.com/repo1/prompts.git"
