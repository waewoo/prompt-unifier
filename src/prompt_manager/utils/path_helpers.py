"""Path helper utilities for environment variable expansion.

This module provides utilities for expanding environment variables in path strings,
supporting standard variables like $HOME, $USER, $PWD in both $VAR and ${VAR} syntaxes.
"""

import os
import re
from pathlib import Path


def expand_env_vars(path: str) -> str:
    """Expand environment variables in a path string.

    Supports expansion of $HOME, $USER, $PWD environment variables
    in both ${VAR} and $VAR syntaxes. Other environment variables
    will also be expanded if present.

    Args:
        path: Path string potentially containing environment variables

    Returns:
        Path string with all environment variables expanded

    Raises:
        ValueError: If a referenced environment variable is not found

    Examples:
        >>> expand_env_vars("$HOME/.continue")
        '/home/user/.continue'

        >>> expand_env_vars("${PWD}/data")
        '/current/working/directory/data'

        >>> expand_env_vars("$HOME/projects/$USER/config")
        '/home/user/projects/username/config'

        >>> expand_env_vars("/usr/local/bin")
        '/usr/local/bin'

        >>> expand_env_vars("$NONEXISTENT/path")
        ValueError: Environment variable NONEXISTENT not found
    """
    # If no environment variable markers present, return unchanged
    if "$" not in path:
        return path

    # Pattern to match both ${VAR} and $VAR syntaxes
    # Match ${VAR} first (more specific), then $VAR (word boundary)
    pattern = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")

    def replace_var(match: re.Match[str]) -> str:
        """Replace a single environment variable match."""
        # Get variable name from either capture group
        var_name = match.group(1) if match.group(1) else match.group(2)

        # Special handling for common path variables
        if var_name == "HOME":
            return str(Path.home())
        elif var_name == "PWD":
            return str(Path.cwd())
        elif var_name in os.environ:
            return os.environ[var_name]
        else:
            raise ValueError(f"Environment variable {var_name} not found")

    # Substitute all environment variables
    return pattern.sub(replace_var, path)
