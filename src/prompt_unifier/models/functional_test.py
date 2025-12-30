"""Data models for functional testing.

This module provides Pydantic models for representing functional test scenarios,
assertions, and results for AI prompt validation.
"""

from typing import Literal

from pydantic import BaseModel, Field


class FunctionalTestAssertion(BaseModel):
    """Represents a single assertion in a functional test.

    Attributes:
        type: Type of assertion (contains, not-contains, regex, max-length)
        value: Expected value (string for text assertions, int for max-length)
        error: Optional custom error message for assertion failure
        case_sensitive: Whether string matching is case-sensitive (default: True)

    Examples:
        >>> assertion = FunctionalTestAssertion(
        ...     type="contains",
        ...     value="expected text",
        ...     error="Text not found"
        ... )
        >>> assertion.type
        'contains'
    """

    type: Literal["contains", "not-contains", "regex", "max-length"] = Field(
        description="Type of assertion to perform"
    )
    value: str | int = Field(
        description="Expected value (string for text assertions, int for max-length)"
    )
    error: str | None = Field(
        default=None, description="Custom error message for assertion failure"
    )
    case_sensitive: bool = Field(
        default=True,
        description="Whether string matching is case-sensitive (only for contains/not-contains)",
    )


class FunctionalTestScenario(BaseModel):
    """Represents a single test scenario with input and expected assertions.

    Attributes:
        description: Human-readable description of the test scenario
        input: Input content to test (supports multi-line with YAML | syntax)
        expect: List of assertions to validate against the output

    Examples:
        >>> scenario = FunctionalTestScenario(
        ...     description="Test refactoring output",
        ...     input="Refactor this code:\\ndef foo(): pass",
        ...     expect=[FunctionalTestAssertion(type="contains", value="def foo")]
        ... )
        >>> len(scenario.expect)
        1
    """

    description: str = Field(description="Human-readable description of the test scenario")
    input: str = Field(description="Input content to test (supports multi-line)")
    expect: list[FunctionalTestAssertion] = Field(
        description="List of assertions to validate against the output"
    )


class FunctionalTestFile(BaseModel):
    """Represents a complete functional test file with multiple scenarios.

    Attributes:
        provider: Optional AI provider/model to use (overrides global config if set)
        iterations: Optional number of times to run each test (default: 1)
        scenarios: List of test scenarios to execute

    Examples:
        >>> test_file = FunctionalTestFile(
        ...     provider="gpt-4o",
        ...     iterations=1,
        ...     scenarios=[
        ...         FunctionalTestScenario(
        ...             description="Test 1",
        ...             input="input",
        ...             expect=[FunctionalTestAssertion(type="contains", value="output")]
        ...         )
        ...     ]
        ... )
        >>> test_file.provider
        'gpt-4o'
    """

    provider: str | None = Field(
        default=None,
        description=(
            "AI provider/model to use "
            "(e.g., 'gpt-4o', 'claude-3-5-sonnet', 'ollama/devstral'). "
            "If None, uses global config."
        ),
    )
    iterations: int | None = Field(
        default=1, description="Optional number of times to run each test (default: 1)"
    )
    scenarios: list[FunctionalTestScenario] = Field(description="List of test scenarios to execute")


class FunctionalTestResult(BaseModel):
    """Represents the result of executing a single test scenario.

    Attributes:
        scenario_description: Description of the scenario that was tested
        status: Overall status (PASS or FAIL)
        passed_count: Number of assertions that passed
        failed_count: Number of assertions that failed
        failures: List of failure details for failed assertions

    Properties:
        is_passing: True if status is PASS, False otherwise

    Examples:
        >>> result = FunctionalTestResult(
        ...     scenario_description="Test scenario",
        ...     status="PASS",
        ...     passed_count=3,
        ...     failed_count=0,
        ...     failures=[]
        ... )
        >>> result.is_passing
        True
    """

    scenario_description: str = Field(description="Description of the scenario that was tested")
    status: Literal["PASS", "FAIL"] = Field(description="Overall status (PASS or FAIL)")
    passed_count: int = Field(description="Number of assertions that passed")
    failed_count: int = Field(description="Number of assertions that failed")
    failures: list[dict[str, str]] = Field(
        default_factory=list,
        description="List of failure details (type, expected, actual_excerpt, error_message)",
    )

    @property
    def is_passing(self) -> bool:
        """Check if the test result is passing.

        Returns:
            True if status is PASS, False otherwise
        """
        return self.status == "PASS"
