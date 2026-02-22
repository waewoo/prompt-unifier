import os
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from prompt_unifier.cli.commands import _get_global_ai_provider
from prompt_unifier.cli.main import app

runner = CliRunner()


class TestTestCommandArgs:
    """Tests for the new arguments of the 'test' command."""

    @patch("prompt_unifier.cli.main.test_command")
    def test_test_command_with_multiple_targets(self, mock_test_cmd):
        """Test that multiple targets are correctly passed to the command handler."""
        result = runner.invoke(app, ["test", "path1", "path2", "path3"])

        assert result.exit_code == 0
        mock_test_cmd.assert_called_once()
        args, _ = mock_test_cmd.call_args
        assert len(args[0]) == 3
        assert Path("path1") in args[0]
        assert Path("path2") in args[0]
        assert Path("path3") in args[0]

    @patch("prompt_unifier.cli.main.test_command")
    def test_test_command_with_provider_option(self, mock_test_cmd):
        """Test that the --provider option is correctly passed."""
        result = runner.invoke(app, ["test", "--provider", "my-custom-model"])

        assert result.exit_code == 0
        mock_test_cmd.assert_called_once()
        assert mock_test_cmd.call_args[1]["provider"] == "my-custom-model"

    @patch("prompt_unifier.cli.commands._validate_ai_connection")
    @patch("prompt_unifier.cli.commands._get_global_ai_provider")
    @patch("prompt_unifier.cli.commands._discover_functional_test_files")
    @patch("prompt_unifier.cli.commands._run_single_functional_test")
    def test_test_prompts_provider_priority(
        self, mock_run, mock_discover, mock_get_provider, mock_validate
    ):
        """Test that explicit provider argument takes precedence."""
        from prompt_unifier.cli.commands import test_prompts

        mock_discover.return_value = [Path("test.yaml")]
        mock_get_provider.return_value = "config-provider"
        mock_run.return_value = {
            "success": True,
            "name": "t",
            "total": 1,
            "passed": 1,
            "failed": 0,
            "pass_rate": 100,
            "path": "p",
        }

        # Call with explicit provider
        test_prompts(targets=[Path("some/dir")], provider="cli-provider")

        # Check that it didn't use the config provider
        mock_run.assert_called_once()
        assert mock_run.call_args[0][1] == "cli-provider"

    def test_get_global_ai_provider_logic(self, tmp_path):
        """Test the logic of _get_global_ai_provider (Config > Env)."""
        config_dir = tmp_path / ".prompt-unifier"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"

        # Case 1: Only Env
        with patch("pathlib.Path.cwd", return_value=tmp_path):
            with patch.dict(os.environ, {"DEFAULT_LLM_MODEL": "env-model"}):
                assert _get_global_ai_provider() == "env-model"

        # Case 2: Config exists but no provider (should fallback to Env)
        config_file.write_text("storage_path: /tmp\n")
        with patch("pathlib.Path.cwd", return_value=tmp_path):
            with patch.dict(os.environ, {"DEFAULT_LLM_MODEL": "env-model"}):
                assert _get_global_ai_provider() == "env-model"

        # Case 3: Config exists with provider (should take Config)
        config_file.write_text("ai_provider: config-model\n")
        with patch("pathlib.Path.cwd", return_value=tmp_path):
            with patch.dict(os.environ, {"DEFAULT_LLM_MODEL": "env-model"}):
                assert _get_global_ai_provider() == "config-model"
