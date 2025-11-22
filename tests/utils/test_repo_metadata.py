"""Tests for RepoMetadata utility class."""

from pathlib import Path

import pytest

from prompt_unifier.utils.repo_metadata import RepoMetadata


class TestRepoMetadata:
    """Tests for RepoMetadata class."""

    def test_load_from_file_not_found(self, tmp_path: Path) -> None:
        """Test that loading from non-existent file raises FileNotFoundError."""
        storage_path = tmp_path / "nonexistent"
        storage_path.mkdir()

        with pytest.raises(FileNotFoundError, match="Metadata file not found"):
            RepoMetadata.load_from_file(storage_path)

    def test_load_from_file_success(self, tmp_path: Path) -> None:
        """Test that loading from valid file succeeds."""
        storage_path = tmp_path / "storage"
        storage_path.mkdir()

        metadata_file = storage_path / ".repo-metadata.json"
        metadata_file.write_text('{"file_sources": {}}')

        metadata = RepoMetadata.load_from_file(storage_path)
        assert metadata is not None

    def test_save_to_file_creates_file(self, tmp_path: Path) -> None:
        """Test that save_to_file creates the metadata file."""
        metadata = RepoMetadata()
        storage_path = tmp_path / "storage"
        storage_path.mkdir()

        metadata.save_to_file(storage_path)

        metadata_file = storage_path / ".repo-metadata.json"
        assert metadata_file.exists()

    def test_add_file(self, tmp_path: Path) -> None:
        """Test adding file source information."""
        metadata = RepoMetadata()

        metadata.add_file(
            file_path="prompts/test.md",
            source_url="https://github.com/test/repo.git",
            branch="main",
            commit="abc123",
            timestamp="2024-11-18T10:00:00Z",
        )

        source = metadata.get_file_source("prompts/test.md")
        assert source is not None
        assert source["source_url"] == "https://github.com/test/repo.git"
        assert source["branch"] == "main"
