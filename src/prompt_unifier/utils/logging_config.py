"""Centralized logging configuration for prompt-unifier CLI.

This module provides utilities for configuring Python's logging system
with Rich terminal output and optional file logging support.
"""

import logging
import sys

from rich.console import Console
from rich.logging import RichHandler

# Format constants for log output
FILE_LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
FILE_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging(verbosity: int = 0, log_file: str | None = None) -> None:
    """Configure the logging system based on verbosity level and optional file output.

    Sets up the root logger with appropriate level and handlers based on the
    verbosity count (number of -v flags passed to CLI).

    Args:
        verbosity: Number of -v flags (0=WARNING, 1=INFO, 2+=DEBUG)
        log_file: Optional path to write log output to a file

    Raises:
        PermissionError: If the log file path is not writable
        OSError: If the log file path is invalid

    Examples:
        >>> configure_logging(verbosity=0)  # WARNING level only
        >>> configure_logging(verbosity=1)  # INFO level
        >>> configure_logging(verbosity=2, log_file="/tmp/debug.log")  # DEBUG with file
    """
    # Map verbosity count to logging level
    if verbosity == 0:
        level = logging.WARNING
    elif verbosity == 1:
        level = logging.INFO
    else:  # verbosity >= 2
        level = logging.DEBUG

    # Get root logger and clear existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)

    # Set the root logger level
    root_logger.setLevel(level)

    # Add RichHandler for console output with colors and timestamps
    # Use stderr to keep stdout clean for JSON output and piping
    stderr_console = Console(file=sys.stderr)
    console_handler = RichHandler(
        level=level,
        console=stderr_console,
        show_time=True,
        show_path=False,
        markup=True,
        rich_tracebacks=True,
    )
    root_logger.addHandler(console_handler)

    # Add file handler if log_file path provided
    if log_file:
        file_handler = logging.FileHandler(log_file, mode="a")
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(FILE_LOG_FORMAT, datefmt=FILE_DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
