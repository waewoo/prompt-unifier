"""Git configuration model for repository sync metadata.

This module provides the GitConfig Pydantic model for storing and validating
repository synchronization configuration including repository URL, last sync
timestamp, and last synced commit hash.
"""

from pydantic import BaseModel, Field


class HandlerConfig(BaseModel):
    """Configuration model for individual tool handler settings.

    This model stores per-handler configuration, currently supporting
    custom base paths for deployment locations.

    Attributes:
        base_path: Custom base path for handler deployment (None to use default)

    Examples:
        >>> # Handler with custom base path
        >>> config = HandlerConfig(base_path="$PWD/.continue")
        >>> config.base_path
        '$PWD/.continue'

        >>> # Handler with default base path (None)
        >>> config = HandlerConfig()
        >>> config.base_path is None
        True
    """

    base_path: str | None = Field(
        default=None,
        description=(
            "Custom base path for handler deployment. "
            "Supports environment variables: $HOME, $USER, $PWD. "
            "Example: $PWD/.continue or ${HOME}/.cursor"
        ),
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"base_path": "$PWD/.continue"},
                {"base_path": "${HOME}/.cursor"},
                {"base_path": "/custom/path/.windsurf"},
                {"base_path": None},
            ]
        }
    }


class GitConfig(BaseModel):
    """Configuration model for Git repository synchronization and deployment.

    This model stores metadata about the Git repository being synced,
    including the repository URL, last sync timestamp, and commit hash.
    All fields are optional to support initial configuration creation.

    Attributes:
        repo_url: URL of the Git repository to sync from (None before first sync)
        last_sync_timestamp: ISO 8601 timestamp of last sync (None before first sync)
        last_sync_commit: Commit hash (SHA) from last sync (None before first sync)
        storage_path: Path to centralized storage directory (defaults to ~/.prompt-unifier/storage)
        deploy_tags: List of tags to filter prompts and rules for deployment (None to deploy all)
        target_handlers: List of target handlers for deployment (None to use all registered)
        handlers: Per-handler configuration including base paths

    Examples:
        >>> # Configuration after init (all None)
        >>> config = GitConfig(
        ...     repo_url=None,
        ...     last_sync_timestamp=None,
        ...     last_sync_commit=None
        ... )
        >>> config.repo_url is None
        True

        >>> # Configuration after sync with deployment settings
        >>> config = GitConfig(
        ...     repo_url="https://github.com/example/prompts.git",
        ...     last_sync_timestamp="2024-11-11T14:30:00Z",
        ...     last_sync_commit="abc1234",
        ...     deploy_tags=["python", "review"],
        ...     target_handlers=["continue", "cursor"]
        ... )
        >>> config.repo_url
        'https://github.com/example/prompts.git'

        >>> # Configuration with custom handler base paths
        >>> config = GitConfig(
        ...     repo_url="https://github.com/example/prompts.git",
        ...     handlers={
        ...         "continue": HandlerConfig(base_path="$PWD/.continue"),
        ...         "cursor": HandlerConfig(base_path="$HOME/.cursor")
        ...     }
        ... )
        >>> config.handlers["continue"].base_path
        '$PWD/.continue'
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
            "(defaults to ~/.prompt-unifier/storage)"
        ),
    )

    deploy_tags: list[str] | None = Field(
        default=None,
        description="List of tags to filter prompts and rules for deployment (None to deploy all)",
    )

    target_handlers: list[str] | None = Field(
        default=None,
        description="List of target handlers for deployment (None to use all registered)",
    )

    handlers: dict[str, HandlerConfig] | None = Field(
        default=None,
        description="Per-handler configuration including base paths",
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
                    "storage_path": "/home/user/.prompt-unifier/storage",
                    "deploy_tags": ["python", "review"],
                    "target_handlers": ["continue", "cursor"],
                },
                {
                    "repo_url": "https://github.com/example/prompts.git",
                    "last_sync_timestamp": "2024-11-15T10:30:00Z",
                    "last_sync_commit": "def5678",
                    "storage_path": "~/.prompt-unifier/storage",
                    "deploy_tags": ["python", "review"],
                    "target_handlers": ["continue"],
                    "handlers": {
                        "continue": {"base_path": "$PWD/.continue"},
                        "cursor": {"base_path": "$PWD/.cursor"},
                        "windsurf": {"base_path": "$PWD/.windsurf"},
                        "aider": {"base_path": "$PWD/.aider"},
                    },
                },
            ]
        }
    }
