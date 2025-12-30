"""Tests for functional test models.

This module tests the Pydantic models used for functional testing:
- FunctionalTestAssertion
- FunctionalTestScenario
- FunctionalTestFile
- FunctionalTestResult
"""

import pytest
from pydantic import ValidationError

from prompt_unifier.models.functional_test import (
    FunctionalTestAssertion,
    FunctionalTestFile,
    FunctionalTestResult,
    FunctionalTestScenario,
)


class TestFunctionalTestAssertion:
    """Tests for FunctionalTestAssertion model."""

    def test_valid_contains_assertion(self) -> None:
        """Test creating a valid contains assertion."""
        assertion = FunctionalTestAssertion(
            type="contains",
            value="expected text",
            error="Custom error message",
        )
        assert assertion.type == "contains"
        assert assertion.value == "expected text"
        assert assertion.error == "Custom error message"
        assert assertion.case_sensitive is True  # Default value

    def test_contains_assertion_case_insensitive(self) -> None:
        """Test contains assertion with case_insensitive option."""
        assertion = FunctionalTestAssertion(
            type="contains",
            value="Text",
            case_sensitive=False,
        )
        assert assertion.case_sensitive is False

    def test_valid_max_length_assertion(self) -> None:
        """Test creating a valid max-length assertion with integer value."""
        assertion = FunctionalTestAssertion(
            type="max-length",
            value=100,
        )
        assert assertion.type == "max-length"
        assert assertion.value == 100
        assert isinstance(assertion.value, int)

    def test_invalid_assertion_type(self) -> None:
        """Test that invalid assertion type raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            FunctionalTestAssertion(
                type="invalid-type",
                value="test",
            )
        assert "type" in str(exc_info.value)

    def test_optional_fields_default_values(self) -> None:
        """Test that optional fields have correct defaults."""
        assertion = FunctionalTestAssertion(
            type="regex",
            value=r"\d+",
        )
        assert assertion.error is None
        assert assertion.case_sensitive is True


class TestFunctionalTestScenario:
    """Tests for FunctionalTestScenario model."""

    def test_valid_scenario_single_assertion(self) -> None:
        """Test creating a scenario with a single assertion."""
        scenario = FunctionalTestScenario(
            description="Test scenario",
            input="Test input",
            expect=[
                FunctionalTestAssertion(type="contains", value="output"),
            ],
        )
        assert scenario.description == "Test scenario"
        assert scenario.input == "Test input"
        assert len(scenario.expect) == 1

    def test_valid_scenario_multiple_assertions(self) -> None:
        """Test scenario with multiple assertions."""
        scenario = FunctionalTestScenario(
            description="Multi-assertion test",
            input="Input text",
            expect=[
                FunctionalTestAssertion(type="contains", value="text1"),
                FunctionalTestAssertion(type="not-contains", value="text2"),
                FunctionalTestAssertion(type="regex", value=r"\d+"),
            ],
        )
        assert len(scenario.expect) == 3

    def test_multiline_input_support(self) -> None:
        """Test that multiline input is properly stored."""
        multiline = """Line 1
Line 2
Line 3"""
        scenario = FunctionalTestScenario(
            description="Multiline test",
            input=multiline,
            expect=[FunctionalTestAssertion(type="contains", value="Line")],
        )
        assert "\n" in scenario.input
        assert "Line 1" in scenario.input


class TestFunctionalTestFile:
    """Tests for FunctionalTestFile model."""

    def test_valid_test_file_minimal(self) -> None:
        """Test creating a minimal valid test file with required provider."""
        test_file = FunctionalTestFile(
            provider="gpt-4o",
            scenarios=[
                FunctionalTestScenario(
                    description="Test 1",
                    input="input",
                    expect=[FunctionalTestAssertion(type="contains", value="out")],
                )
            ],
        )
        assert len(test_file.scenarios) == 1
        assert test_file.provider == "gpt-4o"
        assert test_file.iterations == 1

    def test_valid_test_file_with_provider_and_iterations(self) -> None:
        """Test test file with optional provider and iterations."""
        test_file = FunctionalTestFile(
            provider="openai:gpt-4o",
            iterations=3,
            scenarios=[
                FunctionalTestScenario(
                    description="Test",
                    input="in",
                    expect=[FunctionalTestAssertion(type="contains", value="out")],
                )
            ],
        )
        assert test_file.provider == "openai:gpt-4o"
        assert test_file.iterations == 3

    def test_multiple_scenarios(self) -> None:
        """Test file with multiple scenarios."""
        test_file = FunctionalTestFile(
            provider="gpt-4o",
            scenarios=[
                FunctionalTestScenario(
                    description="Test 1",
                    input="input1",
                    expect=[FunctionalTestAssertion(type="contains", value="out1")],
                ),
                FunctionalTestScenario(
                    description="Test 2",
                    input="input2",
                    expect=[FunctionalTestAssertion(type="regex", value=r"\w+")],
                ),
            ],
        )
        assert len(test_file.scenarios) == 2


class TestFunctionalTestResult:
    """Tests for FunctionalTestResult model."""

    def test_passing_result_no_failures(self) -> None:
        """Test a passing result with no failures."""
        result = FunctionalTestResult(
            scenario_description="Test scenario",
            status="PASS",
            passed_count=3,
            failed_count=0,
            failures=[],
        )
        assert result.status == "PASS"
        assert result.is_passing is True
        assert len(result.failures) == 0

    def test_failing_result_with_failures(self) -> None:
        """Test a failing result with assertion failures."""
        result = FunctionalTestResult(
            scenario_description="Test scenario",
            status="FAIL",
            passed_count=1,
            failed_count=2,
            failures=[
                {
                    "type": "contains",
                    "expected": "text",
                    "actual_excerpt": "other content...",
                    "error_message": "Expected text not found",
                },
                {
                    "type": "max-length",
                    "expected": "100",
                    "actual_excerpt": "Long content...",
                    "error_message": "Content exceeds maximum length",
                },
            ],
        )
        assert result.status == "FAIL"
        assert result.is_passing is False
        assert len(result.failures) == 2
        assert result.failed_count == 2

    def test_is_passing_property(self) -> None:
        """Test the is_passing property returns correct boolean."""
        pass_result = FunctionalTestResult(
            scenario_description="Pass test",
            status="PASS",
            passed_count=1,
            failed_count=0,
            failures=[],
        )
        fail_result = FunctionalTestResult(
            scenario_description="Fail test",
            status="FAIL",
            passed_count=0,
            failed_count=1,
            failures=[
                {"type": "test", "expected": "x", "actual_excerpt": "y", "error_message": "e"}
            ],
        )
        assert pass_result.is_passing is True
        assert fail_result.is_passing is False
