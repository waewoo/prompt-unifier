"""Configuration file management for Git repository sync.

This module provides the ConfigManager class for creating, loading, saving,
and updating Git configuration files (.prompt-manager/config.yaml).
"""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from prompt_manager.models.git_config import GitConfig


class ConfigManager:
    """Manages Git configuration file operations.

    This class handles all interactions with the .prompt-manager/config.yaml
    file, including loading, saving, and updating sync metadata. It follows
    YAML handling patterns from core/yaml_parser.py using safe_load/safe_dump.

    Examples:
        >>> from pathlib import Path
        >>> manager = ConfigManager()
        >>> config = GitConfig(repo_url=None, last_sync_timestamp=None, last_sync_commit=None)
        >>> manager.save_config(Path("config.yaml"), config)
        >>> loaded = manager.load_config(Path("config.yaml"))
        >>> loaded.repo_url is None
        True
    """

    def load_config(self, config_path: Path) -> GitConfig | None:
        """Load Git configuration from YAML file.

        This method reads the config.yaml file, parses it with safe_load,
        validates the structure, and returns a GitConfig model instance.

        Args:
            config_path: Path to the config.yaml file to load

        Returns:
            GitConfig instance if file is valid, None if file not found or invalid

        Examples:
            >>> manager = ConfigManager()
            >>> config = manager.load_config(Path(".prompt-manager/config.yaml"))
            >>> if config:
            ...     print(config.repo_url)
        """
        # Check if file exists
        if not config_path.exists():
            return None

        try:
            # Read and parse YAML file using safe_load (security best practice)
            with open(config_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            # Validate that data is a dictionary
            if not isinstance(data, dict):
                return None

            # Create GitConfig from parsed data
            # Pydantic will validate field types
            config = GitConfig(**data)
            return config

        except yaml.YAMLError:
            # Corrupted YAML file - return None
            return None
        except (ValueError, TypeError):
            # Invalid data structure or validation error
            return None
        except Exception:
            # Catch-all for other errors (e.g., encoding issues)
            return None

    def save_config(self, config_path: Path, config: GitConfig) -> None:
        """Save Git configuration to YAML file.

        This method serializes a GitConfig model to YAML format and writes
        it to the specified file path using safe_dump with proper formatting.

        Args:
            config_path: Path where config.yaml should be saved
            config: GitConfig instance to save

        Examples:
            >>> manager = ConfigManager()
            >>> config = GitConfig(
            ...     repo_url="https://github.com/example/prompts.git",
            ...     last_sync_timestamp="2024-11-11T14:30:00Z",
            ...     last_sync_commit="abc1234"
            ... )
            >>> manager.save_config(Path("config.yaml"), config)
        """
        # Ensure parent directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert GitConfig to dictionary
        config_data: dict[str, Any] = config.model_dump()

        # Write to file using safe_dump with proper formatting
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(
                config_data,
                f,
                default_flow_style=False,  # Use block style (more readable)
                sort_keys=False,  # Preserve field order
            )

    def update_sync_info(self, config_path: Path, repo_url: str, commit_hash: str) -> None:
        """Update sync information in existing config or create new config.

        This method updates the repository URL, commit hash, and timestamp
        in the configuration file. If the file doesn't exist, it creates
        a new configuration.

        Args:
            config_path: Path to the config.yaml file
            repo_url: Git repository URL to store
            commit_hash: Commit hash (SHA) from the sync

        Examples:
            >>> manager = ConfigManager()
            >>> manager.update_sync_info(
            ...     Path(".prompt-manager/config.yaml"),
            ...     "https://github.com/example/prompts.git",
            ...     "abc1234"
            ... )
        """
        # Load existing config or create new one
        config = self.load_config(config_path)

        if config is None:
            # Create new config if loading failed or file doesn't exist
            config = GitConfig(
                repo_url=repo_url,
                last_sync_timestamp=None,
                last_sync_commit=None,
            )

        # Update with new sync information
        config.repo_url = repo_url
        config.last_sync_commit = commit_hash

        # Generate current timestamp in ISO 8601 format
        config.last_sync_timestamp = datetime.now(UTC).isoformat()

        # Save updated config
        self.save_config(config_path, config)
