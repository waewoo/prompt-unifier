"""Repository metadata tracking utility.

This module provides the RepoMetadata class for managing .repo-metadata.json
files that track which files came from which repositories during multi-repo sync.
"""

import json
from pathlib import Path
from typing import Any


class RepoMetadata:
    """Utility class for managing repository metadata during multi-repo sync.

    This class handles creation, loading, and saving of .repo-metadata.json files
    that track file-to-repository mappings and sync information.

    The metadata structure is:
    {
        "files": {
            "path/to/file.md": {
                "source_url": "https://github.com/example/prompts.git",
                "branch": "main",
                "commit": "abc123",
                "timestamp": "2024-11-18T10:00:00Z"
            }
        },
        "repositories": [
            {
                "url": "https://github.com/example/prompts.git",
                "branch": "main",
                "commit": "abc123",
                "timestamp": "2024-11-18T10:00:00Z"
            }
        ]
    }

    Examples:
        >>> metadata = RepoMetadata()
        >>> metadata.add_repository(
        ...     url="https://github.com/example/prompts.git",
        ...     branch="main",
        ...     commit="abc123",
        ...     timestamp="2024-11-18T10:00:00Z"
        ... )
        >>> metadata.add_file(
        ...     file_path="prompts/example.md",
        ...     source_url="https://github.com/example/prompts.git",
        ...     branch="main",
        ...     commit="abc123",
        ...     timestamp="2024-11-18T10:00:00Z"
        ... )
        >>> metadata.save_to_file(Path("/tmp/storage"))
    """

    def __init__(self) -> None:
        """Initialize a new RepoMetadata instance with empty structure."""
        self.data: dict[str, Any] = {
            "files": {},
            "repositories": [],
        }

    def add_repository(
        self,
        url: str,
        branch: str,
        commit: str,
        timestamp: str,
    ) -> None:
        """Add repository sync metadata.

        Args:
            url: Git repository URL
            branch: Branch name that was synced
            commit: Commit hash that was synced
            timestamp: ISO 8601 timestamp of sync
        """
        repo_info = {
            "url": url,
            "branch": branch,
            "commit": commit,
            "timestamp": timestamp,
        }
        self.data["repositories"].append(repo_info)

    def add_file(
        self,
        file_path: str,
        source_url: str,
        branch: str,
        commit: str,
        timestamp: str,
    ) -> None:
        """Add file-to-repository mapping.

        Args:
            file_path: Relative path to file in storage
            source_url: Git repository URL where file came from
            branch: Branch name file was synced from
            commit: Commit hash file was synced from
            timestamp: ISO 8601 timestamp of sync
        """
        file_info = {
            "source_url": source_url,
            "branch": branch,
            "commit": commit,
            "timestamp": timestamp,
        }
        self.data["files"][file_path] = file_info

    def save_to_file(self, storage_path: Path) -> None:
        """Save metadata to .repo-metadata.json in storage directory.

        Args:
            storage_path: Path to storage directory where .repo-metadata.json will be saved
        """
        metadata_file = storage_path / ".repo-metadata.json"
        storage_path.mkdir(parents=True, exist_ok=True)

        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, sort_keys=False)

    @classmethod
    def load_from_file(cls, storage_path: Path) -> "RepoMetadata":
        """Load metadata from .repo-metadata.json in storage directory.

        Args:
            storage_path: Path to storage directory containing .repo-metadata.json

        Returns:
            RepoMetadata instance populated with data from file

        Raises:
            FileNotFoundError: If .repo-metadata.json doesn't exist
        """
        metadata_file = storage_path / ".repo-metadata.json"

        if not metadata_file.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_file}")

        with open(metadata_file, encoding="utf-8") as f:
            data = json.load(f)

        instance = cls()
        instance.data = data
        return instance

    def get_file_source(self, file_path: str) -> dict[str, str] | None:
        """Get source repository information for a specific file.

        Args:
            file_path: Relative path to file in storage

        Returns:
            Dictionary with source_url, branch, commit, timestamp if file exists,
            None if file not tracked
        """
        result = self.data["files"].get(file_path)
        return result if result is None else dict(result)

    def get_repositories(self) -> list[dict[str, str]]:
        """Get list of all synced repositories.

        Returns:
            List of repository metadata dictionaries
        """
        return [dict(repo) for repo in self.data["repositories"]]

    def get_files(self) -> dict[str, dict[str, str]]:
        """Get all file-to-repository mappings.

        Returns:
            Dictionary mapping file paths to source repository info
        """
        return {path: dict(info) for path, info in self.data["files"].items()}
