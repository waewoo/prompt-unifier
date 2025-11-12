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

    def test_valid_frontmatter_format(self, validator: SeparatorValidator) -> None:
        """Test that valid YAML frontmatter format is accepted."""
        content = "---\ntitle: test\ndescription: A test\n---\nThis is the content."

        frontmatter, content_text, issues = validator.validate_separator(content)

        assert frontmatter == "title: test\ndescription: A test"
        assert content_text == "This is the content."
        assert len(issues) == 0

    def test_opening_delimiter_missing_error(self, validator: SeparatorValidator) -> None:
        """Test that missing opening delimiter generates error."""
        content = "title: test\ndescription: A test\n---\nContent"

        frontmatter, content_text, issues = validator.validate_separator(content)

        assert len(issues) == 1
        assert issues[0].code == ErrorCode.NO_SEPARATOR.value
        assert issues[0].severity == ValidationSeverity.ERROR
        assert "must start with '---'" in issues[0].message
        assert issues[0].line == 1

    def test_closing_delimiter_missing_error(self, validator: SeparatorValidator) -> None:
        """Test that missing closing delimiter generates error."""
        content = "---\ntitle: test\ndescription: A test\nNo closing delimiter"

        frontmatter, content_text, issues = validator.validate_separator(content)

        assert len(issues) == 1
        assert issues[0].code == ErrorCode.NO_SEPARATOR.value
        assert issues[0].severity == ValidationSeverity.ERROR
        assert "No closing '---' delimiter found" in issues[0].message

    def test_empty_frontmatter_error(self, validator: SeparatorValidator) -> None:
        """Test that empty frontmatter generates EMPTY_CONTENT error."""
        content = "---\n---\nContent here"

        frontmatter, content_text, issues = validator.validate_separator(content)

        assert len(issues) == 1
        assert issues[0].code == ErrorCode.EMPTY_CONTENT.value
        assert issues[0].severity == ValidationSeverity.ERROR
        assert "frontmatter is empty" in issues[0].message
        assert issues[0].line == 2

    def test_empty_content_after_closing_delimiter_error(
        self, validator: SeparatorValidator
    ) -> None:
        """Test that empty content after closing delimiter generates error."""
        content = "---\ntitle: test\n---\n"

        frontmatter, content_text, issues = validator.validate_separator(content)

        assert len(issues) == 1
        assert issues[0].code == ErrorCode.EMPTY_CONTENT.value
        assert issues[0].severity == ValidationSeverity.ERROR
        assert "Content after frontmatter is empty" in issues[0].message

    def test_whitespace_only_content_after_delimiter_error(
        self, validator: SeparatorValidator
    ) -> None:
        """Test that whitespace-only content after delimiter generates error."""
        content = "---\ntitle: test\n---\n   \n\t\n  "

        frontmatter, content_text, issues = validator.validate_separator(content)

        assert len(issues) == 1
        assert issues[0].code == ErrorCode.EMPTY_CONTENT.value
        assert issues[0].severity == ValidationSeverity.ERROR

    def test_valid_content_with_delimiters(self, validator: SeparatorValidator) -> None:
        """Test that valid content with proper delimiters is accepted."""
        content = "---\ntitle: test\n---\nYou are a helpful assistant.\nProvide clear answers."

        frontmatter, content_text, issues = validator.validate_separator(content)

        assert len(issues) == 0
        assert "You are a helpful assistant" in content_text
        assert "Provide clear answers" in content_text

    def test_delimiter_with_whitespace_accepted(self, validator: SeparatorValidator) -> None:
        """Test that delimiters with leading/trailing whitespace are accepted (stripped)."""
        content = "  ---  \ntitle: test\n  ---  \nContent here"

        frontmatter, content_text, issues = validator.validate_separator(content)

        assert len(issues) == 0
        assert frontmatter == "title: test"
        assert content_text == "Content here"

    def test_empty_file_error(self, validator: SeparatorValidator) -> None:
        """Test that empty file generates appropriate error."""
        content = ""

        frontmatter, content_text, issues = validator.validate_separator(content)

        assert len(issues) == 1
        assert issues[0].code == ErrorCode.NO_SEPARATOR.value
        assert issues[0].severity == ValidationSeverity.ERROR
        # Empty string splits to [""], so it's treated as missing opening delimiter
        assert "must start with '---'" in issues[0].message

    def test_multiline_frontmatter_and_content(self, validator: SeparatorValidator) -> None:
        """Test parsing with multiline frontmatter and content."""
        content = """---
title: Python Style Guide
description: Python coding standards
category: coding-standards
tags: [python, pep8]
version: 1.0.0
---

# Python Style Guide

This is the main content with multiple lines.
It can have various markdown formatting."""

        frontmatter, content_text, issues = validator.validate_separator(content)

        assert len(issues) == 0
        assert "title: Python Style Guide" in frontmatter
        assert "tags: [python, pep8]" in frontmatter
        assert "# Python Style Guide" in content_text
        assert "multiple lines" in content_text
