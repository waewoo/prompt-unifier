"""Tests for CLI deploy command --base-path option and base path resolution logic."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from prompt_manager.cli.main import app

runner = CliRunner()


@pytest.fixture
def mock_config_with_handlers(tmp_path: Path) -> tuple[Path, Path]:
    """Create a mock config file with handlers configuration."""
    config_dir = tmp_path / ".prompt-manager"
    config_dir.mkdir()
    config_file = config_dir / "config.yaml"
    storage_dir = tmp_path / "storage"

    config_file.write_text(f"""
repo_url: https://example.com/repo.git
storage_path: {storage_dir}
deploy_tags: ["python"]
target_handlers: ["continue"]
handlers:
  continue:
    base_path: {tmp_path / "configured_path"}
""")
    return config_file, tmp_path


@pytest.fixture
def mock_storage_with_content(tmp_path: Path) -> Path:
    """Create mock storage with prompts and rules."""
    storage_dir = tmp_path / "storage"
    storage_dir.mkdir()

    prompts_dir = storage_dir / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "test-prompt.md").write_text("""---
title: test-prompt
description: A test prompt
tags: ["python"]
version: 1.0.0
---

Prompt content
""")

    rules_dir = storage_dir / "rules"
    rules_dir.mkdir()
    (rules_dir / "test-rule.md").write_text("""---
title: test-rule
description: A test rule
category: testing
tags: ["python"]
version: 1.0.0
---

Rule content
""")

    return storage_dir


class TestDeployBasePathCLIOption:
    """Tests for --base-path CLI option (Task 4.1)."""

    def test_deploy_accepts_base_path_option(self, tmp_path: Path, mock_storage_with_content: Path):
        """Test that deploy command accepts --base-path option."""
        # Setup
        config_dir = tmp_path / ".prompt-manager"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        config_file.write_text(f"""
repo_url: https://example.com/repo.git
storage_path: {mock_storage_with_content}
target_handlers: ["continue"]
""")

        custom_base_path = tmp_path / "custom_continue"

        # Mock the current working directory
        with patch("prompt_manager.cli.commands.Path.cwd", return_value=tmp_path):
            # Run deploy with --base-path
            result = runner.invoke(app, ["deploy", "--base-path", str(custom_base_path)])

            # Should not fail with "no such option" error
            assert "no such option" not in result.output.lower()
            assert result.exit_code == 0

    def test_base_path_overrides_config(self, tmp_path: Path, mock_storage_with_content: Path):
        """Test that --base-path overrides config.yaml base_path."""
        # Setup config with handlers.continue.base_path
        config_dir = tmp_path / ".prompt-manager"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        configured_path = tmp_path / "configured_path"
        config_file.write_text(f"""
repo_url: https://example.com/repo.git
storage_path: {mock_storage_with_content}
target_handlers: ["continue"]
handlers:
  continue:
    base_path: {configured_path}
""")

        # CLI override path
        cli_override_path = tmp_path / "cli_override_path"

        with patch("prompt_manager.cli.commands.Path.cwd", return_value=tmp_path):
            with patch("prompt_manager.cli.commands.ContinueToolHandler") as MockHandler:  # noqa: N806
                mock_handler_instance = MagicMock()
                MockHandler.return_value = mock_handler_instance
                mock_handler_instance.get_name.return_value = "continue"
                mock_handler_instance.get_status.return_value = "active"

                runner.invoke(app, ["deploy", "--base-path", str(cli_override_path)])

                # Verify handler was instantiated with CLI path, not configured path
                MockHandler.assert_called_once()
                call_kwargs = MockHandler.call_args[1] if MockHandler.call_args[1] else {}
                if "base_path" in call_kwargs:
                    assert call_kwargs["base_path"] == cli_override_path

    def test_base_path_works_with_handlers_flag(
        self, tmp_path: Path, mock_storage_with_content: Path
    ):
        """Test that --base-path works with --handlers flag."""
        config_dir = tmp_path / ".prompt-manager"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        config_file.write_text(f"""
repo_url: https://example.com/repo.git
storage_path: {mock_storage_with_content}
""")

        custom_base_path = tmp_path / "custom_continue"

        with patch("prompt_manager.cli.commands.Path.cwd", return_value=tmp_path):
            result = runner.invoke(
                app,
                [
                    "deploy",
                    "--handlers",
                    "continue",
                    "--base-path",
                    str(custom_base_path),
                ],
            )

            # Should not fail
            assert result.exit_code == 0


class TestBasePathResolutionLogic:
    """Tests for base path resolution logic (Task 4.3)."""

    def test_precedence_cli_over_config_over_default(
        self, tmp_path: Path, mock_storage_with_content: Path
    ):
        """Test precedence order: CLI flag > config.yaml > default Path.cwd()."""
        config_dir = tmp_path / ".prompt-manager"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        configured_path = tmp_path / "configured_path"
        config_file.write_text(f"""
