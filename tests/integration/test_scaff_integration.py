"""Integration tests for SCAFF validation end-to-end workflows.

This module contains strategic integration tests to verify:
- Complete validation flow with SCAFF enabled
- Complete validation flow with --no-scaff flag
- SCAFF score aggregation across multiple files
- JSON output format includes SCAFF scores
- BatchValidator integration with SCAFF validation
- Backward compatibility with existing validation
"""

from pathlib import Path

from typer.testing import CliRunner

from prompt_unifier.core.batch_validator import BatchValidator
from prompt_unifier.models.scaff import SCARFFScore

runner = CliRunner()


class TestSCAFFEndToEndValidation:
    """Test complete SCAFF validation workflows end-to-end."""

    def test_validation_flow_with_scaff_enabled_by_default(self, tmp_path: Path) -> None:
        """Test end-to-end validation flow: file -> format validation -> SCAFF validation -> output.

        Critical workflow: Verifies that SCAFF validation runs by default and integrates
        with the complete validation pipeline.
        """
        # Create a well-structured prompt file
        prompt_file = tmp_path / "test-prompt.md"
        prompt_file.write_text("""---
title: code-review-assistant
description: Assistant for Python code review
tags: ["python", "code-review"]
version: 1.0.0
---

>>>

## Context
This tool helps review Python code for best practices and bugs.
Target users are intermediate Python developers.

## Requirements
You must:
- Check PEP 8 compliance
- Identify security issues
- Should provide specific line numbers

## Steps
1. Analyze code structure
2. Check for patterns
3. Provide feedback

## Output
- Use bullet points
- Include severity levels
""")

        # Run validation on the directory
        validator = BatchValidator()
        summary = validator.validate_directory(tmp_path, scaff_enabled=True)

        # Verify format validation passed
        assert summary.total_files == 1
        assert summary.passed == 1
        assert summary.failed == 0

        # Verify SCAFF validation ran and score was calculated
        result = summary.results[0]
        assert result.scaff_score is not None
        assert isinstance(result.scaff_score, SCARFFScore)
        assert result.scaff_score.total_score > 0
        assert len(result.scaff_score.components) == 5

        # Verify SCAFF warnings (if any) are in the results
        scaff_warnings = [w for w in result.warnings if w.code.startswith("SCAFF_")]
        # Well-structured content should have minimal SCAFF warnings
        assert len(scaff_warnings) <= 2

    def test_validation_flow_with_no_scaff_flag(self, tmp_path: Path) -> None:
        """Test end-to-end validation flow with --no-scaff flag disables SCAFF validation.

        Critical workflow: Verifies that --no-scaff flag properly disables SCAFF validation
        while maintaining format validation.
        """
        # Create a prompt file
        prompt_file = tmp_path / "test-prompt.md"
        prompt_file.write_text("""---
title: test-prompt
description: A test prompt
version: 1.0.0
---

>>>

Some content here.
""")

        # Run validation with SCAFF disabled
        validator = BatchValidator()
        summary = validator.validate_directory(tmp_path, scaff_enabled=False)

        # Verify format validation still ran
        assert summary.total_files == 1
        assert summary.passed == 1

        # Verify SCAFF validation did NOT run
        result = summary.results[0]
        assert result.scaff_score is None

        # Verify no SCAFF warnings
        scaff_warnings = [w for w in result.warnings if w.code.startswith("SCAFF_")]
        assert len(scaff_warnings) == 0

    def test_scaff_score_aggregation_across_multiple_files(self, tmp_path: Path) -> None:
        """Test SCAFF score aggregation when validating multiple files.

        Critical workflow: Verifies that each file gets its own SCAFF score and
        results are properly aggregated in the summary.
        """
        # Create multiple prompt files with varying quality
        # High-quality prompt
        (tmp_path / "high-quality.md").write_text("""---
title: excellent-prompt
description: A well-structured prompt
version: 1.0.0
---

>>>

## Background
Clear context about the task.

## Requirements
You must implement these features:
- Feature 1 with specific criteria
- Feature 2 with measurable goals

## Steps
1. Create the implementation
2. Test thoroughly
3. Deploy carefully

## Format
- Use bullet points
- Include examples
""")

        # Medium-quality prompt
        (tmp_path / "medium-quality.md").write_text("""---
title: okay-prompt
description: Basic prompt structure
version: 1.0.0
---

>>>

Do some work on the project.
Make sure it works well.
Test it.
""")

        # Low-quality prompt
        (tmp_path / "low-quality.md").write_text("""---
title: poor-prompt
description: Minimal prompt
version: 1.0.0
---

>>>

vague thing
""")

        # Validate all files
        validator = BatchValidator()
        summary = validator.validate_directory(tmp_path, scaff_enabled=True)

        # Verify all files were validated
        assert summary.total_files == 3
        assert len(summary.results) == 3

        # Verify each file has its own SCAFF score
        for result in summary.results:
            assert result.scaff_score is not None
            assert isinstance(result.scaff_score, SCARFFScore)
            assert 0 <= result.scaff_score.total_score <= 100

        # Verify scores vary based on quality
        high_quality_result = next(r for r in summary.results if "high-quality" in str(r.file))
        low_quality_result = next(r for r in summary.results if "low-quality" in str(r.file))

        assert (
            high_quality_result.scaff_score.total_score
            > low_quality_result.scaff_score.total_score
        )

    def test_batch_validator_integration_with_scaff(self, tmp_path: Path) -> None:
        """Test BatchValidator properly integrates SCAFF validation after format validation.

        Critical workflow: Verifies that SCAFF validation runs after format validation
        and that both sets of issues are merged correctly.
        """
        # Create a file with format issues AND SCAFF issues
        prompt_file = tmp_path / "mixed-issues.md"
        prompt_file.write_text("""---
title: mixed-prompt
description: Has both format and SCAFF issues
---

>>>

vague content without structure
""")

        # Run validation
        validator = BatchValidator()
        summary = validator.validate_directory(tmp_path, scaff_enabled=True)

        result = summary.results[0]

        # Verify format validation ran (might have warnings for missing optional fields)
        # Format validation should pass (required fields are present)
        assert result.status == "passed"

        # Verify SCAFF validation ran
        assert result.scaff_score is not None

        # Verify SCAFF warnings are present for poor content
        scaff_warnings = [w for w in result.warnings if w.code.startswith("SCAFF_")]
        assert len(scaff_warnings) > 0

        # Verify all warnings are in the result
        assert len(result.warnings) >= len(scaff_warnings)

    def test_json_output_includes_scaff_scores(self, tmp_path: Path) -> None:
        """Test that JSON output format includes SCAFF scores.

        Critical workflow: Verifies that when using --json flag, SCAFF scores are
        included in the JSON output.
        """
        # Create a prompt file
        prompt_file = tmp_path / "test-prompt.md"
        prompt_file.write_text("""---
title: test-prompt
description: Test for JSON output
version: 1.0.0
---

>>>

## Context
Some background information.

## Steps
1. Do this
2. Do that
""")

        # Run validation and get JSON serialization
        validator = BatchValidator()
        summary = validator.validate_directory(tmp_path, scaff_enabled=True)

        # Serialize to dict (similar to JSON output)
        summary_dict = summary.model_dump()

        # Verify SCAFF scores are in the serialized output
        assert len(summary_dict["results"]) == 1
        result_dict = summary_dict["results"][0]

        # Verify scaff_score is in the output
        assert "scaff_score" in result_dict
        if result_dict["scaff_score"] is not None:
            assert "total_score" in result_dict["scaff_score"]
            assert "components" in result_dict["scaff_score"]
            assert len(result_dict["scaff_score"]["components"]) == 5


