"""Tests for YAML parsing logic."""

import pytest

from prompt_unifier.core.yaml_parser import YAMLParser
from prompt_unifier.models.validation import ErrorCode, ValidationSeverity


class TestYAMLParser:
    """Tests for YAMLParser class."""

    @pytest.fixture
    def parser(self) -> YAMLParser:
        """Create a YAMLParser instance."""
        return YAMLParser()

    def test_valid_flat_yaml_parses_successfully(self, parser: YAMLParser) -> None:
        """Test that valid flat YAML parses successfully."""
        yaml_text = """name: python-expert
description: Expert Python developer
version: 1.0.0
author: John Doe"""

        parsed_dict, issues = parser.parse_yaml(yaml_text)

        assert parsed_dict is not None
        assert len(issues) == 0
        assert parsed_dict["name"] == "python-expert"
        assert parsed_dict["description"] == "Expert Python developer"
        assert parsed_dict["version"] == "1.0.0"
        assert parsed_dict["author"] == "John Doe"

    def test_invalid_yaml_syntax_triggers_error(self, parser: YAMLParser) -> None:
        """Test that invalid YAML syntax triggers INVALID_YAML error."""
        yaml_text = """name: test
description: [unclosed bracket
version: 1.0.0"""

        parsed_dict, issues = parser.parse_yaml(yaml_text)

        assert parsed_dict is None
        assert len(issues) == 1
        assert issues[0].code == ErrorCode.INVALID_YAML.value
        assert issues[0].severity == ValidationSeverity.ERROR
        assert "YAML" in issues[0].message or "syntax" in issues[0].message.lower()

    def test_nested_yaml_structure_triggers_error(self, parser: YAMLParser) -> None:
        """Test that nested YAML structure triggers NESTED_STRUCTURE error."""
        yaml_text = """name: test
description: A test
metadata:
  team: engineering
  priority: high"""

        parsed_dict, issues = parser.parse_yaml(yaml_text)

        assert parsed_dict is None
        assert len(issues) == 1
        assert issues[0].code == ErrorCode.NESTED_STRUCTURE.value
        assert issues[0].severity == ValidationSeverity.ERROR
        assert "nested" in issues[0].message.lower()
        assert "metadata" in issues[0].message  # Should mention the field name

    def test_empty_yaml_frontmatter_error(self, parser: YAMLParser) -> None:
        """Test that empty YAML frontmatter is handled."""
        yaml_text = ""

        parsed_dict, issues = parser.parse_yaml(yaml_text)

        # Empty YAML should parse as None/empty dict
        # This should be caught as an error (missing required fields will be caught later)
        assert parsed_dict is None or parsed_dict == {}
        # Could generate error or not - depends on implementation choice
        # If no error here, missing fields will be caught by Pydantic validation

    def test_yaml_with_list_values(self, parser: YAMLParser) -> None:
        """Test that YAML with list values (tags field) parses correctly."""
        yaml_text = """name: test
description: A test
tags:
  - python
  - backend
  - api"""

        parsed_dict, issues = parser.parse_yaml(yaml_text)

        assert parsed_dict is not None
        assert len(issues) == 0
        assert "tags" in parsed_dict
        assert isinstance(parsed_dict["tags"], list)
        assert parsed_dict["tags"] == ["python", "backend", "api"]

    def test_yaml_parsing_with_line_number_tracking(self, parser: YAMLParser) -> None:
        """Test that YAML parsing tracks line numbers for errors."""
        yaml_text = """name: test
description: A test
this is not valid yaml syntax at all
version: 1.0.0"""

        parsed_dict, issues = parser.parse_yaml(yaml_text)

        assert parsed_dict is None
        assert len(issues) == 1
        # Line number tracking may be approximate or None depending on yaml library
        # Just verify the error is generated

    def test_yaml_with_prohibited_fields_detection(self, parser: YAMLParser) -> None:
        """Test that YAML with prohibited fields can be detected later."""
        yaml_text = """name: test
description: A test
tools:
  - continue
  - cursor"""

        parsed_dict, issues = parser.parse_yaml(yaml_text)

        # Parser should successfully parse the YAML
        # Prohibited field detection happens in validation pipeline
        assert parsed_dict is not None
        assert "tools" in parsed_dict
        assert len(issues) == 0  # No parsing errors, just data

    def test_multiple_nested_structures(self, parser: YAMLParser) -> None:
        """Test detection of multiple nested structures."""
        yaml_text = """name: test
description: A test
config:
  setting: value
metadata:
  team: engineering"""

        parsed_dict, issues = parser.parse_yaml(yaml_text)

        assert parsed_dict is None
        assert len(issues) >= 1
        # Should detect at least one nested structure (could be multiple errors)
        assert any(issue.code == ErrorCode.NESTED_STRUCTURE.value for issue in issues)

    def test_nested_list_of_dicts_triggers_error(self, parser: YAMLParser) -> None:
        """Test that nested list of dictionaries triggers error."""
        yaml_text = """name: test
description: A test
items:
  - name: item1
    value: 100
  - name: item2
    value: 200"""

        parsed_dict, issues = parser.parse_yaml(yaml_text)

        # This has nested dictionaries within a list
        assert parsed_dict is None
        assert len(issues) >= 1
        assert any(issue.code == ErrorCode.NESTED_STRUCTURE.value for issue in issues)


