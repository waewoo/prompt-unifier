from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from prompt_manager.cli.commands import MockToolHandler
from prompt_manager.cli.main import app

runner = CliRunner()


@patch("prompt_manager.cli.commands.ToolHandlerRegistry")
def test_deploy_command_triggers_rollback_on_failure(mock_registry_class):
    """Test that the deploy command triggers rollback on handler failure."""

    # Create mock handlers
    handler1 = MockToolHandler("handler1")
    handler2 = MockToolHandler("handler2", should_fail=True)
    handler3 = MockToolHandler("handler3")

    # Mock the registry to return our mock handlers
    mock_registry_instance = MagicMock()
    mock_registry_instance.get_all_handlers.return_value = [handler1, handler2, handler3]
    mock_registry_class.return_value = mock_registry_instance

    # Run the deploy command
    result = runner.invoke(app, ["deploy", "test_prompt"])

    # Assert that the command ran successfully
    assert result.exit_code == 0

    # Assert that deploy was called on all handlers
    assert len(handler1.deployed_prompts) == 1
    assert len(handler2.deployed_prompts) == 0  # Failed
    assert len(handler3.deployed_prompts) == 1

    # Assert that rollback was called on the failing handler
    assert not handler1.rolled_back
    assert handler2.rolled_back
    assert not handler3.rolled_back

    # Check the output for confirmation messages
    assert "Deploying to handler1..." in result.stdout
    assert "Deployment to handler1 successful" in result.stdout
    assert "Deploying to handler2..." in result.stdout
    assert "Deployment to handler2 failed" in result.stdout
    assert "Rolling back handler2..." in result.stdout
    assert "Rollback for handler2 complete" in result.stdout
    assert "Deploying to handler3..." in result.stdout
    assert "Deployment to handler3 successful" in result.stdout
