"""Constants used across the prompt-unifier application.

This module centralizes string literals and other constants to avoid
duplication and improve maintainability.
"""

# Configuration paths
CONFIG_DIR = ".prompt-unifier"
CONFIG_FILE = "config.yaml"

# Glob patterns for file discovery
MD_GLOB_PATTERN = "**/*.md"
BAK_GLOB_PATTERN = "**/*.bak"

# Continue tool handler paths
CONTINUE_DIR = ".continue"

# Kilo Code tool handler paths
KILO_CODE_DIR = ".kilocode"

# Error messages
ERROR_CONFIG_NOT_FOUND = "Error: Configuration not found. Run 'prompt-unifier init' first."

# Example URLs for documentation
EXAMPLE_REPO_URL = "https://github.com/example/prompts.git"
EXAMPLE_TIMESTAMP = "2024-11-18T14:30:00Z"
