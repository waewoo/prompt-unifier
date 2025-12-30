"""Additional tests for GitService to increase coverage."""

from pathlib import Path
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

import git
from prompt_unifier.git.service import GitService, _check_empty_repository, _checkout_branch


class TestGitServiceExtra:
    """Tests for GitService error paths and helpers."""

    def test_extract_prompts_dir_missing_prompts(self, tmp_path: Path):
        """Test extract_prompts_dir raises ValueError when prompts/ is missing."""
        service = GitService()
        source = tmp_path / "source"
        source.mkdir()
        target = tmp_path / "target"

        with pytest.raises(ValueError, match="Repository does not contain a prompts/ directory"):
            service.extract_prompts_dir(source, target)

    @patch("prompt_unifier.git.service.retry_with_backoff")
    @patch("git.Repo.clone_from")
    @patch("prompt_unifier.git.service._check_empty_repository")
    def test_clone_to_temp_checkout_failure(self, mock_check, mock_clone, mock_retry):
        """Test clone_to_temp raises ValueError on branch checkout failure."""
        service = GitService()

        # Mock successful clone
        mock_repo = MagicMock()
        mock_repo.head.commit = MagicMock()
        mock_retry.return_value = mock_repo

        # Mock checkout failure
        # We need to mock _checkout_branch behavior since it's called inside clone_to_temp
        # But _checkout_branch is imported in service.py, so we should patch it there
        with patch("prompt_unifier.git.service._checkout_branch") as mock_checkout:
            mock_checkout.side_effect = ValueError("Failed to checkout branch")

            with pytest.raises(ValueError, match="Failed to checkout branch"):
                service.clone_to_temp("http://repo.git", branch="feature")

    def test_check_empty_repository_error(self):
        """Test _check_empty_repository raises detailed ValueError."""
        mock_repo = MagicMock()
        # Simulate value error when accessing head.commit (empty repo)
        p = PropertyMock(side_effect=ValueError("reference at 'HEAD' does not exist"))
        type(mock_repo.head).commit = p

        with pytest.raises(ValueError, match="Repository is empty"):
            _check_empty_repository(mock_repo, "http://repo.git")

    def test_checkout_branch_error(self):
        """Test _checkout_branch raises detailed ValueError."""
        mock_repo = MagicMock()
        mock_repo.git.checkout.side_effect = git.exc.GitCommandError("checkout", "error")

        with pytest.raises(ValueError, match="Failed to checkout branch"):
            _checkout_branch(mock_repo, "dev", "http://repo.git")
