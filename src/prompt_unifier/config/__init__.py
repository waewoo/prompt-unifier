"""Configuration management module for Git repository sync.

This module provides configuration file management for the .prompt-unifier/
directory, including loading, saving, and updating sync metadata.
"""

from prompt_unifier.config.manager import ConfigManager
from prompt_unifier.models.git_config import GitConfig

__all__ = ["ConfigManager", "GitConfig"]
