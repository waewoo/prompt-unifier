"""Git configuration model for repository sync metadata.

This module provides the GitConfig Pydantic model for storing and validating
repository synchronization configuration including repository URL, last sync
timestamp, and last synced commit hash.
"""

from pydantic import BaseModel, Field


class GitConfig(BaseModel):
    """Configuration model for Git repository synchronization.

    This model stores metadata about the Git repository being synced,
    including the repository URL, last sync timestamp, and commit hash.
    All fields are optional to support initial configuration creation.

    Attributes:
        repo_url: URL of the Git repository to sync from (None before first sync)
        last_sync_timestamp: ISO 8601 timestamp of last sync (None before first sync)
        last_sync_commit: Commit hash (SHA) from last sync (None before first sync)
        storage_path: Path to centralized storage directory (defaults to ~/.prompt-manager/storage)

    Examples:
        >>> # Configuration after init (all None)
        >>> config = GitConfig(
        ...     repo_url=None,
        ...     last_sync_timestamp=None,
        ...     last_sync_commit=None
        ... )
        >>> config.repo_url is None
        True

        >>> # Configuration after sync
        >>> config = GitConfig(
        ...     repo_url="https://github.com/example/prompts.git",
        ...     last_sync_timestamp="2024-11-11T14:30:00Z",
        ...     last_sync_commit="abc1234"
        ... )
        >>> config.repo_url
        'https://github.com/example/prompts.git'
    """

    repo_url: str | None = Field(
        default=None,
        description="Git repository URL to sync prompts from",
    )

    last_sync_timestamp: str | None = Field(
        default=None,
        description="ISO 8601 timestamp of last successful sync",
    )

    last_sync_commit: str | None = Field(
        default=None,
        description="Commit hash (SHA) from last successful sync",
    )

    storage_path: str | None = Field(
        default=None,
        description=(
            "Path to centralized storage directory for prompts and rules "
            "(defaults to ~/.prompt-manager/storage)"
        ),
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "repo_url": None,
                    "last_sync_timestamp": None,
                    "last_sync_commit": None,
                    "storage_path": None,
                },
                {
                    "repo_url": "https://github.com/example/prompts.git",
                    "last_sync_timestamp": "2024-11-11T14:30:00Z",
                    "last_sync_commit": "abc1234",
                    "storage_path": "/home/user/.prompt-manager/storage",
                },
            ]
        }
    }
