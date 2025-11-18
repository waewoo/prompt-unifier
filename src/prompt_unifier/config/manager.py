from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError
from rich.console import Console

from prompt_unifier.models.git_config import GitConfig

console = Console()


class ConfigManager:
    """Manages Git configuration file operations.

    This class handles all interactions with the .prompt-unifier/config.yaml
    file, including loading, saving, and updating sync metadata for both
    single and multi-repository configurations. It follows YAML handling
    patterns from core/yaml_parser.py using safe_load/safe_dump.

    Examples:
        >>> from pathlib import Path
        >>> manager = ConfigManager()
        >>> config = GitConfig(repos=None, last_sync_timestamp=None, repo_metadata=None)
        >>> manager.save_config(Path("config.yaml"), config)
        >>> loaded = manager.load_config(Path("config.yaml"))
        >>> loaded.repos is None
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
            >>> config = manager.load_config(Path(".prompt-unifier/config.yaml"))
            >>> if config:
            ...     print(config.repos)
        """
        # Check if file exists
        if not config_path.exists():
            return None

        try:
            with open(config_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data is None:  # Handle empty YAML file
                    return GitConfig()  # Return default config if file is empty
                return GitConfig(**data)
        except FileNotFoundError:
            return None
        except yaml.YAMLError as e:
            console.print(f"[red]Error: Invalid YAML format in {config_path}: {e}[/red]")
            return None
        except ValidationError as e:
            console.print(
                f"[red]Error: Configuration validation failed for {config_path}: {e}[/red]"
            )
            return None
        except Exception as e:
            console.print(
                f"[red]An unexpected error occurred while loading config from "
                f"{config_path}: {e}[/red]"
            )
            return None

    def save_config(self, config_path: Path, config: GitConfig) -> None:
        """Save Git configuration to YAML file.

        This method serializes a GitConfig model to YAML format and writes
        it to the specified file path using safe_dump with proper formatting.

        Args:
            config_path: Path where config.yaml should be saved
            config: GitConfig instance to save

        Examples:
            >>> from prompt_unifier.models.git_config import RepositoryConfig
            >>> manager = ConfigManager()
            >>> config = GitConfig(
            ...     repos=[
            ...         RepositoryConfig(url="https://github.com/example/prompts.git")
            ...     ],
            ...     last_sync_timestamp="2024-11-18T14:30:00Z"
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

    def update_multi_repo_sync_info(
        self,
        config_path: Path,
        repo_metadata_list: list[dict[str, str]],
    ) -> None:
        """Update sync information for multi-repository configuration.

        This method updates the repo_metadata list and last_sync_timestamp
        in the configuration file after a multi-repo sync completes.

        Args:
            config_path: Path to the config.yaml file
            repo_metadata_list: List of repository metadata dicts containing
                url, branch, commit, and timestamp for each synced repository

        Examples:
            >>> manager = ConfigManager()
            >>> metadata = [
            ...     {
            ...         "url": "https://github.com/repo1/prompts.git",
            ...         "branch": "main",
            ...         "commit": "abc123",
            ...         "timestamp": "2024-11-18T10:00:00Z",
            ...     },
            ...     {
            ...         "url": "https://github.com/repo2/prompts.git",
            ...         "branch": "dev",
            ...         "commit": "def456",
            ...         "timestamp": "2024-11-18T10:01:00Z",
            ...     },
            ... ]
            >>> manager.update_multi_repo_sync_info(
            ...     Path(".prompt-unifier/config.yaml"),
            ...     metadata
            ... )
        """
        # Load existing config or create new one
        config = self.load_config(config_path)

        if config is None:
            # Create new config if loading failed or file doesn't exist
            config = GitConfig(
                repos=None,
                last_sync_timestamp=None,
                repo_metadata=None,
            )

        # Update with new sync information
        config.repo_metadata = repo_metadata_list

        # Generate current timestamp in ISO 8601 format
        config.last_sync_timestamp = datetime.now(UTC).isoformat()

        # Save updated config
        self.save_config(config_path, config)
