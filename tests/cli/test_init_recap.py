from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from prompt_unifier.cli.main import app

runner = CliRunner()


def test_test_prompts_recap_table():
    """Test test_prompts command displays recap table when multiple files are tested."""
    # We patch the functions where they are used/imported in the commands module
    with (
        patch("prompt_unifier.cli.commands._discover_functional_test_files") as mock_discover,
        patch("prompt_unifier.cli.commands._get_global_ai_provider") as mock_provider,
        patch("prompt_unifier.cli.commands._run_single_functional_test") as mock_run,
    ):
        # Setup mocks
        mock_discover.return_value = [Path("test1.yaml"), Path("test2.yaml")]
        mock_provider.return_value = "openai"
        mock_run.side_effect = [
            {
                "name": "test1",
                "success": True,
                "passed": 2,
                "total": 2,
                "pass_rate": 100.0,
                "path": "test1.yaml",
            },
            {
                "name": "test2",
                "success": False,
                "passed": 1,
                "total": 2,
                "pass_rate": 50.0,
                "path": "test2.yaml",
            },
        ]

        result = runner.invoke(app, ["test"])

        # Should fail because one test failed
        assert result.exit_code == 1
        assert "FUNCTIONAL TEST RECAP" in result.stdout
        assert "PASSED" in result.stdout
        assert "FAILED" in result.stdout


def test_init_permission_error():
    """Test init command handles PermissionError."""
    # Patch Path.cwd to raise PermissionError
    # We need to patch where it is used. commands.py uses Path.cwd()
    with patch("prompt_unifier.cli.commands.Path.cwd") as mock_cwd:
        mock_cwd.side_effect = PermissionError("Access denied")

        result = runner.invoke(app, ["init"])

        assert result.exit_code == 1
        assert "Permission denied" in result.stderr


def test_init_general_exception():
    """Test init command handles general Exception."""
    with patch("prompt_unifier.cli.commands.Path.cwd") as mock_cwd:
        mock_cwd.side_effect = Exception("Unexpected error")

        result = runner.invoke(app, ["init"])

        assert result.exit_code == 1
        assert "Error during initialization" in result.stderr
