"""Unit tests for ContentFileParser."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from prompt_manager.core.content_parser import ContentFileParser, parse_content_file
from prompt_manager.models import PromptFrontmatter, RuleFile

# Fixture paths
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
RULES_DIR = FIXTURES_DIR / "rules"
PROMPTS_DIR = FIXTURES_DIR / "prompts"


class TestContentFileParserRules:
    """Test parsing rule files."""

    def test_parse_valid_rule_file(self):
        """Test parsing a valid rule file returns RuleFile instance."""
        parser = ContentFileParser()
        rule_path = RULES_DIR / "python-style.md"

        result = parser.parse_file(rule_path)

        assert isinstance(result, RuleFile)
        assert result.title == "python-style-guide"
        assert result.category == "coding-standards"
        assert "python" in result.tags
        assert result.version == "1.0.0"
        assert len(result.content) > 0
        assert "# Python Style Guide" in result.content

    def test_parse_rule_with_applies_to(self):
        """Test parsing rule with applies_to field."""
        parser = ContentFileParser()
        rule_path = RULES_DIR / "api-design.md"

        result = parser.parse_file(rule_path)

        assert isinstance(result, RuleFile)
        assert result.title == "api-design-patterns"
        assert result.category == "architecture"
        assert result.applies_to == ["python", "fastapi", "flask"]
        assert result.version == "1.2.0"

    def test_parse_invalid_rule_missing_category(self):
        """Test that rule without category raises ValidationError."""
        parser = ContentFileParser()
        rule_path = RULES_DIR / "invalid-missing-category.md"

        with pytest.raises(ValidationError) as exc_info:
            parser.parse_file(rule_path)

        assert "category" in str(exc_info.value).lower()


class TestContentFileParserPrompts:
    """Test parsing prompt files."""

    def test_parse_prompt_without_type_field(self):
        """Test that file without type field defaults to prompt."""
        parser = ContentFileParser()
        prompt_path = PROMPTS_DIR / "code-review.md"

        result = parser.parse_file(prompt_path)

        assert isinstance(result, PromptFrontmatter)
        assert result.title == "code-review"
        assert result.description == "Review code for bugs and improvements"
        assert "python" in result.tags
        assert result.version == "1.0.0"

    def test_parse_prompt_without_rules_in_path(self):
        """Test parsing prompt file (no 'rules' in path)."""
        parser = ContentFileParser()

        # Create temporary prompt file (path doesn't contain 'rules')
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(
                """---
title: test-prompt
description: Test prompt
---

Test content"""
            )
            temp_path = Path(f.name)

        try:
            result = parser.parse_file(temp_path)

            assert isinstance(result, PromptFrontmatter)
            assert result.title == "test-prompt"
        finally:
            temp_path.unlink()


class TestContentFileParserTypeDetection:
    """Test automatic type detection."""

    def test_detects_rule_from_path(self):
        """Test that files in 'rules/' directory are detected as rules."""
        parser = ContentFileParser()
        rule_path = RULES_DIR / "python-style.md"

        result = parser.parse_file(rule_path)

        assert isinstance(result, RuleFile)

    def test_defaults_to_prompt_without_rules_in_path(self):
        """Test that files not in 'rules/' directory are treated as prompts."""
        parser = ContentFileParser()
        prompt_path = PROMPTS_DIR / "code-review.md"

        result = parser.parse_file(prompt_path)

        assert isinstance(result, PromptFrontmatter)

    def test_ignores_type_field_for_backward_compatibility(self):
        """Test that 'type' field is ignored if present (backward compatibility)."""
        parser = ContentFileParser()

        import tempfile

        # Create a file with 'type' field but not in 'rules/' directory
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(
                """---
title: test
description: Test
type: rule
category: testing
---

Content"""
            )
            temp_path = Path(f.name)

        try:
            # Should be treated as prompt because path doesn't contain 'rules'
            result = parser.parse_file(temp_path)
            assert isinstance(result, PromptFrontmatter)
        finally:
            temp_path.unlink()


class TestContentFileParserErrors:
    """Test error handling."""

    def test_invalid_encoding_raises_error(self):
        """Test that invalid encoding raises ValueError."""
        parser = ContentFileParser()

        import tempfile

        # Create file with invalid UTF-8
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".md", delete=False) as f:
            f.write(b"\xff\xfe invalid utf-8")
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError) as exc_info:
                parser.parse_file(temp_path)

            assert "encoding validation failed" in str(exc_info.value).lower()
        finally:
            temp_path.unlink()

    def test_missing_separator_raises_error(self):
        """Test that missing separator raises ValueError."""
        parser = ContentFileParser()

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(
                """---
title: test
description: Test
category: testing
No closing delimiter, just content"""
            )
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError) as exc_info:
                parser.parse_file(temp_path)

            assert "separator validation failed" in str(exc_info.value).lower()
        finally:
            temp_path.unlink()

    def test_invalid_yaml_raises_error(self):
        """Test that invalid YAML raises ValueError."""
        parser = ContentFileParser()

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(
                """---
title: test
description: [invalid yaml structure
---

Content"""
            )
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError) as exc_info:
                parser.parse_file(temp_path)

            assert "invalid yaml" in str(exc_info.value).lower()
        finally:
            temp_path.unlink()


class TestParseContentFileFunction:
    """Test convenience function parse_content_file()."""

    def test_parse_content_file_rule(self):
        """Test parse_content_file() convenience function with rule."""
        rule_path = RULES_DIR / "python-style.md"

        result = parse_content_file(rule_path)

        assert isinstance(result, RuleFile)
        assert result.title == "python-style-guide"

    def test_parse_content_file_prompt(self):
        """Test parse_content_file() convenience function with prompt."""
        prompt_path = PROMPTS_DIR / "code-review.md"

        result = parse_content_file(prompt_path)

        assert isinstance(result, PromptFrontmatter)
        assert result.title == "code-review"


class TestContentFileParserBackwardCompatibility:
    """Test backward compatibility with existing prompt files."""

    def test_existing_prompts_still_parse(self):
        """Test that existing prompt files without type field still work."""
        parser = ContentFileParser()
        prompt_path = PROMPTS_DIR / "code-review.md"

        # Should not raise any errors
        result = parser.parse_file(prompt_path)

        # Should be recognized as prompt
        assert isinstance(result, PromptFrontmatter)
        assert result.title == "code-review"

    def test_prompt_behavior_unchanged(self):
        """Test that prompt parsing behavior is unchanged."""
        parser = ContentFileParser()
        prompt_path = PROMPTS_DIR / "code-review.md"

        result = parser.parse_file(prompt_path)

        # All expected fields should be present
        assert result.title == "code-review"
        assert result.description == "Review code for bugs and improvements"
        assert result.version == "1.0.0"
        assert result.tags == ["python", "review"]
        assert result.author == "test-user"
