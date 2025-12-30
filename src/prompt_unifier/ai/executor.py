"""AI executor for running prompts via LiteLLM with multi-provider support.

This module provides the AIExecutor class which executes prompts using LiteLLM,
supporting 100+ AI providers including OpenAI, Anthropic, Mistral, and local models.
"""

import logging
import os

from dotenv import load_dotenv
from litellm import completion

logger = logging.getLogger(__name__)


class AIExecutor:
    """Executes prompts via LiteLLM with support for multiple AI providers.

    This executor supports:
    - OpenAI: gpt-4o, gpt-4-turbo, gpt-3.5-turbo
    - Anthropic: claude-3-5-sonnet, claude-3-opus, claude-3-haiku
    - Mistral: mistral/mistral-large, mistral/codestral-latest
    - Ollama (local): ollama/llama2, ollama/devstral, ollama/mistral
    - 100+ other providers via LiteLLM

    Configuration is loaded from .env file with the following variables:
    - OPENAI_API_KEY: OpenAI API key
    - ANTHROPIC_API_KEY: Anthropic API key
    - MISTRAL_API_KEY: Mistral API key
    - DEFAULT_LLM_MODEL: Model to use when provider not specified (default: gpt-4o-mini)
    - LITELLM_TIMEOUT: Timeout for API requests in seconds (default: 60)

    Examples:
        >>> executor = AIExecutor()
        >>> response = executor.execute_prompt(
        ...     system_prompt="You are a helpful assistant",
        ...     user_input="Explain recursion",
        ...     provider="gpt-4o"
        ... )
        >>> print(response)
        "Recursion is when a function calls itself..."

        >>> # Using local Ollama model
        >>> response = executor.execute_prompt(
        ...     system_prompt="You are a code generator",
        ...     user_input="Write a Python function",
        ...     provider="ollama/devstral"
        ... )
    """

    def __init__(self) -> None:
        """Initialize AI executor and load environment configuration.

        Loads API keys and configuration from .env file using python-dotenv.
        Sets default model to gpt-4o-mini if not configured.
        """
        load_dotenv()  # Load .env file
        self.default_model = os.getenv("DEFAULT_LLM_MODEL", "gpt-4o-mini")
        logger.debug(f"AIExecutor initialized with default model: {self.default_model}")

    def validate_connection(self, provider: str | None = None) -> None:
        """Validate connection to AI provider with a minimal test request.

        Args:
            provider: AI model to test (e.g., "gpt-4o", "ollama/devstral")
                     If None, uses DEFAULT_LLM_MODEL from environment

        Raises:
            AIExecutionError: If connection test fails (auth, network, etc.)

        Examples:
            >>> executor = AIExecutor()
            >>> executor.validate_connection("gpt-4o-mini")  # Test connection
        """
        model = provider or self.default_model
        logger.debug(f"Validating connection to {model}...")

        try:
            # Send minimal test request
            _ = completion(
                model=model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1,
                timeout=10,  # Short timeout for validation
            )
            logger.info(f"✓ Successfully connected to {model}")
        except Exception as e:
            error_msg = f"Connection test failed for {model}: {e}"
            logger.error(error_msg)
            raise AIExecutionError(error_msg) from e

    def execute_prompt(
        self, system_prompt: str, user_input: str, provider: str | None = None
    ) -> str:
        """Execute a prompt via LiteLLM and return the AI's response.

        Args:
            system_prompt: System prompt (context, role, instructions)
                          Usually the content of the .md prompt file
            user_input: User message/input for the AI
                       From the 'input' field in the test scenario
            provider: AI model to use (e.g., "gpt-4o", "claude-3-5-sonnet", "ollama/devstral")
                     If None, uses DEFAULT_LLM_MODEL from environment

        Returns:
            The AI's response as a string

        Raises:
            AIExecutionError: If the AI execution fails due to:
                - Authentication errors (invalid API key)
                - Rate limiting
                - Timeout (default 60s)
                - Network errors
                - Invalid model name
                - Any other API errors

        Examples:
            >>> executor = AIExecutor()
            >>> response = executor.execute_prompt(
            ...     system_prompt="You are a Python expert",
            ...     user_input="Explain list comprehensions",
            ...     provider="gpt-4o-mini"
            ... )

            >>> # Will use DEFAULT_LLM_MODEL from .env
            >>> response = executor.execute_prompt(
            ...     system_prompt="System prompt",
            ...     user_input="User input"
            ... )
        """
        model = provider or self.default_model
        logger.debug(f"Executing prompt with model: {model}")

        try:
            response = completion(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                ],
                timeout=60,  # 60 second timeout
            )

            # Extract response text from LiteLLM response object
            response_text: str = str(response.choices[0].message.content)
            logger.debug(
                f"Successfully executed prompt with {model}, "
                f"response length: {len(response_text)}"
            )

            return response_text

        except Exception as e:
            # Wrap all exceptions in AIExecutionError for consistent error handling
            error_msg = f"Failed to execute prompt with {model}: {e}"
            logger.error(error_msg)
            raise AIExecutionError(error_msg) from e


class AIExecutionError(Exception):
    """Exception raised when AI execution fails.

    This exception wraps all errors that occur during AI prompt execution,
    including:
    - Authentication errors (invalid/missing API keys)
    - Rate limiting errors
    - Timeout errors
    - Network errors
    - Invalid model errors
    - API service errors

    The original exception is preserved as the cause (__cause__).

    Examples:
        >>> try:
        ...     executor.execute_prompt("prompt", "input", "invalid-model")
        ... except AIExecutionError as e:
        ...     print(f"AI execution failed: {e}")
        ...     # Access original exception via e.__cause__
    """

    pass
