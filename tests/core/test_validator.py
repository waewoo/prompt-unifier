"""Tests for the PromptValidator orchestration pipeline."""

from pathlib import Path

import pytest

from prompt_unifier.core.validator import PromptValidator
from prompt_unifier.models.validation import ErrorCode, WarningCode


class TestPromptValidatorOrchestration:
    """Tests for PromptValidator end-to-end validation pipeline."""

    @pytest.fixture
    def validator(self) -> PromptValidator:
        """Create a PromptValidator instance."""
        return PromptValidator()

    def test_valid_minimal_prompt_passes(self, validator: PromptValidator, tmp_path: Path) -> None:
        """Test that a valid minimal prompt (name, description only) passes validation."""
        test_file = tmp_path / "minimal.md"
        content = """---
title: code-reviewer
description: Reviews code for best practices
---

You are a code reviewer focused on identifying bugs and improvements."""
        test_file.write_text(content, encoding="utf-8")

        result = validator.validate_file(test_file)

        assert result.file == test_file
        assert result.status == "passed"
        assert len(result.errors) == 0
        assert result.is_valid is True
        # May have warnings for missing optional fields
        # We'll allow either warnings or no warnings

    def test_valid_full_prompt_passes_with_warnings(
        self, validator: PromptValidator, tmp_path: Path
    ) -> None:
        """Test that a valid full prompt with all optional fields passes.

        May generate warnings if version or author is missing in this test,
        but this test uses all fields to show NO warnings scenario.
        """
        test_file = tmp_path / "full.md"
        content = """---
title: python-expert
description: Expert Python developer with focus on clean code
version: 1.0.0
tags:
  - python
  - backend
author: John Doe
---

You are an expert Python developer with deep knowledge of clean code."""
        test_file.write_text(content, encoding="utf-8")

        result = validator.validate_file(test_file)

        assert result.file == test_file
        assert result.status == "passed"
        assert len(result.errors) == 0
        assert result.is_valid is True
        # Should have no warnings since all fields are present
        assert len(result.warnings) == 0

    def test_missing_required_field_generates_error(
        self, validator: PromptValidator, tmp_path: Path
    ) -> None:
        """Test that missing required field generates MISSING_REQUIRED_FIELD error."""
        test_file = tmp_path / "missing_description.md"
        content = """---
title: broken-prompt
---

This will fail validation - missing description."""
        test_file.write_text(content, encoding="utf-8")

        result = validator.validate_file(test_file)

        assert result.file == test_file
        assert result.status == "failed"
        assert len(result.errors) >= 1
        assert result.is_valid is False

        # Check that one error is MISSING_REQUIRED_FIELD for 'description'
        error_codes = [e.code for e in result.errors]
        assert ErrorCode.MISSING_REQUIRED_FIELD.value in error_codes

        # Find the missing field error
        missing_field_errors = [
            e for e in result.errors if e.code == ErrorCode.MISSING_REQUIRED_FIELD.value
        ]
        assert any("description" in e.message.lower() for e in missing_field_errors)

    def test_prohibited_field_generates_error(
        self, validator: PromptValidator, tmp_path: Path
    ) -> None:
        """Test that prohibited field generates PROHIBITED_FIELD error."""
        test_file = tmp_path / "prohibited_tools.md"
        content = """---
title: has-tools
description: Contains prohibited tools field
tools:
  - continue
  - cursor
---

Content here"""
        test_file.write_text(content, encoding="utf-8")

        result = validator.validate_file(test_file)

        assert result.file == test_file
        assert result.status == "failed"
        assert len(result.errors) >= 1
        assert result.is_valid is False

        # Check for PROHIBITED_FIELD error
        error_codes = [e.code for e in result.errors]
        assert ErrorCode.PROHIBITED_FIELD.value in error_codes

        # Verify error mentions 'tools'
        prohibited_errors = [e for e in result.errors if e.code == ErrorCode.PROHIBITED_FIELD.value]
        assert any("tools" in e.message.lower() for e in prohibited_errors)

    def test_invalid_semver_generates_error(
        self, validator: PromptValidator, tmp_path: Path
    ) -> None:
        """Test that invalid semantic version generates INVALID_SEMVER error."""
        test_file = tmp_path / "invalid_semver.md"
        content = """---
title: bad-version
description: Has invalid version format
version: 1.0
---

Content here"""
        test_file.write_text(content, encoding="utf-8")

        result = validator.validate_file(test_file)

        assert result.file == test_file
        assert result.status == "failed"
        assert len(result.errors) >= 1
        assert result.is_valid is False

        # Check for INVALID_SEMVER error
        error_codes = [e.code for e in result.errors]
        assert ErrorCode.INVALID_SEMVER.value in error_codes

    def test_missing_optional_fields_generate_warnings(
        self, validator: PromptValidator, tmp_path: Path
    ) -> None:
        """Test that missing optional fields generate MISSING_OPTIONAL_FIELD warnings."""
        test_file = tmp_path / "no_optional.md"
        content = """---
title: general-assistant
description: General purpose coding assistant
---

You are a helpful coding assistant."""
        test_file.write_text(content, encoding="utf-8")

        result = validator.validate_file(test_file)

        assert result.file == test_file
        assert result.status == "passed"  # Warnings don't cause failure
        assert len(result.errors) == 0
        assert result.is_valid is True

        # Should have warnings for missing 'version' and 'author'
        assert len(result.warnings) >= 1

        warning_codes = [w.code for w in result.warnings]
        assert WarningCode.MISSING_OPTIONAL_FIELD.value in warning_codes

        # Check that warnings mention 'version' or 'author'
        warning_messages = [w.message.lower() for w in result.warnings]
        has_version_warning = any("version" in msg for msg in warning_messages)
        has_author_warning = any("author" in msg for msg in warning_messages)
        assert has_version_warning or has_author_warning

    def test_empty_tags_list_generates_warning(
        self, validator: PromptValidator, tmp_path: Path
    ) -> None:
        """Test that empty tags list generates EMPTY_TAGS_LIST warning."""
        test_file = tmp_path / "empty_tags.md"
        content = """---
title: general-assistant
description: General purpose coding assistant
tags: []
---

You are a helpful coding assistant."""
        test_file.write_text(content, encoding="utf-8")

        result = validator.validate_file(test_file)

        assert result.file == test_file
        assert result.status == "passed"  # Warnings don't cause failure
        assert len(result.errors) == 0
        assert result.is_valid is True

        # Should have warning for empty tags list
        assert len(result.warnings) >= 1

        warning_codes = [w.code for w in result.warnings]
        assert WarningCode.EMPTY_TAGS_LIST.value in warning_codes

    def test_multiple_errors_collected_without_stopping(
        self, validator: PromptValidator, tmp_path: Path
    ) -> None:
        """Test that multiple errors are collected without stopping at first error."""
        test_file = tmp_path / "multiple_errors.md"
        # Missing description, invalid semver, multiple separators
        content = """---
title: broken-prompt
version: invalid
---

First section
---

Second section"""
        test_file.write_text(content, encoding="utf-8")

        result = validator.validate_file(test_file)

        assert result.file == test_file
        assert result.status == "failed"
        assert result.is_valid is False

        # Should have multiple errors collected
        # At minimum: MISSING_REQUIRED_FIELD (description), INVALID_SEMVER, MULTIPLE_SEPARATORS
        assert len(result.errors) >= 2

        error_codes = [e.code for e in result.errors]
        # Should contain at least some of the expected errors
        # (exact combination depends on validation order)
        assert (
            ErrorCode.MISSING_REQUIRED_FIELD.value in error_codes
            or ErrorCode.INVALID_SEMVER.value in error_codes
            or ErrorCode.MULTIPLE_SEPARATORS.value in error_codes
        )


