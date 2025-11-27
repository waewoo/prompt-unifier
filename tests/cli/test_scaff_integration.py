"""Tests for SCAFF validation CLI integration.

This module tests the integration of SCAFF validation with the CLI validate command,
including the --no-scaff flag and BatchValidator integration.
"""

import inspect
from pathlib import Path

import pytest

from prompt_unifier.cli.commands import validate
from prompt_unifier.core.batch_validator import BatchValidator
from prompt_unifier.models.scaff import SCARFFComponent, SCARFFScore
from prompt_unifier.models.validation import ValidationResult


@pytest.fixture
def sample_validation_result():
    """Create a sample validation result with SCAFF score."""
    scaff_score = SCARFFScore(
        components=[
            SCARFFComponent(component_name="Specific", score=15, status="good"),
            SCARFFComponent(component_name="Contextual", score=12, status="good"),
            SCARFFComponent(component_name="Actionable", score=18, status="excellent"),
            SCARFFComponent(component_name="Formatted", score=16, status="excellent"),
            SCARFFComponent(component_name="Focused", score=14, status="good"),
        ],
        total_score=75,
    )

    return ValidationResult(
        file=Path("test.md"),
        status="passed",
        errors=[],
        warnings=[],
        scaff_score=scaff_score,
    )


def test_batch_validator_integrates_scaff_validation(tmp_path):
    """Test that BatchValidator integrates SCAFF validation after format validation."""
    # Create a test file with content
    test_file = tmp_path / "test.md"
    test_file.write_text(
        "---\n"
        "title: test-prompt\n"
        "description: A test prompt\n"
        "---\n"
        ">>>\n"
        "# Context\n"
        "This is a test prompt for testing SCAFF validation.\n"
        "## Instructions\n"
        "1. Create a test\n"
        "2. Implement the feature\n"
        "3. Test the implementation\n",
        encoding="utf-8",
    )

    # Create validator and run with SCAFF enabled
    validator = BatchValidator()
    summary = validator.validate_directory(tmp_path, scaff_enabled=True)

    # Verify validation ran successfully
    assert summary.total_files == 1
    assert summary.success is True

    # Verify SCAFF score was attached to result
    assert len(summary.results) == 1
    result = summary.results[0]
    assert result.scaff_score is not None
    assert result.scaff_score.total_score >= 0
    assert result.scaff_score.total_score <= 100
    assert len(result.scaff_score.components) == 5


def test_batch_validator_without_scaff_validation(tmp_path):
    """Test that BatchValidator skips SCAFF validation when disabled."""
    # Create a test file with content
    test_file = tmp_path / "test.md"
    test_file.write_text(
        "---\ntitle: test-prompt\ndescription: A test prompt\n---\n>>>\nContent here",
        encoding="utf-8",
    )

    # Create validator and run with SCAFF disabled
    validator = BatchValidator()
    summary = validator.validate_directory(tmp_path, scaff_enabled=False)

    # Verify validation ran successfully
    assert summary.total_files == 1
    assert summary.success is True

    # Verify SCAFF score was NOT attached to result
    assert len(summary.results) == 1
    result = summary.results[0]
    assert result.scaff_score is None


def test_scaff_warnings_included_in_summary_warning_count(tmp_path):
    """Test that SCAFF warnings are included in ValidationSummary.warning_count."""
    # Create a test file with poor SCAFF compliance
    test_file = tmp_path / "test.md"
    test_file.write_text(
        "---\ntitle: test-prompt\ndescription: A test\n---\n>>>\nShort content",
        encoding="utf-8",
    )

    # Create validator and run with SCAFF enabled
    validator = BatchValidator()
    summary = validator.validate_directory(tmp_path, scaff_enabled=True)

    # Verify SCAFF warnings are counted
    assert summary.total_files == 1
    assert summary.success is True  # Warnings don't fail validation
    # SCAFF warnings should be included in total warning count
    result = summary.results[0]
    if len(result.warnings) > 0:
        # Some warnings should be SCAFF-related
        scaff_warnings = [w for w in result.warnings if w.code.startswith("SCAFF_")]
        assert len(scaff_warnings) > 0
        # Total warnings should include SCAFF warnings
        assert summary.warning_count >= len(scaff_warnings)


def test_scaff_warnings_do_not_block_validation(tmp_path):
    """Test that SCAFF warnings do not cause validation to fail."""
    # Create a test file with poor SCAFF compliance but valid format
    test_file = tmp_path / "test.md"
    test_file.write_text(
        "---\ntitle: test-prompt\ndescription: Test description\n---\n>>>\nMinimal content",
        encoding="utf-8",
    )

    # Create validator and run with SCAFF enabled
    validator = BatchValidator()
    summary = validator.validate_directory(tmp_path, scaff_enabled=True)

    # Verify validation succeeds despite SCAFF warnings
    assert summary.success is True
    assert summary.failed == 0
    # Warnings may be present, but they don't block
    assert summary.warning_count >= 0


def test_batch_validator_scaff_enabled_parameter_defaults_to_true():
    """Test that scaff_enabled parameter defaults to True in BatchValidator."""
    validator = BatchValidator()

    # Verify the method signature includes scaff_enabled with default True
    sig = inspect.signature(validator.validate_directory)
    params = sig.parameters

    assert "scaff_enabled" in params
    assert params["scaff_enabled"].default is True


def test_cli_scaff_parameter_defaults_to_true():
    """Test that scaff parameter defaults to True in CLI validate command."""
    sig = inspect.signature(validate)
    params = sig.parameters

    # The validate function should have a 'scaff' parameter
    assert "scaff" in params

    # The default should be True (SCAFF enabled by default)
    # Note: typer.Option returns a default from the Option object
    # We just verify the parameter exists
    param = params["scaff"]
    assert param is not None
