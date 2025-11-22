"""End-to-end integration tests for multi-repository sync feature.

This module tests complete multi-repo workflows from CLI through to storage and metadata,
focusing on critical integration points and real-world scenarios.

NOTE: Current implementation limitation - selective filtering only affects metadata tracking,
not actual file copying to storage. All files from prompts/ and rules/ directories are copied,
but only filtered files are tracked in .repo-metadata.json.
"""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from prompt_unifier.cli.commands import sync
from prompt_unifier.git.service import GitService
from prompt_unifier.models.git_config import GitConfig, RepositoryConfig
from prompt_unifier.utils.repo_metadata import RepoMetadata


class TestThreeRepoConflictResolution:
    """Test last-wins merge behavior with 3+ repositories."""

    @patch("prompt_unifier.git.service.GitService.clone_to_temp")
    @patch("prompt_unifier.git.service.GitService.get_latest_commit")
    @patch("prompt_unifier.git.service.GitService.validate_repositories")
    def test_last_wins_with_three_overlapping_repos(
        self,
        mock_validate: Mock,
        mock_get_commit: Mock,
        mock_clone: Mock,
        tmp_path: Path,
        caplog: "pytest.LogCaptureFixture",
    ) -> None:
        """Test that with 3 repos having same file, last repo wins and conflicts are reported."""
        service = GitService()
        storage_path = tmp_path / "storage"

        # Create 3 repos with overlapping "example.md" file
        repos = [
            RepositoryConfig(url="https://github.com/repo1/prompts.git"),
            RepositoryConfig(url="https://github.com/repo2/prompts.git"),
            RepositoryConfig(url="https://github.com/repo3/prompts.git"),
        ]

        # Create 3 temp directories with same file, different content
        temp1 = tmp_path / "temp1"
        temp2 = tmp_path / "temp2"
        temp3 = tmp_path / "temp3"
        for temp_dir in [temp1, temp2, temp3]:
            temp_dir.mkdir()
            (temp_dir / "prompts").mkdir()

        (temp1 / "prompts" / "example.md").write_text("Content from repo1")
        (temp2 / "prompts" / "example.md").write_text("Content from repo2")
        (temp3 / "prompts" / "example.md").write_text("Content from repo3 - FINAL")

        # Mock repos
        repo_mock1 = MagicMock()
        repo_mock1.active_branch.name = "main"
        repo_mock2 = MagicMock()
        repo_mock2.active_branch.name = "main"
        repo_mock3 = MagicMock()
        repo_mock3.active_branch.name = "main"

        mock_clone.side_effect = [
            (temp1, repo_mock1),
            (temp2, repo_mock2),
            (temp3, repo_mock3),
        ]
        mock_get_commit.side_effect = ["commit1", "commit2", "commit3"]

        # Call sync
        import logging

        with caplog.at_level(logging.INFO):
            metadata = service.sync_multiple_repos(repos, storage_path)

        # Verify last repo's content wins
        final_file = storage_path / "prompts" / "example.md"
        assert final_file.exists()
        assert final_file.read_text() == "Content from repo3 - FINAL"

        # Verify conflict messages were logged for both overwrites
        log_output = caplog.text.lower()
        assert "overridden" in log_output or "conflict" in log_output

        # Verify metadata tracks final source
        file_source = metadata.get_file_source("prompts/example.md")
        assert file_source is not None
        assert file_source["source_url"] == "https://github.com/repo3/prompts.git"
        assert file_source["commit"] == "commit3"


