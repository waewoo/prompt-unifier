"""Constants used across the prompt-unifier application.

This module centralizes string literals and other constants to avoid
duplication and improve maintainability.
"""

# Configuration paths
CONFIG_DIR = ".prompt-unifier"
CONFIG_FILE = "config.yaml"

# Glob patterns for file discovery
MD_GLOB_PATTERN = "**/*.md"

# Continue tool handler paths
CONTINUE_DIR = ".continue"

# Kilo Code tool handler paths
KILO_CODE_DIR = ".kilocode"
KILO_CODE_MEMORY_BANK_DIR = "memory-bank"  # New constant
KILO_CODE_SKILLS_DIR = "skills"  # Base name; mode-specific = f"skills-{mode}"

# Error messages
ERROR_CONFIG_NOT_FOUND = "Error: Configuration not found. Run 'prompt-unifier init' first."

# Example URLs for documentation
EXAMPLE_REPO_URL = "https://github.com/example/prompts.git"
EXAMPLE_TIMESTAMP = "2024-11-18T14:30:00Z"
