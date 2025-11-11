"""Tests for CLI commands.

This module tests the validate command logic.
"""

import json
from pathlib import Path

import pytest
from click.exceptions import Exit as ClickExit

from prompt_manager.cli.commands import validate


@pytest.fixture
def temp_valid_directory(tmp_path: Path) -> Path:
    """Create a temporary directory with valid prompt files."""
    prompt_file = tmp_path / "valid-prompt.md"
    prompt_file.write_text(
        """name: test-prompt
description: A test prompt for validation
version: 1.0.0
>>>
This is the content of the prompt.
"""
    )
    return tmp_path


@pytest.fixture
def temp_invalid_directory(tmp_path: Path) -> Path:
    """Create a temporary directory with invalid prompt files."""
    prompt_file = tmp_path / "invalid-prompt.md"
    prompt_file.write_text(
        """name: broken-prompt
>>>
Content without description field.
"""
    )
    return tmp_path


def test_command_with_valid_directory_succeeds(temp_valid_directory: Path) -> None:
    """Test validate command with valid directory executes successfully."""
    # Should not raise an exception
    try:
        validate(temp_valid_directory, json_output=False, verbose=False)
    except ClickExit:
        pytest.fail("validate() should not raise Exit for valid directory")


def test_command_with_invalid_directory_shows_error() -> None:
    """Test validate command with non-existent directory shows error."""
    with pytest.raises(ClickExit) as exc_info:
        validate(Path("/nonexistent/directory"), json_output=False, verbose=False)
    assert exc_info.value.exit_code == 1


def test_json_flag_outputs_json_format(
    temp_valid_directory: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test --json flag outputs JSON format."""
    validate(temp_valid_directory, json_output=True, verbose=False)
    captured = capsys.readouterr()

    # Output should be valid JSON
    data = json.loads(captured.out)
    assert "summary" in data
    assert "results" in data


def test_default_output_uses_rich_format(
    temp_valid_directory: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test default output uses Rich format (not JSON)."""
    validate(temp_valid_directory, json_output=False, verbose=False)
    captured = capsys.readouterr()

    # Rich output should NOT be valid JSON
    try:
        json.loads(captured.out)
        pytest.fail("Output should not be JSON by default")
    except json.JSONDecodeError:
        # Expected - Rich format is not JSON
        pass


def test_verbose_flag_shows_progress(
    temp_valid_directory: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test --verbose flag shows detailed progress."""
    validate(temp_valid_directory, json_output=False, verbose=True)
    captured = capsys.readouterr()

    # Verbose mode should show file names or directory info
    assert "valid-prompt.md" in captured.out or "prompts" in captured.out.lower()


def test_exit_code_zero_when_validation_passes(temp_valid_directory: Path) -> None:
    """Test no exception raised when validation passes (warnings are OK)."""
    # Should complete without raising Exit
    try:
        validate(temp_valid_directory, json_output=False, verbose=False)
    except ClickExit:
        pytest.fail("validate() should not raise Exit when validation passes")


def test_exit_code_one_when_validation_fails(temp_invalid_directory: Path) -> None:
    """Test Exit(1) raised when validation fails (errors present)."""
    with pytest.raises(ClickExit) as exc_info:
        validate(temp_invalid_directory, json_output=False, verbose=False)
    assert exc_info.value.exit_code == 1
