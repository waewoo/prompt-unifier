"""Tests for logging configuration utility functions.

This module tests the centralized logging configuration including
verbosity level mapping, file handler creation, and RichHandler integration.
"""

import logging
import tempfile
from pathlib import Path

import pytest

from prompt_unifier.utils.logging_config import configure_logging


class TestConfigureLogging:
    """Test suite for configure_logging function."""

    def setup_method(self) -> None:
        """Reset logging configuration before each test."""
        # Clear all handlers from root logger
        root_logger = logging.getLogger()
        root_logger.handlers = []
        root_logger.setLevel(logging.WARNING)

    def teardown_method(self) -> None:
        """Clean up logging configuration after each test."""
        # Clear all handlers from root logger
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            handler.close()
            root_logger.removeHandler(handler)
        root_logger.setLevel(logging.WARNING)

    def test_verbosity_zero_sets_warning_level(self) -> None:
        """Test that verbosity 0 (no -v flags) sets WARNING level."""
        configure_logging(verbosity=0)
        root_logger = logging.getLogger()
        assert root_logger.level == logging.WARNING

    def test_verbosity_one_sets_info_level(self) -> None:
        """Test that verbosity 1 (single -v flag) sets INFO level."""
        configure_logging(verbosity=1)
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO

    def test_verbosity_two_sets_debug_level(self) -> None:
        """Test that verbosity 2 (-vv flags) sets DEBUG level."""
        configure_logging(verbosity=2)
        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG

    def test_verbosity_higher_than_two_still_sets_debug(self) -> None:
        """Test that verbosity 3+ still maps to DEBUG level."""
        configure_logging(verbosity=5)
        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG

    def test_file_handler_creation_with_valid_path(self) -> None:
        """Test that file handler is created when valid log_file path provided."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            log_path = f.name

        try:
            configure_logging(verbosity=1, log_file=log_path)
            root_logger = logging.getLogger()

            # Check that a file handler was added
            file_handlers = [h for h in root_logger.handlers if isinstance(h, logging.FileHandler)]
            assert len(file_handlers) == 1

            # Verify the file path
            assert file_handlers[0].baseFilename == log_path
        finally:
            # Close handlers before unlink to avoid Windows permission errors
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                handler.close()
                root_logger.removeHandler(handler)
            Path(log_path).unlink(missing_ok=True)

    def test_file_handler_error_for_invalid_path(self) -> None:
        """Test that invalid file path raises appropriate error."""
        invalid_path = "/nonexistent/directory/that/should/not/exist/test.log"

        with pytest.raises((PermissionError, OSError, IOError)):
            configure_logging(verbosity=1, log_file=invalid_path)

    def test_rich_handler_added_for_console_output(self) -> None:
        """Test that RichHandler is added for console output."""
        from rich.logging import RichHandler

        configure_logging(verbosity=1)
        root_logger = logging.getLogger()

        # Check that a RichHandler was added
        rich_handlers = [h for h in root_logger.handlers if isinstance(h, RichHandler)]
        assert len(rich_handlers) == 1

    def test_both_handlers_active_simultaneously(self) -> None:
        """Test that both file handler and RichHandler can be active together."""
        from rich.logging import RichHandler

        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            log_path = f.name

        try:
            configure_logging(verbosity=2, log_file=log_path)
            root_logger = logging.getLogger()

            # Check for RichHandler
            rich_handlers = [h for h in root_logger.handlers if isinstance(h, RichHandler)]
            assert len(rich_handlers) == 1

            # Check for FileHandler
            file_handlers = [h for h in root_logger.handlers if isinstance(h, logging.FileHandler)]
            assert len(file_handlers) == 1

            # Verify total handler count is 2
            assert len(root_logger.handlers) == 2
        finally:
            # Close handlers before unlink to avoid Windows permission errors
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                handler.close()
                root_logger.removeHandler(handler)
            Path(log_path).unlink(missing_ok=True)

    def test_clears_existing_handlers_before_configuration(self) -> None:
        """Test that existing handlers are cleared before adding new ones."""
        from rich.logging import RichHandler

        # Configure logging twice
        configure_logging(verbosity=1)
        configure_logging(verbosity=2)

        root_logger = logging.getLogger()

        # Should only have one RichHandler, not two
        rich_handlers = [h for h in root_logger.handlers if isinstance(h, RichHandler)]
        assert len(rich_handlers) == 1
