from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError
from rich.console import Console

from prompt_manager.models.git_config import GitConfig

console = Console()


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
