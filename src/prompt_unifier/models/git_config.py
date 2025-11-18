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


class RepositoryConfig(BaseModel):
    """Configuration model for individual repository settings in multi-repo sync.

    This model defines configuration for a single repository including URL,
    branch, authentication, and selective file syncing patterns.

    Attributes:
        url: Git repository URL (required)
        branch: Branch name to sync from (optional, defaults to repository default)
        auth_config: Authentication configuration dict (optional)
        include_patterns: Glob patterns for files to include (optional)
        exclude_patterns: Glob patterns for files to exclude (optional)

    Examples:
        >>> # Repository with URL only
        >>> repo = RepositoryConfig(url="https://github.com/example/prompts.git")
        >>> repo.url
        'https://github.com/example/prompts.git'

        >>> # Repository with all options
        >>> repo = RepositoryConfig(
        ...     url="https://github.com/example/prompts.git",
        ...     branch="develop",
        ...     auth_config={"method": "token", "token": "ghp_123"},
        ...     include_patterns=["*.md", "python/**"],
        ...     exclude_patterns=["**/temp/*"]
        ... )
        >>> repo.branch
        'develop'
    """

    url: str = Field(
        description="Git repository URL to sync from",
    )

    branch: str | None = Field(
        default=None,
        description="Branch name to checkout and sync from (None to use repository default)",
    )

    auth_config: dict[str, str] | None = Field(
        default=None,
        description=(
            "Authentication configuration for this repository. "
            "Supports methods: ssh_key, token, credential_helper"
        ),
    )

    include_patterns: list[str] | None = Field(
        default=None,
        description=(
            "Glob patterns for files to include during sync. "
            "Only files matching these patterns will be synced. "
            "Examples: ['*.md', 'python/**', 'prompts/review/*']"
        ),
    )

    exclude_patterns: list[str] | None = Field(
        default=None,
        description=(
            "Glob patterns for files to exclude during sync. "
            "Applied after include patterns. "
            "Examples: ['**/temp/*', '*.tmp', 'drafts/**']"
        ),
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "url": "https://github.com/example/prompts.git",
                },
                {
                    "url": "https://github.com/example/prompts.git",
                    "branch": "main",
                },
                {
                    "url": "https://github.com/example/prompts.git",
                    "branch": "develop",
                    "auth_config": {"method": "token", "token": "ghp_xxxxx"},
                    "include_patterns": ["*.md", "python/**"],
                    "exclude_patterns": ["**/temp/*", "*.tmp"],
                },
            ]
        }
    }


class GitConfig(BaseModel):
    """Configuration model for Git repository synchronization and deployment.

    This model stores metadata about Git repositories being synced,
    including repository configurations, last sync timestamp, and commit hashes.
    All fields are optional to support initial configuration creation.

    Attributes:
        repos: List of repository configurations for multi-repo sync (None before first sync)
        last_sync_timestamp: ISO 8601 timestamp of last sync (None before first sync)
        repo_metadata: List of per-repository sync metadata (None before first sync)
        storage_path: Path to centralized storage directory (defaults to ~/.prompt-unifier/storage)
        deploy_tags: List of tags to filter prompts and rules for deployment (None to deploy all)
        target_handlers: List of target handlers for deployment (None to use all registered)
        handlers: Per-handler configuration including base paths

    Examples:
        >>> # Configuration after init (all None)
        >>> config = GitConfig(repos=None)
        >>> config.repos is None
        True

        >>> # Configuration with multiple repositories
        >>> from prompt_unifier.models.git_config import RepositoryConfig
        >>> config = GitConfig(
        ...     repos=[
        ...         RepositoryConfig(url="https://github.com/repo1/prompts.git"),
        ...         RepositoryConfig(url="https://github.com/repo2/prompts.git", branch="dev"),
        ...     ],
        ...     last_sync_timestamp="2024-11-18T14:30:00Z",
        ... )
        >>> len(config.repos)
        2

        >>> # Configuration with custom handler base paths
        >>> config = GitConfig(
        ...     repos=[RepositoryConfig(url="https://github.com/example/prompts.git")],
        ...     handlers={
        ...         "continue": HandlerConfig(base_path="$PWD/.continue"),
        ...         "cursor": HandlerConfig(base_path="$HOME/.cursor")
        ...     }
        ... )
        >>> config.handlers["continue"].base_path
        '$PWD/.continue'
    """

    repos: list[RepositoryConfig] | None = Field(
        default=None,
        description="List of repository configurations to sync from",
    )

    last_sync_timestamp: str | None = Field(
        default=None,
        description="ISO 8601 timestamp of last successful sync",
    )

    repo_metadata: list[dict[str, str]] | None = Field(
        default=None,
        description=(
            "Per-repository sync metadata tracking URL, branch, commit, and timestamp "
            "for each synced repository"
        ),
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
                    "repos": None,
                    "last_sync_timestamp": None,
                    "repo_metadata": None,
                    "storage_path": None,
                },
                {
                    "repos": [
                        {"url": "https://github.com/repo1/prompts.git"},
                        {"url": "https://github.com/repo2/prompts.git", "branch": "develop"},
                    ],
                    "last_sync_timestamp": "2024-11-18T14:30:00Z",
                    "repo_metadata": [
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
                    ],
                    "storage_path": "/home/user/.prompt-unifier/storage",
                    "deploy_tags": ["python", "review"],
                    "target_handlers": ["continue", "cursor"],
                },
                {
                    "repos": [{"url": "https://github.com/example/prompts.git"}],
                    "last_sync_timestamp": "2024-11-15T10:30:00Z",
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