class TestBranchSpecificMultiRepoSync:
    """Test syncing multiple repositories with different branches."""

    @patch("prompt_unifier.git.service.GitService.clone_to_temp")
    @patch("prompt_unifier.git.service.GitService.get_latest_commit")
    @patch("prompt_unifier.git.service.GitService.validate_repositories")
    def test_sync_with_different_branches_per_repo(
        self,
        mock_validate: Mock,
        mock_get_commit: Mock,
        mock_clone: Mock,
        tmp_path: Path,
    ) -> None:
        """Test that each repo syncs from its configured branch."""
        service = GitService()
        storage_path = tmp_path / "storage"

        # Create repos with different branches
        repos = [
            RepositoryConfig(url="https://github.com/repo1/prompts.git", branch="main"),
            RepositoryConfig(url="https://github.com/repo2/prompts.git", branch="develop"),
            RepositoryConfig(url="https://github.com/repo3/prompts.git", branch="feature-xyz"),
        ]

        # Create temp directories
        temp1 = tmp_path / "temp1"
        temp2 = tmp_path / "temp2"
        temp3 = tmp_path / "temp3"
        for temp_dir in [temp1, temp2, temp3]:
            temp_dir.mkdir()
            (temp_dir / "prompts").mkdir()

        (temp1 / "prompts" / "main-branch.md").write_text("From main")
        (temp2 / "prompts" / "develop-branch.md").write_text("From develop")
        (temp3 / "prompts" / "feature-branch.md").write_text("From feature")

        # Mock repos with different active branches
        repo_mock1 = MagicMock()
        repo_mock1.active_branch.name = "main"
        repo_mock2 = MagicMock()
        repo_mock2.active_branch.name = "develop"
        repo_mock3 = MagicMock()
        repo_mock3.active_branch.name = "feature-xyz"

        mock_clone.side_effect = [
            (temp1, repo_mock1),
            (temp2, repo_mock2),
            (temp3, repo_mock3),
        ]
        mock_get_commit.side_effect = ["abc123", "def456", "ghi789"]

        # Call sync
        metadata = service.sync_multiple_repos(repos, storage_path)

        # Verify clone was called with correct branches
        assert mock_clone.call_count == 3
        mock_clone.assert_any_call(
            "https://github.com/repo1/prompts.git", branch="main", auth_config=None
        )
        mock_clone.assert_any_call(
            "https://github.com/repo2/prompts.git", branch="develop", auth_config=None
        )
        mock_clone.assert_any_call(
            "https://github.com/repo3/prompts.git", branch="feature-xyz", auth_config=None
        )

        # Verify metadata tracks correct branches
        repos_metadata = metadata.get_repositories()
        assert len(repos_metadata) == 3
        assert repos_metadata[0]["branch"] == "main"
        assert repos_metadata[1]["branch"] == "develop"
        assert repos_metadata[2]["branch"] == "feature-xyz"


class TestSelectiveFilteringMetadataTracking:
    """Test that selective filtering affects metadata tracking correctly.

    NOTE: Current implementation copies ALL files to storage but only tracks
    filtered files in metadata. This test verifies metadata tracking behavior.
    """

    @patch("prompt_unifier.git.service.GitService.clone_to_temp")
    @patch("prompt_unifier.git.service.GitService.get_latest_commit")
    @patch("prompt_unifier.git.service.GitService.validate_repositories")
    def test_metadata_only_tracks_filtered_files(
        self,
        mock_validate: Mock,
        mock_get_commit: Mock,
        mock_clone: Mock,
        tmp_path: Path,
    ) -> None:
        """Test that metadata only tracks files passing include/exclude filters."""
        service = GitService()
        storage_path = tmp_path / "storage"

        # Create repo with include pattern that filters some files
        repos = [
            RepositoryConfig(
                url="https://github.com/repo1/prompts.git",
                include_patterns=["**/*.md"],  # Only markdown files tracked in metadata
            ),
        ]

        # Create temp directory with .md and .txt files
        temp1 = tmp_path / "temp1"
        temp1.mkdir()
        (temp1 / "prompts").mkdir()
        (temp1 / "prompts" / "tracked.md").write_text("markdown - should be in metadata")
        (temp1 / "prompts" / "not-tracked.txt").write_text("text - not in metadata")

        repo_mock1 = MagicMock()
        repo_mock1.active_branch.name = "main"

        mock_clone.return_value = (temp1, repo_mock1)
        mock_get_commit.return_value = "abc123"

        # Call sync
        metadata = service.sync_multiple_repos(repos, storage_path)

        # Verify .md file is tracked in metadata
        md_source = metadata.get_file_source("prompts/tracked.md")
        assert md_source is not None
        assert md_source["source_url"] == "https://github.com/repo1/prompts.git"

        # Verify .txt file is NOT tracked in metadata (filtered out by include pattern)
        txt_source = metadata.get_file_source("prompts/not-tracked.txt")
        assert txt_source is None

        # NOTE: Both files are still copied to storage (implementation limitation)
        # but only .md file is tracked in metadata


