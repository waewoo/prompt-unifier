"""Configuration management module for Git repository sync.

This module provides configuration file management for the .prompt-manager/
directory, including loading, saving, and updating sync metadata.
"""

from prompt_manager.config.manager import ConfigManager
from prompt_manager.models.git_config import GitConfig

__all__ = ["ConfigManager", "GitConfig"]