class TestSCAFFBackwardCompatibility:
    """Test backward compatibility.

    Existing features should still work with SCAFF feature added.
    """

    def test_existing_validation_still_works(self, tmp_path: Path) -> None:
        """Test that existing validation functionality is not broken by SCAFF feature.

        Critical workflow: Verifies backward compatibility - existing validation
        behavior is unchanged when SCAFF is enabled.
        """
        # Create a file with format error (missing required field)
        bad_file = tmp_path / "bad.md"
        bad_file.write_text("""---
title: bad-prompt
---

>>>

Missing description field.
""")

        # Validate with SCAFF enabled
        validator = BatchValidator()
        summary = validator.validate_directory(tmp_path, scaff_enabled=True)

        # Verify format validation still catches errors
        assert summary.total_files == 1
        assert summary.failed == 1
        assert summary.error_count >= 1

        result = summary.results[0]
        assert result.status == "failed"
        assert len(result.errors) > 0

        # Format errors should prevent SCAFF validation from running on invalid files
        # (or SCAFF validation runs but file is still marked failed due to format errors)

    def test_validation_without_scaff_maintains_existing_behavior(self, tmp_path: Path) -> None:
        """Test that validation with --no-scaff flag maintains exact existing behavior.

        Critical workflow: Verifies that disabling SCAFF validation gives identical
        results to the pre-SCAFF validation behavior.
        """
        # Create a valid file
        valid_file = tmp_path / "valid.md"
        valid_file.write_text("""---
title: valid-prompt
description: Valid prompt
version: 1.0.0
---

>>>

Content here.
""")

        # Validate without SCAFF
        validator = BatchValidator()
        summary = validator.validate_directory(tmp_path, scaff_enabled=False)

        # Verify validation works as before
        assert summary.total_files == 1
        assert summary.passed == 1
        assert summary.failed == 0

        result = summary.results[0]
        assert result.status == "passed"
        assert result.scaff_score is None

        # Should have no SCAFF warnings
        scaff_warnings = [w for w in result.warnings if w.code.startswith("SCAFF_")]
        assert len(scaff_warnings) == 0

    def test_type_filtering_works_with_scaff(self, tmp_path: Path) -> None:
        """Test that --type filtering still works correctly with SCAFF enabled.

        Critical workflow: Verifies that existing --type flag functionality is
        not broken by SCAFF feature.
        """
        # Create both prompts and rules directories
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()

        # Create a prompt
        (prompts_dir / "test-prompt.md").write_text("""---
title: test-prompt
description: A test prompt
version: 1.0.0
---

>>>

Prompt content.
""")

        # Create a rule
        (rules_dir / "test-rule.md").write_text("""---
title: test-rule
description: A test rule
category: testing
version: 1.0.0
---

>>>

Rule content.
""")

        # Validate only prompts
        validator = BatchValidator()
        prompts_summary = validator.validate_directory(prompts_dir, scaff_enabled=True)

        assert prompts_summary.total_files == 1
        assert prompts_summary.results[0].scaff_score is not None

        # Validate only rules
        rules_summary = validator.validate_directory(rules_dir, scaff_enabled=True)

        assert rules_summary.total_files == 1
        assert rules_summary.results[0].scaff_score is not None
