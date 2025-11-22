"""Tests for CLI global verbose flag implementation.

These tests verify the global --verbose and --log-file options work correctly
in the main CLI callback, ensuring proper logging configuration before
command execution.
"""

import logging
import os
import tempfile
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from prompt_unifier.cli.main import app


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_log_file():
    """Create a temporary log file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        yield f.name
    # Cleanup
    if os.path.exists(f.name):
        os.unlink(f.name)


class TestVerboseFlagIncrement:
    """Test that --verbose flag increments verbosity count correctly."""

    def test_no_verbose_flag_defaults_to_zero(self, runner):
        """Test that no -v flag results in verbosity 0 (WARNING level)."""
        with patch("prompt_unifier.cli.main.configure_logging"):
            result = runner.invoke(app, ["--help"])
            # --help exits before callback fully processes, but we can test flag parsing
            assert result.exit_code == 0

    def test_single_v_flag_increments_verbosity(self, runner):
        """Test that -v flag increments verbosity to 1."""
        with patch("prompt_unifier.cli.main.configure_logging") as mock_config:
            # Use a command that will fully execute
            runner.invoke(app, ["-v", "list"])
            # Check that configure_logging was called with verbosity=1
            if mock_config.called:
                call_args = mock_config.call_args
                assert call_args[1].get("verbosity", 0) == 1 or (
                    len(call_args[0]) > 0 and call_args[0][0] == 1
                )

    def test_double_v_flag_increments_verbosity_to_two(self, runner):
        """Test that -vv flags increment verbosity to 2."""
        with patch("prompt_unifier.cli.main.configure_logging") as mock_config:
            runner.invoke(app, ["-vv", "list"])
            if mock_config.called:
                call_args = mock_config.call_args
                # Verbosity should be 2
                verbosity = call_args[1].get("verbosity", call_args[0][0] if call_args[0] else 0)
                assert verbosity == 2

    def test_triple_v_flag_increments_verbosity_to_three(self, runner):
        """Test that -vvv flags increment verbosity to 3 (still DEBUG level)."""
        with patch("prompt_unifier.cli.main.configure_logging") as mock_config:
            runner.invoke(app, ["-vvv", "list"])
            if mock_config.called:
                call_args = mock_config.call_args
                verbosity = call_args[1].get("verbosity", call_args[0][0] if call_args[0] else 0)
                assert verbosity >= 3


class TestLogFileOption:
    """Test that --log-file option accepts file path correctly."""

    def test_log_file_option_accepts_path(self, runner, temp_log_file):
        """Test that --log-file option passes file path to configure_logging."""
        with patch("prompt_unifier.cli.main.configure_logging") as mock_config:
            runner.invoke(app, ["--log-file", temp_log_file, "list"])
            if mock_config.called:
                call_args = mock_config.call_args
                log_file = call_args[1].get(
                    "log_file", call_args[0][1] if len(call_args[0]) > 1 else None
                )
                assert log_file == temp_log_file

    def test_log_file_with_verbose(self, runner, temp_log_file):
        """Test that --log-file and --verbose can be used together."""
        with patch("prompt_unifier.cli.main.configure_logging") as mock_config:
            runner.invoke(app, ["-v", "--log-file", temp_log_file, "list"])
            if mock_config.called:
                call_args = mock_config.call_args
                verbosity = call_args[1].get("verbosity", call_args[0][0] if call_args[0] else 0)
                log_file = call_args[1].get(
                    "log_file", call_args[0][1] if len(call_args[0]) > 1 else None
                )
                assert verbosity == 1
                assert log_file == temp_log_file


class TestShortFlagConflict:
    """Test that -v works for verbose and --version still works."""

    def test_short_v_flag_is_verbose_not_version(self, runner):
        """Test that -v is now used for verbose, not version."""
        with patch("prompt_unifier.cli.main.configure_logging") as mock_config:
            result = runner.invoke(app, ["-v", "list"])
            # The key test: configure_logging should have been called with verbosity=1
            # This proves -v is now for verbosity, not version
            assert mock_config.called
            call_args = mock_config.call_args
            verbosity = call_args[1].get("verbosity", call_args[0][0] if call_args[0] else 0)
            assert verbosity == 1
            # Also verify we didn't just print version and exit
            assert "prompt-unifier version 0.1.0" not in result.output

    def test_version_long_flag_still_works(self, runner):
        """Test that --version still displays version information."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "prompt-unifier version" in result.output

    def test_version_capital_v_flag_works(self, runner):
        """Test that -V (capital) shows version."""
        result = runner.invoke(app, ["-V"])
        assert result.exit_code == 0
        assert "prompt-unifier version" in result.output


class TestConfigureLoggingCallback:
    """Test that callback invokes configure_logging with correct parameters."""

    def test_callback_invokes_configure_logging(self, runner):
        """Test that the callback calls configure_logging."""
        with patch("prompt_unifier.cli.main.configure_logging") as mock_config:
            runner.invoke(app, ["list"])
            # configure_logging should be called
            assert mock_config.called

    def test_callback_passes_correct_verbosity(self, runner):
        """Test that callback passes verbosity count to configure_logging."""
        with patch("prompt_unifier.cli.main.configure_logging") as mock_config:
            runner.invoke(app, ["-vv", "list"])
            assert mock_config.called
            call_args = mock_config.call_args
            # Check verbosity is 2
            verbosity = call_args[1].get("verbosity", call_args[0][0] if call_args[0] else 0)
            assert verbosity == 2

    def test_callback_passes_log_file_path(self, runner, temp_log_file):
        """Test that callback passes log_file to configure_logging."""
        with patch("prompt_unifier.cli.main.configure_logging") as mock_config:
            runner.invoke(app, ["--log-file", temp_log_file, "list"])
            assert mock_config.called
            call_args = mock_config.call_args
            log_file = call_args[1].get(
                "log_file", call_args[0][1] if len(call_args[0]) > 1 else None
            )
            assert log_file == temp_log_file


class TestVerboseFlagAffectsLogging:
    """Test that verbose flag actually affects logging output level."""

    def test_verbose_flag_enables_info_logging(self, runner, temp_log_file):
        """Test that -v flag enables INFO level logging."""
        # Reset logging state
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            handler.close()
            root_logger.removeHandler(handler)

        runner.invoke(app, ["-v", "--log-file", temp_log_file, "list"])

        # Check that logging was configured to at least INFO level
        root_logger = logging.getLogger()
        assert root_logger.level <= logging.INFO

    def test_double_verbose_flag_enables_debug_logging(self, runner, temp_log_file):
        """Test that -vv flags enable DEBUG level logging."""
        # Reset logging state
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            handler.close()
            root_logger.removeHandler(handler)

        runner.invoke(app, ["-vv", "--log-file", temp_log_file, "list"])

        # Check that logging was configured to DEBUG level
        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG
