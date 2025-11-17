"""Tests for path expansion utility functions.

This module tests environment variable expansion in path strings,
supporting $HOME, $USER, $PWD in both $VAR and ${VAR} syntaxes.
"""

from pathlib import Path

import pytest

from prompt_unifier.utils.path_helpers import expand_env_vars


class TestExpandEnvVars:
    """Test suite for expand_env_vars function."""

    def test_expands_home_variable_with_dollar_syntax(self) -> None:
        """Test that $HOME expands to the user's home directory."""
        path = "$HOME/.continue"
        expected = str(Path.home() / ".continue")
        result = expand_env_vars(path)
        assert result == expected

    def test_expands_home_variable_with_brace_syntax(self) -> None:
        """Test that ${HOME} expands to the user's home directory."""
        path = "${HOME}/.continue"
        expected = str(Path.home() / ".continue")
        result = expand_env_vars(path)
        assert result == expected

    def test_expands_pwd_variable(self) -> None:
        """Test that $PWD expands to the current working directory."""
        path = "$PWD/.continue"
        expected = str(Path.cwd() / ".continue")
        result = expand_env_vars(path)
        assert result == expected

    def test_expands_user_variable(self, monkeypatch) -> None:
        """Test that $USER expands to the current user name."""
        monkeypatch.setenv("USER", "testuser")
        path = "/home/$USER/projects"
        expected = "/home/testuser/projects"
        result = expand_env_vars(path)
        assert result == expected

    def test_expands_multiple_variables_in_same_path(self, monkeypatch) -> None:
        """Test that multiple environment variables expand in a single path."""
        monkeypatch.setenv("USER", "testuser")
        path = "$HOME/projects/$USER/data"
        expected = f"{Path.home()}/projects/testuser/data"
        result = expand_env_vars(path)
        assert result == expected

    def test_returns_unchanged_path_without_variables(self) -> None:
        """Test that paths without environment variables are returned unchanged."""
        path = "/usr/local/bin/continue"
        result = expand_env_vars(path)
        assert result == path

    def test_raises_error_for_missing_environment_variable(self) -> None:
        """Test that missing environment variables raise ValueError with clear message."""
        path = "$NONEXISTENT_VAR/path"
        with pytest.raises(ValueError, match="Environment variable NONEXISTENT_VAR not found"):
            expand_env_vars(path)

    def test_handles_mixed_brace_and_dollar_syntax(self, monkeypatch) -> None:
        """Test that both $VAR and ${VAR} syntax work in the same path."""
        monkeypatch.setenv("USER", "testuser")
        path = "$HOME/projects/${USER}/data"
        expected = f"{Path.home()}/projects/testuser/data"
        result = expand_env_vars(path)
        assert result == expected