class TestValidationResultAggregation:
    """Tests for ValidationResult status aggregation logic."""

    @pytest.fixture
    def validator(self) -> PromptValidator:
        """Create a PromptValidator instance."""
        return PromptValidator()

    def test_file_with_only_errors_has_failed_status(
        self, validator: PromptValidator, tmp_path: Path
    ) -> None:
        """Test that file with only errors has status='failed'."""
        test_file = tmp_path / "errors_only.md"
        content = """---
title: test
---

Missing description field"""
        test_file.write_text(content, encoding="utf-8")

        result = validator.validate_file(test_file)

        assert result.status == "failed"
        assert len(result.errors) >= 1
        assert result.is_valid is False

    def test_file_with_only_warnings_has_passed_status(
        self, validator: PromptValidator, tmp_path: Path
    ) -> None:
        """Test that file with only warnings has status='passed'."""
        test_file = tmp_path / "warnings_only.md"
        content = """---
title: test
description: A test prompt
tags: []
---

Content here"""
        test_file.write_text(content, encoding="utf-8")

        result = validator.validate_file(test_file)

        assert result.status == "passed"
        assert len(result.errors) == 0
        assert len(result.warnings) >= 1
        assert result.is_valid is True

    def test_file_with_errors_and_warnings_has_failed_status(
        self, validator: PromptValidator, tmp_path: Path
    ) -> None:
        """Test that file with both errors and warnings has status='failed'."""
        test_file = tmp_path / "mixed.md"
        # Missing description (error) and empty tags (warning)
        content = """---
title: test
tags: []
---

Missing description"""
        test_file.write_text(content, encoding="utf-8")

        result = validator.validate_file(test_file)

        assert result.status == "failed"
        assert len(result.errors) >= 1
        assert len(result.warnings) >= 1
        assert result.is_valid is False

    def test_file_with_no_issues_has_passed_status(
        self, validator: PromptValidator, tmp_path: Path
    ) -> None:
        """Test that file with no issues has status='passed'."""
        test_file = tmp_path / "perfect.md"
        content = """---
title: perfect-prompt
description: A perfect prompt with all fields
version: 1.0.0
tags:
  - test
author: Test Author
---

Perfect content here"""
        test_file.write_text(content, encoding="utf-8")

        result = validator.validate_file(test_file)

        assert result.status == "passed"
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
        assert result.is_valid is True

    def test_error_warning_count_aggregation(
        self, validator: PromptValidator, tmp_path: Path
    ) -> None:
        """Test that error and warning counts are properly aggregated."""
        test_file = tmp_path / "counts.md"
        # Multiple warnings: missing version, missing author, empty tags
        content = """---
title: test
description: Test prompt
tags: []
---

Content"""
        test_file.write_text(content, encoding="utf-8")

        result = validator.validate_file(test_file)

        # Count should match length of lists
        assert len(result.errors) == len(list(result.errors))
        assert len(result.warnings) == len(list(result.warnings))

        # Should have warnings for: version, author, empty tags
        assert len(result.warnings) >= 1

    def test_is_valid_property(self, validator: PromptValidator, tmp_path: Path) -> None:
        """Test that is_valid property correctly reflects validation status."""
        # Valid file
        valid_file = tmp_path / "valid.md"
        valid_file.write_text(
            "---\ntitle: test\ndescription: Test\n---\n\nContent", encoding="utf-8"
        )
        valid_result = validator.validate_file(valid_file)

        assert valid_result.is_valid is True
        assert len(valid_result.errors) == 0

        # Invalid file
        invalid_file = tmp_path / "invalid.md"
        invalid_file.write_text("---\ntitle: test\n---\n\nMissing description", encoding="utf-8")
        invalid_result = validator.validate_file(invalid_file)

        assert invalid_result.is_valid is False
        assert len(invalid_result.errors) >= 1
