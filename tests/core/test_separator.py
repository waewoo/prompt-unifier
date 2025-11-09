"""Tests for separator validation logic."""

import pytest

from prompt_manager.core.separator import SeparatorValidator
from prompt_manager.models.validation import ErrorCode, ValidationSeverity


class TestSeparatorValidator:
    """Tests for SeparatorValidator class."""

    @pytest.fixture
    def validator(self) -> SeparatorValidator:
        """Create a SeparatorValidator instance."""
        return SeparatorValidator()

    def test_single_valid_separator_detection(self, validator: SeparatorValidator) -> None:
        """Test that a single valid separator is detected correctly."""
        content = "name: test\ndescription: A test\n>>>\nThis is the prompt content."

        frontmatter, prompt_content, issues = validator.validate_separator(content)

        assert frontmatter == "name: test\ndescription: A test"
        assert prompt_content == "This is the prompt content."
        assert len(issues) == 0

    def test_no_separator_error(self, validator: SeparatorValidator) -> None:
        """Test that missing separator generates NO_SEPARATOR error."""
        content = "name: test\ndescription: A test\nThis is content without separator."

        frontmatter, prompt_content, issues = validator.validate_separator(content)

        assert len(issues) == 1
        assert issues[0].code == ErrorCode.NO_SEPARATOR.value
        assert issues[0].severity == ValidationSeverity.ERROR
        assert "No '>>>' separator found" in issues[0].message
        assert "Add a '>>>' separator" in issues[0].suggestion

    def test_multiple_separators_error(self, validator: SeparatorValidator) -> None:
        """Test that multiple separators generate MULTIPLE_SEPARATORS error."""
        content = "name: test\n>>>\nFirst section\n>>>\nSecond section"

        frontmatter, prompt_content, issues = validator.validate_separator(content)

        assert len(issues) == 1
        assert issues[0].code == ErrorCode.MULTIPLE_SEPARATORS.value
        assert issues[0].severity == ValidationSeverity.ERROR
        assert "Multiple '>>>' separators found" in issues[0].message
        assert "2" in issues[0].message  # Should mention count
        assert issues[0].line is not None  # Should track line number

    def test_separator_with_trailing_content_error(self, validator: SeparatorValidator) -> None:
        """Test that separator with trailing content generates SEPARATOR_NOT_ALONE error."""
        content = "name: test\ndescription: A test\n>>> some text\nContent here"

        frontmatter, prompt_content, issues = validator.validate_separator(content)

        assert len(issues) == 1
        assert issues[0].code == ErrorCode.SEPARATOR_NOT_ALONE.value
        assert issues[0].severity == ValidationSeverity.ERROR
        assert "must be on its own line" in issues[0].message
        assert issues[0].line == 3  # Line number where separator appears

    def test_separator_with_leading_whitespace_error(self, validator: SeparatorValidator) -> None:
        """Test that separator with leading whitespace generates SEPARATOR_WHITESPACE error."""
        content = "name: test\ndescription: A test\n   >>>\nContent here"

        frontmatter, prompt_content, issues = validator.validate_separator(content)

        assert len(issues) == 1
        assert issues[0].code == ErrorCode.SEPARATOR_WHITESPACE.value
        assert issues[0].severity == ValidationSeverity.ERROR
        assert "whitespace" in issues[0].message.lower()
        assert issues[0].line == 3

    def test_separator_with_trailing_whitespace_error(self, validator: SeparatorValidator) -> None:
        """Test that separator with trailing whitespace generates SEPARATOR_WHITESPACE error."""
        content = "name: test\ndescription: A test\n>>>   \nContent here"

        frontmatter, prompt_content, issues = validator.validate_separator(content)

        assert len(issues) == 1
        assert issues[0].code == ErrorCode.SEPARATOR_WHITESPACE.value
        assert issues[0].severity == ValidationSeverity.ERROR
        assert "whitespace" in issues[0].message.lower()

    def test_empty_content_after_separator_error(self, validator: SeparatorValidator) -> None:
        """Test that empty content after separator generates EMPTY_CONTENT error."""
        content = "name: test\ndescription: A test\n>>>\n"

        frontmatter, prompt_content, issues = validator.validate_separator(content)

        assert len(issues) == 1
        assert issues[0].code == ErrorCode.EMPTY_CONTENT.value
        assert issues[0].severity == ValidationSeverity.ERROR
        assert "empty" in issues[0].message.lower()
        assert "content after" in issues[0].message.lower()

    def test_whitespace_only_content_after_separator_error(
        self, validator: SeparatorValidator
    ) -> None:
        """Test that whitespace-only content after separator generates EMPTY_CONTENT error."""
        content = "name: test\ndescription: A test\n>>>\n   \n\t\n  "

        frontmatter, prompt_content, issues = validator.validate_separator(content)

        assert len(issues) == 1
        assert issues[0].code == ErrorCode.EMPTY_CONTENT.value
        assert issues[0].severity == ValidationSeverity.ERROR

    def test_valid_content_after_separator(self, validator: SeparatorValidator) -> None:
        """Test that valid content after separator is accepted."""
        content = "name: test\n>>>\nYou are a helpful assistant.\nProvide clear answers."

        frontmatter, prompt_content, issues = validator.validate_separator(content)

        assert len(issues) == 0
        assert "You are a helpful assistant" in prompt_content
        assert "Provide clear answers" in prompt_content

    def test_separator_line_number_tracking(self, validator: SeparatorValidator) -> None:
        """Test that line numbers are correctly tracked for separator errors."""
        content = "line1\nline2\nline3\n>>> extra\nline5"

        frontmatter, prompt_content, issues = validator.validate_separator(content)

        assert len(issues) == 1
        assert issues[0].line == 4  # Separator is on line 4

    def test_multiple_errors_detected(self, validator: SeparatorValidator) -> None:
        """Test that multiple separators with issues are all detected."""
        content = "name: test\n>>> first\nContent\n>>>\nMore content"

        frontmatter, prompt_content, issues = validator.validate_separator(content)

        # Should detect either SEPARATOR_NOT_ALONE or MULTIPLE_SEPARATORS
        assert len(issues) >= 1
        assert any(
            issue.code in [ErrorCode.SEPARATOR_NOT_ALONE.value, ErrorCode.MULTIPLE_SEPARATORS.value]
            for issue in issues
        )
