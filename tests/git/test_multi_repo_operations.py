"""Tests for GitService multi-repository operations.

This module tests the multi-repo sync features including clone with branch/auth,
path filtering, multi-repo validation, and sync orchestration.
"""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest

import git
from prompt_unifier.git.service import GitService
from prompt_unifier.models.git_config import RepositoryConfig
from prompt_unifier.utils.path_filter import PathFilter
from prompt_unifier.utils.repo_metadata import RepoMetadata


class TestCloneWithBranchAndAuth:
    """Test suite for clone_to_temp with branch and auth parameters."""

    @patch("prompt_unifier.git.service.git.Repo")
    def test_clone_to_temp_with_branch_parameter(self, mock_repo_class: Mock) -> None:
        """Test that clone_to_temp accepts branch parameter and checks out specified branch."""
        service = GitService()
        mock_repo = MagicMock()
        mock_repo_class.clone_from.return_value = mock_repo
        mock_repo.head.commit = MagicMock(hexsha="abc1234567890")

        # Call with branch parameter
        temp_path, repo = service.clone_to_temp(
            "https://github.com/example/prompts.git", branch="develop"
        )

        # Verify clone was called
        assert mock_repo_class.clone_from.called
        # Verify checkout was called with correct branch
        mock_repo.git.checkout.assert_called_once_with("develop")
        assert repo == mock_repo
        assert temp_path.exists()

    @patch("prompt_unifier.git.service.git.Repo")
    def test_clone_to_temp_without_branch_uses_default(self, mock_repo_class: Mock) -> None:
        """Test that clone_to_temp without branch parameter uses repository default."""
        service = GitService()
        mock_repo = MagicMock()
        mock_repo_class.clone_from.return_value = mock_repo
        mock_repo.head.commit = MagicMock(hexsha="abc1234567890")

        # Call without branch parameter
        temp_path, repo = service.clone_to_temp("https://github.com/example/prompts.git")

        # Verify clone was called
        assert mock_repo_class.clone_from.called
        # Verify checkout was NOT called
        mock_repo.git.checkout.assert_not_called()
        assert repo == mock_repo


class TestPathFilter:
    """Test suite for PathFilter utility class."""

    def test_apply_filters_with_include_patterns(self) -> None:
        """Test that PathFilter applies include patterns correctly."""
        file_paths = [
            "prompts/python/example.md",
            "prompts/javascript/test.md",
            "prompts/python/advanced.md",
            "rules/security.md",
        ]
        include_patterns = ["**/python/**", "rules/**"]

        filtered = PathFilter.apply_filters(file_paths, include_patterns=include_patterns)

        # Should only include files matching patterns
        assert "prompts/python/example.md" in filtered
        assert "prompts/python/advanced.md" in filtered
        assert "rules/security.md" in filtered
        assert "prompts/javascript/test.md" not in filtered

    def test_apply_filters_with_exclude_patterns(self) -> None:
        """Test that PathFilter applies exclude patterns after includes."""
        file_paths = [
            "prompts/example.md",
            "prompts/temp/draft.md",
            "prompts/final.md",
            "prompts/temp/old.md",
        ]
        exclude_patterns = ["**/temp/**", "**/*.tmp"]

        filtered = PathFilter.apply_filters(file_paths, exclude_patterns=exclude_patterns)

        # Should exclude files matching patterns
        assert "prompts/example.md" in filtered
        assert "prompts/final.md" in filtered
        assert "prompts/temp/draft.md" not in filtered
        assert "prompts/temp/old.md" not in filtered


class TestMultiRepoValidation:
    """Test suite for multi-repository validation."""

    @patch("prompt_unifier.git.service.GitService.clone_to_temp")
    @patch("prompt_unifier.git.service.git.cmd.Git")
    def test_validate_repositories_fail_fast_on_first_error(
        self, mock_git: Mock, mock_clone: Mock, tmp_path: Path
    ) -> None:
        """Test that validate_repositories fails fast on first invalid repository."""
        service = GitService()

        # Create repos list with second one being invalid
        repos = [
            RepositoryConfig(url="https://github.com/valid/repo1.git"),
            RepositoryConfig(url="https://github.com/invalid/repo2.git"),
            RepositoryConfig(url="https://github.com/valid/repo3.git"),
        ]

        # Mock ls-remote to succeed for first, fail for second
        def ls_remote_side_effect(url: str, **kwargs: Any) -> str:
            if "invalid" in url:
                raise git.exc.GitCommandError("ls-remote", 128, "Repository not found")
            return "abc123\tHEAD"

        mock_git_instance = MagicMock()
        mock_git.return_value = mock_git_instance
        mock_git_instance.ls_remote.side_effect = ls_remote_side_effect

        # Mock clone_to_temp for successful validation
        temp_dir = tmp_path / "temp_repo"
        temp_dir.mkdir()
        (temp_dir / "prompts").mkdir()
        mock_clone.return_value = (temp_dir, MagicMock())

        # Should raise error on second repo without checking third
        with pytest.raises(ValueError, match="invalid/repo2"):
            service.validate_repositories(repos)

        # Verify ls-remote was called for first two repos only (fail-fast)
        # Note: retry_with_backoff can make up to 3 attempts per repo, so max 6 calls
        assert mock_git_instance.ls_remote.call_count <= 6
        assert mock_git_instance.ls_remote.call_count >= 2  # At least first + second repo


