import os
from pathlib import Path
from unittest.mock import patch

import pytest
import typer
from typer.testing import CliRunner

from prompt_unifier.cli.commands import (
    _discover_functional_test_files,
    _get_global_ai_provider,
)
from prompt_unifier.cli.commands import (
    test_prompts as run_test_prompts,
)

runner = CliRunner()


class TestTestCommandCLIExtended:
    """Extended tests for 'test' command to increase coverage."""

    def test_discover_functional_test_files_none_discovery(self, tmp_path: Path):
        """Test discovery with no targets provided (None)."""
        # Create a mock config directory and file
        config_dir = tmp_path / ".prompt-unifier"
        config_dir.mkdir()
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        # Create a test file in storage
        test_file = storage_dir / "test.md.test.yaml"
        test_file.touch()

        with patch(
            "prompt_unifier.cli.commands.resolve_validation_directory", return_value=storage_dir
        ):
            with patch("pathlib.Path.cwd", return_value=tmp_path):
                discovered = _discover_functional_test_files(None)
                assert test_file in discovered

    def test_discover_functional_test_files_none_no_files_raises(self, tmp_path: Path):
        """Test discovery with no targets and no files found raises Exit."""
        with patch(
            "prompt_unifier.cli.commands.resolve_validation_directory", return_value=tmp_path
        ):
            with patch("pathlib.Path.cwd", return_value=tmp_path):
                with pytest.raises(typer.Exit) as exc:
                    _discover_functional_test_files(None)
                assert exc.value.exit_code == 1

    def test_discover_functional_test_files_direct_test_yaml(self, tmp_path: Path):
        """Test passing a .test.yaml file directly."""
        test_file = tmp_path / "my.test.yaml"
        test_file.touch()

        discovered = _discover_functional_test_files([test_file])
        assert discovered == [test_file]

    def test_discover_functional_test_files_missing_prompt_test_yaml(self, tmp_path: Path):
        """Test passing a .md file without corresponding .test.yaml shows warning."""
        prompt_file = tmp_path / "no_test.md"
        prompt_file.touch()

        # Should raise Exit because no test files were found at all
        with pytest.raises(typer.Exit) as exc:
            _discover_functional_test_files([prompt_file])
        assert exc.value.exit_code == 1

    def test_discover_functional_test_files_empty_dir_warning(self, tmp_path: Path):
        """Test passing an empty directory shows warning."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        with pytest.raises(typer.Exit) as exc:
            _discover_functional_test_files([empty_dir])
        assert exc.value.exit_code == 1

    def test_get_global_ai_provider_env_fallback(self):
        """Test _get_global_ai_provider falls back to DEFAULT_LLM_MODEL."""
        with patch("pathlib.Path.exists", return_value=False):
            with patch.dict(os.environ, {"DEFAULT_LLM_MODEL": "env-model"}):
                provider = _get_global_ai_provider()
                assert provider == "env-model"

    def test_get_global_ai_provider_none(self):
        """Test _get_global_ai_provider returns None when no source found."""
        with patch("pathlib.Path.exists", return_value=False):
            with patch.dict(os.environ, {}, clear=True):
                # Ensure DEFAULT_LLM_MODEL is not set
                if "DEFAULT_LLM_MODEL" in os.environ:
                    del os.environ["DEFAULT_LLM_MODEL"]
                provider = _get_global_ai_provider()
                assert provider is None

    @patch("prompt_unifier.cli.commands._validate_ai_connection")
    @patch("prompt_unifier.cli.commands._get_global_ai_provider")
    @patch("prompt_unifier.cli.commands._discover_functional_test_files")
    def test_test_prompts_early_exit_on_connection_error_extended(
        self, mock_discover, mock_provider, mock_validate
    ):
        """Test that test_prompts exits early if global connection check fails."""
        mock_discover.return_value = [Path("test.yaml")]
        mock_provider.return_value = "failing-provider"
        mock_validate.side_effect = Exception("Connection failed")

        with pytest.raises(typer.Exit) as exc:
            run_test_prompts()
        assert exc.value.exit_code == 1
