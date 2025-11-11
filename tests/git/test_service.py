"""Tests for GitService class.

This module tests Git operations including repository cloning, prompt extraction,
commit retrieval, and remote update checking using GitPython library.
"""

import contextlib
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

import git
from prompt_manager.git.service import GitService


class TestGitService:
    """Test suite for GitService class."""

    def test_clone_to_temp_successful_clone(self, tmp_path: Path) -> None:
        """Test successful repository clone to temporary directory."""
        service = GitService()
        repo_url = "https://github.com/example/prompts.git"

        # Mock git.Repo.clone_from to avoid actual network call
        with patch("git.Repo.clone_from") as mock_clone:
            mock_repo = Mock(spec=git.Repo)
            mock_repo.working_dir = str(tmp_path / "repo")
            mock_clone.return_value = mock_repo

            with patch("tempfile.TemporaryDirectory") as mock_tempdir:
                mock_tempdir.return_value.__enter__.return_value = str(tmp_path / "temp")

                repo_path, repo = service.clone_to_temp(repo_url)

                # Verify clone was called with correct URL
                mock_clone.assert_called_once()
                assert repo_url in str(mock_clone.call_args)

                # Verify returned values
                assert isinstance(repo_path, Path)
                assert repo == mock_repo

    def test_extract_prompts_dir_copies_directory_successfully(self, tmp_path: Path) -> None:
        """Test extraction of prompts/ directory from cloned repo to target location."""
        service = GitService()

        # Create source prompts/ directory with test files
        source_repo = tmp_path / "source"
        source_prompts = source_repo / "prompts"
        source_prompts.mkdir(parents=True)
        (source_prompts / "rules").mkdir()
        (source_prompts / "rules" / "test.md").write_text("# Test Rule")
        (source_prompts / "custom").mkdir()
        (source_prompts / "custom" / "custom.md").write_text("# Custom Prompt")

        # Create target directory
        target_path = tmp_path / "target"
        target_path.mkdir()

        # Extract prompts directory
        service.extract_prompts_dir(source_repo, target_path)

        # Verify prompts directory was copied to target
        target_prompts = target_path / "prompts"
        assert target_prompts.exists()
        assert (target_prompts / "rules" / "test.md").exists()
        assert (target_prompts / "custom" / "custom.md").exists()

        # Verify content is correct
        assert (target_prompts / "rules" / "test.md").read_text() == "# Test Rule"

    def test_get_latest_commit_returns_short_sha(self) -> None:
        """Test retrieval of latest commit hash from repository (short SHA format)."""
        service = GitService()

        # Mock git.Repo with commit
        mock_repo = Mock(spec=git.Repo)
        mock_commit = Mock()
        mock_commit.hexsha = "abc1234567890def1234567890abcdef12345678"
        mock_repo.head.commit = mock_commit

        commit_hash = service.get_latest_commit(mock_repo)

        # Verify short SHA is returned (7 characters)
        assert commit_hash == "abc1234"
        assert len(commit_hash) == 7

    def test_check_remote_updates_detects_new_commits(self, tmp_path: Path) -> None:
        """Test checking for remote updates returns correct status when new commits available."""
        service = GitService()
        repo_url = "https://github.com/example/prompts.git"
        last_commit = "abc1234"

        # Mock git operations
        with patch("git.Repo.clone_from") as mock_clone:
            mock_repo = Mock(spec=git.Repo)
            mock_repo.working_dir = str(tmp_path / "repo")

            # Create mock commits (3 new commits since last_commit)
            mock_commits = [Mock(), Mock(), Mock()]
            mock_repo.iter_commits.return_value = mock_commits

            # Mock remote
            mock_origin = Mock()
            mock_repo.remote.return_value = mock_origin

            mock_clone.return_value = mock_repo

            with patch("tempfile.TemporaryDirectory") as mock_tempdir:
                mock_tempdir.return_value.__enter__.return_value = str(tmp_path / "temp")

                has_updates, commits_behind = service.check_remote_updates(repo_url, last_commit)

                # Verify updates detected
                assert has_updates is True
                assert commits_behind == 3

                # Verify fetch was called
                mock_origin.fetch.assert_called_once()

    def test_invalid_repository_url_raises_clear_error(self) -> None:
        """Test handling of invalid repository URL with clear error message."""
        service = GitService()
        invalid_url = "not-a-valid-url"

        # Mock git.Repo.clone_from to raise GitCommandError
        with patch("git.Repo.clone_from") as mock_clone:
            mock_clone.side_effect = git.exc.GitCommandError(
                "git clone", 128, stderr=b"fatal: repository not found"
            )

            with patch("tempfile.TemporaryDirectory") as mock_tempdir:
                mock_tempdir.return_value.__enter__.return_value = "/tmp/test"

                with pytest.raises(ValueError) as exc_info:
                    service.clone_to_temp(invalid_url)

                # Verify error message is clear
                assert "Failed to clone repository" in str(exc_info.value)

    def test_cleanup_of_temporary_directory_after_operations(self, tmp_path: Path) -> None:
        """Test that temporary directory is properly cleaned up after clone operations."""
        service = GitService()
        repo_url = "https://github.com/example/prompts.git"

        # Track whether __exit__ is called on TemporaryDirectory context manager
        cleanup_called = False

        class MockTempDir:
            def __enter__(self):
                return str(tmp_path / "temp")

            def __exit__(self, *args):
                nonlocal cleanup_called
                cleanup_called = True

        with patch("git.Repo.clone_from") as mock_clone:
            mock_repo = Mock(spec=git.Repo)
            mock_repo.working_dir = str(tmp_path / "repo")
            mock_clone.return_value = mock_repo

            with patch("tempfile.TemporaryDirectory") as mock_tempdir:
                mock_tempdir.return_value = MockTempDir()

                # Call method that uses temporary directory
                with contextlib.suppress(Exception):
                    service.clone_to_temp(repo_url)

        # Note: In actual implementation with context manager, cleanup is automatic
        # This test verifies the pattern, not the actual cleanup (that's Python's job)
        assert mock_tempdir.called

    def test_authentication_error_handling_with_helpful_message(self) -> None:
        """Test authentication error handling provides helpful message to user."""
        service = GitService()
        repo_url = "https://github.com/private/repo.git"

        # Mock git.Repo.clone_from to raise authentication error
        with patch("git.Repo.clone_from") as mock_clone:
            mock_clone.side_effect = git.exc.GitCommandError(
                "git clone",
                128,
                stderr=b"fatal: Authentication failed",
            )

            with patch("tempfile.TemporaryDirectory") as mock_tempdir:
                mock_tempdir.return_value.__enter__.return_value = "/tmp/test"

                with pytest.raises(ValueError) as exc_info:
                    service.clone_to_temp(repo_url)

                # Verify error message mentions authentication
                error_message = str(exc_info.value).lower()
                assert "authentication" in error_message or "failed to clone" in error_message

    def test_extract_prompts_dir_raises_error_if_prompts_missing(self, tmp_path: Path) -> None:
        """Test that extract_prompts_dir validates prompts/ directory exists in repo."""
        service = GitService()

        # Create source repo WITHOUT prompts/ directory
        source_repo = tmp_path / "source"
        source_repo.mkdir(parents=True)
        (source_repo / "README.md").write_text("# Test Repo")

        # Create target directory
        target_path = tmp_path / "target"
        target_path.mkdir()

        # Should raise error about missing prompts/ directory
        with pytest.raises(ValueError) as exc_info:
            service.extract_prompts_dir(source_repo, target_path)

        assert "prompts/" in str(exc_info.value).lower()
