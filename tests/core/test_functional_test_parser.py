"""Tests for functional test YAML parser.

This module tests the FunctionalTestParser class for parsing
.test.yaml files containing functional test scenarios.
"""

from pathlib import Path
from textwrap import dedent

from prompt_unifier.core.functional_test_parser import FunctionalTestParser
from prompt_unifier.models.functional_test import FunctionalTestFile


class TestFunctionalTestParser:
    """Tests for FunctionalTestParser class."""

    def test_get_test_file_path_convention(self) -> None:
        """Test that test file path follows .test.yaml convention."""
        source_file = Path("prompts/refactor.md")
        test_file_path = FunctionalTestParser.get_test_file_path(source_file)
        assert test_file_path == Path("prompts/refactor.md.test.yaml")

    def test_get_test_file_path_preserves_extension(self) -> None:
        """Test that original extension is preserved in test file name."""
        source_file = Path("docs/guide.txt")
        test_file_path = FunctionalTestParser.get_test_file_path(source_file)
        assert test_file_path == Path("docs/guide.txt.test.yaml")

    def test_parse_valid_minimal_yaml(self, tmp_path: Path) -> None:
        """Test parsing valid minimal YAML test file."""
        test_file = tmp_path / "test.md.test.yaml"
        test_file.write_text(
            dedent(
                """
                provider: "gpt-4o"
                scenarios:
                  - description: "Test scenario"
                    input: "test input"
                    expect:
                      - type: contains
                        value: "expected"
                """
            )
        )

        parser = FunctionalTestParser(test_file)
        result = parser.parse()

        assert result is not None
        assert isinstance(result, FunctionalTestFile)
        assert len(result.scenarios) == 1
        assert result.scenarios[0].description == "Test scenario"

    def test_parse_valid_yaml_with_provider_and_iterations(self, tmp_path: Path) -> None:
        """Test parsing YAML with optional provider and iterations fields."""
        test_file = tmp_path / "test.md.test.yaml"
        test_file.write_text(
            dedent(
                """
                provider: openai:gpt-4o
                iterations: 3
                scenarios:
                  - description: "Test 1"
                    input: "input text"
                    expect:
                      - type: contains
                        value: "output"
                """
            )
        )

        parser = FunctionalTestParser(test_file)
        result = parser.parse()

        assert result is not None
        assert result.provider == "openai:gpt-4o"
        assert result.iterations == 3

    def test_parse_multiline_input_with_pipe_syntax(self, tmp_path: Path) -> None:
        """Test parsing multi-line input using YAML | syntax."""
        test_file = tmp_path / "test.md.test.yaml"
        test_file.write_text(
            dedent(
                """
                provider: "gpt-4o"
                scenarios:
                  - description: "Multiline test"
                    input: |
                      Line 1
                      Line 2
                      Line 3
                    expect:
                      - type: contains
                        value: "Line"
                """
            )
        )

        parser = FunctionalTestParser(test_file)
        result = parser.parse()

        assert result is not None
        assert "Line 1" in result.scenarios[0].input
        assert "Line 2" in result.scenarios[0].input
        assert "\n" in result.scenarios[0].input

    def test_parse_missing_file_returns_none(self, tmp_path: Path) -> None:
        """Test that parser returns None for missing file."""
        non_existent = tmp_path / "missing.test.yaml"
        parser = FunctionalTestParser(non_existent)
        result = parser.parse()

        assert result is None

    def test_parse_invalid_yaml_syntax_returns_none(self, tmp_path: Path) -> None:
        """Test that invalid YAML syntax returns None with warning."""
        test_file = tmp_path / "invalid.test.yaml"
        test_file.write_text("scenarios:\n  - description: 'Unclosed quote")

        parser = FunctionalTestParser(test_file)
        result = parser.parse()

        assert result is None

    def test_parse_multiple_scenarios(self, tmp_path: Path) -> None:
        """Test parsing file with multiple test scenarios."""
        test_file = tmp_path / "multi.test.yaml"
        test_file.write_text(
            dedent(
                """
                provider: "gpt-4o"
                scenarios:
                  - description: "Test 1"
                    input: "input 1"
                    expect:
                      - type: contains
                        value: "output 1"
                  - description: "Test 2"
                    input: "input 2"
                    expect:
                      - type: regex
                        value: "\\\\w+"
                  - description: "Test 3"
                    input: "input 3"
                    expect:
                      - type: max-length
                        value: 100
                """
            )
        )

        parser = FunctionalTestParser(test_file)
        result = parser.parse()

        assert result is not None
        assert len(result.scenarios) == 3
        assert result.scenarios[0].description == "Test 1"
        assert result.scenarios[1].description == "Test 2"
        assert result.scenarios[2].description == "Test 3"

    def test_parse_scenario_with_case_insensitive_option(self, tmp_path: Path) -> None:
        """Test parsing assertions with case_sensitive option."""
        test_file = tmp_path / "case.test.yaml"
        test_file.write_text(
            dedent(
                """
                provider: "gpt-4o"
                scenarios:
                  - description: "Case insensitive test"
                    input: "Test Input"
                    expect:
                      - type: contains
                        value: "test"
                        case_sensitive: false
                """
            )
        )

        parser = FunctionalTestParser(test_file)
        result = parser.parse()

        assert result is not None
        assert result.scenarios[0].expect[0].case_sensitive is False

    def test_parse_empty_yaml_returns_none(self, tmp_path: Path) -> None:
        """Test that empty YAML file returns None with warning."""
        test_file = tmp_path / "empty.test.yaml"
        test_file.write_text("")

        parser = FunctionalTestParser(test_file)
        result = parser.parse()

        assert result is None

    def test_parse_yaml_with_only_comments_returns_none(self, tmp_path: Path) -> None:
        """Test that YAML file with only comments returns None."""
        test_file = tmp_path / "comments.test.yaml"
        test_file.write_text("# This is a comment\n# Another comment\n")

        parser = FunctionalTestParser(test_file)
        result = parser.parse()

        assert result is None

    def test_parse_validation_error_returns_none(self, tmp_path: Path) -> None:
        """Test that ValidationError during model creation returns None."""
        test_file = tmp_path / "invalid_model.test.yaml"
        # Missing required 'description' field in scenario
        test_file.write_text(
            dedent(
                """
                provider: "gpt-4o"
                scenarios:
                  - input: "test input"
                    expect:
                      - type: contains
                        value: "text"
                """
            )
        )

        parser = FunctionalTestParser(test_file)
        result = parser.parse()

        assert result is None

    def test_parse_unexpected_exception_returns_none(self, tmp_path: Path) -> None:
        """Test that unexpected exceptions during parsing return None."""
        test_file = tmp_path / "invalid_structure.test.yaml"
        # Invalid structure that will cause validation issues
        test_file.write_text(
            dedent(
                """
                provider: "gpt-4o"
                scenarios: "not a list"
                """
            )
        )

        parser = FunctionalTestParser(test_file)
        result = parser.parse()

        assert result is None

    def test_parse_yaml_load_exception_returns_none(self, tmp_path: Path) -> None:
        """Test that YAML load exceptions return None with warning."""
        from unittest.mock import patch

        test_file = tmp_path / "exception.test.yaml"
        test_file.write_text(
            dedent(
                """
                provider: "gpt-4o"
                scenarios:
                  - description: "Test"
                    input: "test"
                    expect:
                      - type: contains
                        value: "text"
                """
            )
        )

        # Mock yaml.safe_load to raise a generic Exception
        with patch("yaml.safe_load", side_effect=Exception("Unexpected YAML error")):
            parser = FunctionalTestParser(test_file)
            result = parser.parse()

        assert result is None
