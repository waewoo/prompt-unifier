"""Tests for functional validator AI execution.

This module tests the FunctionalValidator class for AI-based execution
of functional test scenarios.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

from prompt_unifier.ai.executor import AIExecutionError, AIExecutor
from prompt_unifier.core.functional_validator import FunctionalValidator
from prompt_unifier.models.functional_test import (
    FunctionalTestAssertion,
    FunctionalTestFile,
    FunctionalTestScenario,
)


class TestFunctionalValidatorAI:
    """Tests for FunctionalValidator AI execution."""

    @patch("prompt_unifier.ai.executor.AIExecutor.execute_prompt")
    def test_validate_with_ai_success(self, mock_execute: MagicMock, tmp_path: Path) -> None:
        """Test successful AI execution and validation."""
        # Create a prompt file
        prompt_file = tmp_path / "test_prompt.md"
        prompt_file.write_text("You are a helpful assistant.")

        # Mock AI response
        mock_execute.return_value = "This response contains expected text"

        # Create test file
        test_file = FunctionalTestFile(
            provider="gpt-4o",
            scenarios=[
                FunctionalTestScenario(
                    description="Test AI response",
                    input="Generate text",
                    expect=[
                        FunctionalTestAssertion(
                            type="contains",
                            value="expected text",
                        )
                    ],
                )
            ],
        )

        validator = FunctionalValidator(test_file)
        results = validator.validate_with_ai(prompt_file)

        assert len(results) == 1
        assert results[0].status == "PASS"
        assert results[0].passed_count == 1
        assert results[0].failed_count == 0

        # Verify AI was called with correct arguments
        mock_execute.assert_called_once_with(
            system_prompt="You are a helpful assistant.",
            user_input="Generate text",
            provider="gpt-4o",
        )

    @patch("prompt_unifier.ai.executor.AIExecutor.execute_prompt")
    def test_validate_with_ai_creates_executor_if_none(
        self, mock_execute: MagicMock, tmp_path: Path
    ) -> None:
        """Test that validator creates AIExecutor if not provided."""
        prompt_file = tmp_path / "test_prompt.md"
        prompt_file.write_text("System prompt")

        mock_execute.return_value = "AI response"

        test_file = FunctionalTestFile(
            provider="gpt-4o",
            scenarios=[
                FunctionalTestScenario(
                    description="Test",
                    input="input",
                    expect=[FunctionalTestAssertion(type="contains", value="response")],
                )
            ],
        )

        validator = FunctionalValidator(test_file)
        # Don't provide executor - should create one internally
        results = validator.validate_with_ai(prompt_file, executor=None)

        assert len(results) == 1
        assert results[0].status == "PASS"

    @patch("prompt_unifier.ai.executor.AIExecutor.execute_prompt")
    def test_validate_with_ai_uses_provided_executor(
        self, mock_execute: MagicMock, tmp_path: Path
    ) -> None:
        """Test that validator uses provided executor."""
        prompt_file = tmp_path / "test_prompt.md"
        prompt_file.write_text("System prompt")

        mock_execute.return_value = "AI response"

        test_file = FunctionalTestFile(
            provider="gpt-4o",
            scenarios=[
                FunctionalTestScenario(
                    description="Test",
                    input="input",
                    expect=[FunctionalTestAssertion(type="contains", value="response")],
                )
            ],
        )

        # Create custom executor
        custom_executor = AIExecutor()

        validator = FunctionalValidator(test_file)
        results = validator.validate_with_ai(prompt_file, executor=custom_executor)

        assert len(results) == 1
        assert results[0].status == "PASS"

    def test_validate_with_ai_file_read_error(self, tmp_path: Path) -> None:
        """Test that file read errors return empty results."""
        # Non-existent file
        non_existent_file = tmp_path / "missing.md"

        test_file = FunctionalTestFile(
            provider="gpt-4o",
            scenarios=[
                FunctionalTestScenario(
                    description="Test",
                    input="input",
                    expect=[FunctionalTestAssertion(type="contains", value="text")],
                )
            ],
        )

        validator = FunctionalValidator(test_file)
        results = validator.validate_with_ai(non_existent_file)

        # Should return empty list due to file read error
        assert results == []

    @patch("prompt_unifier.ai.executor.AIExecutor.execute_prompt")
    def test_validate_with_ai_handles_execution_error(
        self, mock_execute: MagicMock, tmp_path: Path
    ) -> None:
        """Test that AI execution errors are handled gracefully."""
        prompt_file = tmp_path / "test_prompt.md"
        prompt_file.write_text("System prompt")

        # Mock AI execution to raise error
        mock_execute.side_effect = AIExecutionError("API key invalid")

        test_file = FunctionalTestFile(
            provider="gpt-4o",
            scenarios=[
                FunctionalTestScenario(
                    description="Test scenario",
                    input="input",
                    expect=[
                        FunctionalTestAssertion(type="contains", value="text1"),
                        FunctionalTestAssertion(type="contains", value="text2"),
                    ],
                )
            ],
        )

        validator = FunctionalValidator(test_file)
        results = validator.validate_with_ai(prompt_file)

        assert len(results) == 1
        assert results[0].status == "FAIL"
        assert results[0].passed_count == 0
        assert results[0].failed_count == 2  # Number of assertions
        assert len(results[0].failures) == 1

        # Check failure details
        failure = results[0].failures[0]
        assert failure["type"] == "AI_EXECUTION_ERROR"
        assert failure["expected"] == "Successful AI execution"
        assert "API key invalid" in failure["error_message"]
        assert "AI execution failed" in failure["error_message"]

    @patch("prompt_unifier.ai.executor.AIExecutor.execute_prompt")
    def test_validate_with_ai_multiple_scenarios(
        self, mock_execute: MagicMock, tmp_path: Path
    ) -> None:
        """Test AI validation with multiple scenarios."""
        prompt_file = tmp_path / "test_prompt.md"
        prompt_file.write_text("System prompt")

        # Mock different responses for each scenario
        mock_execute.side_effect = [
            "Response with text1",
            "Response with text2",
        ]

        test_file = FunctionalTestFile(
            provider="gpt-4o",
            scenarios=[
                FunctionalTestScenario(
                    description="Scenario 1",
                    input="input1",
                    expect=[FunctionalTestAssertion(type="contains", value="text1")],
                ),
                FunctionalTestScenario(
                    description="Scenario 2",
                    input="input2",
                    expect=[FunctionalTestAssertion(type="contains", value="text2")],
                ),
            ],
        )

        validator = FunctionalValidator(test_file)
        results = validator.validate_with_ai(prompt_file)

        assert len(results) == 2
        assert results[0].status == "PASS"
        assert results[1].status == "PASS"
        assert results[0].scenario_description == "Scenario 1"
        assert results[1].scenario_description == "Scenario 2"

        # Verify both AI calls were made
        assert mock_execute.call_count == 2

    @patch("prompt_unifier.ai.executor.AIExecutor.execute_prompt")
    def test_validate_with_ai_mixed_results(self, mock_execute: MagicMock, tmp_path: Path) -> None:
        """Test AI validation with one passing and one failing scenario."""
        prompt_file = tmp_path / "test_prompt.md"
        prompt_file.write_text("System prompt")

        # First call succeeds, second raises error
        mock_execute.side_effect = [
            "Response with expected text",
            AIExecutionError("Rate limit exceeded"),
        ]

        test_file = FunctionalTestFile(
            provider="gpt-4o",
            scenarios=[
                FunctionalTestScenario(
                    description="Passing scenario",
                    input="input1",
                    expect=[FunctionalTestAssertion(type="contains", value="expected")],
                ),
                FunctionalTestScenario(
                    description="Failing scenario",
                    input="input2",
                    expect=[FunctionalTestAssertion(type="contains", value="text")],
                ),
            ],
        )

        validator = FunctionalValidator(test_file)
        results = validator.validate_with_ai(prompt_file)

        assert len(results) == 2
        assert results[0].status == "PASS"
        assert results[1].status == "FAIL"
        assert "Rate limit exceeded" in results[1].failures[0]["error_message"]
