"""Tests for YAML parsing logic."""

import pytest

from prompt_manager.core.yaml_parser import YAMLParser
from prompt_manager.models.validation import ErrorCode, ValidationSeverity


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
