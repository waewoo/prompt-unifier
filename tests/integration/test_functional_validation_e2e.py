"""End-to-end integration tests for functional validation.

This module tests complete workflows from YAML file → validation → output.
"""

from pathlib import Path
from textwrap import dedent
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from prompt_unifier.cli.main import app
from prompt_unifier.core.functional_test_parser import FunctionalTestParser
from prompt_unifier.core.functional_validator import FunctionalValidator

runner = CliRunner()


@patch("prompt_unifier.ai.executor.AIExecutor.validate_connection")
class TestFunctionalValidationEndToEnd:
    """End-to-end tests for functional validation workflows."""

    @patch("prompt_unifier.ai.executor.AIExecutor.execute_prompt")
    def test_e2e_complete_workflow_with_passing_tests(
        self, mock_execute: MagicMock, mock_validate_conn: MagicMock, tmp_path: Path
    ) -> None:
        """Test complete workflow: file → test.yaml → validation → pass."""
        # Mock AI response with keywords that match assertions
        mock_execute.return_value = "I am a helpful assistant providing detailed accurate responses"

        source_file = tmp_path / "prompt.md"
        source_file.write_text(
            dedent(
                """
                title: Test Prompt
                description: A test prompt
                >>>
                You are a helpful assistant.
                Please provide detailed, accurate responses.
                """
            )
        )

        test_file = tmp_path / "prompt.md.test.yaml"
        test_file.write_text(
            dedent(
                """
                provider: openai:gpt-4o
                iterations: 1
                scenarios:
                  - description: "Check for helpful tone"
                    input: "test"
                    expect:
                      - type: contains
                        value: "helpful"
                      - type: contains
                        value: "assistant"
                  - description: "Check response quality"
                    input: "test"
                    expect:
                      - type: contains
                        value: "detailed"
                      - type: not-contains
                        value: "ERROR"
                      - type: max-length
                        value: 1000
                """
            )
        )

        result = runner.invoke(app, ["test", str(source_file)])

        assert result.exit_code == 0
        assert "PASS" in result.stdout
        assert "2" in result.stdout  # 2 scenarios
        assert "100.0%" in result.stdout  # Pass rate

    @patch("prompt_unifier.ai.executor.AIExecutor.execute_prompt")
    def test_e2e_workflow_with_mixed_pass_fail(
        self, mock_execute: MagicMock, mock_validate_conn: MagicMock, tmp_path: Path
    ) -> None:
        """Test workflow with some passing and some failing scenarios."""
        # Mock AI response that passes first test but fails second (too long)
        mock_execute.return_value = "This response has expected text and is longer than 10 chars"

        source_file = tmp_path / "test.md"
        source_file.write_text(
            dedent(
                """
                title: Test
                description: Test
                >>>
                Output contains expected text but is too long for the max-length check.
                """
            )
        )

        test_file = tmp_path / "test.md.test.yaml"
        test_file.write_text(
            dedent(
                """
                provider: "gpt-4o"
                scenarios:
                  - description: "Passing scenario"
                    input: "test"
                    expect:
                      - type: contains
                        value: "expected"
                  - description: "Failing scenario"
                    input: "test"
                    expect:
                      - type: max-length
                        value: 10
                """
            )
        )

        result = runner.invoke(app, ["test", str(source_file)])

        assert result.exit_code == 1
        assert "PASS" in result.stdout
        assert "FAIL" in result.stdout

    @patch("prompt_unifier.ai.executor.AIExecutor.execute_prompt")
    def test_e2e_all_four_assertion_types(
        self, mock_execute: MagicMock, mock_validate_conn: MagicMock, tmp_path: Path
    ) -> None:
        """Test all four assertion types in realistic scenarios."""
        # Mock AI response that matches all assertions
        mock_execute.return_value = "The quick brown fox jumps. Call me at 555-1234 for details."

        source_file = tmp_path / "comprehensive.md"
        source_file.write_text(
            dedent(
                """
                title: Comprehensive Test
                description: Testing all assertion types
                >>>
                The quick brown fox jumps over the lazy dog.
                Phone: 555-1234
                """
            )
        )

        test_file = tmp_path / "comprehensive.md.test.yaml"
        test_file.write_text(
            dedent(
                """
                provider: "gpt-4o"
                scenarios:
                  - description: "All assertion types"
                    input: "test"
                    expect:
                      - type: contains
                        value: "quick brown fox"
                      - type: not-contains
                        value: "ERROR"
                      - type: regex
                        value: "\\\\d{3}-\\\\d{4}"
                        error: "Phone number pattern not found"
                      - type: max-length
                        value: 200
                """
            )
        )

        result = runner.invoke(app, ["test", str(source_file)])

        assert result.exit_code == 0
        assert "4" in result.stdout or "Passed: 4" in result.stdout.replace("\n", " ")

    @patch("prompt_unifier.ai.executor.AIExecutor.execute_prompt")
    def test_e2e_case_insensitive_matching(
        self, mock_execute: MagicMock, mock_validate_conn: MagicMock, tmp_path: Path
    ) -> None:
        """Test case-insensitive matching variations."""
        # Mock AI response with QUICK and BROWN in different cases (no error word)
        mock_execute.return_value = "The QUICK and BROWN response without any issues"

        source_file = tmp_path / "case.md"
        source_file.write_text(
            dedent(
                """
                title: Case Test
                description: Test
                >>>
                The QUICK Brown FOX
                """
            )
        )

        test_file = tmp_path / "case.md.test.yaml"
        test_file.write_text(
            dedent(
                """
                provider: "gpt-4o"
                scenarios:
                  - description: "Case insensitive contains"
                    input: "test"
                    expect:
                      - type: contains
                        value: "quick"
                        case_sensitive: false
                      - type: contains
                        value: "brown"
                        case_sensitive: false
                  - description: "Case insensitive not-contains"
                    input: "test"
                    expect:
                      - type: not-contains
                        value: "error"
                        case_sensitive: false
                """
            )
        )

        result = runner.invoke(app, ["test", str(source_file)])

        assert result.exit_code == 0

    @patch("prompt_unifier.ai.executor.AIExecutor.execute_prompt")
    def test_e2e_parser_and_validator_integration(
        self, mock_execute: MagicMock, mock_validate_conn: MagicMock, tmp_path: Path
    ) -> None:
        """Test direct integration between parser and validator (no CLI)."""
        # Mock AI response
        mock_execute.return_value = (
            "Test response from AI with expected content matching assertions"
        )

        test_file = tmp_path / "integration.test.yaml"
        test_file.write_text(
            dedent(
                """
                provider: test-provider
                iterations: 2
                scenarios:
                  - description: "Integration test"
                    input: "input text"
                    expect:
                      - type: contains
                        value: "success"
                      - type: max-length
                        value: 100
                """
            )
        )

        # Parse
        parser = FunctionalTestParser(test_file)
        test_spec = parser.parse()

        assert test_spec is not None
        assert test_spec.provider == "test-provider"
        assert test_spec.iterations == 2

        # Validate
        validator = FunctionalValidator(test_spec)
        output = "Test success output"
        results = validator.validate(output)

        assert len(results) == 1
        assert results[0].status == "PASS"

    @patch("prompt_unifier.ai.executor.AIExecutor.execute_prompt")
    def test_e2e_invalid_yaml_recovery(
        self, mock_execute: MagicMock, mock_validate_conn: MagicMock, tmp_path: Path
    ) -> None:
        """Test that invalid YAML is handled gracefully."""
        # Mock AI response
        mock_execute.return_value = (
            "Test response from AI with expected content matching assertions"
        )

        source_file = tmp_path / "test.md"
        source_file.write_text("title: Test\ndescription: Test\n>>>\nContent")

        test_file = tmp_path / "test.md.test.yaml"
        test_file.write_text("scenarios:\n  - description: 'Unclosed")

        result = runner.invoke(app, ["test", str(source_file)])

        assert result.exit_code == 1  # Failed due to discovery/parsing error

    @patch("prompt_unifier.ai.executor.AIExecutor.execute_prompt")
    def test_e2e_multiline_input_parsing(
        self, mock_execute: MagicMock, mock_validate_conn: MagicMock, tmp_path: Path
    ) -> None:
        """Test multi-line input is correctly parsed and used."""
        # Mock AI response that contains Line 1 and Line 3
        mock_execute.return_value = "Processing Line 1 and Line 2 and Line 3 complete"

        source_file = tmp_path / "multiline.md"
        source_file.write_text(
            dedent(
                """
                title: Test
                description: Test
                >>>
                Line 1
                Line 2
                Line 3
                """
            )
        )

        test_file = tmp_path / "multiline.md.test.yaml"
        test_file.write_text(
            dedent(
                """
                provider: "gpt-4o"
                scenarios:
                  - description: "Multiline test"
                    input: |
                      This is a multi-line
                      input that spans
                      several lines
                    expect:
                      - type: contains
                        value: "Line 1"
                      - type: contains
                        value: "Line 3"
                """
            )
        )

        result = runner.invoke(app, ["test", str(source_file)])

        assert result.exit_code == 0

    @patch("prompt_unifier.ai.executor.AIExecutor.execute_prompt")
    def test_e2e_custom_error_messages(
        self, mock_execute: MagicMock, mock_validate_conn: MagicMock, tmp_path: Path
    ) -> None:
        """Test custom error messages are displayed on failure."""
        # Mock AI response that FAILS the assertion to trigger custom error
        mock_execute.return_value = "Wrong content without the expected text"

        source_file = tmp_path / "error.md"
        source_file.write_text("title: Test\ndescription: Test\n>>>\nWrong content")

        test_file = tmp_path / "error.md.test.yaml"
        test_file.write_text(
            dedent(
                """
                provider: "gpt-4o"
                scenarios:
                  - description: "Custom error test"
                    input: "test"
                    expect:
                      - type: contains
                        value: "Expected content"
                        error: "This is a custom error message"
                """
            )
        )

        result = runner.invoke(app, ["test", str(source_file)])

        assert result.exit_code == 1
        assert "custom error message" in result.stdout

    @patch("prompt_unifier.ai.executor.AIExecutor.execute_prompt")
    def test_e2e_regex_pattern_validation(
        self, mock_execute: MagicMock, mock_validate_conn: MagicMock, tmp_path: Path
    ) -> None:
        """Test regex patterns work correctly in realistic scenarios."""
        # Mock AI response with version number and email patterns
        mock_execute.return_value = "Version 1.2.3 released. Contact: user@example.com"

        source_file = tmp_path / "regex.md"
        source_file.write_text(
            dedent(
                """
                title: Regex Test
                description: Test
                >>>
                Version: 1.2.3
                Email: user@example.com
                """
            )
        )

        test_file = tmp_path / "regex.md.test.yaml"
        test_file.write_text(
            dedent(
                """
                provider: "gpt-4o"
                scenarios:
                  - description: "Regex patterns"
                    input: "test"
                    expect:
                      - type: regex
                        value: "\\\\d+\\\\.\\\\d+\\\\.\\\\d+"
                        error: "Version number not found"
                      - type: regex
                        value: "\\\\w+@\\\\w+\\\\.\\\\w+"
                        error: "Email pattern not found"
                """
            )
        )

        result = runner.invoke(app, ["test", str(source_file)])

        assert result.exit_code == 0
