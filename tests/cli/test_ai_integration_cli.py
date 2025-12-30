"""Additional tests for CLI commands to increase coverage."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer
from typer.testing import CliRunner

from prompt_unifier.ai.executor import AIExecutionError
from prompt_unifier.cli.commands import (
    _run_single_functional_test,
    _setup_deployment_handlers,
    _validate_ai_connection,
    validate,
)

runner = CliRunner()


class TestCommandsExtra2:
    """Tests for CLI command error paths and helpers."""

    def test_validate_ai_connection_errors(self):
        """Test _validate_ai_connection handles different error types."""
        executor = MagicMock()

        # API Key error
        executor.validate_connection.side_effect = AIExecutionError("Invalid api_key provided")
        with pytest.raises(AIExecutionError):
            _validate_ai_connection(executor, "openai")

        # Model error
        executor.validate_connection.side_effect = AIExecutionError("Model not found")
        with pytest.raises(AIExecutionError):
            _validate_ai_connection(executor, "openai")

        # Timeout error
        executor.validate_connection.side_effect = AIExecutionError("Connection timeout")
        with pytest.raises(AIExecutionError):
            _validate_ai_connection(executor, "ollama")

    @patch("prompt_unifier.core.functional_test_parser.FunctionalTestParser")
    @patch("prompt_unifier.cli.commands._resolve_prompt_path_and_title")
    def test_run_single_functional_test_exception(
        self, mock_resolve, mock_parser_cls, tmp_path: Path
    ):
        """Test _run_single_functional_test handles exceptions during execution."""
        test_file = tmp_path / "test.yaml"
        test_file.touch()

        mock_resolve.return_value = (tmp_path / "prompt.md", "Test Prompt")

        mock_spec = MagicMock()
        mock_spec.provider = "openai"

        # Mock the parser instance and its parse method
        mock_parser_instance = mock_parser_cls.return_value
        mock_parser_instance.parse.return_value = mock_spec

        # Mock AIExecutor to raise generic exception
        with patch("prompt_unifier.ai.executor.AIExecutor") as mock_executor_cls:
            mock_executor_cls.side_effect = Exception("Unexpected error")

            result = _run_single_functional_test(test_file)

            assert result["success"] is False
            assert result["passed"] == 0
            assert result["total"] == 0

    @patch("prompt_unifier.cli.commands._validate_ai_connection")
    @patch("prompt_unifier.cli.commands._get_global_ai_provider")
    @patch("prompt_unifier.cli.commands._run_single_functional_test")
    @patch("prompt_unifier.cli.commands._discover_functional_test_files")
    def test_validate_test_mode_failure(
        self, mock_discover, mock_run, mock_get_provider, mock_validate_conn
    ):
        """Test validate command in test mode exits with 1 on failure."""
        mock_discover.return_value = [Path("test1.yaml")]
        mock_get_provider.return_value = None

        # Simulate failure result
        mock_run.return_value = {
            "success": False,
            "name": "Test",
            "total": 1,
            "passed": 0,
            "failed": 1,
            "pass_rate": 0,
            "path": "path/to/test1.yaml",
        }

        with pytest.raises(typer.Exit) as exc:
            validate(test=True)
        assert exc.value.exit_code == 1

    @patch("prompt_unifier.handlers.registry.ToolHandlerRegistry")
    @patch("prompt_unifier.cli.commands.KiloCodeToolHandler")
    def test_setup_deployment_handlers_kilo_validation_error(
        self, mock_kilo_cls, mock_registry_cls
    ):
        """Test _setup_deployment_handlers handles KiloCode validation error."""
        config = MagicMock()

        mock_kilo_instance = mock_kilo_cls.return_value
        mock_kilo_instance.validate_tool_installation.side_effect = OSError("Kilo not found")

        mock_registry = mock_registry_cls.return_value
        mock_registry.get_all_handlers.return_value = []  # Return empty if registration fails

        with patch("prompt_unifier.cli.helpers.resolve_handler_base_path"):
            # Expect Exit because "kilocode" was requested but failed validation (so not registered)
            with pytest.raises(typer.Exit) as exc:
                _setup_deployment_handlers(None, config, ["kilocode"])
            assert exc.value.exit_code == 1

        # Verify validate_tool_installation was called
        mock_kilo_instance.validate_tool_installation.assert_called_once()