class TestMetadataAccuracyVerification:
    """Test .repo-metadata.json accuracy after multi-repo sync."""

    @patch("prompt_unifier.git.service.GitService.clone_to_temp")
    @patch("prompt_unifier.git.service.GitService.get_latest_commit")
    @patch("prompt_unifier.git.service.GitService.validate_repositories")
    def test_metadata_file_contains_accurate_mappings(
        self,
        mock_validate: Mock,
        mock_get_commit: Mock,
        mock_clone: Mock,
        tmp_path: Path,
    ) -> None:
        """Test that .repo-metadata.json correctly maps all files to their source repos."""
        service = GitService()
        storage_path = tmp_path / "storage"

        # Create 2 repos with different files
        repos = [
            RepositoryConfig(url="https://github.com/repo1/prompts.git"),
            RepositoryConfig(url="https://github.com/repo2/prompts.git"),
        ]

        # Create temp directories
        temp1 = tmp_path / "temp1"
        temp2 = tmp_path / "temp2"
        temp1.mkdir()
        temp2.mkdir()
        (temp1 / "prompts").mkdir()
        (temp2 / "prompts").mkdir()

        (temp1 / "prompts" / "file1.md").write_text("From repo1")
        (temp2 / "prompts" / "file2.md").write_text("From repo2")

        repo_mock1 = MagicMock()
        repo_mock1.active_branch.name = "main"
        repo_mock2 = MagicMock()
        repo_mock2.active_branch.name = "develop"

        mock_clone.side_effect = [(temp1, repo_mock1), (temp2, repo_mock2)]
        mock_get_commit.side_effect = ["commit1", "commit2"]

        # Call sync
        service.sync_multiple_repos(repos, storage_path)

        # Verify .repo-metadata.json was created
        metadata_file = storage_path / ".repo-metadata.json"
        assert metadata_file.exists()

        # Load and verify metadata contents
        loaded_metadata = RepoMetadata.load_from_file(storage_path)

        # Verify file mappings
        file1_source = loaded_metadata.get_file_source("prompts/file1.md")
        assert file1_source is not None
        assert file1_source["source_url"] == "https://github.com/repo1/prompts.git"
        assert file1_source["branch"] == "main"
        assert file1_source["commit"] == "commit1"

        file2_source = loaded_metadata.get_file_source("prompts/file2.md")
        assert file2_source is not None
        assert file2_source["source_url"] == "https://github.com/repo2/prompts.git"
        assert file2_source["branch"] == "develop"
        assert file2_source["commit"] == "commit2"

        # Verify repositories list
        repos_list = loaded_metadata.get_repositories()
        assert len(repos_list) == 2
        assert repos_list[0]["url"] == "https://github.com/repo1/prompts.git"
        assert repos_list[1]["url"] == "https://github.com/repo2/prompts.git"


class TestCompleteStorageReplacement:
    """Test that storage directory is completely cleared before sync."""

    @patch("prompt_unifier.git.service.GitService.clone_to_temp")
    @patch("prompt_unifier.git.service.GitService.get_latest_commit")
    @patch("prompt_unifier.git.service.GitService.validate_repositories")
    def test_storage_cleared_before_multi_repo_sync(
        self,
        mock_validate: Mock,
        mock_get_commit: Mock,
        mock_clone: Mock,
        tmp_path: Path,
    ) -> None:
        """Test that existing files in storage are removed before new sync."""
        service = GitService()
        storage_path = tmp_path / "storage"

        # Create existing storage with old files
        storage_path.mkdir()
        (storage_path / "prompts").mkdir()
        old_file = storage_path / "prompts" / "old-file.md"
        old_file.write_text("This should be deleted")
        old_metadata = storage_path / ".repo-metadata.json"
        old_metadata.write_text('{"old": "metadata"}')

        # Create repo with new file
        repos = [RepositoryConfig(url="https://github.com/repo1/prompts.git")]

        temp1 = tmp_path / "temp1"
        temp1.mkdir()
        (temp1 / "prompts").mkdir()
        (temp1 / "prompts" / "new-file.md").write_text("New content")

        repo_mock1 = MagicMock()
        repo_mock1.active_branch.name = "main"
        mock_clone.return_value = (temp1, repo_mock1)
        mock_get_commit.return_value = "abc123"

        # Call sync
        service.sync_multiple_repos(repos, storage_path)

        # Verify old file was removed
        assert not old_file.exists()

        # Verify new file exists
        assert (storage_path / "prompts" / "new-file.md").exists()

        # Verify new metadata was created (not old metadata)
        metadata = RepoMetadata.load_from_file(storage_path)
        assert metadata.get_file_source("prompts/new-file.md") is not None
        files = metadata.get_files()
        assert "prompts/old-file.md" not in files


