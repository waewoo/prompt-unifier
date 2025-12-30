"""Tests for AI executor that executes prompts via LiteLLM.

This module tests the AIExecutor class for executing prompts
with various AI providers through LiteLLM's unified interface.
"""

from unittest.mock import MagicMock, patch

import pytest

from prompt_unifier.ai.executor import AIExecutionError, AIExecutor


class TestAIExecutor:
    """Tests for AIExecutor class."""

    @patch("prompt_unifier.ai.executor.completion")
    @patch("prompt_unifier.ai.executor.load_dotenv")
    def test_validate_connection_success(
        self, mock_load_dotenv: MagicMock, mock_completion: MagicMock
    ) -> None:
        """Test successful connection validation."""
        # Setup mock response
        mock_response = MagicMock()
        mock_completion.return_value = mock_response

        # Execute
        executor = AIExecutor()
        executor.validate_connection("gpt-4o-mini")  # Should not raise

        # Assert
        mock_completion.assert_called_once()
        call_args = mock_completion.call_args
        assert call_args.kwargs["model"] == "gpt-4o-mini"
        assert call_args.kwargs["max_tokens"] == 1
        assert call_args.kwargs["timeout"] == 10

    @patch("prompt_unifier.ai.executor.completion")
    @patch("prompt_unifier.ai.executor.load_dotenv")
    def test_validate_connection_failure(
        self, mock_load_dotenv: MagicMock, mock_completion: MagicMock
    ) -> None:
        """Test connection validation with authentication error."""
        # Setup mock to raise authentication error
        mock_completion.side_effect = Exception("AuthenticationError: Invalid API key")

        # Execute and assert
        executor = AIExecutor()
        with pytest.raises(AIExecutionError) as exc_info:
            executor.validate_connection("gpt-4o")

        assert "Connection test failed" in str(exc_info.value)
        assert "Invalid API key" in str(exc_info.value)

    @patch("prompt_unifier.ai.executor.completion")
    @patch("prompt_unifier.ai.executor.load_dotenv")
    def test_execute_prompt_success(
        self, mock_load_dotenv: MagicMock, mock_completion: MagicMock
    ) -> None:
        """Test successful prompt execution with mocked LiteLLM response."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Mocked AI response about recursion"
        mock_completion.return_value = mock_response

        # Execute
        executor = AIExecutor()
        result = executor.execute_prompt(
            system_prompt="You are a helpful programming tutor",
            user_input="Explain recursion",
            provider="gpt-4o",
        )

        # Assert
        assert result == "Mocked AI response about recursion"
        mock_completion.assert_called_once()
        call_args = mock_completion.call_args
        assert call_args.kwargs["model"] == "gpt-4o"
        assert len(call_args.kwargs["messages"]) == 2
        assert call_args.kwargs["messages"][0]["role"] == "system"
        assert call_args.kwargs["messages"][1]["role"] == "user"

    @patch("prompt_unifier.ai.executor.completion")
    @patch("prompt_unifier.ai.executor.load_dotenv")
    @patch("prompt_unifier.ai.executor.os.getenv")
    def test_execute_prompt_uses_default_model(
        self, mock_getenv: MagicMock, mock_load_dotenv: MagicMock, mock_completion: MagicMock
    ) -> None:
        """Test that default model is used when provider is None."""
        # Setup
        mock_getenv.return_value = "gpt-4o-mini"
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Response"
        mock_completion.return_value = mock_response

        # Execute without provider
        executor = AIExecutor()
        executor.execute_prompt(
            system_prompt="System prompt",
            user_input="User input",
            provider=None,  # Should use default
        )

        # Assert default model was used
        call_args = mock_completion.call_args
        assert call_args.kwargs["model"] == "gpt-4o-mini"

    @patch("prompt_unifier.ai.executor.completion")
    @patch("prompt_unifier.ai.executor.load_dotenv")
    def test_execute_prompt_api_error(
        self, mock_load_dotenv: MagicMock, mock_completion: MagicMock
    ) -> None:
        """Test that API errors are wrapped in AIExecutionError."""
        # Setup mock to raise exception
        mock_completion.side_effect = Exception("API rate limit exceeded")

        # Execute and expect error
        executor = AIExecutor()
        with pytest.raises(AIExecutionError) as exc_info:
            executor.execute_prompt(system_prompt="System", user_input="Input", provider="gpt-4o")

        # Assert error message includes model and original error
        assert "gpt-4o" in str(exc_info.value)
        assert "API rate limit exceeded" in str(exc_info.value)

    @patch("prompt_unifier.ai.executor.completion")
    @patch("prompt_unifier.ai.executor.load_dotenv")
    def test_execute_prompt_timeout(
        self, mock_load_dotenv: MagicMock, mock_completion: MagicMock
    ) -> None:
        """Test that timeout exceptions are handled properly."""
        # Setup mock to raise timeout
        mock_completion.side_effect = TimeoutError("Request timeout after 60s")

        # Execute and expect AIExecutionError
        executor = AIExecutor()
        with pytest.raises(AIExecutionError) as exc_info:
            executor.execute_prompt(
                system_prompt="Long prompt", user_input="Complex task", provider="claude-3-opus"
            )

        assert "claude-3-opus" in str(exc_info.value)
        assert "timeout" in str(exc_info.value).lower()

    @patch("prompt_unifier.ai.executor.completion")
    @patch("prompt_unifier.ai.executor.load_dotenv")
    def test_execute_prompt_with_ollama(
        self, mock_load_dotenv: MagicMock, mock_completion: MagicMock
    ) -> None:
        """Test execution with local Ollama model."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "def add(a, b):\n    return a + b"
        mock_completion.return_value = mock_response

        # Execute with ollama/ prefix
        executor = AIExecutor()
        result = executor.execute_prompt(
            system_prompt="You are a Python code generator",
            user_input="Write a function to add two numbers",
            provider="ollama/devstral",
        )

        # Assert
        assert "def add" in result
        call_args = mock_completion.call_args
        assert call_args.kwargs["model"] == "ollama/devstral"

    @patch("prompt_unifier.ai.executor.load_dotenv")
    def test_init_loads_dotenv(self, mock_load_dotenv: MagicMock) -> None:
        """Test that __init__ loads environment variables from .env."""
        AIExecutor()
        mock_load_dotenv.assert_called_once()

    @patch("prompt_unifier.ai.executor.completion")
    @patch("prompt_unifier.ai.executor.load_dotenv")
    def test_execute_prompt_with_timeout_param(
        self, mock_load_dotenv: MagicMock, mock_completion: MagicMock
    ) -> None:
        """Test that timeout parameter is passed to completion call."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Response"
        mock_completion.return_value = mock_response

        # Execute
        executor = AIExecutor()
        executor.execute_prompt(system_prompt="System", user_input="Input", provider="gpt-4o")

        # Assert timeout was passed
        call_args = mock_completion.call_args
        assert call_args.kwargs["timeout"] == 60