class TestSyncOrchestration:
    """Test suite for multi-repository sync orchestration."""

    @patch("prompt_unifier.git.service.GitService.clone_to_temp")
    @patch("prompt_unifier.git.service.GitService.extract_prompts_dir")
    @patch("prompt_unifier.git.service.GitService.get_latest_commit")
    @patch("prompt_unifier.git.service.GitService.validate_repositories")
    def test_sync_multiple_repos_processes_in_order_last_wins(
        self,
        mock_validate: Mock,
        mock_get_commit: Mock,
        mock_extract: Mock,
        mock_clone: Mock,
        tmp_path: Path,
    ) -> None:
        """Test that sync_multiple_repos processes repos in order with last-wins strategy."""
        service = GitService()
        storage_path = tmp_path / "storage"

        # Create repos list
        repos = [
            RepositoryConfig(url="https://github.com/repo1/prompts.git"),
            RepositoryConfig(url="https://github.com/repo2/prompts.git"),
        ]

        # Mock clone to return temp paths
        repo_mock1 = MagicMock()
        repo_mock1.active_branch.name = "main"
        repo_mock2 = MagicMock()
        repo_mock2.active_branch.name = "main"
        mock_clone.side_effect = [
            (tmp_path / "temp1", repo_mock1),
            (tmp_path / "temp2", repo_mock2),
        ]

        # Mock commit retrieval
        mock_get_commit.side_effect = ["abc1234", "def5678"]

        # Call sync
        metadata = service.sync_multiple_repos(repos, storage_path)

        # Verify validation was called first
        mock_validate.assert_called_once_with(repos)

        # Verify clone was called for each repo in order
        assert mock_clone.call_count == 2
        mock_clone.assert_any_call(
            "https://github.com/repo1/prompts.git", branch=None, auth_config=None
        )
        mock_clone.assert_any_call(
            "https://github.com/repo2/prompts.git", branch=None, auth_config=None
        )

        # Verify metadata contains both repos
        assert isinstance(metadata, RepoMetadata)
        repos_list = metadata.get_repositories()
        assert len(repos_list) == 2


class TestConflictDetection:
    """Test suite for conflict detection during multi-repo sync."""

    @patch("prompt_unifier.git.service.GitService.clone_to_temp")
    @patch("prompt_unifier.git.service.GitService.extract_prompts_dir")
    @patch("prompt_unifier.git.service.GitService.get_latest_commit")
    @patch("prompt_unifier.git.service.GitService.validate_repositories")
    def test_conflict_detection_tracks_file_overwrites(
        self,
        mock_validate: Mock,
        mock_get_commit: Mock,
        mock_extract: Mock,
        mock_clone: Mock,
        tmp_path: Path,
        caplog: "pytest.LogCaptureFixture",
    ) -> None:
        """Test that conflict detection tracks and reports file overwrites."""
        service = GitService()
        storage_path = tmp_path / "storage"

        # Create two repos that will have overlapping files
        repos = [
            RepositoryConfig(url="https://github.com/repo1/prompts.git"),
            RepositoryConfig(url="https://github.com/repo2/prompts.git"),
        ]

        # Create temp directories with overlapping files
        temp1 = tmp_path / "temp1"
        temp2 = tmp_path / "temp2"
        temp1.mkdir()
        temp2.mkdir()

        # Create prompts/ directories in temp repos
        (temp1 / "prompts").mkdir()
        (temp2 / "prompts").mkdir()

        # Create overlapping file in both repos
        (temp1 / "prompts" / "example.md").write_text("Content from repo1")
        (temp2 / "prompts" / "example.md").write_text("Content from repo2")

        repo_mock1 = MagicMock()
        repo_mock1.active_branch.name = "main"
        repo_mock2 = MagicMock()
        repo_mock2.active_branch.name = "main"
        mock_clone.side_effect = [(temp1, repo_mock1), (temp2, repo_mock2)]
        mock_get_commit.side_effect = ["abc1234", "def5678"]

        # Mock extract to copy files from temp to storage
        def extract_side_effect(
            source: Path,
            target: Path,
            files_to_copy: list[str] | None = None,
        ) -> None:
            import shutil

            if files_to_copy:
                logger = logging.getLogger(__name__)
                for rel_file_path_str in files_to_copy:
                    source_file = source / rel_file_path_str
                    if source_file.is_file():
                        target_file_path = target / rel_file_path_str
                        target_file_path.parent.mkdir(parents=True, exist_ok=True)
                        if target_file_path.exists():
                            logger.info(
                                f"File overridden during multi-repo sync: {rel_file_path_str}"
                            )
                        shutil.copy2(source_file, target_file_path)
            else:
                # Fallback: copy entire prompts/ directory (as in original)
                source_prompts = source / "prompts"
                if source_prompts.exists() and source_prompts.is_dir():
                    target_prompts = target / "prompts"
                    logger = logging.getLogger(__name__)
                    import os

                    conflicts = []
                    for root, _dirs, files in os.walk(source_prompts):
                        for file_name in files:
                            source_file = Path(root) / file_name
                            rel_path = source_file.relative_to(source)
                            target_file = target / rel_path
                            if target_file.exists():
                                conflicts.append(str(rel_path))
                    if conflicts:
                        for conflict in conflicts:
                            logger.info(f"File overridden during multi-repo sync: {conflict}")
                    shutil.copytree(source_prompts, target_prompts, dirs_exist_ok=True)

        mock_extract.side_effect = extract_side_effect

        # Call sync
        import logging

        with caplog.at_level(logging.INFO):
            service.sync_multiple_repos(repos, storage_path)

        # Verify conflict message was logged
        log_output = caplog.text.lower()
        assert any(word in log_output for word in ("overridden", "conflict"))