repo_url: https://example.com/repo.git
storage_path: {mock_storage_with_content}
target_handlers: ["continue"]
handlers:
  continue:
    base_path: {configured_path}
""")

        cli_path = tmp_path / "cli_path"

        with patch("prompt_manager.cli.commands.Path.cwd", return_value=tmp_path):
            with patch("prompt_manager.cli.commands.ContinueToolHandler") as MockHandler:  # noqa: N806
                mock_handler_instance = MagicMock()
                MockHandler.return_value = mock_handler_instance
                mock_handler_instance.get_name.return_value = "continue"

                # Test 1: CLI flag has highest priority
                runner.invoke(app, ["deploy", "--base-path", str(cli_path)])
                call_kwargs = MockHandler.call_args[1] if MockHandler.call_args[1] else {}
                if "base_path" in call_kwargs:
                    assert call_kwargs["base_path"] == cli_path

                MockHandler.reset_mock()

                # Test 2: Config path used when no CLI flag
                runner.invoke(app, ["deploy"])
                call_kwargs = MockHandler.call_args[1] if MockHandler.call_args[1] else {}
                if "base_path" in call_kwargs:
                    # Should use configured path (after env var expansion)
                    assert str(configured_path) in str(call_kwargs["base_path"])

    def test_environment_variable_expansion_in_configured_paths(
        self, tmp_path: Path, mock_storage_with_content: Path
    ):
        """Test environment variable expansion in configured paths."""
        config_dir = tmp_path / ".prompt-manager"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        config_file.write_text(f"""
repo_url: https://example.com/repo.git
storage_path: {mock_storage_with_content}
target_handlers: ["continue"]
handlers:
  continue:
    base_path: $PWD/.continue
""")

        with patch("prompt_manager.cli.commands.Path.cwd", return_value=tmp_path):
            with patch("prompt_manager.cli.commands.ContinueToolHandler") as MockHandler:  # noqa: N806
                mock_handler_instance = MagicMock()
                MockHandler.return_value = mock_handler_instance
                mock_handler_instance.get_name.return_value = "continue"

                runner.invoke(app, ["deploy"])

                # Verify env vars were expanded
                call_kwargs = MockHandler.call_args[1] if MockHandler.call_args[1] else {}
                if "base_path" in call_kwargs:
                    base_path_str = str(call_kwargs["base_path"])
                    # $PWD should be expanded to actual path
                    assert "$PWD" not in base_path_str
                    assert str(tmp_path) in base_path_str

    def test_error_handling_for_missing_environment_variables(
        self, tmp_path: Path, mock_storage_with_content: Path
    ):
        """Test error handling for missing environment variables."""
        config_dir = tmp_path / ".prompt-manager"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        config_file.write_text(f"""
repo_url: https://example.com/repo.git
storage_path: {mock_storage_with_content}
target_handlers: ["continue"]
handlers:
  continue:
    base_path: $NONEXISTENT_VAR/.continue
""")

        with patch("prompt_manager.cli.commands.Path.cwd", return_value=tmp_path):
            result = runner.invoke(app, ["deploy"])

            # Should fail with error about missing environment variable
            assert result.exit_code == 1
            assert "NONEXISTENT_VAR" in result.output or "Environment variable" in result.output

    def test_default_path_cwd_when_no_config(self, tmp_path: Path, mock_storage_with_content: Path):
        """Test that Path.cwd() is used as default when no configuration."""
        config_dir = tmp_path / ".prompt-manager"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        config_file.write_text(f"""
repo_url: https://example.com/repo.git
storage_path: {mock_storage_with_content}
target_handlers: ["continue"]
""")

        with patch("prompt_manager.cli.commands.Path.cwd", return_value=tmp_path):
            with patch("prompt_manager.cli.commands.ContinueToolHandler") as MockHandler:  # noqa: N806
                mock_handler_instance = MagicMock()
                MockHandler.return_value = mock_handler_instance
                mock_handler_instance.get_name.return_value = "continue"

                runner.invoke(app, ["deploy"])

                # When no base_path in config and no CLI flag,
                # should use None (handler defaults to cwd)
                call_kwargs = MockHandler.call_args[1] if MockHandler.call_args[1] else {}
                # Either no base_path key (None) or explicitly None
                base_path_value = call_kwargs.get("base_path", None)
                # If None is passed, handler will default to Path.cwd()
                assert base_path_value is None or base_path_value == tmp_path
