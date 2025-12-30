"""Tests for functional validator.

This module tests the FunctionalValidator class for executing
functional test scenarios and validating assertions.
"""

from typing import cast

from prompt_unifier.core.functional_validator import FunctionalValidator
from prompt_unifier.models.functional_test import (
    FunctionalTestAssertion,
    FunctionalTestFile,
    FunctionalTestScenario,
)


class TestFunctionalValidator:
    """Tests for FunctionalValidator class."""

    def test_validate_contains_assertion_case_sensitive(self) -> None:
        """Test contains assertion with case-sensitive matching."""
        test_file = FunctionalTestFile(
            provider="gpt-4o",
            scenarios=[
                FunctionalTestScenario(
                    description="Contains test",
                    input="input",
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
        output = "This is the expected text in the output"

        results = validator.validate(output)

        assert len(results) == 1
        assert results[0].status == "PASS"
        assert results[0].passed_count == 1
        assert results[0].failed_count == 0

    def test_validate_contains_assertion_case_insensitive(self) -> None:
        """Test contains assertion with case-insensitive matching."""
        test_file = FunctionalTestFile(
            provider="gpt-4o",
            scenarios=[
                FunctionalTestScenario(
                    description="Case insensitive test",
                    input="input",
                    expect=[
                        FunctionalTestAssertion(
                            type="contains",
                            value="Expected",
                            case_sensitive=False,
                        )
                    ],
                )
            ],
        )
        validator = FunctionalValidator(test_file)
        output = "This is the EXPECTED text"

        results = validator.validate(output)

        assert len(results) == 1
        assert results[0].status == "PASS"

    def test_validate_not_contains_assertion(self) -> None:
        """Test not-contains assertion passes when text is absent."""
        test_file = FunctionalTestFile(
            provider="gpt-4o",
            scenarios=[
                FunctionalTestScenario(
                    description="Not-contains test",
                    input="input",
                    expect=[
                        FunctionalTestAssertion(
                            type="not-contains",
                            value="forbidden text",
                        )
                    ],
                )
            ],
        )
        validator = FunctionalValidator(test_file)
        output = "This output does not contain the unwanted string"

        results = validator.validate(output)

        assert len(results) == 1
        assert results[0].status == "PASS"

    def test_validate_regex_assertion_matches(self) -> None:
        """Test regex assertion with successful pattern match."""
        test_file = FunctionalTestFile(
            provider="gpt-4o",
            scenarios=[
                FunctionalTestScenario(
                    description="Regex test",
                    input="input",
                    expect=[
                        FunctionalTestAssertion(
                            type="regex",
                            value=r"\d{3}-\d{4}",
                        )
                    ],
                )
            ],
        )
        validator = FunctionalValidator(test_file)
        output = "Call me at 555-1234"

        results = validator.validate(output)

        assert len(results) == 1
        assert results[0].status == "PASS"

    def test_validate_max_length_assertion_passes(self) -> None:
        """Test max-length assertion passes when within limit."""
        test_file = FunctionalTestFile(
            provider="gpt-4o",
            scenarios=[
                FunctionalTestScenario(
                    description="Max length test",
                    input="input",
                    expect=[
                        FunctionalTestAssertion(
                            type="max-length",
                            value=100,
                        )
                    ],
                )
            ],
        )
        validator = FunctionalValidator(test_file)
        output = "Short output"

        results = validator.validate(output)

        assert len(results) == 1
        assert results[0].status == "PASS"

    def test_validate_max_length_assertion_fails(self) -> None:
        """Test max-length assertion fails when exceeding limit."""
        test_file = FunctionalTestFile(
            provider="gpt-4o",
            scenarios=[
                FunctionalTestScenario(
                    description="Max length exceeded",
                    input="input",
                    expect=[
                        FunctionalTestAssertion(
                            type="max-length",
                            value=10,
                        )
                    ],
                )
            ],
        )
        validator = FunctionalValidator(test_file)
        output = "This is a very long output that exceeds the limit"

        results = validator.validate(output)

        assert len(results) == 1
        assert results[0].status == "FAIL"
        assert results[0].failed_count == 1
        assert len(results[0].failures) == 1

    def test_validate_multiple_assertions_all_pass(self) -> None:
        """Test scenario with multiple assertions all passing."""
        test_file = FunctionalTestFile(
            provider="gpt-4o",
            scenarios=[
                FunctionalTestScenario(
                    description="Multiple assertions",
                    input="input",
                    expect=[
                        FunctionalTestAssertion(type="contains", value="text1"),
                        FunctionalTestAssertion(type="contains", value="text2"),
                        FunctionalTestAssertion(type="max-length", value=100),
                    ],
                )
            ],
        )
        validator = FunctionalValidator(test_file)
        output = "Output contains text1 and text2"

        results = validator.validate(output)

        assert len(results) == 1
        assert results[0].status == "PASS"
        assert results[0].passed_count == 3
        assert results[0].failed_count == 0

    def test_validate_collects_all_failures(self) -> None:
        """Test that validator collects all failures, not just the first one."""
        test_file = FunctionalTestFile(
            provider="gpt-4o",
            scenarios=[
                FunctionalTestScenario(
                    description="Multiple failures",
                    input="input",
                    expect=[
                        FunctionalTestAssertion(
                            type="contains",
                            value="missing1",
                            error="First text not found",
                        ),
                        FunctionalTestAssertion(
                            type="contains",
                            value="missing2",
                            error="Second text not found",
                        ),
                        FunctionalTestAssertion(type="max-length", value=5),
                    ],
                )
            ],
        )
        validator = FunctionalValidator(test_file)
        output = "Some output that doesn't match"

        results = validator.validate(output)

        assert len(results) == 1
        assert results[0].status == "FAIL"
        assert results[0].failed_count == 3
        assert len(results[0].failures) == 3

    def test_validate_multiple_scenarios(self) -> None:
        """Test validator executes multiple scenarios."""
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
                    expect=[FunctionalTestAssertion(type="max-length", value=100)],
                ),
            ],
        )
        validator = FunctionalValidator(test_file)
        output = "Output contains text1"

        results = validator.validate(output)

        assert len(results) == 2
        assert results[0].scenario_description == "Scenario 1"
        assert results[1].scenario_description == "Scenario 2"

    def test_validate_failure_includes_excerpt(self) -> None:
        """Test that failures include excerpt of actual output."""
        test_file = FunctionalTestFile(
            provider="gpt-4o",
            scenarios=[
                FunctionalTestScenario(
                    description="Excerpt test",
                    input="input",
                    expect=[
                        FunctionalTestAssertion(
                            type="contains",
                            value="nonexistent",
                        )
                    ],
                )
            ],
        )
        validator = FunctionalValidator(test_file)
        output = "This is the actual output that will be excerpted"

        results = validator.validate(output)

        assert len(results) == 1
        assert results[0].status == "FAIL"
        assert len(results[0].failures) == 1
        failure = results[0].failures[0]
        assert "actual_excerpt" in failure
        assert len(failure["actual_excerpt"]) <= 100  # First 100 chars

    def test_validate_invalid_regex_pattern_fails(self) -> None:
        """Test that invalid regex pattern returns False and logs warning."""
        test_file = FunctionalTestFile(
            provider="gpt-4o",
            scenarios=[
                FunctionalTestScenario(
                    description="Invalid regex test",
                    input="input",
                    expect=[
                        FunctionalTestAssertion(
                            type="regex",
                            value="[invalid(regex",  # Invalid regex pattern
                        )
                    ],
                )
            ],
        )
        validator = FunctionalValidator(test_file)
        output = "Some output text"

        results = validator.validate(output)

        assert len(results) == 1
        assert results[0].status == "FAIL"
        assert results[0].failed_count == 1

    def test_validate_default_error_message_for_not_contains(self) -> None:
        """Test default error message generation for not-contains assertion."""
        test_file = FunctionalTestFile(
            provider="gpt-4o",
            scenarios=[
                FunctionalTestScenario(
                    description="Not-contains failure test",
                    input="input",
                    expect=[
                        FunctionalTestAssertion(
                            type="not-contains",
                            value="forbidden",
                        )
                    ],
                )
            ],
        )
        validator = FunctionalValidator(test_file)
        output = "This output contains the forbidden text"

        results = validator.validate(output)

        assert len(results) == 1
        assert results[0].status == "FAIL"
        assert len(results[0].failures) == 1
        assert "NOT contain" in results[0].failures[0]["error_message"]

    def test_validate_default_error_message_for_regex(self) -> None:
        """Test default error message generation for regex assertion."""
        test_file = FunctionalTestFile(
            provider="gpt-4o",
            scenarios=[
                FunctionalTestScenario(
                    description="Regex failure test",
                    input="input",
                    expect=[
                        FunctionalTestAssertion(
                            type="regex",
                            value=r"\d{5}",  # Looking for 5 digits
                        )
                    ],
                )
            ],
        )
        validator = FunctionalValidator(test_file)
        output = "No five digit numbers here"

        results = validator.validate(output)

        assert len(results) == 1
        assert results[0].status == "FAIL"
        assert len(results[0].failures) == 1
        assert "regex pattern" in results[0].failures[0]["error_message"]

    def test_validate_unknown_assertion_type_returns_false(self) -> None:
        """Test that unknown assertion type logs warning and returns False."""
        # Create assertion with invalid type using model_construct to bypass validation
        invalid_assertion = FunctionalTestAssertion.model_construct(
            type=cast(str, "unknown-type"), value="test", case_sensitive=True
        )

        test_file = FunctionalTestFile(
            provider="gpt-4o",
            scenarios=[
                FunctionalTestScenario(
                    description="Unknown assertion type test",
                    input="input",
                    expect=[invalid_assertion],
                )
            ],
        )
        validator = FunctionalValidator(test_file)
        output = "Some output"

        results = validator.validate(output)

        assert len(results) == 1
        assert results[0].status == "FAIL"
        assert results[0].failed_count == 1
        assert "Assertion failed: unknown-type" in results[0].failures[0]["error_message"]
