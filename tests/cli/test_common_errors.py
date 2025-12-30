"""Extra tests for CLI commands to increase coverage.

This module tests error paths and edge cases in sync, status, and deploy.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer
from typer.testing import CliRunner

from prompt_unifier.cli.commands import (
    _get_global_ai_provider,
    _prepare_content_for_deployment,
    _setup_deployment_handlers,
    _validate_with_json_output,
)
from prompt_unifier.cli.main import app
from prompt_unifier.constants import CONFIG_DIR, CONFIG_FILE

runner = CliRunner()


class TestCommandsExtra:
    """Tests for CLI command error paths."""

    def test_sync_corrupted_config(self, tmp_path: Path):
        """Test sync with corrupted config file."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            config_dir = Path.cwd() / CONFIG_DIR
            config_dir.mkdir()
            config_file = config_dir / CONFIG_FILE
            config_file.write_text("invalid: yaml: :")

            result = runner.invoke(app, ["sync"])
            assert result.exit_code == 1
            assert "corrupted" in result.output or "Failed to load" in result.output

    def test_status_corrupted_config(self, tmp_path: Path):
        """Test status with corrupted config file."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            config_dir = Path.cwd() / CONFIG_DIR
            config_dir.mkdir()
            config_file = config_dir / CONFIG_FILE
            config_file.write_text("invalid: yaml: :")

            result = runner.invoke(app, ["status"])
            # status handles errors and prints them, usually doesn't exit 1
            assert "corrupted" in result.output or "Failed to load" in result.output

    @patch("prompt_unifier.cli.commands._load_and_validate_config")
    def test_deploy_no_matching_content(self, mock_load, tmp_path: Path):
        """Test deploy when no files match criteria."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            mock_config = MagicMock()
            mock_config.deploy_tags = None
            mock_config.target_handlers = None
            mock_load.return_value = (tmp_path, mock_config)

            # Mock _prepare_content_for_deployment to return empty list
            patch_path = "prompt_unifier.cli.commands._prepare_content_for_deployment"
            with patch(patch_path, return_value=[]):
                result = runner.invoke(app, ["deploy"])
                assert result.exit_code == 0
                assert "No content files match" in result.output

    def test_deploy_missing_config(self, tmp_path: Path):
        """Test deploy fails when config is missing."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(app, ["deploy"])
            assert result.exit_code == 1
            assert "Configuration not found" in result.output

    @patch("prompt_unifier.cli.commands.ConfigManager.load_config")
    def test_sync_permission_error(self, mock_load, tmp_path: Path):
        """Test sync handles PermissionError."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            config_dir = Path.cwd() / CONFIG_DIR
            config_dir.mkdir()
            (config_dir / CONFIG_FILE).touch()

            mock_load.side_effect = PermissionError("Access denied")

            result = runner.invoke(app, ["sync"])
            assert result.exit_code == 1
            assert "Permission denied" in result.output

    @patch("prompt_unifier.cli.commands.GitService.sync_multiple_repos")
    @patch("prompt_unifier.cli.commands.ConfigManager.load_config")
    def test_sync_value_error(self, mock_load, mock_sync, tmp_path: Path):
        """Test sync handles ValueError from GitService."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            config_dir = Path.cwd() / CONFIG_DIR
            config_dir.mkdir()
            (config_dir / CONFIG_FILE).touch()

            mock_config = MagicMock()
            mock_config.repos = [MagicMock()]
            mock_load.return_value = mock_config
            mock_sync.side_effect = ValueError("Invalid repository")

            result = runner.invoke(app, ["sync"])
            assert result.exit_code == 1
            assert "Invalid repository" in result.output

    def test_validate_with_json_output_failed(self):
        """Test _validate_with_json_output exits 1 on failure."""
        validator = MagicMock()
        summary = MagicMock()
        summary.success = False
        summary.total_files = 1
        summary.passed = 0
        summary.failed = 1
        summary.error_count = 1
        summary.warning_count = 0
        summary.results = []
        validator.validate_directory.return_value = summary

        with pytest.raises(typer.Exit) as exc:
            _validate_with_json_output(validator, [Path("p")], True)
        assert exc.value.exit_code == 1

    def test_get_global_ai_provider_none(self, tmp_path: Path):
        """Test _get_global_ai_provider returns None when no config."""
        with patch("pathlib.Path.cwd", return_value=tmp_path):
            assert _get_global_ai_provider() is None

    def test_setup_deployment_handlers_none_found(self):
        """Test _setup_deployment_handlers fails when no handlers match."""
        config = MagicMock()
        # Mocking registry to return empty
        patch_path = "prompt_unifier.handlers.registry.ToolHandlerRegistry.get_all_handlers"
        with patch(patch_path, return_value=[]):
            with pytest.raises(typer.Exit) as exc:
                _setup_deployment_handlers(None, config, ["nonexistent"])
            assert exc.value.exit_code == 1

    def test_prepare_content_for_deployment_duplicates(self, tmp_path: Path):
        """Test _prepare_content_for_deployment fails on duplicates."""
        with patch("prompt_unifier.cli.commands.scan_content_files") as mock_scan:
            p1 = MagicMock()
            p1.title = "Dup"
            p2 = MagicMock()
            p2.title = "Dup"
            mock_scan.return_value = [(p1, "p", Path("f1")), (p2, "p", Path("f2"))]

            with pytest.raises(typer.Exit) as exc:
                _prepare_content_for_deployment(tmp_path, None, None)
            assert exc.value.exit_code == 1
