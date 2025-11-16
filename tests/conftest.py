"""Pytest fixtures for validation engine integration tests.

This module provides fixtures for accessing test prompt files
used in integration testing of the validation engine.
"""

from pathlib import Path

import pytest


@pytest.fixture
def valid_prompts_dir() -> Path:
    """Return path to directory containing valid prompt files."""
    return Path(__file__).parent / "fixtures" / "valid_prompts"


@pytest.fixture
def invalid_prompts_dir() -> Path:
    """Return path to directory containing invalid prompt files."""
    return Path(__file__).parent / "fixtures" / "invalid_prompts"


@pytest.fixture
def minimal_valid_prompt(valid_prompts_dir: Path) -> Path:
    """Return path to minimal valid prompt file."""
    return valid_prompts_dir / "prompts" / "minimal_valid.md"


@pytest.fixture
def full_valid_prompt(valid_prompts_dir: Path) -> Path:
    """Return path to full valid prompt file with all fields."""
    return valid_prompts_dir / "prompts" / "full_valid.md"


@pytest.fixture
def prompt_with_warnings(valid_prompts_dir: Path) -> Path:
    """Return path to valid prompt that generates warnings."""
    return valid_prompts_dir / "prompts" / "with_warnings.md"


@pytest.fixture
def missing_name_prompt(invalid_prompts_dir: Path) -> Path:
    """Return path to prompt missing required 'name' field."""
    return invalid_prompts_dir / "missing_name.md"


@pytest.fixture
def missing_description_prompt(invalid_prompts_dir: Path) -> Path:
    """Return path to prompt missing required 'description' field."""
    return invalid_prompts_dir / "missing_description.md"


@pytest.fixture
def no_separator_prompt(invalid_prompts_dir: Path) -> Path:
    """Return path to prompt with no separator."""
    return invalid_prompts_dir / "no_separator.md"


@pytest.fixture
def multiple_separators_prompt(invalid_prompts_dir: Path) -> Path:
    """Return path to prompt with multiple separators."""
    return invalid_prompts_dir / "multiple_separators.md"


@pytest.fixture
def nested_yaml_prompt(invalid_prompts_dir: Path) -> Path:
    """Return path to prompt with nested YAML structure."""
    return invalid_prompts_dir / "nested_yaml.md"


@pytest.fixture
def invalid_semver_prompt(invalid_prompts_dir: Path) -> Path:
    """Return path to prompt with invalid semantic version."""
    return invalid_prompts_dir / "invalid_semver.md"


@pytest.fixture
def prohibited_field_prompt(invalid_prompts_dir: Path) -> Path:
    """Return path to prompt with prohibited 'tools' field."""
    return invalid_prompts_dir / "prohibited_tools.md"
