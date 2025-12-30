"""Tests for functional validation CLI integration.

This module tests the CLI integration for functional testing,
including the test command and output formatting.
"""

from pathlib import Path
from textwrap import dedent
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from prompt_unifier.cli.main import app

runner = CliRunner()


@patch("prompt_unifier.cli.commands._get_global_ai_provider")
@patch("prompt_unifier.ai.executor.AIExecutor.validate_connection")
class TestFunctionalValidationCLI:
    """Tests for CLI integration of functional validation."""

    @patch("prompt_unifier.ai.executor.AIExecutor.execute_prompt")
    def test_test_command_executes_functional_tests(
        self,
        mock_execute: MagicMock,
        mock_validate_conn: MagicMock,
        mock_global_provider: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test that test command triggers functional test execution."""
        mock_global_provider.return_value = None
        # Mock AI response
        mock_execute.return_value = "Content here from AI"

        # Create a source file
        source_file = tmp_path / "test.md"
        source_file.write_text(
            dedent(
                """
                title: Test
                description: Test prompt
                >>>
                Content here
                """
            )
        )

        # Create corresponding test file
        test_file = tmp_path / "test.md.test.yaml"
        test_file.write_text(
            dedent(
                """
                provider: "gpt-4o"
                scenarios:
                  - description: "Test scenario"
                    input: "test"
                    expect:
                      - type: contains
                        value: "Content"
                """
            )
        )

        result = runner.invoke(app, ["test", str(source_file)])

        assert result.exit_code == 0
        # The output should mention functional tests
        assert "functional" in result.stdout.lower() or "test" in result.stdout.lower()

    def test_test_command_missing_file_shows_warning(
        self,
        mock_validate_conn: MagicMock,
        mock_global_provider: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test that missing .test.yaml file shows warning and exits with 1."""
        mock_global_provider.return_value = None
        # Create source file without test file
        source_file = tmp_path / "test.md"
        source_file.write_text(
            dedent(
                """
                provider: "gpt-4o"
                title: Test
                description: Test
                >>>
                Content
                """
            )
        )

        result = runner.invoke(app, ["test", str(source_file)])

        assert result.exit_code == 1
        assert "not found" in result.stdout.lower() or "missing" in result.stdout.lower()

    def test_test_command_skips_scaff_validation(
        self,
        mock_validate_conn: MagicMock,
        mock_global_provider: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test that test command skips SCAFF validation."""
        mock_global_provider.return_value = None
        source_file = tmp_path / "test.md"
        source_file.write_text(
            dedent(
                """
                title: Test
                description: Test
                >>>
                Content
                """
            )
        )

        test_file = tmp_path / "test.md.test.yaml"
        test_file.write_text(
            dedent(
                """
                provider: "gpt-4o"
                scenarios:
                  - description: "Test"
                    input: "test"
                    expect:
                      - type: contains
                        value: "Content"
                """
            )
        )

        result = runner.invoke(app, ["test", str(source_file)])

        # SCAFF-related output should not be present
        assert "SCAFF" not in result.stdout

    def test_test_command_failed_assertions_exit_code_1(
        self,
        mock_validate_conn: MagicMock,
        mock_global_provider: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test that failed assertions cause exit code 1."""
        mock_global_provider.return_value = None
        source_file = tmp_path / "test.md"
        source_file.write_text(
            dedent(
                """
                provider: "gpt-4o"
                title: Test
                description: Test
                >>>
                Different content
                """
            )
        )

        test_file = tmp_path / "test.md.test.yaml"
        test_file.write_text(
            dedent(
                """
                provider: "gpt-4o"
                scenarios:
                  - description: "Failing test"
                    input: "test"
                    expect:
                      - type: contains
                        value: "NonexistentText"
                """
            )
        )

        result = runner.invoke(app, ["test", str(source_file)])

        assert result.exit_code == 1

    def test_test_command_invalid_yaml_shows_warning(
        self,
        mock_validate_conn: MagicMock,
        mock_global_provider: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test that invalid YAML in test file shows warning."""
        mock_global_provider.return_value = None
        source_file = tmp_path / "test.md"
        source_file.write_text(
            dedent(
                """
                provider: "gpt-4o"
                title: Test
                description: Test
                >>>
                Content
                """
            )
        )

        test_file = tmp_path / "test.md.test.yaml"
        test_file.write_text("scenarios:\n  - description: 'Unclosed quote")

        result = runner.invoke(app, ["test", str(source_file)])

        # Should show warning about invalid YAML
        assert result.exit_code == 1

    @patch("prompt_unifier.ai.executor.AIExecutor.execute_prompt")
    def test_test_command_successful_tests_exit_code_0(
        self,
        mock_execute: MagicMock,
        mock_validate_conn: MagicMock,
        mock_global_provider: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test that all passing tests result in exit code 0."""
        mock_global_provider.return_value = None
        # Mock AI response that passes all assertions
        mock_execute.return_value = "Expected content here from AI response"

        source_file = tmp_path / "test.md"
        source_file.write_text(
            dedent(
                """
                title: Test
                description: Test
                >>>
                Expected content here
                """
            )
        )

        test_file = tmp_path / "test.md.test.yaml"
        test_file.write_text(
            dedent(
                """
                provider: "gpt-4o"
                scenarios:
                  - description: "Passing test"
                    input: "test"
                    expect:
                      - type: contains
                        value: "Expected"
                      - type: max-length
                        value: 1000
                """
            )
        )

        result = runner.invoke(app, ["test", str(source_file)])

        assert result.exit_code == 0
        assert "PASS" in result.stdout or "pass" in result.stdout.lower()

    def test_test_command_connection_failure_auth_error(
        self,
        mock_validate_conn: MagicMock,
        mock_global_provider: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test authentication error shows helpful troubleshooting."""
        mock_global_provider.return_value = None
        from prompt_unifier.ai.executor import AIExecutionError

        # Mock validation to raise auth error
        mock_validate_conn.side_effect = AIExecutionError(
            "Connection test failed for gpt-4o: AuthenticationError: Invalid API key"
        )

        source_file = tmp_path / "test.md"
        source_file.write_text("title: Test\ndescription: Test\n>>>\nContent")

        test_file = tmp_path / "test.md.test.yaml"
        test_file.write_text(
            dedent(
                """
                provider: gpt-4o
                scenarios:
                  - description: "Test"
                    input: "test"
                    expect:
                      - type: contains
                        value: "test"
                """
            )
        )

        result = runner.invoke(app, ["test", str(source_file)])

        assert result.exit_code == 1
        assert "Connection validation failed" in result.stdout
        assert "Troubleshooting" in result.stdout
        assert "API key" in result.stdout or "OPENAI_API_KEY" in result.stdout

    def test_test_command_connection_failure_timeout_error(
        self,
        mock_validate_conn: MagicMock,
        mock_global_provider: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test timeout error shows network troubleshooting."""
        mock_global_provider.return_value = None
        from prompt_unifier.ai.executor import AIExecutionError

        # Mock validation to raise timeout error
        mock_validate_conn.side_effect = AIExecutionError(
            "Connection test failed for gpt-4o: Timeout error"
        )

        source_file = tmp_path / "test.md"
        source_file.write_text("title: Test\ndescription: Test\n>>>\nContent")

        test_file = tmp_path / "test.md.test.yaml"
        test_file.write_text(
            dedent(
                """
                provider: gpt-4o
                scenarios:
                  - description: "Test"
                    input: "test"
                    expect:
                      - type: contains
                        value: "test"
                """
            )
        )

        result = runner.invoke(app, ["test", str(source_file)])

        assert result.exit_code == 1
        assert "Connection validation failed" in result.stdout
        assert "internet connection" in result.stdout or "firewall" in result.stdout

    def test_test_command_connection_failure_ollama_timeout(
        self,
        mock_validate_conn: MagicMock,
        mock_global_provider: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test Ollama timeout shows Ollama-specific help."""
        mock_global_provider.return_value = None
        from prompt_unifier.ai.executor import AIExecutionError

        # Mock validation to raise timeout for Ollama
        mock_validate_conn.side_effect = AIExecutionError(
            "Connection test failed for ollama/llama2: Connection refused"
        )

        source_file = tmp_path / "test.md"
        source_file.write_text("title: Test\ndescription: Test\n>>>\nContent")

        test_file = tmp_path / "test.md.test.yaml"
        test_file.write_text(
            dedent(
                """
                provider: ollama/llama2
                scenarios:
                  - description: "Test"
                    input: "test"
                    expect:
                      - type: contains
                        value: "test"
                """
            )
        )

        result = runner.invoke(app, ["test", str(source_file)])

        assert result.exit_code == 1
        assert "Ollama" in result.stdout or "ollama serve" in result.stdout

    def test_test_command_connection_failure_invalid_model(
        self,
        mock_validate_conn: MagicMock,
        mock_global_provider: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test invalid model error shows model help."""
        mock_global_provider.return_value = None
        from prompt_unifier.ai.executor import AIExecutionError

        # Mock validation to raise model not found error
        mock_validate_conn.side_effect = AIExecutionError(
            "Connection test failed for invalid-model: Model not found"
        )

        source_file = tmp_path / "test.md"
        source_file.write_text("title: Test\ndescription: Test\n>>>\nContent")

        test_file = tmp_path / "test.md.test.yaml"
        test_file.write_text(
            dedent(
                """
                provider: invalid-model
                scenarios:
                  - description: "Test"
                    input: "test"
                    expect:
                      - type: contains
                        value: "test"
                """
            )
        )

        result = runner.invoke(app, ["test", str(source_file)])

        assert result.exit_code == 1
        assert "invalid-model" in result.stdout
        assert "litellm.ai" in result.stdout or "supported models" in result.stdout