class TestCLIToStorageEndToEnd:
    """Test complete workflow from CLI command to storage and metadata."""

    def test_cli_sync_creates_correct_metadata_structure(self, tmp_path: Path) -> None:
        """Test that CLI sync command results in correct metadata structure."""
        config_dir = tmp_path / ".prompt-unifier"
        config_dir.mkdir()
        config_path = config_dir / "config.yaml"
        storage_path = tmp_path / "storage"

        with patch("prompt_unifier.cli.commands.Path.cwd", return_value=tmp_path):
            with patch("prompt_unifier.cli.commands.ConfigManager") as mock_manager_class:
                with patch("prompt_unifier.cli.commands.GitService") as mock_service_class:
                    # Setup mocks
                    mock_manager = MagicMock()
                    mock_manager_class.return_value = mock_manager

                    config = GitConfig(storage_path=str(storage_path))
                    mock_manager.load_config.return_value = config

                    mock_service = MagicMock()
                    mock_service_class.return_value = mock_service

                    # Create real metadata object for sync result
                    real_metadata = RepoMetadata()
                    real_metadata.add_repository(
                        url="https://github.com/repo1/prompts.git",
                        branch="main",
                        commit="abc123",
                        timestamp="2024-11-18T10:00:00Z",
                    )
                    real_metadata.add_file(
                        file_path="prompts/example.md",
                        source_url="https://github.com/repo1/prompts.git",
                        branch="main",
                        commit="abc123",
                        timestamp="2024-11-18T10:00:00Z",
                    )

                    # Mock get_repositories and get_files to return proper structure
                    mock_metadata = MagicMock()
                    mock_metadata.get_repositories.return_value = [
                        {
                            "url": "https://github.com/repo1/prompts.git",
                            "branch": "main",
                            "commit": "abc123",
                            "timestamp": "2024-11-18T10:00:00Z",
                        }
                    ]
                    mock_metadata.get_files.return_value = {"prompts/test.md": {}}
                    mock_service.sync_multiple_repos.return_value = mock_metadata

                    # Create config file
                    config_path.write_text("repos: []")

                    # Run CLI sync command
                    repos = ["https://github.com/repo1/prompts.git"]
                    sync(repos=repos, storage_path=None)

                    # Verify GitService.sync_multiple_repos was called correctly
                    assert mock_service.sync_multiple_repos.called
                    call_args = mock_service.sync_multiple_repos.call_args

                    # Verify repo was passed correctly
                    repos_arg = call_args[1]["repos"]
                    assert len(repos_arg) == 1
                    assert repos_arg[0].url == "https://github.com/repo1/prompts.git"

                    # Verify storage path was passed
                    storage_arg = call_args[1]["storage_path"]
                    assert str(storage_arg) == str(storage_path)

                    # Verify config was updated with metadata
                    assert mock_manager.update_multi_repo_sync_info.called
                    update_call_args = mock_manager.update_multi_repo_sync_info.call_args
                    assert update_call_args[0][0] == config_path
                    metadata_arg = update_call_args[0][1]
                    assert len(metadata_arg) == 1
                    assert metadata_arg[0]["url"] == "https://github.com/repo1/prompts.git"
                    assert metadata_arg[0]["commit"] == "abc123"


class TestFailFastValidationWithMultipleRepos:
    """Test fail-fast validation behavior with invalid repo in middle of list."""

    @patch("prompt_unifier.git.service.GitService.clone_to_temp")
    @patch("prompt_unifier.git.service.git.cmd.Git")
    def test_validation_fails_on_invalid_repo_without_syncing(
        self, mock_git: Mock, mock_clone: Mock, tmp_path: Path
    ) -> None:
        """Test that validation error on invalid repo prevents any syncing."""
        service = GitService()
        storage_path = tmp_path / "storage"

        # Create 3 repos, second one invalid
        repos = [
            RepositoryConfig(url="https://github.com/valid/repo1.git"),
            RepositoryConfig(url="https://github.com/invalid/repo2.git"),  # This will fail
            RepositoryConfig(url="https://github.com/valid/repo3.git"),
        ]

        # Mock Git.ls_remote to succeed for all (URL is valid format)
        mock_git_instance = MagicMock()
        mock_git.return_value = mock_git_instance
        mock_git_instance.ls_remote.return_value = "abc123\tHEAD\ndef456\trefs/heads/main"

        # Mock clone_to_temp to fail on second repo (prompts/ dir doesn't exist)
        temp1 = tmp_path / "temp1"
        temp1.mkdir()
        (temp1 / "prompts").mkdir()  # Valid repo has prompts/

        temp2 = tmp_path / "temp2"
        temp2.mkdir()
        # Note: no prompts/ directory in temp2 - this will cause validation to fail

        temp3 = tmp_path / "temp3"
        temp3.mkdir()
        (temp3 / "prompts").mkdir()

        repo_mock1 = MagicMock()
        repo_mock2 = MagicMock()
        repo_mock3 = MagicMock()

        mock_clone.side_effect = [
            (temp1, repo_mock1),  # First repo validates OK
            (temp2, repo_mock2),  # Second repo - missing prompts/ dir
            (temp3, repo_mock3),  # Third repo (should never be called)
        ]

        # Call sync and expect validation error on second repo
        with pytest.raises(ValueError) as exc_info:
            service.sync_multiple_repos(repos, storage_path)

        # Verify error message mentions the invalid repo and missing prompts/ directory
        error_msg = str(exc_info.value)
        assert "Repository 2/3 validation failed" in error_msg
        assert "invalid/repo2" in error_msg
        assert "does not contain a prompts/ directory" in error_msg

        # Verify clone was called max 2 times (validation stops on second repo)
        assert mock_clone.call_count == 2

        # Verify storage was not created (fail-fast before sync)
        assert not storage_path.exists()
