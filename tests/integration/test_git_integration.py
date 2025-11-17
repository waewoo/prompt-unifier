"""Integration tests for Git synchronization workflows.

These tests validate end-to-end Git integration scenarios including
complete workflows (init -> sync -> status), error handling, and
conflict resolution behaviors.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer

import git
from prompt_unifier.cli.commands import init, status, sync
from prompt_unifier.config.manager import ConfigManager
from prompt_unifier.git.service import GitService
from prompt_unifier.models.git_config import GitConfig


class TestCompleteGitWorkflow:
    """Integration tests for complete Git workflow scenarios."""

    def test_complete_workflow_init_sync_status(self, tmp_path: Path) -> None:
        """Test complete workflow: init -> sync -> status (end-to-end).

        This test validates that a user can:
        1. Initialize a project with init command
        2. Sync prompts from a repository
        3. Check status to see sync information
        """
        # Change to temporary directory for test
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            # Use temporary storage directory for this test
            storage_dir = tmp_path / "test_storage"

            # Step 1: Initialize project with custom storage path
            init(storage_path=str(storage_dir))

            # Verify .prompt-unifier/ directory and config were created
            assert (tmp_path / ".prompt-unifier").exists()
            assert (tmp_path / ".prompt-unifier" / "config.yaml").exists()

            # Verify prompts/ and rules/ in storage directory
            assert (storage_dir / "prompts").exists()
            assert (storage_dir / "rules").exists()

            # Step 2: Mock sync operation (create fake prompts directory in mock repo)
            mock_temp_dir = tmp_path / "mock_repo"
            mock_temp_dir.mkdir()
            mock_prompts_dir = mock_temp_dir / "prompts"
            mock_prompts_dir.mkdir()
            (mock_prompts_dir / "test.md").write_text("# Test prompt")

            with patch.object(GitService, "clone_to_temp") as mock_clone:
                with patch.object(GitService, "get_latest_commit") as mock_commit:
                    # Configure mocks
                    mock_repo = MagicMock(spec=git.Repo)
                    mock_clone.return_value = (mock_temp_dir, mock_repo)
                    mock_commit.return_value = "abc1234"

                    # Sync with repository
                    sync(repo="https://github.com/example/prompts.git")

                    # Verify prompts were synced to storage directory
                    assert (storage_dir / "prompts" / "test.md").exists()

                    # Verify config was updated
                    config_manager = ConfigManager()
                    config = config_manager.load_config(
                        tmp_path / ".prompt-unifier" / "config.yaml"
                    )
                    assert config is not None
                    assert config.repo_url == "https://github.com/example/prompts.git"
                    assert config.last_sync_commit == "abc1234"
                    assert config.last_sync_timestamp is not None

            # Step 3: Check status
            with patch.object(GitService, "check_remote_updates") as mock_updates:
                mock_updates.return_value = (False, 0)  # No updates available

                # Status should display without errors
                status()  # Should not raise any exceptions

        finally:
            os.chdir(original_cwd)

    def test_sync_overwrites_local_changes(self, tmp_path: Path) -> None:
        """Test sync overwrites local changes (auto-resolve to remote).

        This test validates that the sync command always takes remote changes
        and overwrites local modifications without prompting the user.
        """
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            # Use temporary storage directory for this test
            storage_dir = tmp_path / "test_storage"

            # Initialize project with custom storage path
            init(storage_path=str(storage_dir))

            # Create local prompts with content in storage directory
            local_prompts = storage_dir / "prompts"
            (local_prompts / "existing.md").write_text("# Local content")
            (local_prompts / "to_delete.md").write_text("# Will be removed")

            # Mock sync with different remote content
            mock_temp_dir = tmp_path / "mock_repo"
            mock_temp_dir.mkdir()
            mock_prompts_dir = mock_temp_dir / "prompts"
            mock_prompts_dir.mkdir()
            (mock_prompts_dir / "existing.md").write_text("# Remote content UPDATED")
            (mock_prompts_dir / "new_file.md").write_text("# New remote file")
            # Note: to_delete.md is NOT in remote

            with patch.object(GitService, "clone_to_temp") as mock_clone:
                with patch.object(GitService, "get_latest_commit") as mock_commit:
                    mock_repo = MagicMock(spec=git.Repo)
                    mock_clone.return_value = (mock_temp_dir, mock_repo)
                    mock_commit.return_value = "xyz5678"

                    # Sync - should overwrite local changes
                    sync(repo="https://github.com/example/prompts.git")

                    # Verify remote content overwrote local content
                    assert (local_prompts / "existing.md").read_text() == "# Remote content UPDATED"
                    assert (local_prompts / "new_file.md").exists()
                    # Note: Local file that's not in remote should remain
                    # (copytree with dirs_exist_ok=True doesn't delete extra files)

        finally:
            os.chdir(original_cwd)

    def test_sync_handles_missing_prompts_directory(self, tmp_path: Path) -> None:
        """Test sync handles missing prompts/ directory in remote repo.

        This test validates that sync fails gracefully with a clear error
        message when the remote repository doesn't contain a prompts/ directory.
        """
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            # Initialize project
            init()

            # Mock repo without prompts/ directory
            mock_temp_dir = tmp_path / "mock_repo_no_prompts"
            mock_temp_dir.mkdir()
            # No prompts/ directory created

            with patch.object(GitService, "clone_to_temp") as mock_clone:
                mock_repo = MagicMock(spec=git.Repo)
                mock_clone.return_value = (mock_temp_dir, mock_repo)

                # Sync should fail with ValueError about missing prompts/
                with pytest.raises(typer.Exit) as exc_info:
                    sync(repo="https://github.com/example/no-prompts.git")

                assert exc_info.value.exit_code == 1

        finally:
            os.chdir(original_cwd)

    def test_sync_with_authentication_error_shows_helpful_message(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test sync with authentication error shows helpful message.

        This test validates that authentication failures provide clear,
        actionable error messages to users about configuring Git credentials.
        """
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            # Initialize project
            init()

            # Mock authentication failure
            with patch.object(GitService, "clone_to_temp") as mock_clone:
                mock_clone.side_effect = ValueError(
                    "Failed to clone repository: Authentication failed. "
                    "Ensure Git credentials are configured."
                )

                # Sync should fail with authentication error
                with pytest.raises(typer.Exit) as exc_info:
                    sync(repo="https://github.com/private/repo.git")

                assert exc_info.value.exit_code == 1

                # Check that error message was displayed
                captured = capsys.readouterr()
                assert "Authentication failed" in captured.err

        finally:
            os.chdir(original_cwd)

    def test_sync_with_network_failure_retries_and_fails_gracefully(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test sync with network failure retries and fails gracefully.

        This test validates that network failures trigger retry logic
        (3 attempts) and eventually fail with a clear error message.
        """
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            # Initialize project
            init()

            # Mock network failure (retry logic is tested in GitService tests)
            with patch.object(GitService, "clone_to_temp") as mock_clone:
                mock_clone.side_effect = ValueError(
                    "Failed to clone repository: https://github.com/example/prompts.git. "
                    "Check URL and network connection."
                )

                # Sync should fail after retries
                with pytest.raises(typer.Exit) as exc_info:
                    sync(repo="https://github.com/example/prompts.git")

                assert exc_info.value.exit_code == 1

                # Check that error message was displayed
                captured = capsys.readouterr()
                assert "Check URL and network connection" in captured.err

        finally:
            os.chdir(original_cwd)

    def test_status_with_no_remote_access_shows_cached_information(self, tmp_path: Path) -> None:
        """Test status with no remote access shows cached information.

        This test validates that the status command gracefully handles
        network failures when checking for updates and displays cached
        sync information instead.
        """
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            # Initialize and configure project
            init()

            # Create config with sync information
            config_manager = ConfigManager()
            config_path = tmp_path / ".prompt-unifier" / "config.yaml"
            config = GitConfig(
                repo_url="https://github.com/example/prompts.git",
                last_sync_timestamp="2024-11-11T14:30:00Z",
                last_sync_commit="abc1234",
            )
            config_manager.save_config(config_path, config)

            # Mock network failure when checking for updates
            with patch.object(GitService, "check_remote_updates") as mock_updates:
                mock_updates.side_effect = ConnectionError("Network unreachable")

                # Status should still display cached information (no exception)
                status()  # Should not raise typer.Exit

        finally:
            os.chdir(original_cwd)

    def test_multiple_sync_operations(self, tmp_path: Path) -> None:
        """Test multiple sync operations (subsequent syncs after first).

        This test validates that subsequent syncs work correctly, reading
        the repository URL from config and updating sync metadata each time.
        """
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            # Use temporary storage directory for this test
            storage_dir = tmp_path / "test_storage"

            # Initialize project with custom storage path
            init(storage_path=str(storage_dir))

            # First sync with --repo flag
            mock_temp_dir_1 = tmp_path / "mock_repo_1"
            mock_temp_dir_1.mkdir()
            mock_prompts_1 = mock_temp_dir_1 / "prompts"
            mock_prompts_1.mkdir()
            (mock_prompts_1 / "first.md").write_text("# First sync")

            with patch.object(GitService, "clone_to_temp") as mock_clone:
                with patch.object(GitService, "get_latest_commit") as mock_commit:
                    mock_repo_1 = MagicMock(spec=git.Repo)
                    mock_clone.return_value = (mock_temp_dir_1, mock_repo_1)
                    mock_commit.return_value = "abc1111"

                    sync(repo="https://github.com/example/prompts.git")

                    # Verify first sync to storage directory
                    assert (storage_dir / "prompts" / "first.md").exists()

            # Second sync WITHOUT --repo flag (should read from config)
            mock_temp_dir_2 = tmp_path / "mock_repo_2"
            mock_temp_dir_2.mkdir()
            mock_prompts_2 = mock_temp_dir_2 / "prompts"
            mock_prompts_2.mkdir()
            (mock_prompts_2 / "second.md").write_text("# Second sync")

            with patch.object(GitService, "clone_to_temp") as mock_clone:
                with patch.object(GitService, "get_latest_commit") as mock_commit:
                    mock_repo_2 = MagicMock(spec=git.Repo)
                    mock_clone.return_value = (mock_temp_dir_2, mock_repo_2)
                    mock_commit.return_value = "abc2222"

                    # Sync without --repo (reads URL from config)
                    # Pass repo=None explicitly to avoid default OptionInfo
                    sync(repo=None)

                    # Verify second sync updated files in storage directory
                    assert (storage_dir / "prompts" / "second.md").exists()

                    # Verify config was updated with new commit
                    config_manager = ConfigManager()
                    config = config_manager.load_config(
                        tmp_path / ".prompt-unifier" / "config.yaml"
                    )
                    assert config is not None
                    assert config.last_sync_commit == "abc2222"

        finally:
            os.chdir(original_cwd)

    def test_init_is_idempotent(self, tmp_path: Path) -> None:
        """Test that init command is idempotent.

        This test validates that running init twice in the same directory
        succeeds both times (idempotent behavior).
        """
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            # First init should succeed
            init()

            # Verify .prompt-unifier/ was created
            assert (tmp_path / ".prompt-unifier").exists()
            assert (tmp_path / ".prompt-unifier" / "config.yaml").exists()

            # Second init should also succeed (idempotent)
            init()

            # Verify everything still exists
            assert (tmp_path / ".prompt-unifier").exists()
            assert (tmp_path / ".prompt-unifier" / "config.yaml").exists()

        finally:
            os.chdir(original_cwd)