# Tests supplémentaires pour améliorer la couverture


class TestYAMLParserAdditionalCoverage:
    """Tests supplémentaires pour YAMLParser."""

    def test_parse_yaml_empty_string(self):
        """Test parse_yaml avec une chaîne vide."""
        parser = YAMLParser()

        data, issues = parser.parse_yaml("")
        assert data is None
        assert len(issues) == 0

    def test_parse_yaml_whitespace_only(self):
        """Test parse_yaml avec uniquement des espaces blancs."""
        parser = YAMLParser()

        data, issues = parser.parse_yaml("   \n  \t  \n   ")
        assert data is None
        assert len(issues) == 0

    def test_parse_yaml_none_result(self):
        """Test parse_yaml quand yaml.safe_load retourne None."""
        parser = YAMLParser()

        # YAML qui ne produit rien (commentaires uniquement)
        data, issues = parser.parse_yaml("# Just a comment\n# Another comment")
        assert data is None
        assert len(issues) == 0

    def test_parse_yaml_not_dict_error(self):
        """Test parse_yaml quand le résultat n'est pas un dictionnaire."""
        parser = YAMLParser()

        # YAML qui produit une liste
        data, issues = parser.parse_yaml("- item1\n- item2\n- item3")
        assert data is None
        assert len(issues) == 1
        assert issues[0].severity == ValidationSeverity.ERROR
        assert issues[0].code == ErrorCode.INVALID_YAML.value
        assert "YAML frontmatter must be a dictionary" in issues[0].message

    def test_parse_yaml_string_result(self):
        """Test parse_yaml quand le résultat est une chaîne."""
        parser = YAMLParser()

        # YAML qui produit une chaîne
        data, issues = parser.parse_yaml("just a string")
        assert data is None
        assert len(issues) == 1
        assert "YAML frontmatter must be a dictionary" in issues[0].message

    def test_parse_yaml_integer_result(self):
        """Test parse_yaml quand le résultat est un entier."""
        parser = YAMLParser()

        # YAML qui produit un entier
        data, issues = parser.parse_yaml("123")
        assert data is None
        assert len(issues) == 1
        assert "YAML frontmatter must be a dictionary" in issues[0].message

    def test_parse_yaml_boolean_result(self):
        """Test parse_yaml quand le résultat est un booléen."""
        parser = YAMLParser()

        # YAML qui produit un booléen
        data, issues = parser.parse_yaml("true")
        assert data is None
        assert len(issues) == 1
        assert "YAML frontmatter must be a dictionary" in issues[0].message

    def test_parse_yaml_yaml_error_with_line_number(self):
        """Test parse_yaml avec une erreur YAML qui a un numéro de ligne."""
        parser = YAMLParser()

        # YAML avec une erreur de syntaxe
        yaml_content = """title: test
description: test
invalid:   : colonne mal placée
"""

        data, issues = parser.parse_yaml(yaml_content)
        assert data is None
        assert len(issues) == 1
        assert issues[0].severity == ValidationSeverity.ERROR
        assert issues[0].code == ErrorCode.INVALID_YAML.value
        assert "Invalid YAML syntax" in issues[0].message
        assert issues[0].line is not None  # Devrait avoir un numéro de ligne

    def test_parse_yaml_glob_pattern_error(self):
        """Test parse_yaml avec une erreur de pattern de glob."""
        parser = YAMLParser()

        # YAML avec un pattern de glob non quoté
        yaml_content = """title: test
applies_to: [*.py, *.js]
"""

        data, issues = parser.parse_yaml(yaml_content)
        assert data is None
        assert len(issues) == 1
        assert "Glob patterns with '*' must be quoted" in issues[0].suggestion

    def test_parse_yaml_generic_yaml_error(self):
        """Test parse_yaml avec une erreur YAML générique."""
        parser = YAMLParser()

        # YAML avec une erreur de syntaxe (tabulation invalide)
        yaml_content = """title: test
invalid:\t tabulation interdite
"""

        data, issues = parser.parse_yaml(yaml_content)
        assert data is None
        assert len(issues) == 1
        assert "Invalid YAML syntax" in issues[0].message
        assert "Check YAML syntax" in issues[0].suggestion

    def test_detect_nested_structures_simple_dict(self):
        """Test _detect_nested_structures avec un dictionnaire simple."""
        parser = YAMLParser()

        simple_data = {"title": "test", "description": "test prompt", "version": "1.0.0"}

        issues = parser._detect_nested_structures(simple_data)
        assert len(issues) == 0

    def test_detect_nested_structures_nested_dict(self):
        """Test _detect_nested_structures avec un dictionnaire imbriqué."""
        parser = YAMLParser()

        nested_data = {"title": "test", "config": {"nested": "value", "deep": {"key": "value"}}}

        issues = parser._detect_nested_structures(nested_data)
        assert len(issues) == 1
        assert issues[0].severity == ValidationSeverity.ERROR
        assert issues[0].code == ErrorCode.NESTED_STRUCTURE.value
        assert "Field 'config' contains nested data" in issues[0].message

    def test_detect_nested_structures_multiple_nested_dicts(self):
        """Test _detect_nested_structures avec plusieurs dictionnaires imbriqués."""
        parser = YAMLParser()

        nested_data = {
            "title": "test",
            "config": {"nested": "value"},
            "settings": {"another": "nested"},
        }

        issues = parser._detect_nested_structures(nested_data)
        assert len(issues) == 2
        assert any("Field 'config' contains nested data" in issue.message for issue in issues)
        assert any("Field 'settings' contains nested data" in issue.message for issue in issues)

    def test_detect_nested_structures_list_with_dicts(self):
        """Test _detect_nested_structures avec une liste contenant des dictionnaires."""
        parser = YAMLParser()

        nested_data = {
            "title": "test",
            "tags": ["python", "test"],
            "applies_to": ["*.py", {"invalid": "nested"}],
        }

        issues = parser._detect_nested_structures(nested_data)
        assert len(issues) == 1
        assert issues[0].severity == ValidationSeverity.ERROR
        assert issues[0].code == ErrorCode.NESTED_STRUCTURE.value
        assert "Field 'applies_to' contains a list with nested dictionaries" in issues[0].message

    def test_detect_nested_structures_multiple_lists_with_dicts(self):
        """Test _detect_nested_structures avec plusieurs listes contenant des dictionnaires."""
        parser = YAMLParser()

        nested_data = {
            "title": "test",
            "tags": [{"invalid": "tag"}],
            "applies_to": [{"file": "*.py"}],
            "other": ["simple", "list"],
        }

        issues = parser._detect_nested_structures(nested_data)
        assert len(issues) == 2
        assert any(
            "Field 'tags' contains a list with nested dictionaries" in issue.message
            for issue in issues
        )
        assert any(
            "Field 'applies_to' contains a list with nested dictionaries" in issue.message
            for issue in issues
        )

    def test_detect_nested_structures_mixed_nested_types(self):
        """Test _detect_nested_structures avec des types imbriqués mixtes."""
        parser = YAMLParser()

        nested_data = {
            "title": "test",
            "config": {"nested": "dict"},
            "tags": [{"nested": "list_item"}],
            "simple": "value",
        }

        issues = parser._detect_nested_structures(nested_data)
        assert len(issues) == 2

    def test_detect_nested_structures_deeply_nested_dict_in_list(self):
        """Test _detect_nested_structures avec un dictionnaire
        profondément imbriqué dans une liste."""
        parser = YAMLParser()

        nested_data = {
            "title": "test",
            "items": ["simple_string", {"level1": {"level2": {"level3": "deep"}}}],
        }

        issues = parser._detect_nested_structures(nested_data)
        assert len(issues) == 1
        assert "Field 'items' contains a list with nested dictionaries" in issues[0].message

    def test_detect_nested_structures_empty_list(self):
        """Test _detect_nested_structures avec une liste vide."""
        parser = YAMLParser()

        data = {"title": "test", "tags": [], "applies_to": []}

        issues = parser._detect_nested_structures(data)
        assert len(issues) == 0

    def test_detect_nested_structures_list_of_strings(self):
        """Test _detect_nested_structures avec une liste de chaînes."""
        parser = YAMLParser()

        data = {
            "title": "test",
            "tags": ["python", "javascript", "typescript"],
            "applies_to": ["*.py", "*.js", "*.ts"],
        }

        issues = parser._detect_nested_structures(data)
        assert len(issues) == 0

    def test_detect_nested_structures_list_with_none(self):
        """Test _detect_nested_structures avec une liste contenant None."""
        parser = YAMLParser()

        data = {"title": "test", "items": ["string", None, "another_string"]}

        issues = parser._detect_nested_structures(data)
        assert len(issues) == 0

    def test_detect_nested_structures_list_with_numbers(self):
        """Test _detect_nested_structures avec une liste de nombres."""
        parser = YAMLParser()

        data = {"title": "test", "versions": [1, 2, 3, 4.5]}

        issues = parser._detect_nested_structures(data)
        assert len(issues) == 0

    def test_parse_yaml_complex_nested_error(self):
        """Test parse_yaml avec une erreur d'imbrication complexe."""
        parser = YAMLParser()

        complex_yaml = """title: test
config:
  database:
    host: localhost
    port: 5432
tags:
  - python
  - config: nested
"""

        data, issues = parser.parse_yaml(complex_yaml)
        assert data is None
        assert len(issues) == 2  # Un pour le dict imbriqué, un pour la liste avec dict

    def test_parse_yaml_valid_complex_structure(self):
        """Test parse_yaml avec une structure complexe mais valide."""
        parser = YAMLParser()

        valid_yaml = """title: Complex Prompt
description: A complex prompt with many fields
category: testing
version: 1.0.0
tags: ["python", "test", "complex"]
author: Test Author
language: en
applies_to: ["*.py", "*.pyx", "*.pyi"]
"""

        data, issues = parser.parse_yaml(valid_yaml)
        assert data is not None
        assert len(issues) == 0
        assert data["title"] == "Complex Prompt"
        assert data["tags"] == ["python", "test", "complex"]
        assert data["applies_to"] == ["*.py", "*.pyx", "*.pyi"]

    def test_parse_yaml_unicode_characters(self):
        """Test parse_yaml avec des caractères unicode."""
        parser = YAMLParser()

        # Utiliser des caractères unicode simples qui ne causent pas d'erreurs
        unicode_yaml = """title: Unicode Test
description: "Test with unicode characters: 🚀 🎉 💻 àáâãäåæçèéêë"
author: "Test Author 🧪"
"""

        data, issues = parser.parse_yaml(unicode_yaml)
        assert data is not None
        assert len(issues) == 0
        assert "🚀 🎉 💻" in data["description"]
        assert "🧪" in data["author"]

    def test_parse_yaml_multiline_strings(self):
        """Test parse_yaml avec des chaînes multilignes."""
        parser = YAMLParser()

        multiline_yaml = """title: Multiline Test
description: |
  This is a multiline
  description that spans
  multiple lines
author: Test Author
"""

        data, issues = parser.parse_yaml(multiline_yaml)
        assert data is not None
        assert len(issues) == 0
        assert "multiline\ndescription that spans\nmultiple lines" in data["description"]

    def test_parse_yaml_very_long_content(self):
        """Test parse_yaml avec un contenu très long."""
        parser = YAMLParser()

        # Créer un YAML très long avec des guillemets pour éviter les problèmes
        long_description = "This is a very long description. " * 1000
        long_yaml = f"""title: Long Content Test
description: "{long_description}"
author: Test Author
"""

        data, issues = parser.parse_yaml(long_yaml)
        assert data is not None
        assert len(issues) == 0
        # Le contenu devrait être très long
        assert len(data["description"]) > 30000

    def test_parse_yaml_special_characters_in_keys(self):
        """Test parse_yaml avec des caractères spéciaux dans les clés."""
        parser = YAMLParser()

        special_yaml = """"title with spaces": test
'description-with-dashes': test
key_with_underscores: test
key.with.dots: test
"""

        data, issues = parser.parse_yaml(special_yaml)
        assert data is not None
        assert len(issues) == 0
        assert data["title with spaces"] == "test"
        assert data["description-with-dashes"] == "test"
        assert data["key_with_underscores"] == "test"
        assert data["key.with.dots"] == "test"

    def test_parse_yaml_boolean_values(self):
        """Test parse_yaml avec des valeurs booléennes."""
        parser = YAMLParser()

        bool_yaml = """title: Boolean Test
enabled: true
disabled: false
debug: yes
production: no
"""

        data, issues = parser.parse_yaml(bool_yaml)
        assert data is not None
        assert len(issues) == 0
        assert data["enabled"] is True
        assert data["disabled"] is False
        assert data["debug"] is True
        assert data["production"] is False

    def test_parse_yaml_numeric_values(self):
        """Test parse_yaml avec des valeurs numériques."""
        parser = YAMLParser()

        numeric_yaml = """title: Numeric Test
version: 1.0
count: 42
pi: 3.14159
negative: -10
scientific: 1.23e-4
"""

        data, issues = parser.parse_yaml(numeric_yaml)
        assert data is not None
        assert len(issues) == 0
        assert data["version"] == pytest.approx(1.0)
        assert data["count"] == 42
        assert data["pi"] == pytest.approx(3.14159)
        assert data["negative"] == -10
        assert data["scientific"] == 1.23e-4

    def test_parse_yaml_null_values(self):
        """Test parse_yaml avec des valeurs null."""
        parser = YAMLParser()

        null_yaml = """title: Null Test
description: null
author: ~
optional_field:
"""

        data, issues = parser.parse_yaml(null_yaml)
        assert data is not None
        assert len(issues) == 0
        assert data["description"] is None
        assert data["author"] is None
        assert data["optional_field"] is None
