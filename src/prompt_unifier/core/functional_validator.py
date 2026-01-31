"""Functional validator for executing test scenarios and assertions.

This module provides the validation logic for functional testing,
executing assertions against AI prompt outputs.
"""

import logging
import re
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from prompt_unifier.models.functional_test import (
    FunctionalTestAssertion,
    FunctionalTestFile,
    FunctionalTestResult,
    FunctionalTestScenario,
)

if TYPE_CHECKING:
    from prompt_unifier.ai.executor import AIExecutor

logger = logging.getLogger(__name__)


class FunctionalValidator:
    """Validator for functional test scenarios.

    This validator executes test scenarios against provided output,
    checking various assertion types (contains, not-contains, regex, max-length).
    Collects all failures before returning results.

    Examples:
        >>> from prompt_unifier.models.functional_test import (
        ...     FunctionalTestFile,
        ...     FunctionalTestScenario,
        ...     FunctionalTestAssertion
        ... )
        >>> test_file = FunctionalTestFile(
        ...     scenarios=[
        ...         FunctionalTestScenario(
        ...             description="Test",
        ...             input="input",
        ...             expect=[FunctionalTestAssertion(type="contains", value="text")]
        ...         )
        ...     ]
        ... )
        >>> validator = FunctionalValidator(test_file)
        >>> results = validator.validate("Some text here")
        >>> results[0].status
        'PASS'
    """

    def __init__(self, test_file: FunctionalTestFile):
        """Initialize validator with test file.

        Args:
            test_file: Parsed functional test file containing scenarios
        """
        self.test_file = test_file

    def validate(self, output: str) -> list[FunctionalTestResult]:
        """Validate output against all test scenarios.

        Args:
            output: The output text to validate against assertions

        Returns:
            List of FunctionalTestResult objects, one per scenario

        Examples:
            >>> # validator already initialized with test_file
            >>> results = validator.validate("Test output")
            >>> len(results)
            1
        """
        results: list[FunctionalTestResult] = []

        for scenario in self.test_file.scenarios:
            result = self._execute_scenario(scenario, output)
            results.append(result)

        return results

    def validate_with_ai(
        self, prompt_file: Path, executor: "AIExecutor | None" = None, provider: str | None = None
    ) -> list[FunctionalTestResult]:
        """Validate by executing prompts via AI and checking assertions.

        This method:
        1. Reads the prompt file content as the system prompt
        2. For each scenario, calls the AI with the scenario input
        3. Validates the AI's response against the scenario assertions

        Args:
            prompt_file: Path to the .md file containing the prompt template
            executor: AIExecutor instance (created if not provided)
            provider: AI provider/model to use (overrides test file and executor default)

        Returns:
            List of FunctionalTestResult objects, one per scenario

        Examples:
            >>> from pathlib import Path
            >>> from prompt_unifier.ai.executor import AIExecutor
            >>> prompt = Path("prompts/refactor.md")
            >>> validator = FunctionalValidator(test_file)
            >>> results = validator.validate_with_ai(prompt)
            >>> results[0].status
            'PASS'
        """
        # Import here to avoid circular dependency
        from prompt_unifier.ai.executor import AIExecutionError, AIExecutor

        # Create executor if not provided
        if executor is None:
            executor = AIExecutor()

        # Determine effective provider (Priority: Parameter > Test File > None)
        effective_provider = provider or self.test_file.provider

        # Read the prompt file content (system prompt)
        try:
            system_prompt = prompt_file.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to read prompt file {prompt_file}: {e}")
            return []

        results: list[FunctionalTestResult] = []

        for scenario in self.test_file.scenarios:
            try:
                # Execute the prompt with AI
                logger.debug(
                    f"Executing scenario '{scenario.description}' "
                    f"with provider {effective_provider}"
                )
                ai_output = executor.execute_prompt(
                    system_prompt=system_prompt,
                    user_input=scenario.input,
                    provider=effective_provider,
                )

                # Validate AI response against assertions
                result = self._execute_scenario(scenario, ai_output)
                results.append(result)

            except AIExecutionError as e:
                # Create a FAIL result for AI execution errors
                logger.error(f"AI execution failed for scenario '{scenario.description}': {e}")
                results.append(
                    FunctionalTestResult(
                        scenario_description=scenario.description,
                        status="FAIL",
                        passed_count=0,
                        failed_count=len(scenario.expect),
                        failures=[
                            {
                                "type": "AI_EXECUTION_ERROR",
                                "expected": "Successful AI execution",
                                "actual_excerpt": str(e)[:100],
                                "error_message": f"AI execution failed: {e}",
                            }
                        ],
                    )
                )

        return results

    def _execute_scenario(
        self, scenario: FunctionalTestScenario, output: str
    ) -> FunctionalTestResult:
        """Execute a single test scenario against output.

        Args:
            scenario: The test scenario to execute
            output: The output text to validate

        Returns:
            FunctionalTestResult with pass/fail status and failure details
        """
        passed_count = 0
        failed_count = 0
        failures: list[dict[str, str]] = []

        for assertion in scenario.expect:
            is_passing = self._execute_assertion(assertion, output)

            if is_passing:
                passed_count += 1
            else:
                failed_count += 1
                # Generate failure details
                failure = self._create_failure_detail(assertion, output)
                failures.append(failure)

        # Determine overall status
        status: Literal["PASS", "FAIL"] = "PASS" if failed_count == 0 else "FAIL"

        return FunctionalTestResult(
            scenario_description=scenario.description,
            status=status,
            passed_count=passed_count,
            failed_count=failed_count,
            failures=failures,
        )

    def _execute_assertion(self, assertion: FunctionalTestAssertion, output: str) -> bool:
        """Execute a single assertion against output.

        Args:
            assertion: The assertion to execute
            output: The output text to validate

        Returns:
            True if assertion passes, False otherwise
        """
        # Dispatch to appropriate validator based on assertion type
        validators: dict[str, Callable[[FunctionalTestAssertion, str], bool]] = {
            "contains": self._validate_contains,
            "not-contains": self._validate_not_contains,
            "regex": self._validate_regex,
            "max-length": self._validate_max_length,
        }

        validator_func = validators.get(assertion.type)
        if validator_func is None:
            logger.warning(f"Unknown assertion type '{assertion.type}', skipping")
            return False

        return validator_func(assertion, output)

    def _validate_contains(self, assertion: FunctionalTestAssertion, output: str) -> bool:
        """Validate contains assertion.

        Args:
            assertion: The contains assertion
            output: The output text to check

        Returns:
            True if substring is found, False otherwise
        """
        # assertion.value should be str for contains check
        value_str = str(assertion.value)
        if assertion.case_sensitive:
            return value_str in output
        else:
            return value_str.lower() in output.lower()

    def _validate_not_contains(self, assertion: FunctionalTestAssertion, output: str) -> bool:
        """Validate not-contains assertion.

        Args:
            assertion: The not-contains assertion
            output: The output text to check

        Returns:
            True if substring is NOT found, False otherwise
        """
        # assertion.value should be str for not-contains check
        value_str = str(assertion.value)
        if assertion.case_sensitive:
            return value_str not in output
        else:
            return value_str.lower() not in output.lower()

    def _validate_regex(self, assertion: FunctionalTestAssertion, output: str) -> bool:
        """Validate regex assertion.

        Args:
            assertion: The regex assertion
            output: The output text to search

        Returns:
            True if pattern matches, False otherwise
        """
        try:
            # assertion.value should be str for regex pattern
            pattern = str(assertion.value)
            match = re.search(pattern, output)
            return match is not None
        except re.error as e:
            logger.warning(f"Invalid regex pattern '{assertion.value}': {e}")
            return False

    def _validate_max_length(self, assertion: FunctionalTestAssertion, output: str) -> bool:
        """Validate max-length assertion.

        Args:
            assertion: The max-length assertion
            output: The output text to check

        Returns:
            True if length is within limit, False otherwise
        """
        max_length = int(assertion.value)
        return len(output) <= max_length

    def _create_failure_detail(
        self, assertion: FunctionalTestAssertion, output: str
    ) -> dict[str, str]:
        """Create failure detail dictionary for a failed assertion.

        Args:
            assertion: The failed assertion
            output: The actual output

        Returns:
            Dictionary with type, expected, actual_excerpt, and error_message
        """
        # Extract first 100 characters of output for excerpt
        actual_excerpt = output[:100]
        if len(output) > 100:
            actual_excerpt += "..."

        # Use custom error message if provided, otherwise generate default
        error_message = assertion.error or self._generate_default_error_message(assertion)

        return {
            "passed": False,
            "error": error_message,
            "assertion": assertion.type,
            "params": assertion.params,
        }

    def _generate_default_error_message(self, assertion: FunctionalTestAssertion) -> str:
        """Generate a default error message for failed assertion.

        Args:
            assertion: The failed assertion

        Returns:
            Default error message string
        """
        if assertion.type == "contains":
            return f"Expected output to contain '{assertion.value}'"
        elif assertion.type == "not-contains":
            return f"Expected output to NOT contain '{assertion.value}'"
        elif assertion.type == "regex":
            return f"Expected output to match regex pattern '{assertion.value}'"
        elif assertion.type == "max-length":
            return f"Expected output length to be <= {assertion.value} characters"
        else:
            return f"Assertion failed: {assertion.type}"
