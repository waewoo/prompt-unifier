"""Path helper utilities for environment variable expansion and path normalization.

This module provides utilities for expanding environment variables in path strings,
supporting standard variables like $HOME, $USER, $PWD in both $VAR and ${VAR} syntaxes,
as well as cross-platform path normalization for comparisons.
"""

import os
import re
from pathlib import Path, PurePath


def expand_env_vars(path: str) -> str:
    """Expand environment variables in a path string.

    Supports expansion of $VAR, ${VAR}, Windows %VAR% syntax, and leading '~'.
    Returns a normalized path string appropriate for the current OS.
    """
    # Handle leading tilde
    if path.startswith("~"):
        # Join using Path to handle separators correctly
        path = str(Path.home() / path[1:])
        return os.path.normpath(path)

    # If no variable markers, return unchanged (but normalize anyway)
    if "$" not in path and "%" not in path:
        return os.path.normpath(path)

    # Patterns for $VAR/${VAR} and %VAR%
    dollar_pattern = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")
    # Pattern for %VAR% (Windows)
    percent_pattern = re.compile(r"%([A-Za-z_][A-Za-z0-9_]*)%")

    def replace_var(match: re.Match[str]) -> str:
        var_name = match.group(1) if match.group(1) else match.group(2)
        if var_name == "HOME":
            return str(Path.home())
        elif var_name == "PWD":
            return str(Path.cwd())
        elif var_name in os.environ:
            return os.environ[var_name]
        else:
            raise ValueError(f"Environment variable {var_name} not found")

    def replace_percent(match: re.Match[str]) -> str:
        var_name = match.group(1)
        if var_name in os.environ:
            return os.environ[var_name]
        else:
            raise ValueError(f"Environment variable {var_name} not found")

    # Apply replacements
    path = dollar_pattern.sub(replace_var, path)
    path = percent_pattern.sub(replace_percent, path)
    # Normalize path separators for the OS
    return os.path.normpath(path)


def normalize_path_for_comparison(path: str | Path | PurePath) -> str:
    """Normalize a path to POSIX format for cross-platform comparisons.

    This function converts all path separators to forward slashes,
    making it suitable for string comparisons in tests that need to
    work on both Windows and Linux.

    Args:
        path: A path string, Path object, or PurePath object to normalize.

    Returns:
        A POSIX-style path string with forward slashes.

    Examples:
        >>> normalize_path_for_comparison("prompts\\\\test.md")
        'prompts/test.md'
        >>> normalize_path_for_comparison(Path("rules/example.md"))
        'rules/example.md'
    """
    if isinstance(path, str):
        if not path:
            return "."
        path = Path(path)

    # PurePath and Path both have as_posix() method
    return path.as_posix()
