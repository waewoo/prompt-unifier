"""Unit tests for ContentFileParser."""

from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

import prompt_unifier.models.scaff  # noqa: F401
from prompt_unifier.core.content_parser import ContentFileParser, parse_content_file
from prompt_unifier.models import PromptFrontmatter, RuleFile
from prompt_unifier.models.prompt import PromptFile

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


# Tests supplémentaires pour améliorer la couverture


class TestContentParserAdditionalCoverage:
    """Tests supplémentaires pour ContentFileParser."""

    def test_parse_file_encoding_error(self, tmp_path: Path):
        """Test parse_file avec une erreur d'encodage."""
        parser = ContentFileParser()

        # Créer un fichier avec un encodage invalide
        test_file = tmp_path / "invalid_encoding.md"
        test_file.write_bytes(b"\xff\xfe\x00invalid utf-8")

        with pytest.raises(ValueError, match="encoding validation failed"):
            parser.parse_file(test_file)

    def test_parse_file_separator_validation_failed(self, tmp_path: Path):
        """Test parse_file quand la validation du séparateur échoue."""
        parser = ContentFileParser()

        # Créer un fichier sans séparateur YAML valide
        test_file = tmp_path / "no_separator.md"
        test_file.write_text("Contenu sans frontmatter valide", encoding="utf-8")

        with pytest.raises(ValueError, match="separator validation failed"):
            parser.parse_file(test_file)

    def test_parse_file_invalid_yaml(self, tmp_path: Path):
        """Test parse_file avec du YAML invalide."""
        parser = ContentFileParser()

        # Créer un fichier avec du YAML invalide
        test_file = tmp_path / "invalid_yaml.md"
        test_file.write_text(
            """---
nom: test
  description: test
invalid yaml
---
content""",
            encoding="utf-8",
        )

        with pytest.raises(ValueError, match="invalid yaml"):
            parser.parse_file(test_file)

    def test_parse_file_unknown_content_type(self, tmp_path: Path):
        """Test parse_file avec un type de contenu inconnu."""
        parser = ContentFileParser()

        # Créer un fichier dans un répertoire qui n'est ni prompts ni rules
        test_file = tmp_path / "unknown" / "test.md"
        test_file.parent.mkdir()
        test_file.write_text(
            """---
title: test
description: test
---
content""",
            encoding="utf-8",
        )

        # Forcer le type de contenu à être inconnu
        with patch.object(parser, "_determine_content_type", return_value="unknown"):
            with pytest.raises(ValueError, match="Unknown content type for file"):
                parser.parse_file(test_file)

    def test_parse_file_remove_type_field(self, tmp_path: Path):
        """Test que le champ 'type' est retiré pour la compatibilité descendante."""
        parser = ContentFileParser()

        # Créer un fichier avec un champ 'type'
        test_file = tmp_path / "prompts" / "test.md"
        test_file.parent.mkdir()
        test_file.write_text(
            """---
title: test
description: test
type: prompt
---
content""",
            encoding="utf-8",
        )

        result = parser.parse_file(test_file)
        assert isinstance(result, PromptFile)
        assert result.title == "test"
        # Le champ 'type' devrait avoir été retiré
        assert not hasattr(result, "type")

    def test_validate_file_with_validation_error(self, tmp_path: Path):
        """Test validate_file avec une erreur de validation Pydantic."""
        parser = ContentFileParser()

        # Créer un fichier avec des données qui causeront une erreur de validation
        test_file = tmp_path / "prompts" / "invalid.md"
        test_file.parent.mkdir()
        test_file.write_text(
            """---
title: test
description: test
version: not-a-semver
---
content""",
            encoding="utf-8",
        )

        # validate_file ne lève pas d'exception, il retourne un ValidationResult
        # avec status="failed"
        result = parser.validate_file(test_file)
        assert result.status == "failed"
        assert len(result.errors) > 0
        assert "validation error" in result.errors[0].message.lower()

    def test_validate_file_with_value_error(self, tmp_path: Path):
        """Test validate_file avec une ValueError."""
        parser = ContentFileParser()

        # Créer un fichier sans séparateur valide
        test_file = tmp_path / "invalid.md"
        test_file.write_text("invalid content without proper separators", encoding="utf-8")

        # validate_file ne lève pas d'exception, il retourne un ValidationResult
        # avec status="failed"
        result = parser.validate_file(test_file)
        assert result.status == "failed"
        assert len(result.errors) > 0
        assert "separator validation failed" in result.errors[0].message.lower()

    def test_determine_content_type_rules_directory(self, tmp_path: Path):
        """Test _determine_content_type pour un fichier dans rules/."""
        parser = ContentFileParser()

        test_file = tmp_path / "rules" / "test.md"
        test_file.parent.mkdir()

        content_type = parser._determine_content_type(test_file)
        assert content_type == "rule"

    def test_determine_content_type_prompts_directory(self, tmp_path: Path):
        """Test _determine_content_type pour un fichier dans prompts/."""
        parser = ContentFileParser()

        test_file = tmp_path / "prompts" / "test.md"
        test_file.parent.mkdir()

        content_type = parser._determine_content_type(test_file)
        assert content_type == "prompt"

    def test_determine_content_type_default(self, tmp_path: Path):
        """Test _determine_content_type avec le comportement par défaut."""
        parser = ContentFileParser()

        test_file = tmp_path / "other" / "test.md"
        test_file.parent.mkdir()

        content_type = parser._determine_content_type(test_file)
        assert content_type == "prompt"  # Par défaut

    def test_parse_content_file_convenience_function(self, tmp_path: Path):
        """Test la fonction utilitaire parse_content_file."""
        test_file = tmp_path / "prompts" / "test.md"
        test_file.parent.mkdir()
        test_file.write_text(
            """---
title: test
description: test
---
content""",
            encoding="utf-8",
        )

        result = parse_content_file(test_file)
        assert isinstance(result, PromptFile)
        assert result.title == "test"
        assert result.content == "content"

    def test_parse_content_file_error(self, tmp_path: Path):
        """Test parse_content_file avec une erreur."""
        test_file = tmp_path / "invalid.md"
        test_file.write_text("invalid content", encoding="utf-8")

        with pytest.raises(ValueError, match="separator validation failed"):
            parse_content_file(test_file)

    def test_parse_file_custom_separator(self, tmp_path: Path):
        """Test parse_file avec un séparateur personnalisé."""
        parser = ContentFileParser(separator="+++")

        test_file = tmp_path / "prompts" / "test.md"
        test_file.parent.mkdir()
        test_file.write_text(
            """+++
title: test
description: test
+++
content""",
            encoding="utf-8",
        )

        result = parser.parse_file(test_file)
        assert isinstance(result, PromptFile)
        assert result.title == "test"

    def test_parse_file_complex_frontmatter(self, tmp_path: Path):
        """Test parse_file avec un frontmatter complexe."""
        parser = ContentFileParser()

        test_file = tmp_path / "prompts" / "complex.md"
        test_file.parent.mkdir()
        test_file.write_text(
            """---
title: Complex Prompt
description: A complex prompt with multiple fields
category: testing
version: 1.0.0
tags: ["python", "test"]
author: Test Author
language: en
---
This is the content body
with multiple lines
and special characters: àáâãäåæçèéêë 🚀 🎉
""",
            encoding="utf-8",
        )

        result = parser.parse_file(test_file)
        assert isinstance(result, PromptFile)
        assert result.title == "Complex Prompt"
        assert result.description == "A complex prompt with multiple fields"
        assert result.category == "testing"
        assert result.version == "1.0.0"
        assert result.tags == ["python", "test"]
        assert result.author == "Test Author"
        assert result.language == "en"
        assert "This is the content body" in result.content
        assert "àáâãäåæçèéêë 🚀 🎉" in result.content

    def test_parse_file_minimal_frontmatter(self, tmp_path: Path):
        """Test parse_file avec un frontmatter minimal."""
        parser = ContentFileParser()

        test_file = tmp_path / "prompts" / "minimal.md"
        test_file.parent.mkdir()
        test_file.write_text(
            """---
title: Minimal
description: A minimal prompt
---
Minimal content""",
            encoding="utf-8",
        )

        result = parser.parse_file(test_file)
        assert isinstance(result, PromptFile)
        assert result.title == "Minimal"
        assert result.description == "A minimal prompt"
        assert result.content == "Minimal content"

    def test_parse_file_empty_body(self, tmp_path: Path):
        """Test parse_file avec un corps vide."""
        parser = ContentFileParser()

        test_file = tmp_path / "prompts" / "empty_body.md"
        test_file.parent.mkdir()
        test_file.write_text(
            """---
title: Empty Body
description: A prompt with empty body
---
Some minimal content""",
            encoding="utf-8",
        )

        result = parser.parse_file(test_file)
        assert isinstance(result, PromptFile)
        assert result.title == "Empty Body"
        assert result.description == "A prompt with empty body"
        assert result.content == "Some minimal content"

    def test_parse_file_multiline_body(self, tmp_path: Path):
        """Test parse_file avec un corps multiligne."""
        parser = ContentFileParser()

        test_file = tmp_path / "prompts" / "multiline.md"
        test_file.parent.mkdir()
        test_file.write_text(
            """---
title: Multiline
description: A multiline prompt
---
First line

Second line

Third line""",
            encoding="utf-8",
        )

        result = parser.parse_file(test_file)
        assert isinstance(result, PromptFile)
        assert result.title == "Multiline"
        assert result.description == "A multiline prompt"
        assert "First line" in result.content
        assert "Second line" in result.content
        assert "Third line" in result.content

    def test_parse_file_special_characters_in_content(self, tmp_path: Path):
        """Test parse_file avec des caractères spéciaux dans le contenu."""
        parser = ContentFileParser()

        test_file = tmp_path / "prompts" / "special_chars.md"
        test_file.parent.mkdir()
        test_file.write_text(
            """---
title: Special Characters
description: Prompt with unicode characters
---
Content with special characters: àáâãäåæçèéêë 🚀 🎉 💻
And some code:
```python
def hello():
    print("Hello, world!")
```
""",
            encoding="utf-8",
        )

        result = parser.parse_file(test_file)
        assert isinstance(result, PromptFile)
        assert result.title == "Special Characters"
        assert result.description == "Prompt with unicode characters"
        assert "àáâãäåæçèéêë 🚀 🎉 💻" in result.content
        assert "```python" in result.content
        assert 'print("Hello, world!")' in result.content

    def test_parse_file_frontmatter_with_quotes(self, tmp_path: Path):
        """Test parse_file avec des guillemets dans le frontmatter."""
        parser = ContentFileParser()

        test_file = tmp_path / "prompts" / "quotes.md"
        test_file.parent.mkdir()
        test_file.write_text(
            """---
title: "Prompt with quotes"
description: 'Description with "quotes"'
tags: ["tag with spaces", 'single quoted']
---
Content""",
            encoding="utf-8",
        )

        result = parser.parse_file(test_file)
        assert isinstance(result, PromptFile)
        assert result.title == "Prompt with quotes"
        assert result.description == 'Description with "quotes"'
        assert result.tags == ["tag with spaces", "single quoted"]

    def test_parse_file_nested_paths(self, tmp_path: Path):
        """Test parse_file avec des chemins imbriqués."""
        parser = ContentFileParser()

        # Test avec un chemin très imbriqué
        test_file = tmp_path / "very" / "deeply" / "nested" / "path" / "prompts" / "test.md"
        test_file.parent.mkdir(parents=True)
        test_file.write_text(
            """---
title: Nested Path
description: A deeply nested prompt
---
Content""",
            encoding="utf-8",
        )

        result = parser.parse_file(test_file)
        assert isinstance(result, PromptFile)
        assert result.title == "Nested Path"
        assert result.description == "A deeply nested prompt"

    def test_parse_file_rule_with_applies_to(self, tmp_path: Path):
        """Test parse_file pour une règle avec applies_to."""
        parser = ContentFileParser()

        test_file = tmp_path / "rules" / "python_rule.md"
        test_file.parent.mkdir(parents=True)
        test_file.write_text(
            """---
title: Python Rule
description: Rule for Python files
category: coding-standards
applies_to: ["*.py", "*.pyx"]
---
This rule applies to Python files""",
            encoding="utf-8",
        )

        result = parser.parse_file(test_file)
        assert isinstance(result, RuleFile)
        assert result.title == "Python Rule"
        assert result.applies_to == ["*.py", "*.pyx"]

    def test_validate_file_success(self, tmp_path: Path):
        """Test validate_file with valid prompt returns passed status."""
        parser = ContentFileParser()

        test_file = tmp_path / "prompts" / "valid.md"
        test_file.parent.mkdir(parents=True)
        test_file.write_text(
            """---
title: Valid Prompt
description: A valid prompt for testing
---
This is valid content.""",
            encoding="utf-8",
        )

        result = parser.validate_file(test_file)
        assert result.status == "passed"
        assert len(result.errors) == 0
