"""End-to-end integration tests for the validation engine.

These tests validate complete workflows using real file fixtures,
testing the entire validation pipeline from file discovery to output formatting.
"""

import json
from pathlib import Path

import pytest

from prompt_unifier.cli.commands import validate
from prompt_unifier.core.batch_validator import BatchValidator
from prompt_unifier.core.validator import PromptValidator
from prompt_unifier.models.validation import ErrorCode, WarningCode


class TestValidationPipelineIntegration:
    """Integration tests for complete validation pipeline."""

    def test_valid_prompts_directory_passes(self, valid_prompts_dir: Path) -> None:
        """Test that directory with only valid prompts passes validation."""
        # Act
        validator = BatchValidator()
        summary = validator.validate_directory(valid_prompts_dir)

        # Assert
        assert summary.success is True
        assert summary.failed == 0
        assert summary.error_count == 0
        # May have warnings (with_warnings.md)
        assert summary.total_files == 3

    def test_invalid_prompts_directory_fails(self, invalid_prompts_dir: Path) -> None:
        """Test that directory with invalid prompts fails validation."""
        # Act
        validator = BatchValidator()
        summary = validator.validate_directory(invalid_prompts_dir)

        # Assert
        assert summary.success is False
        assert summary.failed > 0
        assert summary.error_count > 0
        assert summary.total_files == 9  # All invalid prompt files

    def test_minimal_valid_prompt_validation(self, minimal_valid_prompt: Path) -> None:
        """Test validation of minimal prompt with only required fields."""
        # Act
        validator = PromptValidator()
        result = validator.validate_file(minimal_valid_prompt)

        # Assert
        assert result.is_valid is True
        assert result.status == "passed"
        assert len(result.errors) == 0

    def test_full_valid_prompt_has_no_warnings(self, full_valid_prompt: Path) -> None:
        """Test that prompt with all fields generates no warnings."""
        # Act
        validator = PromptValidator()
        result = validator.validate_file(full_valid_prompt)

        # Assert
        assert result.is_valid is True
        assert len(result.warnings) == 0

    def test_prompt_with_warnings_still_passes(self, prompt_with_warnings: Path) -> None:
        """Test that prompts with warnings still pass validation."""
        # Act
        validator = PromptValidator()
        result = validator.validate_file(prompt_with_warnings)

        # Assert
        assert result.is_valid is True
        assert result.status == "passed"
        assert len(result.warnings) > 0
        # Should warn about missing version, author, and empty tags
        warning_codes = [w.code for w in result.warnings]
        assert WarningCode.MISSING_OPTIONAL_FIELD.value in warning_codes
        assert WarningCode.EMPTY_TAGS_LIST.value in warning_codes

    def test_missing_required_field_generates_error(self, missing_name_prompt: Path) -> None:
        """Test that missing required field generates appropriate error."""
        # Act
        validator = PromptValidator()
        result = validator.validate_file(missing_name_prompt)

        # Assert
        assert result.is_valid is False
        assert result.status == "failed"
        assert len(result.errors) > 0
        error_codes = [e.code for e in result.errors]
        assert ErrorCode.MISSING_REQUIRED_FIELD.value in error_codes

    def test_nested_yaml_generates_error(self, nested_yaml_prompt: Path) -> None:
        """Test that nested YAML structure generates error."""
        # Act
        validator = PromptValidator()
        result = validator.validate_file(nested_yaml_prompt)

        # Assert
        assert result.is_valid is False
        error_codes = [e.code for e in result.errors]
        assert ErrorCode.NESTED_STRUCTURE.value in error_codes

    def test_invalid_semver_generates_error(self, invalid_semver_prompt: Path) -> None:
        """Test that invalid semantic version generates error."""
        # Act
        validator = PromptValidator()
        result = validator.validate_file(invalid_semver_prompt)

        # Assert
        assert result.is_valid is False
        error_codes = [e.code for e in result.errors]
        assert ErrorCode.INVALID_SEMVER.value in error_codes


class TestCLIIntegration:
    """Integration tests for CLI with real fixtures."""

    def test_cli_with_valid_directory_succeeds(
        self, valid_prompts_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test CLI validation with valid directory."""
        # Act
        import typer  # Import typer here

        try:
            validate(
                directory=valid_prompts_dir,
                json_output=False,
                content_type="all",
                scaff=True,
                test=False,
            )
            # If no typer.Exit is raised, it's a success (implicitly exit code 0)
            exit_code = 0
        except typer.Exit as e:
            exit_code = e.exit_code

        # Assert
        assert exit_code == 0  # Ensure the exit code is 0 (success)

    def test_cli_json_output_is_valid_json(
        self, valid_prompts_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that CLI --json flag produces valid JSON output."""
        # Act
        # Expect successful validation (exit code 0), so validate should not raise typer.Exit(1)
        validate(
            directory=valid_prompts_dir,
            json_output=True,
            content_type="all",
            scaff=True,
            test=False,
        )
        captured = capsys.readouterr()

        # Assert - should be valid JSON
        data = json.loads(captured.out)
        assert "summary" in data
        assert "results" in data
        assert data["summary"]["total_files"] == 3
        assert data["summary"]["success"] is True
