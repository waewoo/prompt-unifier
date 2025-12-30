"""Tests for the 'test' CLI command.

This module tests functional testing command and its helpers.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from prompt_unifier.ai.executor import AIExecutionError
from prompt_unifier.cli.commands import (
    _discover_functional_test_files,
    _get_global_ai_provider,
    _resolve_prompt_path_and_title,
    _run_single_functional_test,
    _validate_ai_connection,
)
from prompt_unifier.cli.main import app

runner = CliRunner()


class TestTestCommandCLI:
    """Tests for 'test' command and its internal helpers."""

    def test_discover_functional_test_files_single_file(self, tmp_path: Path):
        """Test discovery with a single .test.yaml file."""
        test_file = tmp_path / "my.md.test.yaml"
        test_file.touch()

        discovered = _discover_functional_test_files(test_file)
        assert discovered == [test_file]

    def test_discover_functional_test_files_prompt_file(self, tmp_path: Path):
        """Test discovery with a .md file (should find corresponding .test.yaml)."""
        prompt_file = tmp_path / "prompt.md"
        prompt_file.touch()
        test_file = tmp_path / "prompt.md.test.yaml"
        test_file.touch()

        discovered = _discover_functional_test_files(prompt_file)
        assert discovered == [test_file]

    def test_discover_functional_test_files_recursive(self, tmp_path: Path):
        """Test recursive discovery in a directory."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        test1 = tmp_path / "test1.md.test.yaml"
        test2 = subdir / "test2.md.test.yaml"
        test1.touch()
        test2.touch()

        discovered = _discover_functional_test_files(tmp_path)
        assert len(discovered) == 2
        assert test1 in discovered
        assert test2 in discovered

    def test_get_global_ai_provider(self, tmp_path: Path):
        """Test loading global AI provider from config."""
        config_dir = tmp_path / ".prompt-unifier"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        config_file.write_text("ai_provider: my-provider\n")

        with patch("pathlib.Path.cwd", return_value=tmp_path):
            provider = _get_global_ai_provider()
            assert provider == "my-provider"

    def test_resolve_prompt_path_and_title(self, tmp_path: Path):
        """Test resolving prompt path and extracting title."""
        prompt_file = tmp_path / "hello.md"
        prompt_file.write_text(
            "---\ntitle: Hello World\ndescription: d\nversion: 1.0.0\nauthor: a\n---\nContent"
        )
        test_file = tmp_path / "hello.md.test.yaml"

        path, title = _resolve_prompt_path_and_title(test_file)
        assert path == prompt_file
        assert title == "Hello World"

    @patch("prompt_unifier.cli.commands._run_single_functional_test")
    @patch("prompt_unifier.cli.commands._discover_functional_test_files")
    def test_test_command_success(self, mock_discover, mock_run, tmp_path: Path):
        """Test successful execution of 'test' command."""
        mock_discover.return_value = [Path("test1.md.test.yaml")]
        mock_run.return_value = {
            "success": True,
            "name": "Test1",
            "total": 1,
            "passed": 1,
            "failed": 0,
            "pass_rate": 100.0,
            "path": "path/to/test1",
        }

        result = runner.invoke(app, ["test"])
        assert result.exit_code == 0
        assert "discovered test file" in result.stdout.lower()

    @patch("prompt_unifier.cli.commands._run_single_functional_test")
    @patch("prompt_unifier.cli.commands._discover_functional_test_files")
    def test_test_command_failure(self, mock_discover, mock_run, tmp_path: Path):
        """Test 'test' command exits with 1 on failed tests."""
        mock_discover.return_value = [Path("fail.md.test.yaml")]
        mock_run.return_value = {
            "success": False,
            "name": "Fail",
            "total": 1,
            "passed": 0,
            "failed": 1,
            "pass_rate": 0.0,
            "path": "path/to/fail",
        }

        result = runner.invoke(app, ["test"])
        assert result.exit_code == 1

    @patch("rich.console.Console.print")
    def test_validate_ai_connection_auth_error(self, mock_print):
        """Test _validate_ai_connection with API key error."""
        executor = MagicMock()
        executor.validate_connection.side_effect = AIExecutionError("api_key error")

        with pytest.raises(AIExecutionError):
            _validate_ai_connection(executor, "provider")
        assert any("API key" in str(args) for args in mock_print.call_args_list)

    @patch("rich.console.Console.print")
    def test_validate_ai_connection_timeout_error(self, mock_print):
        """Test _validate_ai_connection with timeout error."""
        executor = MagicMock()
        executor.validate_connection.side_effect = AIExecutionError("timeout")

        with pytest.raises(AIExecutionError):
            _validate_ai_connection(executor, "provider")
        assert any("internet connection" in str(args) for args in mock_print.call_args_list)

    @patch("prompt_unifier.core.functional_test_parser.FunctionalTestParser.parse")
    def test_run_single_functional_test_missing_provider(self, mock_parse, tmp_path: Path):
        """Test _run_single_functional_test fails when no provider available."""
        test_file = tmp_path / "test.md.test.yaml"
        test_file.touch()

        mock_spec = MagicMock()
        mock_spec.provider = None
        mock_parse.return_value = mock_spec

        result = _run_single_functional_test(test_file, global_provider=None)
        assert result["success"] is False
        assert "name" in result
